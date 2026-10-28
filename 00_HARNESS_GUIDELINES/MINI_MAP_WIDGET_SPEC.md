# QUY CHUẨN THIẾT KẾ MINI-MAP VIỆT NAM (TOP-RIGHT COMPACT OVERLAY)
## VỊ TRÍ GÓC TRÊN BÊN PHẢI - THIẾT KẾ SIÊU GỌN - KHÔNG CHE CHẮN DIỄN HOẠT

---

### I. NGUYÊN TẮC: "ĐỦ ĐỊNH VỊ - KHÔNG CHE DIỄN XUẤT"

Trong video hoạt hình ngắn 60s (Shorts), biểu cảm khuôn mặt và cử chỉ hành động của nhân vật là linh hồn của tác phẩm. Vì vậy:
1. **Chuyển sang góc trên bên phải (Top-Right Corner)**: Đây là góc thoáng mắt nhất, không che chắn góc nhìn chính diện hay góc nhìn 3/4 của nhân vật (thường nằm ở trung tâm hoặc góc trái dưới).
2. **Kích thước siêu gọn (Compact Minimalist)**: Giảm xuống kích thước `180 x 240 px` (tỷ lệ rất nhỏ trên tổng khung hình 1080 x 1920, chiếm chưa đến 3% diện tích hiển thị).
3. **Nền kính tối bán trong suốt (Dark Glassmorphism)**: Độ mờ nhẹ `opacity: 0.78` giúp người xem nhìn thoáng qua là nhận biết được vị trí, nhưng không làm phân tán sự chú ý khỏi mạch phim.

---

### II. BỐ TRÍ KHUNG HÌNH (LAYOUT TRÊN VIDEO DỌC 9:16 - 1080x1920)

```
┌──────────────────────────────────────────────────────────┐
│  [TOP SAFE ZONE]               ┌───────────────────────┐ │
│                                │ 🇻🇳 MINI-MAP COMPACT   │ │
│                                │     /\                │ │
│                                │    (  )   (Hoàng Sa)  │ │
│                                │     \ \        *      │ │
│                                │      \ \              │ │
│                                │       ) ) (Trường Sa) │ │
│                                │    🔴<_/       *      │ │
│                                │   📍 Tân Biên, Tây Ninh│ │
│                                └───────────────────────┘ │
│                                                          │
│                                                          │
│                 KHUNG HÌNH DIỄN HOẠT                     │
│                 NHÂN VẬT & ĐỐI THOẠI                     │
│            (HOÀN TOÀN THÔNG THOÁNG KHÔNG GIAN)           │
│                                                          │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ SUBTITLES (Khớp nhịp thoại Vieneu)                 │  │
│  └────────────────────────────────────────────────────┘  │
│  [BOTTOM SAFE ZONE]                                      │
└──────────────────────────────────────────────────────────┘
```

* **Vị trí**: Góc trên bên phải (Top-Right).
* **Tọa độ đề xuất trên canvas 1080 x 1920**: `X = 860px`, `Y = 70px`.
* **Kích thước**: `180 x 240 px`.
* **Mỹ thuật & Tương tác**:
  - Viền bản đồ S-shape màu xanh ngọc radar (`#38bdf8`) thanh mảnh.
  - Quần đảo **Hoàng Sa** và **Trường Sa** thể hiện đầy đủ bằng các chấm vàng kim và chữ chú thích nhỏ gọn.
  - Đảo **Phú Quốc** và Quần đảo **Thổ Chu** hiển thị rõ ràng trên vùng biển Tây Nam.
  - **Radar Marker**: Điểm đỏ nhấp nháy phát xung nhẹ chu kỳ 1.3s tại địa bàn tập phim.
  - **Huy hiệu địa danh**: `📍 [Tên Địa Danh]` bo góc mềm mại ở đáy widget.

---

### III. DANH MỤC ASSET SVG CÓ SẴN (TRONG `04_PROMPTS_ASSETS/MAP_WIDGETS/`)

1. `mini_map_ep00_phuquoc.svg` ➔ 📍 Bãi Dài, Phú Quốc
2. `mini_map_ep01_tayninh.svg` ➔ 📍 Tân Biên, Tây Ninh
3. `mini_map_ep02_locninh.svg` ➔ 📍 Lộc Ninh, Bình Phước
4. `mini_map_ep03_thochu.svg` ➔ 📍 Quần đảo Thổ Chu
5. `mini_map_ep04_angiang.svg` ➔ 📍 Kênh Vĩnh Tế, An Giang
6. `mini_map_ep05_phuhoi.svg` ➔ 📍 Đồn Phú Hội, An Giang

Script tái tạo hoặc mở rộng cho các tập tiếp theo: [generate_map_widget.py](file:///c:/projects/borderWarSW779/04_PROMPTS_ASSETS/MAP_WIDGETS/generate_map_widget.py).
