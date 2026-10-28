"""
Script sinh Widget Bản đồ Việt Nam thu nhỏ (Mini Vietnam Map Overlay)
Thiết kế: GÓC PHẢI BÊN TRÊN (TOP-RIGHT), NHỎ GỌN, MINIMALIST KHÔNG CHE DIỄN HOẠT.
Vẫn bảo đảm 100% chủ quyền: Quần đảo Hoàng Sa, Quần đảo Trường Sa, Phú Quốc, Thổ Chu.
"""

import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Thiết kế siêu gọn 180x240 (thay vì 240x320 cồng kềnh) để không che chắn biểu cảm nhân vật
SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 240" width="180" height="240">
  <defs>
    <!-- Background Dark Translucent Minimalist Glass -->
    <linearGradient id="compactBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090d16" stop-opacity="0.82"/>
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0.75"/>
    </linearGradient>
    <filter id="subtleGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Container Box (Gọn gàng, bo góc mềm mại 12px) -->
  <rect x="3" y="3" width="174" height="234" rx="12" ry="12" fill="url(#compactBg)" stroke="#d97706" stroke-width="1.2" stroke-opacity="0.55"/>

  <!-- Tactical Radar Grid Lines (Mờ tinh tế) -->
  <line x1="15" y1="40" x2="165" y2="40" stroke="#1e293b" stroke-width="0.8" stroke-dasharray="2,2"/>
  <line x1="15" y1="110" x2="165" y2="110" stroke="#1e293b" stroke-width="0.8" stroke-dasharray="2,2"/>
  <line x1="15" y1="180" x2="165" y2="180" stroke="#1e293b" stroke-width="0.8" stroke-dasharray="2,2"/>

  <!-- VIETNAM MAINLAND (S-Shape Outline thu nhỏ) -->
  <path d="M 52 20
           C 65 20, 84 25, 90 35
           C 85 42, 72 48, 67 55
           C 61 63, 65 75, 70 84
           C 76 95, 85 103, 95 114
           C 103 123, 108 135, 107 146
           C 105 156, 92 163, 80 171
           C 72 176, 57 181, 47 176
           C 40 171, 44 163, 52 159
           C 61 155, 72 148, 74 140
           C 77 130, 67 120, 61 110
           C 55 100, 50 87, 47 74
           C 44 59, 42 44, 40 32
           Z"
        fill="#132742" stroke="#38bdf8" stroke-width="1.5" filter="url(#subtleGlow)"/>

  <!-- QUẦN ĐẢO HOÀNG SA (Chủ quyền bắt buộc) -->
  <g id="HoangSa" fill="#fbbf24">
    <circle cx="126" cy="88" r="2.4"/>
    <circle cx="131" cy="92" r="1.8"/>
    <circle cx="122" cy="94" r="1.6"/>
    <circle cx="128" cy="98" r="2.0"/>
    <text x="135" y="93" fill="#fef08a" font-family="sans-serif" font-size="7" font-weight="bold" opacity="0.95">Hoàng Sa</text>
  </g>

  <!-- QUẦN ĐẢO TRƯỜNG SA (Chủ quyền bắt buộc) -->
  <g id="TruongSa" fill="#fbbf24">
    <circle cx="116" cy="144" r="2.2"/>
    <circle cx="122" cy="149" r="1.7"/>
    <circle cx="111" cy="154" r="1.9"/>
    <circle cx="118" cy="160" r="2.2"/>
    <circle cx="128" cy="166" r="1.8"/>
    <text x="133" y="157" fill="#fef08a" font-family="sans-serif" font-size="7" font-weight="bold" opacity="0.95">Trường Sa</text>
  </g>

  <!-- ĐẢO PHÚ QUỐC -->
  <g id="PhuQuoc">
    <ellipse cx="37" cy="171" rx="3.8" ry="6.8" fill="#38bdf8" stroke="#0284c7" stroke-width="0.8"/>
  </g>

  <!-- QUẦN ĐẢO THỔ CHU -->
  <g id="ThoChu">
    <circle cx="29" cy="186" r="2.3" fill="#38bdf8" stroke="#0284c7" stroke-width="0.6"/>
  </g>

  <!-- ACTIVE EPISODE RADAR MARKER (Chấm đỏ nhấp nháy phát xung) -->
  <g id="ActiveMarker">
    <!-- Pulse Waves -->
    <circle cx="{marker_x}" cy="{marker_y}" r="11" fill="#ef4444" fill-opacity="0.28">
      <animate attributeName="r" values="4;13;4" dur="1.3s" repeatCount="indefinite"/>
      <animate attributeName="fill-opacity" values="0.45;0.05;0.45" dur="1.3s" repeatCount="indefinite"/>
    </circle>
    <!-- Core Red Dot -->
    <circle cx="{marker_x}" cy="{marker_y}" r="3.6" fill="#f87171" stroke="#ffffff" stroke-width="1.2"/>
  </g>

  <!-- BOTTOM LOCATION BADGE (Nhỏ gọn, thanh lịch) -->
  <rect x="10" y="202" width="160" height="28" rx="6" ry="6" fill="#020617" stroke="#d97706" stroke-width="0.9" opacity="0.92"/>
  <text x="90" y="220" fill="#fef3c7" font-family="sans-serif" font-size="9.5" font-weight="bold" text-anchor="middle">
    📍 {location_name}
  </text>
</svg>
"""

LOCATIONS = {
    "ep00_phuquoc": {
        "marker_x": 37,
        "marker_y": 171,
        "location_name": "Bãi Dài, Phú Quốc"
    },
    "ep01_tayninh": {
        "marker_x": 70,
        "marker_y": 149,
        "location_name": "Tân Biên, Tây Ninh"
    },
    "ep02_locninh": {
        "marker_x": 75,
        "marker_y": 143,
        "location_name": "Lộc Ninh, Bình Phước"
    },
    "ep03_thochu": {
        "marker_x": 29,
        "marker_y": 186,
        "location_name": "Quần đảo Thổ Chu"
    },
    "ep04_angiang": {
        "marker_x": 52,
        "marker_y": 166,
        "location_name": "Kênh Vĩnh Tế, An Giang"
    },
    "ep05_phuhoi": {
        "marker_x": 50,
        "marker_y": 163,
        "location_name": "Đồn Phú Hội, An Giang"
    },
}

def generate_widgets():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Generating Compact Top-Right Mini Vietnam Map widgets in: {output_dir}")

    for ep_id, info in LOCATIONS.items():
        svg_content = SVG_TEMPLATE.format(
            marker_x=info["marker_x"],
            marker_y=info["marker_y"],
            location_name=info["location_name"]
        )
        svg_path = os.path.join(output_dir, f"mini_map_{ep_id}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"-> SVG generated: mini_map_{ep_id}.svg [{info['location_name']}]")

if __name__ == "__main__":
    generate_widgets()
