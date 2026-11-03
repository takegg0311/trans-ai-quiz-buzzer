#!/usr/bin/env python3
"""trans-ai-quiz-buzzer の回路図 SVG を生成するスクリプト。

README.md に掲載するための配線図（SVG形式）を出力する。
1. ボタン配線図 (circuit_button.svg)
2. LED配線図（3.3V直接駆動：試作） (circuit_led_3v3.svg)
3. LED配線図（5Vトランジスタ駆動：LED内蔵ボタン用） (circuit_led_5v_transistor.svg)
4. 1ボタン分の統合配線図 (circuit_button_and_led.svg)
5. 4席分の統合配線図（GPIO 40pinヘッダ対応） (circuit_4players_gpio40pin.svg)
"""

from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"


def generate_button_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 300" width="760" height="300">
  <defs>
    <style>
      .bg { fill: #ffffff; stroke: #e2e8f0; stroke-width: 1.5; rx: 12px; }
      .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 16px; font-weight: bold; fill: #1e293b; }
      .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; fill: #64748b; }
      .box-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 13px; font-weight: bold; fill: #334155; }
      .pin-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 13px; font-weight: 600; fill: #0f172a; }
      .pin-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 11px; fill: #64748b; }
      .term-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; font-weight: 600; fill: #1e293b; }
      .note-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 11.5px; fill: #475569; }
      .wire-gpio { stroke: #2563eb; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .wire-gnd { stroke: #1e293b; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .pin-dot { fill: #ffffff; stroke-width: 2.5; }
      .pin-dot-gpio { stroke: #2563eb; }
      .pin-dot-gnd { stroke: #1e293b; }
    </style>
  </defs>

  <!-- Background Card -->
  <rect x="2" y="2" width="756" height="296" class="bg" />

  <!-- Header -->
  <text x="24" y="32" class="title">ボタンの配線（Raspberry Pi 内部プルアップ利用）</text>
  <text x="24" y="50" class="subtitle">アーケードボタンのスイッチ端子を GPIO と GND に直結します（Pi 内部のプルアップを使うため外付け抵抗は不要です）</text>

  <!-- Raspberry Pi Box -->
  <g transform="translate(30, 75)">
    <rect x="0" y="0" width="200" height="145" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
    <text x="14" y="24" class="box-label">Raspberry Pi</text>

    <!-- Internal pull-up note -->
    <rect x="14" y="36" width="172" height="34" rx="4" fill="#f1f5f9" stroke="#e2e8f0" stroke-width="1" />
    <text x="20" y="50" style="font-family: sans-serif; font-size: 10px; fill: #64748b;">内部プルアップ有効 (3.3V)</text>
    <text x="20" y="63" style="font-family: sans-serif; font-size: 10px; fill: #94a3b8;">ソフトウェアで設定 (gpiozero: pull_up=True)</text>

    <!-- GPIO Pin -->
    <text x="20" y="98" class="pin-label">GPIO（ボタン）</text>
    <text x="20" y="112" class="pin-sub">例: GPIO17（物理 Pin 11）</text>
    <circle cx="200" cy="100" r="5" class="pin-dot pin-dot-gpio" />

    <!-- GND Pin -->
    <text x="20" y="132" class="pin-label">GND 端子</text>
    <text x="90" y="132" class="pin-sub">例: Pin 9 / 14</text>
    <circle cx="200" cy="132" r="5" class="pin-dot pin-dot-gnd" />
  </g>

  <!-- Wires -->
  <path d="M 230 175 L 470 175" class="wire-gpio" />
  <path d="M 230 207 L 470 207" class="wire-gnd" />

  <!-- Wire Labels -->
  <rect x="310" y="157" width="84" height="20" rx="4" fill="#eff6ff" stroke="#bfdbfe" />
  <text x="352" y="171" text-anchor="middle" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #1d4ed8;">GPIO 信号線</text>

  <rect x="320" y="211" width="64" height="20" rx="4" fill="#f8fafc" stroke="#cbd5e1" />
  <text x="352" y="225" text-anchor="middle" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #334155;">GND</text>

  <!-- Arcade Button Box -->
  <g transform="translate(470, 75)">
    <rect x="0" y="0" width="250" height="145" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
    <text x="16" y="24" class="box-label">アーケードボタン（OBSF-30 等）</text>

    <!-- Terminal 1 (NO) -->
    <circle cx="0" cy="100" r="5" class="pin-dot pin-dot-gpio" />
    <text x="14" y="98" class="term-label">端子 1（NO / 常開接点）</text>
    <text x="14" y="112" class="pin-sub">押したときに導通する端子</text>

    <!-- Terminal 2 (COM) -->
    <circle cx="0" cy="132" r="5" class="pin-dot pin-dot-gnd" />
    <text x="14" y="132" class="term-label">端子 2（COM / 共通端子）</text>

    <!-- Switch Schematic Symbol -->
    <g transform="translate(170, 80)">
      <!-- Switch body outline -->
      <circle cx="30" cy="30" r="28" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5" />
      <circle cx="30" cy="30" r="21" fill="#fef2f2" stroke="#ef4444" stroke-width="2" />
      <!-- Contacts -->
      <circle cx="15" cy="23" r="2.5" fill="#1e293b" />
      <circle cx="45" cy="23" r="2.5" fill="#1e293b" />
      <!-- Lever (open) -->
      <line x1="16" y1="21" x2="43" y2="10" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" />
      <text x="30" y="68" text-anchor="middle" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #64748b;">PUSH</text>
    </g>

    <!-- Warning badge for NC -->
    <rect x="14" y="38" width="222" height="24" rx="4" fill="#fef3c7" stroke="#fde68a" />
    <text x="20" y="54" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #92400e;">⚠️ 端子が3つの場合: COM と NO を使用（NCは未使用）</text>
  </g>

  <!-- Bottom Notes -->
  <g transform="translate(24, 238)">
    <rect x="0" y="0" width="712" height="46" rx="6" fill="#f1f5f9" />
    <text x="14" y="19" class="note-text">• 通常時: GPIO は内部プルアップにより HIGH（3.3V）です。ボタンを押すと端子が短絡し LOW（GND）を検出します。</text>
    <text x="14" y="35" class="note-text">• 延長時のノイズ対策: ケーブルを数 m に延ばす場合は、GPIO と 3.3V の間に外付けで 10kΩ 抵抗を足すと安定します。</text>
  </g>
</svg>
"""


def generate_led_3v3_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 300" width="760" height="300">
  <defs>
    <style>
      .bg { fill: #ffffff; stroke: #e2e8f0; stroke-width: 1.5; rx: 12px; }
      .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 16px; font-weight: bold; fill: #1e293b; }
      .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; fill: #64748b; }
      .box-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 13px; font-weight: bold; fill: #334155; }
      .pin-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 13px; font-weight: 600; fill: #0f172a; }
      .pin-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 11px; fill: #64748b; }
      .part-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; font-weight: bold; fill: #1e293b; }
      .part-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 10.5px; fill: #64748b; }
      .note-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 11.5px; fill: #475569; }
      .wire-led { stroke: #16a34a; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .wire-gnd { stroke: #1e293b; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .pin-dot { fill: #ffffff; stroke-width: 2.5; }
      .pin-dot-led { stroke: #16a34a; }
      .pin-dot-gnd { stroke: #1e293b; }
    </style>
  </defs>

  <!-- Background Card -->
  <rect x="2" y="2" width="756" height="296" class="bg" />

  <!-- Header -->
  <text x="24" y="32" class="title">LED の配線（3.3V 直接点灯：試作）</text>
  <text x="24" y="50" class="subtitle">赤色 LED 単体を GPIO の 3.3V 出力で直接点灯させる配線です（電流制限抵抗 1kΩ 必須）</text>

  <!-- Raspberry Pi Box -->
  <g transform="translate(30, 75)">
    <rect x="0" y="0" width="180" height="145" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
    <text x="14" y="24" class="box-label">Raspberry Pi</text>

    <!-- GPIO Pin -->
    <text x="16" y="65" class="pin-label">GPIO（LED）</text>
    <text x="16" y="80" class="pin-sub">例: GPIO27（物理 Pin 13）</text>
    <circle cx="180" cy="70" r="5" class="pin-dot pin-dot-led" />

    <!-- GND Pin -->
    <text x="16" y="115" class="pin-label">GND 端子</text>
    <text x="16" y="130" class="pin-sub">例: Pin 14</text>
    <circle cx="180" cy="120" r="5" class="pin-dot pin-dot-gnd" />
  </g>

  <!-- Wire: GPIO to Resistor -->
  <path d="M 210 145 L 260 145" class="wire-led" />

  <!-- Resistor 1k ohm -->
  <g transform="translate(260, 130)">
    <rect x="0" y="5" width="70" height="20" rx="3" fill="#ffffff" stroke="#1e293b" stroke-width="2" />
    <!-- Color bands: 1kΩ (Brown Black Red Gold) -->
    <rect x="12" y="5" width="5" height="20" fill="#854d0e" />
    <rect x="25" y="5" width="5" height="20" fill="#0f172a" />
    <rect x="38" y="5" width="5" height="20" fill="#dc2626" />
    <rect x="52" y="5" width="5" height="20" fill="#eab308" />
    <text x="35" y="-3" text-anchor="middle" class="part-label">抵抗 1kΩ</text>
    <text x="35" y="38" text-anchor="middle" class="part-sub">電流制限</text>
  </g>

  <!-- Wire: Resistor to LED Anode -->
  <path d="M 330 145 L 380 145" class="wire-led" />

  <!-- LED Symbol Card -->
  <g transform="translate(380, 105)">
    <rect x="0" y="0" width="130" height="85" rx="6" fill="#fef2f2" stroke="#fecaca" stroke-width="1.5" />
    <text x="65" y="18" text-anchor="middle" class="part-label" style="fill: #b91c1c;">LED（赤色など）</text>

    <!-- Schematic symbol (Anode on left, Cathode on right) -->
    <g transform="translate(45, 40)">
      <!-- Lead in (Anode) -->
      <line x1="-45" y1="0" x2="0" y2="0" stroke="#16a34a" stroke-width="3" />
      <!-- Triangle (Base at x=0, Apex at x=20) -->
      <polygon points="0,-12 20,0 0,12" fill="#ef4444" stroke="#1e293b" stroke-width="2" />
      <!-- Cathode Bar (at x=20) -->
      <line x1="20" y1="-14" x2="20" y2="14" stroke="#1e293b" stroke-width="2.5" />
      <!-- Lead out (Cathode) -->
      <line x1="20" y1="0" x2="85" y2="0" stroke="#1e293b" stroke-width="3" />

      <!-- Photons / Light emission arrows (pointing up-right) -->
      <path d="M 8,-12 L 15,-20" stroke="#ef4444" stroke-width="1.8" stroke-linecap="round" />
      <polygon points="17,-22 12,-19 14,-16" fill="#ef4444" />
      <path d="M 16,-8 L 23,-16" stroke="#ef4444" stroke-width="1.8" stroke-linecap="round" />
      <polygon points="25,-18 20,-15 22,-12" fill="#ef4444" />
    </g>

    <!-- Pin labels -->
    <text x="14" y="65" class="part-sub" style="font-weight: bold; fill: #16a34a;">＋ 長い足</text>
    <text x="14" y="76" class="part-sub">(アノード)</text>
    <text x="116" y="65" text-anchor="end" class="part-sub" style="font-weight: bold; fill: #1e293b;">− 短い足</text>
    <text x="116" y="76" text-anchor="end" class="part-sub">(カソード)</text>
  </g>

  <!-- Wire: LED Cathode to GND -->
  <!-- LED Cathode ends at x = 380 + 130 = 510, y = 145 -->
  <path d="M 510 145 L 540 145 L 540 195 L 210 195" class="wire-gnd" />

  <!-- LED Legs Guide Box -->
  <g transform="translate(565, 75)">
    <rect x="0" y="0" width="165" height="145" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
    <text x="12" y="22" class="box-label">LED の足の見分け方</text>

    <!-- LED bulb drawing -->
    <g transform="translate(45, 30)">
      <!-- Red dome -->
      <path d="M 15 25 A 15 15 0 0 1 45 25 L 45 32 L 15 32 Z" fill="#ef4444" stroke="#b91c1c" stroke-width="1.5" />
      <!-- Rim with flat edge on cathode -->
      <rect x="13" y="32" width="34" height="4" rx="1" fill="#dc2626" />
      <!-- Anode lead (longer) -->
      <line x1="23" y1="36" x2="23" y2="82" stroke="#94a3b8" stroke-width="2.5" />
      <!-- Cathode lead (shorter) -->
      <line x1="37" y1="36" x2="37" y2="70" stroke="#94a3b8" stroke-width="2.5" />

      <!-- Labels -->
      <text x="21" y="96" text-anchor="middle" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #16a34a;">長い: ＋</text>
      <text x="41" y="96" text-anchor="middle" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #1e293b;">短い: −</text>
      <!-- Flat spot note -->
      <text x="31" y="110" text-anchor="middle" style="font-family: sans-serif; font-size: 9px; fill: #64748b;">(切り欠き側がマイナス)</text>
    </g>
  </g>

  <!-- Bottom Notes -->
  <g transform="translate(24, 238)">
    <rect x="0" y="0" width="712" height="46" rx="6" fill="#f1f5f9" />
    <text x="14" y="19" class="note-text">• GPIO 出力（3.3V）で点灯します。Pi の GPIO ピンの過電流破損を防ぐため、必ず 1kΩ の電流制限抵抗を入れてください。</text>
    <text x="14" y="35" class="note-text">• LED には極性があります。GPIO 側に長い足（アノード＋）、GND 側に短い足（カソード−）を接続します。</text>
  </g>
</svg>
"""


def generate_led_5v_transistor_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 430" width="780" height="430">
  <defs>
    <style>
      .bg { fill: #ffffff; stroke: #e2e8f0; stroke-width: 1.5; rx: 12px; }
      .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 16px; font-weight: bold; fill: #1e293b; }
      .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; fill: #64748b; }
      .box-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 13px; font-weight: bold; fill: #334155; }
      .pin-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12.5px; font-weight: 600; fill: #0f172a; }
      .pin-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 10.5px; fill: #64748b; }
      .part-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; font-weight: bold; fill: #1e293b; }
      .part-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 10.5px; fill: #64748b; }
      .note-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 11px; fill: #475569; }
      .wire-5v { stroke: #dc2626; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .wire-gpio { stroke: #16a34a; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .wire-gnd { stroke: #1e293b; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .wire-load { stroke: #ea580c; stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .pin-dot { fill: #ffffff; stroke-width: 2.5; }
      .pin-dot-5v { stroke: #dc2626; }
      .pin-dot-gpio { stroke: #16a34a; }
      .pin-dot-gnd { stroke: #1e293b; }
    </style>
  </defs>

  <!-- Background Card -->
  <rect x="2" y="2" width="776" height="426" class="bg" />

  <!-- Header -->
  <text x="24" y="32" class="title">LED の配線（5V トランジスタ駆動：LED 内蔵ボタン用）</text>
  <text x="24" y="50" class="subtitle">5V 電源を NPN トランジスタ（2SC1815）でスイッチングし、5V 定格の LED 内蔵ボタンを安全・明るく点灯させます</text>

  <!-- Raspberry Pi Box -->
  <g transform="translate(24, 75)">
    <rect x="0" y="0" width="170" height="235" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
    <text x="14" y="24" class="box-label">Raspberry Pi</text>

    <!-- 5V Power Pin -->
    <text x="16" y="60" class="pin-label" style="fill: #dc2626;">5V 電源</text>
    <text x="16" y="74" class="pin-sub">物理 Pin 2 または 4</text>
    <circle cx="170" cy="65" r="5" class="pin-dot pin-dot-5v" />

    <!-- GPIO Pin -->
    <text x="16" y="145" class="pin-label" style="fill: #16a34a;">GPIO（LED）</text>
    <text x="16" y="159" class="pin-sub">例: GPIO27（物理 Pin 13）</text>
    <circle cx="170" cy="150" r="5" class="pin-dot pin-dot-gpio" />

    <!-- GND Pin -->
    <text x="16" y="210" class="pin-label">GND 端子</text>
    <text x="16" y="224" class="pin-sub">Pin 6 / 9 / 14 / 20...</text>
    <circle cx="170" cy="215" r="5" class="pin-dot pin-dot-gnd" />
  </g>

  <!-- 5V Wire from Pi to LED (+) -->
  <!-- Pi 5V at (24+170=194, 75+65=140) -->
  <path d="M 194 140 L 370 140" class="wire-5v" />

  <!-- LED / Button LED Box -->
  <g transform="translate(370, 100)">
    <rect x="0" y="0" width="150" height="80" rx="6" fill="#fef2f2" stroke="#fca5a5" stroke-width="1.5" />
    <text x="75" y="22" text-anchor="middle" class="part-label" style="fill: #991b1b;">LED 内蔵ボタン</text>
    <text x="75" y="36" text-anchor="middle" class="part-sub">（5V 定格 / 抵抗内蔵）</text>

    <!-- Terminals inside -->
    <circle cx="0" cy="40" r="4" fill="#dc2626" />
    <text x="10" y="44" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #dc2626;">LED（＋）</text>

    <circle cx="150" cy="40" r="4" fill="#ea580c" />
    <text x="140" y="44" text-anchor="end" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #ea580c;">LED（−）</text>

    <text x="75" y="70" text-anchor="middle" style="font-family: sans-serif; font-size: 9.5px; fill: #b91c1c;">※単体LEDの場合は1kΩを直列に追加</text>
  </g>

  <!-- Wire from LED(-) down to Collector -->
  <!-- LED(-) is at (370+150=520, 100+40=140) -->
  <!-- Collector lead is at (455, 203) -->
  <path d="M 520 140 L 550 140 L 550 203 L 455 203" class="wire-load" />

  <!-- Base Circuit: Pi GPIO at (194, 225) to Resistor -->
  <path d="M 194 225 L 245 225" class="wire-gpio" />

  <!-- Resistor 1k ohm (Base resistor) -->
  <g transform="translate(245, 215)">
    <rect x="0" y="0" width="60" height="20" rx="3" fill="#ffffff" stroke="#1e293b" stroke-width="2" />
    <rect x="10" y="0" width="4" height="20" fill="#854d0e" />
    <rect x="22" y="0" width="4" height="20" fill="#0f172a" />
    <rect x="34" y="0" width="4" height="20" fill="#dc2626" />
    <rect x="46" y="0" width="4" height="20" fill="#eab308" />
    <text x="30" y="-5" text-anchor="middle" class="part-label">1kΩ</text>
    <text x="30" y="32" text-anchor="middle" class="part-sub">ベース抵抗</text>
  </g>

  <!-- Wire from Resistor to Transistor Base -->
  <!-- Resistor ends at 245+60=305. Base pin is at 385 -->
  <path d="M 305 225 L 385 225" class="wire-gpio" />

  <!-- NPN Transistor (2SC1815) Schematic Symbol -->
  <!-- Center at (420, 225) -->
  <g transform="translate(420, 225)">
    <!-- Transistor outer circle -->
    <circle cx="0" cy="0" r="34" fill="#ffffff" stroke="#64748b" stroke-width="1.5" />

    <!-- Base bar (vertical) -->
    <line x1="-12" y1="-18" x2="-12" y2="18" stroke="#1e293b" stroke-width="3" />

    <!-- Base lead (horizontal in from left) -->
    <line x1="-35" y1="0" x2="-12" y2="0" stroke="#16a34a" stroke-width="3" />
    <circle cx="-35" cy="0" r="4" fill="#16a34a" />
    <text x="-26" y="-8" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #16a34a;">B（ベース）</text>

    <!-- Collector lead (top right) -->
    <line x1="-12" y1="-8" x2="16" y2="-22" stroke="#ea580c" stroke-width="2.5" />
    <line x1="16" y1="-22" x2="35" y2="-22" stroke="#ea580c" stroke-width="2.5" />
    <circle cx="35" cy="-22" r="3.5" fill="#ea580c" />
    <text x="18" y="-28" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #ea580c;">C（コレクタ）</text>

    <!-- Emitter lead with NPN arrow (bottom right, pointing OUT) -->
    <line x1="-12" y1="8" x2="16" y2="22" stroke="#1e293b" stroke-width="2.5" />
    <line x1="16" y1="22" x2="35" y2="22" stroke="#1e293b" stroke-width="2.5" />
    <!-- Arrow pointing outward towards emitter terminal -->
    <polygon points="15,22 6,12 8,22" fill="#1e293b" stroke="#1e293b" />
    <circle cx="35" cy="22" r="3.5" fill="#1e293b" />
    <text x="18" y="38" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #1e293b;">E（エミッタ）</text>

    <text x="0" y="-42" text-anchor="middle" class="part-label">2SC1815-GR (NPN)</text>
  </g>

  <!-- Wire from Transistor Emitter to GND -->
  <!-- Emitter pin at (420+35=455, 225+22=247) -->
  <!-- Pi GND at (194, 290) -->
  <path d="M 455 247 L 490 247 L 490 290 L 194 290" class="wire-gnd" />

  <!-- Transistor Pinout Diagram Box (TO-92 Package) -->
  <g transform="translate(590, 75)">
    <rect x="0" y="0" width="166" height="235" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
    <text x="12" y="24" class="box-label">2SC1815 の足の並び</text>
    <text x="12" y="38" class="pin-sub">TO-92 パッケージ（東芝 / UTC）</text>

    <!-- TO-92 Transistor Drawing -->
    <g transform="translate(48, 55)">
      <!-- Package flat face view -->
      <path d="M 5,20 A 30,30 0 0,1 65,20 L 65,55 L 5,55 Z" fill="#334155" stroke="#1e293b" stroke-width="1.5" />
      <rect x="8" y="25" width="54" height="25" rx="2" fill="#1e293b" />
      <!-- Text on package -->
      <text x="35" y="38" text-anchor="middle" style="font-family: monospace; font-size: 8px; fill: #ffffff; font-weight: bold;">C1815</text>
      <text x="35" y="47" text-anchor="middle" style="font-family: monospace; font-size: 7px; fill: #94a3b8;">GR</text>

      <!-- Leads -->
      <line x1="16" y1="55" x2="16" y2="105" stroke="#94a3b8" stroke-width="2.5" />
      <line x1="35" y1="55" x2="35" y2="105" stroke="#94a3b8" stroke-width="2.5" />
      <line x1="54" y1="55" x2="54" y2="105" stroke="#94a3b8" stroke-width="2.5" />

      <!-- Pin numbers & letters -->
      <text x="16" y="118" text-anchor="middle" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #1e293b;">E</text>
      <text x="16" y="129" text-anchor="middle" style="font-family: sans-serif; font-size: 9px; fill: #64748b;">(1)</text>

      <text x="35" y="118" text-anchor="middle" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #ea580c;">C</text>
      <text x="35" y="129" text-anchor="middle" style="font-family: sans-serif; font-size: 9px; fill: #64748b;">(2)</text>

      <text x="54" y="118" text-anchor="middle" style="font-family: sans-serif; font-size: 11px; font-weight: bold; fill: #16a34a;">B</text>
      <text x="54" y="129" text-anchor="middle" style="font-family: sans-serif; font-size: 9px; fill: #64748b;">(3)</text>
    </g>

    <!-- Legend note -->
    <rect x="8" y="195" width="150" height="30" rx="4" fill="#f1f5f9" />
    <text x="14" y="208" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #334155;">平らな印字面を手前にして</text>
    <text x="14" y="220" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #0284c7;">左から E ・ C ・ B</text>
  </g>

  <!-- Bottom Notes -->
  <g transform="translate(24, 325)">
    <rect x="0" y="0" width="732" height="92" rx="6" fill="#f1f5f9" />
    <text x="14" y="18" class="note-text" style="font-weight: bold; fill: #b91c1c;">⚠️ 注意: 5V（物理ピン 2 または 4）を絶対に GPIO ピンに直結させないでください。Pi が破損します。</text>
    <text x="14" y="36" class="note-text">• 仕組み: GPIO を HIGH（3.3V）にすると、1kΩ 抵抗を通してベース（B）に電流が流れ、コレクタ（C）〜エミッタ（E）間が導通して 5V LED が点灯します。</text>
    <text x="14" y="54" class="note-text">• LED 内蔵ボタン: 内部に電流制限抵抗が組み込まれているため、追加の抵抗なしで 5V とコレクタ端子に直結できます。</text>
    <text x="14" y="72" class="note-text">• 単体 LED の場合: 赤色 LED などの単体部品を 5V で点灯させる際は、破損防止のため LED の前に必ず 1kΩ 抵抗を入れてください。</text>
  </g>
</svg>
"""


def generate_single_player_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 470" width="840" height="470">
  <defs>
    <style>
      .bg { fill: #ffffff; stroke: #e2e8f0; stroke-width: 1.5; rx: 12px; }
      .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 16px; font-weight: bold; fill: #1e293b; }
      .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; fill: #64748b; }
      .box-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 13px; font-weight: bold; fill: #334155; }
      .pin-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; font-weight: 600; fill: #0f172a; }
      .pin-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 10px; fill: #64748b; }
      .part-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; font-weight: bold; fill: #1e293b; }
      .part-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 10px; fill: #64748b; }
      .note-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 11px; fill: #475569; }
      .wire-5v { stroke: #dc2626; stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .wire-btn { stroke: #2563eb; stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .wire-led { stroke: #16a34a; stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .wire-gnd { stroke: #1e293b; stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .wire-load { stroke: #ea580c; stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }
      .pin-dot { fill: #ffffff; stroke-width: 2.5; }
    </style>
  </defs>

  <!-- Background Card -->
  <rect x="2" y="2" width="836" height="466" class="bg" />

  <!-- Header -->
  <text x="24" y="32" class="title">1 席分（ボタン 1 ＋ 回答権 LED）の総合配線図</text>
  <text x="24" y="50" class="subtitle">例: ボタン 1（GPIO17: 入力）と LED 1（GPIO27: 5V トランジスタ駆動）を組み合わせた配線の全体像</text>

  <!-- Raspberry Pi Header Section -->
  <g transform="translate(24, 75)">
    <rect x="0" y="0" width="180" height="280" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
    <text x="14" y="24" class="box-label">Raspberry Pi（40 Pin）</text>

    <!-- 5V -->
    <text x="16" y="58" class="pin-label" style="fill: #dc2626;">5V 電源</text>
    <text x="16" y="70" class="pin-sub">物理 Pin 2 または 4</text>
    <circle cx="180" cy="62" r="5" class="pin-dot" stroke="#dc2626" />

    <!-- Button GPIO -->
    <text x="16" y="110" class="pin-label" style="fill: #2563eb;">GPIO 17（ボタン入力）</text>
    <text x="16" y="122" class="pin-sub">物理 Pin 11 / 内蔵プルアップ</text>
    <circle cx="180" cy="115" r="5" class="pin-dot" stroke="#2563eb" />

    <!-- LED GPIO -->
    <text x="16" y="165" class="pin-label" style="fill: #16a34a;">GPIO 27（LED制御）</text>
    <text x="16" y="177" class="pin-sub">物理 Pin 13 / 出力</text>
    <circle cx="180" cy="170" r="5" class="pin-dot" stroke="#16a34a" />

    <!-- GND -->
    <text x="16" y="225" class="pin-label" style="fill: #1e293b;">GND（共通接地）</text>
    <text x="16" y="237" class="pin-sub">物理 Pin 6, 9, 14, 20...</text>
    <circle cx="180" cy="230" r="5" class="pin-dot" stroke="#1e293b" />
  </g>

  <!-- Arcade Button Unit (Right side) -->
  <g transform="translate(560, 75)">
    <rect x="0" y="0" width="250" height="280" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
    <text x="16" y="24" class="box-label">アーケードボタン（LED内蔵型）</text>

    <!-- Button Switch Section -->
    <rect x="14" y="36" width="222" height="100" rx="6" fill="#eff6ff" stroke="#bfdbfe" />
    <text x="24" y="56" class="part-label" style="fill: #1d4ed8;">スイッチ端子（マイクロスイッチ）</text>

    <circle cx="14" cy="80" r="4.5" fill="#2563eb" />
    <text x="24" y="84" style="font-family: sans-serif; font-size: 11px; font-weight: 600; fill: #1e293b;">端子 1（NO / 常開接点）</text>

    <circle cx="14" cy="115" r="4.5" fill="#1e293b" />
    <text x="24" y="119" style="font-family: sans-serif; font-size: 11px; font-weight: 600; fill: #1e293b;">端子 2（COM / 共通端子）</text>

    <!-- LED Section -->
    <rect x="14" y="148" width="222" height="118" rx="6" fill="#fef2f2" stroke="#fecaca" />
    <text x="24" y="170" class="part-label" style="fill: #b91c1c;">LED 端子（5V仕様）</text>

    <circle cx="14" cy="195" r="4.5" fill="#dc2626" />
    <text x="24" y="199" style="font-family: sans-serif; font-size: 11px; font-weight: 600; fill: #dc2626;">LED（＋）アノード</text>

    <circle cx="14" cy="235" r="4.5" fill="#ea580c" />
    <text x="24" y="239" style="font-family: sans-serif; font-size: 11px; font-weight: 600; fill: #ea580c;">LED（−）カソード</text>
  </g>

  <!-- Wiring connections between Pi, Transistor circuit, and Button -->
  <!-- 1. 5V Wire: Pi (204, 137) -> Button LED (+) (574, 270) -->
  <path d="M 204 137 L 300 137 L 300 100 L 520 100 L 520 270 L 574 270" class="wire-5v" />

  <!-- 2. Button GPIO: Pi (204, 190) -> Button Switch NO (574, 155) -->
  <path d="M 204 190 L 480 190 L 480 155 L 574 155" class="wire-btn" />

  <!-- 3. Button GND: Button COM (574, 190) -> Common GND line -->
  <path d="M 574 190 L 530 190 L 530 305 L 204 305" class="wire-gnd" />

  <!-- 4. LED GPIO -> 1k Resistor -> Transistor Base -->
  <path d="M 204 245 L 260 245" class="wire-led" />

  <!-- 1k Resistor -->
  <g transform="translate(260, 235)">
    <rect x="0" y="0" width="55" height="20" rx="3" fill="#ffffff" stroke="#1e293b" stroke-width="1.5" />
    <text x="27" y="14" text-anchor="middle" style="font-family: sans-serif; font-size: 10px; font-weight: bold;">1kΩ</text>
  </g>

  <path d="M 315 245 L 365 245" class="wire-led" />

  <!-- Transistor Block -->
  <g transform="translate(390, 245)">
    <!-- Symbol -->
    <circle cx="0" cy="0" r="22" fill="#ffffff" stroke="#64748b" stroke-width="1.5" />
    <line x1="-8" y1="-12" x2="-8" y2="12" stroke="#1e293b" stroke-width="2.5" />
    <line x1="-25" y1="0" x2="-8" y2="0" stroke="#16a34a" stroke-width="2.5" />
    <circle cx="-25" cy="0" r="3" fill="#16a34a" />
    <!-- Collector lead -->
    <line x1="-8" y1="-6" x2="10" y2="-16" stroke="#ea580c" stroke-width="2" />
    <line x1="10" y1="-16" x2="22" y2="-16" stroke="#ea580c" stroke-width="2" />
    <circle cx="22" cy="-16" r="3" fill="#ea580c" />
    <!-- Emitter lead -->
    <line x1="-8" y1="6" x2="10" y2="16" stroke="#1e293b" stroke-width="2" />
    <line x1="10" y1="16" x2="22" y2="16" stroke="#1e293b" stroke-width="2" />
    <polygon points="10,16 2,10 4,18" fill="#1e293b" />
    <circle cx="22" cy="16" r="3" fill="#1e293b" />

    <text x="0" y="-28" text-anchor="middle" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #334155;">2SC1815</text>
    <text x="-16" y="-6" style="font-family: sans-serif; font-size: 8px; font-weight: bold; fill: #16a34a;">B</text>
    <text x="14" y="-22" style="font-family: sans-serif; font-size: 8px; font-weight: bold; fill: #ea580c;">C</text>
    <text x="14" y="28" style="font-family: sans-serif; font-size: 8px; font-weight: bold; fill: #1e293b;">E</text>
  </g>

  <!-- Transistor Collector (390+22=412, 245-16=229) -> LED (-) (574, 310) -->
  <path d="M 412 229 L 460 229 L 460 310 L 574 310" class="wire-load" />

  <!-- Transistor Emitter (390+22=412, 245+16=261) -> Common GND line at y=305 -->
  <path d="M 412 261 L 435 261 L 435 305" class="wire-gnd" />
  <circle cx="435" cy="305" r="3.5" fill="#1e293b" />

  <!-- Bottom Notes -->
  <g transform="translate(24, 375)">
    <rect x="0" y="0" width="786" height="75" rx="6" fill="#f1f5f9" />
    <text x="14" y="18" class="note-text" style="font-weight: bold; fill: #1e293b;">【1席分の配線の要点】</text>
    <text x="14" y="36" class="note-text">• 入力系（早押しボタン）: GPIO17 ── スイッチ NO端子 ／ スイッチ COM端子 ── GND（押すと GPIO が LOW）</text>
    <text x="14" y="54" class="note-text">• 出力系（回答権LED）: GPIO27 ── 1kΩ ── トランジスタ B ／ トランジスタ E ── GND ／ 5V ── LED(＋) ／ LED(−) ── トランジスタ C</text>
    <text x="14" y="68" class="note-text" style="font-size: 10px; fill: #64748b;">※GNDはすべて共通（ブレッドボードのマイナス電源ラインで1つにまとめてPiのGNDへ接続）にします。</text>
  </g>
</svg>
"""


def generate_4players_gpio40pin_svg() -> str:
    """4席分のボタンとLED、およびRaspberry Pi 40pin GPIOヘッダの接続図を生成する。"""

    # 40pin データ定義 (row 0..19)
    # (odd_pin, odd_label, odd_role, even_pin, even_label, even_role)
    pins_data = [
        (1, "3.3V", "pwr3v", 2, "5V", "pwr5v"),
        (3, "GPIO 2", "other", 4, "5V", "pwr5v_unused"),
        (5, "GPIO 3", "other", 6, "GND", "gnd"),
        (7, "GPIO 4", "other", 8, "GPIO 14", "other"),
        (9, "GND", "other", 10, "GPIO 15", "other"),
        (11, "GPIO 17", "btn1", 12, "GPIO 18", "other"),
        (13, "GPIO 27", "led1", 14, "GND", "other"),
        (15, "GPIO 22", "other", 16, "GPIO 23", "other"),
        (17, "3.3V", "pwr3v", 18, "GPIO 24", "other"),
        (19, "GPIO 10", "other", 20, "GND", "other"),
        (21, "GPIO 9", "other", 22, "GPIO 25", "other"),
        (23, "GPIO 11", "other", 24, "GPIO 8", "other"),
        (25, "GND", "other", 26, "GPIO 7", "other"),
        (27, "GPIO 0", "other", 28, "GPIO 1", "other"),
        (29, "GPIO 5", "btn2", 30, "GND", "other"),
        (31, "GPIO 6", "led2", 32, "GPIO 12", "other"),
        (33, "GPIO 13", "btn3", 34, "GND", "other"),
        (35, "GPIO 19", "led3", 36, "GPIO 16", "led4"),
        (37, "GPIO 26", "btn4", 38, "GPIO 20", "other"),
        (39, "GND", "gnd_unused", 40, "GPIO 21", "other"),
    ]

    # ピンヘッダ位置
    hdr_odd_x = 115
    hdr_even_x = 139
    hdr_y0 = 118
    hdr_dy = 28

    # 各席のY位置 (height=145, gap=35)
    seats_y = [75, 255, 435, 615]

    def pin_color(role: str) -> tuple[str, str]:
        # (fill, text_color)
        if role == "pwr5v":
            return "#dc2626", "#dc2626"
        if role == "gnd":
            return "#1e293b", "#1e293b"
        if role.startswith("btn"):
            return "#2563eb", "#1d4ed8"
        if role.startswith("led"):
            return "#16a34a", "#15803d"
        return "#cbd5e1", "#94a3b8"

    pin_elements = []
    for r, (p_odd, l_odd, r_odd, p_even, l_even, r_even) in enumerate(pins_data):
        py = hdr_y0 + r * hdr_dy

        # Odd pin (Left)
        c_odd_fill, c_odd_text = pin_color(r_odd)
        is_odd_used = r_odd in ("btn1", "led1", "btn2", "led2", "btn3", "led3", "btn4")
        font_weight_odd = "bold" if is_odd_used else "normal"
        pin_elements.append(f"""
        <!-- Row {r}: Pin {p_odd} -->
        <circle cx="{hdr_odd_x}" cy="{py}" r="5.5" fill="{c_odd_fill}" stroke="#ffffff" stroke-width="1.2" />
        <text x="{hdr_odd_x - 12}" y="{py + 4}" text-anchor="end" style="font-family: sans-serif; font-size: 10.5px; font-weight: {font_weight_odd}; fill: {c_odd_text};">{l_odd} [{p_odd}]</text>
        """)

        # Even pin (Right)
        c_even_fill, c_even_text = pin_color(r_even)
        is_even_used = r_even in ("pwr5v", "gnd", "led4")
        font_weight_even = "bold" if is_even_used else "normal"
        pin_elements.append(f"""
        <!-- Row {r}: Pin {p_even} -->
        <circle cx="{hdr_even_x}" cy="{py}" r="5.5" fill="{c_even_fill}" stroke="#ffffff" stroke-width="1.2" />
        <text x="{hdr_even_x + 12}" y="{py + 4}" text-anchor="start" style="font-family: sans-serif; font-size: 10.5px; font-weight: {font_weight_even}; fill: {c_even_text};">[{p_even}] {l_even}</text>
        """)

    # 席モジュールの生成
    seat_configs = [
        (1, "席 1", "GPIO 17 [Pin 11]", "GPIO 27 [Pin 13]", "#2563eb", "#16a34a"),
        (2, "席 2", "GPIO 5 [Pin 29]", "GPIO 6 [Pin 31]", "#2563eb", "#16a34a"),
        (3, "席 3", "GPIO 13 [Pin 33]", "GPIO 19 [Pin 35]", "#2563eb", "#16a34a"),
        (4, "席 4", "GPIO 26 [Pin 37]", "GPIO 16 [Pin 36]", "#2563eb", "#16a34a"),
    ]

    seat_elements = []
    box_x = 640
    box_w = 460
    box_h = 145

    for idx, name, btn_pin, led_pin, c_btn, c_led in seat_configs:
        sy = seats_y[idx - 1]
        seat_elements.append(f"""
    <!-- Seat {idx} Module -->
    <g transform="translate({box_x}, {sy})">
      <!-- Outer Card -->
      <rect x="0" y="0" width="{box_w}" height="{box_h}" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
      
      <!-- Header -->
      <rect x="0" y="0" width="{box_w}" height="26" rx="8" fill="#f1f5f9" />
      <rect x="0" y="16" width="{box_w}" height="10" fill="#f1f5f9" />
      <text x="12" y="18" style="font-family: sans-serif; font-size: 12px; font-weight: bold; fill: #1e293b;">{name}</text>
      <text x="60" y="18" style="font-family: sans-serif; font-size: 11px; fill: #64748b;">(ボタン: <tspan fill="{c_btn}" font-weight="600">{btn_pin}</tspan> ／ LED: <tspan fill="{c_led}" font-weight="600">{led_pin}</tspan>)</text>

      <!-- Terminals Left Edge -->
      <!-- Button Input (NO) -->
      <circle cx="0" cy="46" r="4.5" fill="#2563eb" />
      <text x="8" y="50" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #2563eb;">ボタン信号 (NO)</text>

      <!-- LED GPIO Input -->
      <circle cx="0" cy="74" r="4.5" fill="#16a34a" />
      <text x="8" y="78" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #16a34a;">LED 信号</text>

      <!-- 5V Input -->
      <circle cx="0" cy="102" r="4.5" fill="#dc2626" />
      <text x="8" y="106" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #dc2626;">5V 電源</text>

      <!-- GND Input -->
      <circle cx="0" cy="126" r="4.5" fill="#1e293b" />
      <text x="8" y="130" style="font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #1e293b;">GND</text>

      <!-- Internal Components -->
      <!-- 1k Resistor for LED -->
      <line x1="0" y1="74" x2="105" y2="74" stroke="#16a34a" stroke-width="2" />
      <g transform="translate(105, 66)">
        <rect x="0" y="0" width="38" height="16" rx="2" fill="#ffffff" stroke="#1e293b" stroke-width="1.5" />
        <text x="19" y="11" text-anchor="middle" style="font-family: sans-serif; font-size: 9px; font-weight: bold;">1kΩ</text>
      </g>
      <line x1="143" y1="74" x2="175" y2="74" stroke="#16a34a" stroke-width="2" />

      <!-- Transistor 2SC1815 -->
      <g transform="translate(195, 74)">
        <circle cx="0" cy="0" r="18" fill="#ffffff" stroke="#64748b" stroke-width="1.2" />
        <line x1="-7" y1="-10" x2="-7" y2="10" stroke="#1e293b" stroke-width="2" />
        <!-- Base -->
        <line x1="-20" y1="0" x2="-7" y2="0" stroke="#16a34a" stroke-width="2" />
        <!-- Collector -->
        <line x1="-7" y1="-5" x2="8" y2="-13" stroke="#ea580c" stroke-width="2" />
        <line x1="8" y1="-13" x2="18" y2="-13" stroke="#ea580c" stroke-width="2" />
        <!-- Emitter -->
        <line x1="-7" y1="5" x2="8" y2="13" stroke="#1e293b" stroke-width="2" />
        <line x1="8" y1="13" x2="18" y2="13" stroke="#1e293b" stroke-width="2" />
        <polygon points="7,12 1,7 2,14" fill="#1e293b" />
        <!-- Labels -->
        <text x="-1" y="-21" text-anchor="middle" style="font-family: sans-serif; font-size: 8px; font-weight: bold; fill: #475569;">2SC1815</text>
      </g>

      <!-- Transistor Emitter (195+18=213, 74+13=87) to GND Line -->
      <path d="M 213 87 L 230 87 L 230 126 L 0 126" stroke="#1e293b" stroke-width="2" fill="none" />
      <circle cx="230" cy="126" r="2.5" fill="#1e293b" />

      <!-- Transistor Collector (195+18=213, 74-13=61) to LED Cathode -->
      <path d="M 213 61 L 245 61 L 245 118 L 290 118" stroke="#ea580c" stroke-width="2" fill="none" />

      <!-- 5V to LED Anode -->
      <path d="M 0 102 L 290 102" stroke="#dc2626" stroke-width="2" fill="none" />

      <!-- Button NO to Switch Terminal 1 -->
      <path d="M 0 46 L 290 46" stroke="#2563eb" stroke-width="2" fill="none" />

      <!-- Button COM to GND -->
      <path d="M 290 64 L 270 64 L 270 126" stroke="#1e293b" stroke-width="2" fill="none" />
      <circle cx="270" cy="126" r="2.5" fill="#1e293b" />

      <!-- Arcade Button Unit Box -->
      <g transform="translate(290, 34)">
        <rect x="0" y="0" width="160" height="98" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2" />
        
        <!-- Switch Section -->
        <rect x="4" y="4" width="152" height="42" rx="4" fill="#eff6ff" />
        <circle cx="0" cy="12" r="3" fill="#2563eb" />
        <text x="8" y="15" style="font-family: sans-serif; font-size: 9.5px; font-weight: bold; fill: #1d4ed8;">スイッチ NO</text>
        <circle cx="0" cy="30" r="3" fill="#1e293b" />
        <text x="8" y="33" style="font-family: sans-serif; font-size: 9.5px; fill: #334155;">スイッチ COM</text>
        <circle cx="132" cy="21" r="14" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5" />
        <circle cx="132" cy="21" r="10" fill="#ef4444" />

        <!-- LED Section -->
        <rect x="4" y="50" width="152" height="44" rx="4" fill="#fef2f2" />
        <circle cx="0" cy="68" r="3" fill="#dc2626" />
        <text x="8" y="71" style="font-family: sans-serif; font-size: 9.5px; font-weight: bold; fill: #dc2626;">LED (＋)</text>
        <circle cx="0" cy="84" r="3" fill="#ea580c" />
        <text x="8" y="87" style="font-family: sans-serif; font-size: 9.5px; font-weight: bold; fill: #ea580c;">LED (−)</text>
        <text x="132" y="75" text-anchor="middle" style="font-family: sans-serif; font-size: 9px; font-weight: bold; fill: #b91c1c;">LED内蔵</text>
      </g>
    </g>
        """)

    # 配線バスのルーティング (Manhattan routing)
    # 5V バス: X=580, GND バス: X=550
    # 信号線バス:
    # Btn 1 (Pin 11): X=260
    # LED 1 (Pin 13): X=290
    # Btn 2 (Pin 29): X=320
    # LED 2 (Pin 31): X=350
    # Btn 3 (Pin 33): X=380
    # LED 3 (Pin 35): X=410
    # LED 4 (Pin 36): X=440
    # Btn 4 (Pin 37): X=470

    # 各席の端子Y座標 (sy + 46, sy + 74, sy + 102, sy + 126)
    # 席 1 (sy=75):  Btn=121, LED=149, 5V=177, GND=201
    # 席 2 (sy=255): Btn=301, LED=329, 5V=357, GND=381
    # 席 3 (sy=435): Btn=481, LED=509, 5V=537, GND=561
    # 席 4 (sy=615): Btn=661, LED=689, 5V=717, GND=741

    wires = f"""
    <!-- Underlay for Wire Crossings (White borders to show jumps) -->
    <g stroke="#ffffff" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <!-- 5V Bus Main Line -->
      <path d="M {hdr_even_x} 118 L 580 118 L 580 717" />
      <!-- GND Bus Main Line -->
      <path d="M {hdr_even_x} 174 L 550 174 L 550 741" />

      <!-- Horizontal branches from Buses to Seats -->
      <!-- 5V Branches -->
      <path d="M 580 177 L {box_x} 177" />
      <path d="M 580 357 L {box_x} 357" />
      <path d="M 580 537 L {box_x} 537" />
      <path d="M 580 717 L {box_x} 717" />

      <!-- GND Branches -->
      <path d="M 550 201 L {box_x} 201" />
      <path d="M 550 381 L {box_x} 381" />
      <path d="M 550 561 L {box_x} 561" />
      <path d="M 550 741 L {box_x} 741" />

      <!-- Seat 1 Signals -->
      <path d="M {hdr_odd_x} 258 L 260 258 L 260 121 L {box_x} 121" />
      <path d="M {hdr_odd_x} 286 L 290 286 L 290 149 L {box_x} 149" />

      <!-- Seat 2 Signals -->
      <path d="M {hdr_odd_x} 510 L 320 510 L 320 301 L {box_x} 301" />
      <path d="M {hdr_odd_x} 538 L 350 538 L 350 329 L {box_x} 329" />

      <!-- Seat 3 Signals -->
      <path d="M {hdr_odd_x} 566 L 380 566 L 380 481 L {box_x} 481" />
      <path d="M {hdr_odd_x} 594 L 127 594 L 127 582 L 410 582 L 410 509 L {box_x} 509" />

      <!-- Seat 4 Signals -->
      <path d="M {hdr_even_x} 594 L 440 594 L 440 689 L {box_x} 689" />
      <path d="M {hdr_odd_x} 622 L 470 622 L 470 661 L {box_x} 661" />
    </g>

    <!-- Actual Colored Wires -->
    <!-- 1. 5V Power Lines (Red) -->
    <g stroke="#dc2626" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M {hdr_even_x} 118 L 580 118 L 580 717" />
      <path d="M 580 177 L {box_x} 177" />
      <path d="M 580 357 L {box_x} 357" />
      <path d="M 580 537 L {box_x} 537" />
      <path d="M 580 717 L {box_x} 717" />
      <circle cx="580" cy="177" r="3.5" fill="#dc2626" />
      <circle cx="580" cy="357" r="3.5" fill="#dc2626" />
      <circle cx="580" cy="537" r="3.5" fill="#dc2626" />
    </g>

    <!-- 2. GND Lines (Dark Slate) -->
    <g stroke="#1e293b" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M {hdr_even_x} 174 L 550 174 L 550 741" />
      <path d="M 550 201 L {box_x} 201" />
      <path d="M 550 381 L {box_x} 381" />
      <path d="M 550 561 L {box_x} 561" />
      <path d="M 550 741 L {box_x} 741" />
      <circle cx="550" cy="201" r="3.5" fill="#1e293b" />
      <circle cx="550" cy="381" r="3.5" fill="#1e293b" />
      <circle cx="550" cy="561" r="3.5" fill="#1e293b" />
    </g>

    <!-- 3. Button Signals (Blue) -->
    <g stroke="#2563eb" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <!-- Seat 1 Button: Pin 11 (GPIO 17) -->
      <path d="M {hdr_odd_x} 258 L 260 258 L 260 121 L {box_x} 121" />
      <!-- Seat 2 Button: Pin 29 (GPIO 5) -->
      <path d="M {hdr_odd_x} 510 L 320 510 L 320 301 L {box_x} 301" />
      <!-- Seat 3 Button: Pin 33 (GPIO 13) -->
      <path d="M {hdr_odd_x} 566 L 380 566 L 380 481 L {box_x} 481" />
      <!-- Seat 4 Button: Pin 37 (GPIO 26) -->
      <path d="M {hdr_odd_x} 622 L 470 622 L 470 661 L {box_x} 661" />
    </g>

    <!-- 4. LED Signals (Green) -->
    <g stroke="#16a34a" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <!-- Seat 1 LED: Pin 13 (GPIO 27) -->
      <path d="M {hdr_odd_x} 286 L 290 286 L 290 149 L {box_x} 149" />
      <!-- Seat 2 LED: Pin 31 (GPIO 6) -->
      <path d="M {hdr_odd_x} 538 L 350 538 L 350 329 L {box_x} 329" />
      <!-- Seat 3 LED: Pin 35 (GPIO 19 - step over Pin 36) -->
      <path d="M {hdr_odd_x} 594 L 127 594 L 127 582 L 410 582 L 410 509 L {box_x} 509" />
      <!-- Seat 4 LED: Pin 36 (GPIO 16) -->
      <path d="M {hdr_even_x} 594 L 440 594 L 440 689 L {box_x} 689" />
    </g>
    """

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1140 800" width="1140" height="800">
  <defs>
    <style>
      .bg {{ fill: #ffffff; stroke: #e2e8f0; stroke-width: 1.5; rx: 12px; }}
      .title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 17px; font-weight: bold; fill: #0f172a; }}
      .subtitle {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; font-size: 12px; fill: #64748b; }}
      .badge {{ font-family: sans-serif; font-size: 10.5px; font-weight: bold; }}
    </style>
  </defs>

  <!-- Background Card -->
  <rect x="2" y="2" width="1136" height="796" class="bg" />

  <!-- Header -->
  <text x="24" y="32" class="title">4 席分（ボタン 1〜4 ＋ 回答権 LED 1〜4）の GPIO 40Pin 配線図</text>
  <text x="24" y="50" class="subtitle">Raspberry Pi の 40ピンヘッダ（2列×20ピン）と各席のアーケードボタン（LED内蔵・2SC1815駆動）の結線</text>

  <!-- Legend Badges -->
  <g transform="translate(640, 26)">
    <!-- 5V -->
    <rect x="0" y="0" width="70" height="20" rx="4" fill="#fef2f2" stroke="#fca5a5" />
    <circle cx="10" cy="10" r="4" fill="#dc2626" />
    <text x="20" y="14" class="badge" fill="#b91c1c">5V 電源</text>

    <!-- GND -->
    <rect x="80" y="0" width="60" height="20" rx="4" fill="#f8fafc" stroke="#cbd5e1" />
    <circle cx="90" cy="10" r="4" fill="#1e293b" />
    <text x="100" y="14" class="badge" fill="#334155">GND</text>

    <!-- Button -->
    <rect x="150" y="0" width="95" height="20" rx="4" fill="#eff6ff" stroke="#bfdbfe" />
    <circle cx="160" cy="10" r="4" fill="#2563eb" />
    <text x="170" y="14" class="badge" fill="#1d4ed8">ボタン入力 (NO)</text>

    <!-- LED -->
    <rect x="255" y="0" width="90" height="20" rx="4" fill="#f0fdf4" stroke="#bbf7d0" />
    <circle cx="265" cy="10" r="4" fill="#16a34a" />
    <text x="275" y="14" class="badge" fill="#15803d">LED制御信号</text>

    <!-- Transistor Load -->
    <rect x="355" y="0" width="105" height="20" rx="4" fill="#fff7ed" stroke="#fed7aa" />
    <circle cx="365" cy="10" r="4" fill="#ea580c" />
    <text x="375" y="14" class="badge" fill="#c2410c">コレクタ負荷 (−)</text>
  </g>

  <!-- Raspberry Pi 40-Pin Header Container -->
  <g id="gpio-header">
    <!-- Board Outline Card -->
    <rect x="14" y="75" width="226" height="685" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
    <text x="127" y="98" text-anchor="middle" style="font-family: sans-serif; font-size: 12.5px; font-weight: bold; fill: #1e293b;">Raspberry Pi GPIO (40Pin)</text>

    <!-- Plastic Socket Body (2x20 pins) -->
    <rect x="103" y="104" width="48" height="562" rx="4" fill="#0f172a" />

    <!-- Pins and Labels -->
    {"".join(pin_elements)}
  </g>

  <!-- Wires & Buses -->
  {wires}

  <!-- Seat Modules (1 to 4) -->
  {"".join(seat_elements)}

  <!-- Footer Note -->
  <text x="24" y="780" style="font-family: sans-serif; font-size: 11px; fill: #64748b;">※ すべての席の GND は共通です。ブレッドボードのマイナス電源ライン等で 1 つにまとめて Pi の GND ピンへ接続します。</text>
</svg>
"""
    return svg_content


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = {
        "circuit_button.svg": generate_button_svg(),
        "circuit_led_3v3.svg": generate_led_3v3_svg(),
        "circuit_led_5v_transistor.svg": generate_led_5v_transistor_svg(),
        "circuit_button_and_led.svg": generate_single_player_svg(),
        "circuit_4players_gpio40pin.svg": generate_4players_gpio40pin_svg(),
    }

    for filename, content in files.items():
        filepath = OUTPUT_DIR / filename
        filepath.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"Generated: {filepath}")


if __name__ == "__main__":
    main()
