# KẾ HOẠCH HÀNH ĐỘNG SPRINT: MỤC TIÊU BẢN MVP THỨ SÁU (CHUẨN v6.0)
## LỘ TRÌNH 3 NGÀY TỪ TẠO HÌNH NHÂN VẬT ĐẾN RENDER THÀNH PHẨM TRÊN HAIZFLOW
*Cập nhật: 29/10/2026 | Đồng bộ theo kịch bản `EP01_DemDauThang5_PhuQuoc_v6_60s.md` (60s – Thế Kẹt Độc Đạo, Zero Map Policy)*

---

### I. MỤC TIÊU CỐT LÕI (FRIDAY MVP GOAL)

* **Hạn chót**: Thứ Sáu (30/10/2026).
* **Sản phẩm bàn giao**: 01 Video Short 60s hoàn chỉnh chuẩn điện ảnh hoạt hình phóng tác vi mô (9:16 - 1080x1920).
* **Tập phim thực hiện**: **Tập 01 – Đêm Đầu Tháng 5 Ở Phú Quốc (v6 – 60 giây: Thế Kẹt Độc Đạo)** (`EP01_DemDauThang5_PhuQuoc_v6_60s.md`).
* **Thành phần video chuẩn v6.0**:
  1. **5 phân cảnh hoạt hình bán tả thực (Semi-realistic Graphic Novel / Painterly Cinematic)** đã render tại `factory/staging/Chapter1/assets/` (`scene1_boat_night.jpg` → `scene5_sunrise_peace.jpg`).
  2. **Chính sách Zero Map Policy (Không bản đồ)**: Tuyệt đối không gắn bất kỳ widget hay hình ảnh bản đồ nào; sử dụng góc máy điện ảnh từ trên cao (`Cinematic High-Angle Shot`) ở Nhịp 4 để thể hiện thế kẹt địa hình tự nhiên (biển sâu – dải cát hẹp – đầm lầy ngập mặn – chốt chặn độc đạo).
  3. **Lồng tiếng 3 nhân vật hình tượng ẩn danh (3 câu thoại siêu ngắn ~15 từ)**:
     - *Người chài trẻ* (Nhịp 3, giọng thở dốc gấp gáp): `"Tàu lạ đổ bộ bãi cát... quân đông lắm, báo gấp!"`
     - *Người trực đêm* (Nhịp 4, giọng đanh gọn dứt khoát): `"Chúng kẹt rồi!"`
     - *Lão chài* (Nhịp 5, giọng trầm ấm nhẹ nhõm): `"Hòn đảo của mình... sóng lại êm rồi."`
  4. **Hiệu ứng âm thanh Foley / SFX & BGM**: Tiếng máy ghe *tạch... tạch...*, sóng vỗ, cú quật cần lái *BỐP!*, tiếng nhảy xuống biển *ÙM!*, tiếng súng nổ rát rạt xa dần, tiếng đập cửa *Cộc! Cộc! Cộc!*, tiếng kẻng báo động, tiếng bùn lầy, tiếng sóng biển êm dịu và giai điệu sáo trúc / đàn bầu nhẹ nhàng khép lại.
  5. **Text Overlay & Phụ đề vùng an toàn (Safe Zone 25% dưới)**:
     - Giây `01–03`: *"Đêm đầu tháng 5/1975"*
     - Phụ đề khớp 3 câu thoại ở Nhịp 3, 4, 5.
     - Giây `57–60` (Disclaimer bắt buộc): *"Phóng tác từ lời kể của một cựu chiến binh. Nhân vật và tình tiết đã được hư cấu hóa."*
  6. **Mẫu Description & Bình luận ghim chuẩn phóng tác**: Ghi rõ tác phẩm hoạt hình phóng tác hư cấu hóa nghệ thuật, khai báo nội dung có hỗ trợ bởi công cụ AI, không khẳng định chi tiết sự kiện hay nêu tên thật nhận diện cá nhân.

---

### II. TIẾN ĐỘ THỰC HIỆN THEO TỪNG NGÀY

```
     THỨ TƯ (ĐÃ XONG ✅)              THỨ NĂM (HÔM NAY ⏳)               THỨ SÁU (DEADLINE 🎯)
┌───────────────────────────┐   ┌───────────────────────────────┐   ┌───────────────────────────────┐
│ HÌNH TƯỢNG & KỊCH BẢN v6  │   │ VISUAL QA & SẢN XUẤT AUDIO    │   │ HAIZFLOW RENDER & QA          │
│ • Chuẩn hóa Archetypes    │──>│ • Render 5 Scene 9:16 (XONG)  │──>│ • Ghép Timeline 60s (5 nhịp)  │
│   (Lão chài, Anh chài...) │   │ • Rà soát Visual QA Scene 4,5 │   │ • Áp dụng Zero Map Policy     │
│ • Khóa kịch bản v6 (60s)  │   │ • Tạo 3 câu TTS + SFX 5 nhịp  │   │ • Xuất MP4 1080x1920 & Kiểm QA│
└───────────────────────────┘   └───────────────────────────────┘   └───────────────────────────────┘
```

#### 📅 NGÀY 1: THỨ TƯ – CHUẨN HÓA HÌNH TƯỢNG NHÂN VẬT & KỊCH BẢN v6.0 (ĐÃ HOÀN THÀNH ✅)
- [x] Chuyển đổi từ nhân vật tên thật sang bộ **Hình mẫu điển hình thuần Việt (Archetypes)** trong `02_CHARACTER_PROFILES/CORE_CHARACTERS.md`: *Lão chài*, *Người chài trẻ*, *Người trực đêm*, *Lính áo đen*.
- [x] Khóa phong cách mỹ thuật **Semi-realistic Graphic Novel / Painterly Cinematic** (tránh lỗi mắt to kiểu Anime Nhật Bản, chuẩn hóa áo bà ba, khăn rằn, nón lá, ghe máy vỏ gỗ Nam Bộ).
- [x] Hoàn thiện kịch bản `EP01_DemDauThang5_PhuQuoc_v6_60s.md` (60 giây, 5 nhịp, 3 câu thoại ngắn, áp dụng **Zero Map Policy**).

#### 📅 NGÀY 2: THỨ NĂM – RENDER 5 PHÂN CẢNH, VISUAL QA & SẢN XUẤT AUDIO
- [x] **Render 5 khung hình chính (Nhịp 1 đến Nhịp 5)** lưu tại `factory/staging/Chapter1/assets/`:
  - [x] **Nhịp 1 (00–10s)** – `scene1_boat_night.jpg`: Ghe máy rẽ sóng biển đêm, bóng lính lạ cầm súng AK đứng mũi ghe, hai người dân chài liếc mắt ra hiệu ngầm.
  - [x] **Nhịp 2 (10–20s)** – `scene2_action_tiller.jpg`: Cú quật cần lái gỗ *BỐP!* và pha lao mình nhảy xuống biển đêm thoát hiểm.
  - [x] **Nhịp 3 (20–30s)** – `scene3_alert_cabin.jpg`: Hai ngư dân ướt sũng đập cửa trạm gác báo động dưới ánh đèn bão của người trực đêm.
  - [x] **Nhịp 4 (30–46s)** – `scene4_bottleneck_swamp.jpg`: Góc máy cao (`Cinematic High-Angle Shot`, không dùng bản đồ) khắc họa thế kẹt giữa biển sâu, dải cát hẹp, đầm lầy ngập mặn và chốt chặn độc đạo.
  - [x] **Nhịp 5 (46–60s)** – `scene5_sunrise_peace.jpg`: Bình minh trên đảo ngọc, bóng tàu rút dần ngoài khơi, hai ngư dân đứng dưới lá cờ Tổ quốc tung bay.
- [x] **Rà soát thị giác (Visual QA – GATE 1)** trước khi đưa vào dựng:
  - Đã sao lưu bản gốc vào `assets/originals_backup/`, nâng cấp `scene4_bottleneck_swamp.jpg` (giữ nguyên 3 nhân vật key giữa bãi cát + bổ sung lính áo đen lún bùn rễ đước bên phải) và xoay đuôi tàu hướng về phía bờ rút ra khơi trong `scene5_sunrise_peace.jpg`. Đã xuất [`factory/production/Chapter1/motion_plan.json`](file:///c:/projects/borderWarSW779/factory/production/Chapter1/motion_plan.json).
- [ ] **Tạo 3 file audio thoại qua engine TTS Vieneu**:
  - *Người chài trẻ*: `"Tàu lạ đổ bộ bãi cát... quân đông lắm, báo gấp!"`
  - *Người trực đêm*: `"Chúng kẹt rồi!"`
  - *Lão chài*: `"Hòn đảo của mình... sóng lại êm rồi."`
- [ ] **Chuẩn bị bộ âm thanh Foley / SFX & Nhạc nền**: Máy ghe nổ *tạch... tạch...*, sóng vỗ, gậy gỗ đập *BỐP!*, nhảy nước *ÙM!*, súng nổ xa dần, đập cửa gỗ, kẻng báo động, tiếng lội bùn, tiếng sóng êm & nhạc sáo trúc/đàn bầu kết tập.

#### 📅 NGÀY 3: THỨ SÁU – GHÉP TIMELINE 60S (ZERO MAP), CHÈN TEXT & RENDER MP4
- [ ] Khởi tạo cấu hình dự án HaizFlow (`05_HAIZFLOW_PROJECTS/` hoặc `factory/production/`).
- [ ] Áp dụng chuyển động camera (Ken Burns pan/zoom/shake hoặc Image-to-Video) cho 5 phân cảnh khớp tổng thời lượng **60 giây** (`10s + 10s + 10s + 16s + 14s`).
- [ ] **Thực thi Zero Map Policy**: Đảm bảo không gắn `mini_map_ep01_phuquoc.svg` hay bất kỳ đồ họa bản đồ nào lên khung hình.
- [ ] Chèn Text Overlay đầu (`"Đêm đầu tháng 5/1975"`), đồng bộ phụ đề 3 câu thoại và dòng chữ Disclaimer cuối phim (giây `57–60`) trong vùng Safe Zone.
- [ ] Chạy lệnh Render video dọc chuẩn `1080 x 1920` MP4 (60 giây) và lưu vào `06_RENDERED_SHORTS/`.
- [ ] Kiểm tra lần cuối theo bảng **QA Harness Checklist** & **Sổ Ràng Buộc Rủi Ro** trước khi xuất bản!
