#!/usr/bin/env python3
"""trans-ai-quiz の物理早押しボタン中継器。

Raspberry Pi の GPIO に繋いだボタンを、ボタン 1 つにつき参加者 1 人として
trans-ai-quiz のサーバへ WebSocket で接続する。スマホの回答者画面と同じ
メッセージ（join / buzz）だけを使うので、本体側の変更は要らない。

使い方:
    python3 buzz_relay.py --config config.toml
    python3 buzz_relay.py --config config.toml --url http://192.168.2.102:8000/player

ボタンの LED:
    回答権を取った       点灯
    お手つき             0.5 秒ごとに点滅（次の問題で消える）
    サーバ未接続         2 秒ごとに短く点滅
    大会終了・URL 無効    消灯（そのボタンは接続をやめる）
    それ以外             消灯

状態表示 LED（任意）:
    全ボタンが接続中     点灯
    未接続のボタンがある 1 秒ごとに短く点滅
    全ボタンが停止       消灯
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

import websockets
from gpiozero import LED, Button

log = logging.getLogger("buzz_relay")

DEFAULT_TOKEN_FILE = Path.home() / ".config" / "trans-ai-quiz-buzzer" / "tokens.json"

# 自分が回答権を持っている間、LED を点けておく phase
HOLDING_PHASES = {"buzzed", "check"}

# Cloud Run 版が「大会終了」「参加 URL 無効」で接続を閉じるときのコード。
# 再接続しても入れないので、そのボタンは接続をやめる。
FINAL_CLOSE_CODES = {4403, 4404}
# 接続を受け付ける前に拒否されたときの HTTP ステータス。意味は上と同じ
FINAL_HTTP_STATUSES = {401, 403, 404, 410}

# 投影に出す名前の上限（本体の MAX_NAME_LENGTH と同じ）
MAX_NAME_LENGTH = 12


# ------------------------------------------------------------------ 設定


class ConfigError(ValueError):
    """設定ファイルや --url の誤り。起動時に 1 行で知らせる。"""


@dataclass(frozen=True)
class ButtonConfig:
    name: str
    button: int
    led: int | None


@dataclass(frozen=True)
class Config:
    url: str
    buttons: tuple[ButtonConfig, ...]
    status_led: int | None = None
    token_file: Path = DEFAULT_TOKEN_FILE


def build_endpoint(player_url: str) -> tuple[str, str]:
    """参加者用 URL から WebSocket の URL と Origin を組み立てる。

    Cloud Run 版は event / key のクエリと、公開 URL と一致する Origin を要求する。
    ローカル版はどちらも見ないので、同じ処理で両方に対応できる。
    """
    parts = urlsplit(player_url.strip())
    if parts.scheme not in ("http", "https"):
        raise ConfigError("url は http:// か https:// で始まる参加者用 URL を指定してください")
    host = parts.hostname or ""
    if not host or any(label == "" for label in host.split(".")):
        # 「192.168.2..102」のような打ち間違いは、接続時に分かりにくい例外になるので先に弾く
        raise ConfigError(f"url のホスト名が不正です（ドットの重複などを確認してください）: {host!r}")
    try:
        parts.port  # ポート番号が数値でなければここで例外になる
    except ValueError:
        raise ConfigError(f"url のポート番号が不正です: {parts.netloc!r}") from None
    ws_scheme = "wss" if parts.scheme == "https" else "ws"
    query = {k: v[0] for k, v in parse_qs(parts.query).items() if k in ("event", "key")}
    ws_url = urlunsplit((ws_scheme, parts.netloc, "/ws", urlencode(query), ""))
    origin = f"{parts.scheme}://{parts.netloc}"
    return ws_url, origin


def redact(ws_url: str) -> str:
    """ログに参加キーを残さない。"""
    parts = urlsplit(ws_url)
    query = {k: ("***" if k == "key" else v[0]) for k, v in parse_qs(parts.query).items()}
    return urlunsplit(parts._replace(query=urlencode(query, safe="*")))


def _pin(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 27:
        raise ConfigError(f"{where} には GPIO 番号（BCM、0〜27）を整数で書いてください: {value!r}")
    return value


def parse_config(data: dict[str, Any], url_override: str | None = None) -> Config:
    url = url_override or data.get("url")
    if not isinstance(url, str) or not url.strip():
        raise ConfigError("url（参加者用 URL）を設定ファイルか --url で指定してください")
    build_endpoint(url)

    raw_buttons = data.get("buttons")
    if not isinstance(raw_buttons, list) or not raw_buttons:
        raise ConfigError("[[buttons]] を 1 つ以上書いてください")

    buttons: list[ButtonConfig] = []
    for index, raw in enumerate(raw_buttons, start=1):
        where = f"{index} 番目の [[buttons]]"
        if not isinstance(raw, dict):
            raise ConfigError(f"{where} の形式が不正です")
        name = raw.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ConfigError(f"{where} に name（投影に出す名前）を書いてください")
        if len(name.strip()) > MAX_NAME_LENGTH:
            raise ConfigError(f"{where} の name は {MAX_NAME_LENGTH} 文字以内にしてください: {name!r}")
        led = raw.get("led")
        buttons.append(ButtonConfig(
            name=name.strip(),
            button=_pin(raw.get("button"), f"{where} の button"),
            led=None if led is None else _pin(led, f"{where} の led"),
        ))

    status_led = data.get("status_led")
    if status_led is not None:
        status_led = _pin(status_led, "status_led")

    # 同じピンを 2 か所で使うと、押下や点灯が混ざる
    used: dict[int, str] = {}
    pins = [(b.button, f"{b.name} の button") for b in buttons]
    pins += [(b.led, f"{b.name} の led") for b in buttons if b.led is not None]
    if status_led is not None:
        pins.append((status_led, "status_led"))
    for pin, label in pins:
        if pin in used:
            raise ConfigError(f"GPIO{pin} が重複しています（{used[pin]} と {label}）")
        used[pin] = label

    names = [b.name for b in buttons]
    duplicated = {n for n in names if names.count(n) > 1}
    if duplicated:
        raise ConfigError(f"name が重複しています: {', '.join(sorted(duplicated))}")

    token_file = data.get("token_file")
    return Config(
        url=url.strip(),
        buttons=tuple(buttons),
        status_led=status_led,
        token_file=Path(token_file).expanduser() if token_file else DEFAULT_TOKEN_FILE,
    )


def load_config(path: Path, url_override: str | None = None) -> Config:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(f"設定ファイルがありません: {path}") from None
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"設定ファイルの書式が不正です（{path}）: {error}") from None
    return parse_config(data, url_override)


# ------------------------------------------------------------------ token


class TokenStore:
    """再接続時に同じ参加者へ戻るための token を保存する。

    サーバ（と Cloud Run 版の大会）とボタンのピンごとに持つ。名前は鍵に含めない。
    本体は token が一致すると名前だけを更新するので、設定の name を変えて
    再起動すれば、同じ参加者のまま改名できる。
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def _read(self) -> dict[str, str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def get(self, key: str) -> str | None:
        return self._read().get(key)

    def put(self, key: str, token: str) -> None:
        data = self._read()
        data[key] = token
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as error:
            # 保存できなくても参加はできる。再起動時に別の参加者になるだけ
            log.warning("token を保存できませんでした: %s", error)


def token_key(ws_url: str, button_pin: int) -> str:
    parts = urlsplit(ws_url)
    event = parse_qs(parts.query).get("event", [""])[0]
    return f"{parts.scheme}://{parts.netloc}?event={event}|gpio{button_pin}"


# ------------------------------------------------------------------ ボタン 1 つ分


class LedLike:
    """LED を付けないボタン用の何もしない LED。"""

    value = 0

    def on(self) -> None: ...
    def off(self) -> None: ...
    def blink(self, **_: Any) -> None: ...
    def close(self) -> None: ...


def _final_status(error: BaseException) -> int | None:
    """接続前に拒否されたときの HTTP ステータス（websockets の版で属性が違う）。"""
    status = getattr(error, "status_code", None)  # websockets 10
    if status is None:
        response = getattr(error, "response", None)  # websockets 11 以降
        status = getattr(response, "status_code", None)
    return status if isinstance(status, int) else None


class ButtonClient:
    """ボタン 1 つを参加者 1 人としてサーバへ繋ぐ。"""

    def __init__(
        self,
        config: ButtonConfig,
        ws_url: str,
        origin: str,
        tokens: TokenStore,
        on_change: Callable[[], None],
    ) -> None:
        self.config = config
        self.name = config.name
        self.ws_url = ws_url
        self.origin = origin
        self.tokens = tokens
        self.token_key = token_key(ws_url, config.button)
        self.on_change = on_change

        self.button = Button(config.button, bounce_time=0.02)
        self.led: Any = LED(config.led) if config.led is not None else LedLike()
        self.led_mode = ""
        self.closed = False

        self.ws: Any = None
        self.stopped = False  # 大会終了・URL 無効で接続をやめた
        self.player_id: str | None = None
        self.round_id: int | None = None
        self.phase = "idle"
        self.buzzed_id: str | None = None
        self.locked_out = False

        self.loop: asyncio.AbstractEventLoop | None = None
        self.presses: asyncio.Queue[float] = asyncio.Queue()

    @property
    def connected(self) -> bool:
        return self.ws is not None and self.player_id is not None

    # ---------------------------------------------------------- LED

    def set_led(self, mode: str) -> None:
        # 終了処理の後に点滅を始めると、閉じた LED へ点滅スレッドが書き込んで例外になる
        if self.closed or mode == self.led_mode:
            return
        self.led_mode = mode
        if mode == "on":
            self.led.on()
        elif mode == "locked":
            self.led.blink(on_time=0.5, off_time=0.5)
        elif mode == "offline":
            self.led.blink(on_time=0.1, off_time=1.9)
        else:
            self.led.off()

    def refresh(self) -> None:
        if self.stopped:
            self.set_led("off")
        elif not self.connected:
            self.set_led("offline")
        elif self.buzzed_id == self.player_id and self.phase in HOLDING_PHASES:
            self.set_led("on")
        elif self.locked_out:
            self.set_led("locked")
        else:
            self.set_led("off")
        self.on_change()

    # ---------------------------------------------------------- ボタン

    def on_press(self) -> None:
        # gpiozero のコールバックは別スレッドで動くため、イベントループへ渡す
        if self.loop is not None:
            self.loop.call_soon_threadsafe(self.presses.put_nowait, time.time())

    async def send_presses(self) -> None:
        while True:
            pressed_at = await self.presses.get()
            if not self.connected or self.round_id is None:
                log.info("[%s] 押下を無視（未接続）", self.name)
                continue
            try:
                await self.ws.send(json.dumps({
                    "type": "buzz",
                    "round_id": self.round_id,
                    # 端末時計は判定に使われない（本体側でログ用）
                    "client_sent_at": int(pressed_at * 1000),
                }))
                log.info("[%s] buzz 送信 round_id=%s", self.name, self.round_id)
            except websockets.WebSocketException as error:
                log.info("[%s] buzz を送れませんでした: %s", self.name, error)

    # ---------------------------------------------------------- 受信

    def handle(self, message: dict[str, Any]) -> None:
        kind = message.get("type")
        if kind == "welcome":
            self.player_id = message["player_id"]
            self.tokens.put(self.token_key, message["token"])
            log.info("[%s] 参加しました player_id=%s", self.name, self.player_id)
        elif kind == "room_state":
            self.round_id = message["round_id"]
            self.phase = message["phase"]
            buzzed = message.get("buzzed")
            self.buzzed_id = buzzed["player_id"] if buzzed else None
            me = next((p for p in message.get("players", []) if p.get("id") == self.player_id), None)
            self.locked_out = bool(me and me.get("locked_out"))
        elif kind == "buzz_accepted":
            # room_state より先に届く。LED を最速で点けるためにここでも反映する
            self.buzzed_id = message["player_id"]
            self.phase = "buzzed"
            if self.buzzed_id == self.player_id:
                log.info("[%s] 回答権を取りました", self.name)
        elif kind == "buzz_rejected":
            log.info("[%s] buzz 不成立 reason=%s", self.name, message.get("reason"))
        elif kind == "error":
            log.warning("[%s] サーバからのエラー: %s", self.name, message.get("message", message))
        self.refresh()

    async def session(self) -> None:
        async with websockets.connect(self.ws_url, origin=self.origin, open_timeout=10) as ws:
            self.ws = ws
            await ws.send(json.dumps({
                "type": "join",
                "name": self.name,
                "token": self.tokens.get(self.token_key),
            }))
            try:
                async for raw in ws:
                    self.handle(json.loads(raw))
            except websockets.ConnectionClosed:
                pass  # 閉じられた理由は下で close_code を見て判断する
            code = ws.close_code
            if code in FINAL_CLOSE_CODES:
                self.stop(f"サーバが接続を終了しました（code={code}）")
            else:
                log.warning("[%s] 切断されました（code=%s）", self.name, code)

    def stop(self, reason: str) -> None:
        if not self.stopped:
            log.warning("[%s] 接続をやめます: %s", self.name, reason)
        self.stopped = True

    async def run(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.button.when_pressed = self.on_press
        self.refresh()
        sender = asyncio.create_task(self.send_presses())
        delay = 1.0
        try:
            while not self.stopped:
                try:
                    log.info("[%s] 接続します %s", self.name, redact(self.ws_url))
                    await self.session()
                    delay = 1.0
                except websockets.InvalidHandshake as error:
                    status = _final_status(error)
                    if status in FINAL_HTTP_STATUSES:
                        self.stop(f"接続を拒否されました（HTTP {status}）。参加 URL を確認してください")
                    else:
                        log.warning("[%s] 接続できませんでした: %s", self.name, error)
                except (OSError, websockets.WebSocketException, asyncio.TimeoutError) as error:
                    log.warning("[%s] 切断されました: %s", self.name, error)
                finally:
                    self.ws = None
                    self.player_id = None if self.stopped else self.player_id
                    self.refresh()
                if self.stopped:
                    break
                await asyncio.sleep(delay)
                delay = min(delay * 2, 10.0)
        finally:
            sender.cancel()

    def close(self) -> None:
        # 点滅中にいきなり close すると点滅スレッドが例外を出すので、先に止める
        self.closed = True
        self.led.off()
        self.button.close()
        self.led.close()


# ------------------------------------------------------------------ 全体


class StatusLed:
    """全ボタンの接続状態をまとめて 1 つの LED で示す。"""

    def __init__(self, pin: int | None) -> None:
        self.led: Any = LED(pin) if pin is not None else LedLike()
        self.mode = ""
        self.closed = False

    def update(self, clients: list[ButtonClient]) -> None:
        if self.closed:
            return
        active = [c for c in clients if not c.stopped]
        if not active:
            mode = "off"
        elif all(c.connected for c in active):
            mode = "on"
        else:
            mode = "offline"
        if mode == self.mode:
            return
        self.mode = mode
        if mode == "on":
            self.led.on()
        elif mode == "offline":
            self.led.blink(on_time=0.1, off_time=0.9)
        else:
            self.led.off()

    def close(self) -> None:
        self.closed = True
        self.led.off()
        self.led.close()


async def run(config: Config) -> int:
    ws_url, origin = build_endpoint(config.url)
    tokens = TokenStore(config.token_file)
    status = StatusLed(config.status_led)
    clients: list[ButtonClient] = []

    def changed() -> None:
        status.update(clients)

    for button in config.buttons:
        clients.append(ButtonClient(button, ws_url, origin, tokens, changed))
    log.info("ボタン %d 個で起動します: %s", len(clients), ", ".join(c.name for c in clients))
    try:
        await asyncio.gather(*(client.run() for client in clients))
    finally:
        for client in clients:
            client.close()
        status.close()
    # 全ボタンが大会終了などで止まった。systemd に再起動させないため正常終了にする
    log.warning("すべてのボタンが接続をやめたので終了します")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="trans-ai-quiz の物理早押しボタン中継器")
    parser.add_argument("--config", type=Path, default=Path("config.toml"), help="設定ファイル（既定: config.toml）")
    parser.add_argument("--url", help="参加者用 URL。設定ファイルの url を上書きする")
    parser.add_argument("--verbose", action="store_true", help="websockets の詳細ログも出す")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )
    if not args.verbose:
        logging.getLogger("websockets").setLevel(logging.WARNING)

    try:
        config = load_config(args.config, args.url)
    except ConfigError as error:
        parser.error(str(error))
    try:
        return asyncio.run(run(config))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
