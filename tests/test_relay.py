"""中継器のテスト。

GPIO は gpiozero の MockFactory で模擬し、サーバは websockets で立てた
簡易サーバで模擬する。Raspberry Pi でなくても（Mac でも）実行できる。

    pip install gpiozero websockets pytest
    python3 -m pytest
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
import websockets
from gpiozero import Device
from gpiozero.pins.mock import MockFactory

import buzz_relay as relay


CREATED: list = []


@pytest.fixture(autouse=True)
def mock_pins():
    Device.pin_factory = MockFactory()
    yield
    # 点滅スレッドを残したままにしないよう、作った GPIO 機器を閉じる
    while CREATED:
        CREATED.pop().close()
    Device.pin_factory.reset()


# ------------------------------------------------------------------ URL と設定


def test_endpoint_local():
    assert relay.build_endpoint("http://192.168.2.102:8000/player") == (
        "ws://192.168.2.102:8000/ws",
        "http://192.168.2.102:8000",
    )


def test_endpoint_cloud_keeps_event_and_key_only():
    ws_url, origin = relay.build_endpoint("https://quiz.example.run.app/player?event=e1&key=k1&x=1")
    assert ws_url == "wss://quiz.example.run.app/ws?event=e1&key=k1"
    assert origin == "https://quiz.example.run.app"


@pytest.mark.parametrize(
    "url",
    ["http://192.168.2..102:8000/player", "http://192.168.2.102:80x0/player", "192.168.2.102:8000/player"],
)
def test_endpoint_rejects_typos(url):
    with pytest.raises(relay.ConfigError):
        relay.build_endpoint(url)


def test_redact_hides_key():
    assert "k1" not in relay.redact("wss://h/ws?event=e1&key=k1")


def config_data(**overrides):
    data = {
        "url": "http://192.168.2.102:8000/player",
        "status_led": 22,
        "buttons": [{"name": "物理1", "button": 17, "led": 27}, {"name": "物理2", "button": 5}],
    }
    data.update(overrides)
    return data


def test_parse_config():
    config = relay.parse_config(config_data())
    assert [b.name for b in config.buttons] == ["物理1", "物理2"]
    assert config.buttons[1].led is None
    assert config.status_led == 22


def test_url_override_wins():
    config = relay.parse_config(config_data(), url_override="http://10.0.0.5:8000/player")
    assert config.url == "http://10.0.0.5:8000/player"


@pytest.mark.parametrize(
    "overrides",
    [
        {"buttons": []},
        {"buttons": [{"name": "", "button": 17}]},
        {"buttons": [{"name": "あいうえおかきくけこさしす", "button": 17}]},  # 13 文字
        {"buttons": [{"name": "A", "button": 17}, {"name": "B", "button": 17}]},
        {"buttons": [{"name": "A", "button": 17, "led": 22}]},  # status_led と重複
        {"buttons": [{"name": "A", "button": 17}, {"name": "A", "button": 5}]},
        {"buttons": [{"name": "A", "button": 40}]},
        {"buttons": [{"name": "A", "button": "17"}]},
        {"url": ""},
    ],
)
def test_parse_config_rejects(overrides):
    with pytest.raises(relay.ConfigError):
        relay.parse_config(config_data(**overrides))


def test_example_config_is_valid():
    path = Path(__file__).resolve().parent.parent / "config.example.toml"
    relay.load_config(path)


# ------------------------------------------------------------------ 状態と LED


def make_client(tmp_path, name="物理1", button=17, led=27):
    ws_url, origin = relay.build_endpoint("http://127.0.0.1:1/player")
    client = relay.ButtonClient(
        relay.ButtonConfig(name, button, led), ws_url, origin, relay.TokenStore(tmp_path / "t.json"), lambda: None
    )
    CREATED.append(client)
    return client


def state(phase, round_id=1, buzzed=None, locked=()):
    return {
        "type": "room_state",
        "round_id": round_id,
        "phase": phase,
        "buzzed": buzzed,
        "players": [{"id": "p_1", "name": "物理1", "connected": True, "locked_out": "p_1" in locked}],
    }


def test_led_follows_room_state(tmp_path):
    client = make_client(tmp_path)
    client.ws = object()  # 接続中とみなす
    client.handle({"type": "welcome", "player_id": "p_1", "token": "t1", "role": "player"})
    client.handle(state("reading"))
    assert client.led_mode == "off"

    client.handle({"type": "buzz_accepted", "round_id": 1, "player_id": "p_1", "name": "物理1"})
    assert client.led_mode == "on"
    client.handle(state("check", buzzed={"player_id": "p_1", "name": "物理1"}))
    assert client.led_mode == "on"

    client.handle(state("result", locked=("p_1",)))
    assert client.led_mode == "locked"
    client.handle(state("reading", round_id=2))
    assert client.led_mode == "off"


def test_other_players_buzz_does_not_light(tmp_path):
    client = make_client(tmp_path)
    client.ws = object()
    client.handle({"type": "welcome", "player_id": "p_1", "token": "t1", "role": "player"})
    client.handle({"type": "buzz_accepted", "round_id": 1, "player_id": "p_2", "name": "スマホ"})
    assert client.led_mode == "off"


def test_offline_blinks(tmp_path):
    client = make_client(tmp_path)
    client.refresh()
    assert client.led_mode == "offline"


def test_status_led(tmp_path):
    a, b = make_client(tmp_path), make_client(tmp_path, "物理2", 5, 6)
    status = relay.StatusLed(22)
    CREATED.append(status.led)
    for c in (a, b):
        c.ws, c.player_id = object(), "p"
    status.update([a, b])
    assert status.mode == "on"
    b.ws = None
    status.update([a, b])
    assert status.mode == "offline"
    a.stopped = b.stopped = True
    status.update([a, b])
    assert status.mode == "off"


# ------------------------------------------------------------------ 模擬サーバとの通信


class FakeServer:
    """本体の /ws の回答者まわりだけを真似る。"""

    def __init__(self, close_code: int | None = None, reject_status: int | None = None):
        self.close_code = close_code
        self.reject_status = reject_status
        self.joins: list[dict] = []
        self.buzzes: list[dict] = []
        self.origins: list[str | None] = []

    async def handler(self, ws):
        self.origins.append(ws.request.headers.get("Origin"))
        join = json.loads(await ws.recv())
        self.joins.append(join)
        token = join.get("token") or f"token{len(self.joins)}"
        await ws.send(json.dumps({"type": "welcome", "player_id": "p_1", "token": token, "role": "player"}))
        await ws.send(json.dumps(state("reading")))
        if self.close_code is not None:
            await ws.close(code=self.close_code)
            return
        async for raw in ws:
            message = json.loads(raw)
            self.buzzes.append(message)
            await ws.send(json.dumps({"type": "buzz_accepted", "round_id": 1, "player_id": "p_1", "name": "物理1"}))

    def process_request(self, connection, request):
        if self.reject_status is not None:
            return connection.respond(self.reject_status, "forbidden\n")
        return None


async def start(server: FakeServer):
    return await websockets.serve(server.handler, "127.0.0.1", 0, process_request=server.process_request)


def client_for(port, tmp_path, query=""):
    ws_url, origin = relay.build_endpoint(f"http://127.0.0.1:{port}/player{query}")
    return relay.ButtonClient(
        relay.ButtonConfig("物理1", 17, 27), ws_url, origin, relay.TokenStore(tmp_path / "t.json"), lambda: None
    )


async def cancel(task):
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def wait_for(condition, timeout=3.0):
    loop = asyncio.get_running_loop()
    end = loop.time() + timeout
    while not condition():
        if loop.time() > end:
            raise AssertionError("時間内に条件が満たされませんでした")
        await asyncio.sleep(0.02)


def test_join_buzz_and_token_reuse(tmp_path):
    async def scenario():
        server = FakeServer()
        async with await start(server) as ws_server:
            port = ws_server.sockets[0].getsockname()[1]
            client = client_for(port, tmp_path)
            task = asyncio.create_task(client.run())
            await wait_for(lambda: client.round_id == 1)
            assert server.joins[0] == {"type": "join", "name": "物理1", "token": None}
            assert server.origins[0] == f"http://127.0.0.1:{port}"

            # ボタンを押す
            pin = Device.pin_factory.pin(17)
            pin.drive_low()
            await wait_for(lambda: client.led_mode == "on")
            pin.drive_high()
            assert server.buzzes[0]["type"] == "buzz" and server.buzzes[0]["round_id"] == 1

            await cancel(task)
            client.close()

            # 再起動しても保存した token で入り直す
            again = client_for(port, tmp_path)
            task = asyncio.create_task(again.run())
            await wait_for(lambda: len(server.joins) == 2)
            assert server.joins[1]["token"] == "token1"
            await cancel(task)
            again.close()

    asyncio.run(scenario())


def test_stops_when_tournament_ended(tmp_path):
    async def scenario():
        server = FakeServer(close_code=4404)
        async with await start(server) as ws_server:
            port = ws_server.sockets[0].getsockname()[1]
            client = client_for(port, tmp_path, "?event=e1&key=k1")
            await asyncio.wait_for(client.run(), timeout=5)
            assert client.stopped and client.led_mode == "off"
            assert len(server.joins) == 1  # 再接続していない
            client.close()

    asyncio.run(scenario())


def test_stops_when_rejected_before_accept(tmp_path):
    async def scenario():
        server = FakeServer(reject_status=403)
        async with await start(server) as ws_server:
            port = ws_server.sockets[0].getsockname()[1]
            client = client_for(port, tmp_path, "?event=e1&key=bad")
            await asyncio.wait_for(client.run(), timeout=5)
            assert client.stopped
            client.close()

    asyncio.run(scenario())
