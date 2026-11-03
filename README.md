# trans-ai-quiz-buzzer

[trans-ai-quiz](https://github.com/takegg0311/trans-ai-quiz) のオンライン早押しに、**物理ボタンで参加する**ための中継器。
Raspberry Pi の GPIO に繋いだボタン 1 つを、参加者 1 人としてサーバへ接続する。

スマホから回答者画面を開けない人（iPhone の Safari で HTTP のページを開けない場合など）や、
スマホを持っていない人のための代替手段として使う。

```
[アーケードボタン] ─GPIO─ [Raspberry Pi] ─WiFi─ [trans-ai-quiz サーバ] ─ [出題者画面（投影）]
                                                     │
                                         [スマホの回答者] も同じルームに参加
```

- スマホの回答者画面と**同じメッセージだけ**を使う。trans-ai-quiz 本体の変更は要らない
- 早押しの判定（誰が最初か）は本体のサーバが行う。スマホの参加者と同じ条件で競う
- 回答権を取ると、ボタンの LED が点く。スマホ画面の「回答権」表示の代わり

## 必要なもの

| 部品 | 数 | 補足 |
| --- | --- | --- |
| Raspberry Pi 3B 以降 | 1 | Raspberry Pi OS（64-bit、Lite で可）。WiFi は 2.4GHz のみ（3B の場合） |
| microSD カード（16GB 以上）、5V 2.5A 電源 | 1 | |
| アーケードボタン | 参加者数 | 例: 三和電子 OBSF-30。端子は 110（2.8mm）ファストン |
| LED（回答権表示） | 参加者数 | 試作では赤色 LED（OSDR5113A など）。将来は 5V の LED 内蔵ボタンに置き換える |
| 抵抗 1kΩ | 参加者数 × 1〜2 | LED の電流制限、トランジスタのベース抵抗 |
| NPN トランジスタ 2SC1815-GR | 参加者数 | 5V の LED を点ける場合のみ。足の並びは購入品のデータシートで確認 |
| 状態表示用 LED と抵抗 | 1 | 任意。画面が無いので、無いと未接続に気づけない |
| ブレッドボード、ジャンパ線（**オス-メス**） | 1 式 | Pi の GPIO はオスのピンなので、メス側で受ける |
| 抵抗 10kΩ | 参加者数 | 任意。ケーブルを数 m に延ばすときの外付けプルアップ |
| タクトスイッチ | 1 | 任意。安全にシャットダウンするためのボタン |

本番でボタンを延長する場合は、加えて電線（AWG22〜24 のより線）とファストン端子の圧着工具が要る。

## ピンの割り当て

GPIO 番号は BCM 番号（`config.toml` に書く番号）。物理ピンは基板上の 1〜40 番。
Pi で `pinout` を実行すると、物理ピンの位置を図で確認できる。

| 用途 | GPIO（BCM） | 物理ピン |
| --- | --- | --- |
| ボタン 1 / LED 1 | 17 / 27 | 11 / 13 |
| ボタン 2 / LED 2 | 5 / 6 | 29 / 31 |
| ボタン 3 / LED 3 | 13 / 19 | 33 / 35 |
| ボタン 4 / LED 4 | 26 / 16 | 37 / 36 |
| ボタン 5 / LED 5 | 20 / 21 | 38 / 40 |
| ボタン 6 / LED 6 | 12 / 25 | 32 / 22 |
| ボタン 7 / LED 7 | 24 / 23 | 18 / 16 |
| ボタン 8 / LED 8 | 18 / 4 | 12 / 7 |
| 状態表示 LED | 22 | 15 |
| シャットダウンボタン | 3 | 5 |
| GND | — | 6, 9, 14, 20, 25, 30, 34, 39 |

次のピンはボタンや LED に使わない。

- GPIO0 / 1（HAT の識別用）
- GPIO2 / 3（基板上に 1.8kΩ のプルアップがある。GPIO3 はシャットダウンボタン専用にする）
- GPIO14 / 15（シリアル用）

## 配線

**配線は必ず Pi の電源を切ってから行う。** 5V（物理ピン 2・4）を GPIO に繋ぐと Pi が壊れる。

### ボタン

```
GPIO（ボタン） ── ボタンの端子1
GND           ── ボタンの端子2
```

Pi 内部のプルアップを使うので、抵抗は要らない。
ボタンの端子が 3 つ（COM・NO・NC）ある場合は COM と NO を使う。NC だと押していないときに押したと判定される。
ケーブルを数 m に延ばす場合は、GPIO と 3.3V の間に 10kΩ を足すとノイズに強くなる。

### LED（3.3V で直接点ける：試作）

```
GPIO（LED） ── 1kΩ ── LED の長い足（＋） ── LED の短い足（−） ── GND
```

### LED（5V をトランジスタで点ける：LED 内蔵ボタン用）

```
GPIO（LED） ── 1kΩ ── トランジスタの B
トランジスタの E ── GND
5V ── LED（＋）── LED（−）── トランジスタの C
```

LED 内蔵ボタンは LED 用の抵抗を内蔵していることが多い。その場合は LED の前に抵抗を入れない。
赤色 LED などの単体の LED を 5V で点ける場合は、LED の前に 1kΩ を入れる。
2SC1815 の足は、文字の面を手前・足を下にして左から E・C・B（東芝品と UTC 品）。購入品のデータシートで確認する。

### ブレッドボードの注意

- 同じ番号の a〜e の 5 穴、f〜j の 5 穴が内部で繋がっている。アルファベットが同じでも、番号が違えば繋がっていない
- 左右のマイナス（青線）の電源ラインは繋がっていない。GND は片側にまとめるか、左右をジャンパ線で繋ぐ

## セットアップ

### 1. Raspberry Pi OS を用意する

Raspberry Pi Imager で Raspberry Pi OS（64-bit）を書き込む。書き込む前の設定で WiFi・SSH・ユーザー名を入れておく。

### 2. 中継器を置く

```bash
sudo apt install -y git python3-gpiozero python3-websockets
git clone https://github.com/takegg0311/trans-ai-quiz-buzzer.git ~/trans-ai-quiz-buzzer
cd ~/trans-ai-quiz-buzzer
cp config.example.toml config.toml
```

`config.toml` を開き、`url` とボタンの一覧（`[[buttons]]`）を書き換える。

### 3. 本体のサーバを起動する（ローカル版）

本体側（Mac など）で、**`--host 0.0.0.0` を付けて**起動する。付けないと Pi から繋がらない。

```bash
cd server && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

起動ログに出る「参加者用」の URL を、`config.toml` の `url` に書く。

### 4. 手で起動して確かめる

```bash
python3 buzz_relay.py --config config.toml
```

- 「[物理1] 参加しました」と出て、出題者画面の参加者一覧に名前が出れば接続できている
- 出題中にボタンを押し、回答権を取って LED が点けば完成

会場で URL だけ変えたいときは、`--url` を付けると設定ファイルより優先される。

```bash
python3 buzz_relay.py --config config.toml --url http://192.168.2.102:8000/player
```

### 5. 自動起動（systemd）

電源を入れたら自動で起動するようにする。ユーザーサービスとして動かすので root は要らない。

```bash
mkdir -p ~/.config/systemd/user
cp systemd/trans-ai-quiz-buzzer.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now trans-ai-quiz-buzzer
# ログインしていなくても起動時に動かす
sudo loginctl enable-linger "$USER"
```

ログは `journalctl --user -u trans-ai-quiz-buzzer -f` で見る。
`config.toml` を変えたら `systemctl --user restart trans-ai-quiz-buzzer` で反映する。

リポジトリを `~/trans-ai-quiz-buzzer` 以外に置いた場合は、ユニットファイルのパスを書き換える。

### 6. シャットダウンボタン（任意）

ソフトウェアは要らない。`/boot/firmware/config.txt` に次の 1 行を足し、再起動する。

```
dtoverlay=gpio-shutdown,gpio_pin=3
```

GPIO3（物理ピン 5）と GND の間にタクトスイッチを繋ぐ。押すと安全にシャットダウンし、止まった状態で押すと起動する。
電源を抜く前にこれで止めると、SD カードの破損を防げる。

## LED の表示

| ボタンの LED | 状態 |
| --- | --- |
| 点灯 | 回答権を取った |
| 0.5 秒ごとに点滅 | 不正解と判定された（お手つき）。次の問題で消える |
| 2 秒ごとに短く点滅 | サーバに繋がっていない。繋がるまで再接続を続ける |
| 消灯 | それ以外。大会終了・参加 URL 無効で接続をやめた場合も消灯 |

| 状態表示 LED | 状態 |
| --- | --- |
| 点灯 | すべてのボタンが接続中 |
| 1 秒ごとに短く点滅 | 繋がっていないボタンがある |
| 消灯 | すべてのボタンが接続をやめた（このときプログラムも終了する） |

## 名前を変える・再接続

- 一度参加すると、サーバが発行した token を `~/.config/trans-ai-quiz-buzzer/tokens.json` に保存する
- Pi やプログラムを再起動しても、**同じ参加者として戻る**（お手つきや投影の一覧もそのまま）
- `config.toml` の `name` を書き換えて再起動すると、同じ参加者のまま名前だけが変わる
- 名前は 12 文字以内（本体の上限に合わせている）

## Cloud Run 版で使う

本体の Cloud Run 版（HTTPS）でも、`url` に参加 URL（`https://…/player?event=…&key=…`）を貼れば同じように動く。**実環境では未検証。**

- 参加 URL は大会ごとに変わる。大会のたびに `config.toml` を書き換えるか `--url` で渡す
- 参加 URL には参加キーが含まれる。`config.toml` は Git に含めない（`.gitignore` 済み）。ログでは伏せ字にする
- 大会が終わる、または参加 URL が無効になると、そのボタンは再接続をやめる（Cloud Run 版が接続を閉じるコード 4403・4404 と、接続前の拒否 HTTP 401・403・404・410 を見ている）
- 物理ボタンも、Cloud Run 版の**参加者の上限（20 人）に数えられる**
- Pi にインターネット接続が要る

## うまくいかないとき

| 症状 | 確認すること |
| --- | --- |
| 起動直後に `--url のホスト名が不正です` | URL の打ち間違い（ドットの重複など） |
| 「切断されました」が繰り返し出る | 本体を `--host 0.0.0.0` で起動しているか。Pi と本体が同じネットワークにいるか。`curl http://<IP>:8000/player` が通るか |
| 押していないのに押したことになる | ボタンの端子が COM と NC になっていないか。GPIO の列に GND の線が紛れていないか |
| 押しても反応しない | GND が反対側の電源ラインに挿さっていないか（左右は繋がっていない） |
| LED が点かない | LED の向き（長い足が＋）。トランジスタの足の並び |
| 会場の WiFi に繋がらない | Pi 3B は 2.4GHz のみ。ログイン画面が出る WiFi や企業向け認証（802.1X）には繋がらない |

## trans-ai-quiz 本体との互換範囲

このリポジトリは本体と別に管理している。本体の回答者向けの通信仕様が変わると、**気づかないまま動かなくなる**おそれがある。
本体の `server/app/protocol.py` を変えるときは、次の範囲に影響しないか確認する。

| 向き | メッセージ | 使っている項目 |
| --- | --- | --- |
| 中継器 → サーバ | `join` | `name`、`token` |
| 中継器 → サーバ | `buzz` | `round_id`、`client_sent_at` |
| サーバ → 中継器 | `welcome` | `player_id`、`token` |
| サーバ → 中継器 | `room_state` | `round_id`、`phase`（`buzzed` / `check` を見る）、`buzzed.player_id`、`players[].id`、`players[].locked_out` |
| サーバ → 中継器 | `buzz_accepted` | `player_id` |
| サーバ → 中継器 | `buzz_rejected` | `reason`（ログ表示のみ） |
| サーバ → 中継器 | `error` | `message`（ログ表示のみ） |

ほかに次の前提を置いている。

- WebSocket の経路は `/ws`。Cloud Run 版は `event` / `key` のクエリと、公開 URL と一致する `Origin` ヘッダーを要求する
- Cloud Run 版は大会終了で close code 4404、認証失敗で 4403 を使う
- 名前の上限は 12 文字（本体の `MAX_NAME_LENGTH`）

動作を確認した本体のバージョン: `develop`（`ca2aac2`）のローカル版。回答者向けの通信仕様は `feature/037-deploy-cloud-run`（`44e1e8a`）でも変わっていない。

## 開発

テストは Raspberry Pi でなくても（Mac でも）動く。GPIO は gpiozero の模擬ピンで、サーバは簡易サーバで模擬する。

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install gpiozero websockets pytest
python3 -m pytest
```

テストの模擬サーバは websockets 13 以降の API を使う。中継器本体は、Raspberry Pi OS の標準パッケージ（websockets 10.4 以降）で動く。
