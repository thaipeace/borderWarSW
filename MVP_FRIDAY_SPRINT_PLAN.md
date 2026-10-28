# KẾ HOẠCH HÀNH ĐỘNG SPRINT: MỤC TIÊU BẢN MVP THỨ SÁU
## LỘ TRÌNH 3 NGÀY TỪ TẠO HÌNH NHÂN VẬT ĐẾN RENDER THÀNH PHẨM TRÊN HAIZFLOW

---

### I. MỤC TIÊU CỐT LÕI (FRIDAY MVP GOAL)

* **Hạn chót**: Thứ Sáu (30/10/2026).
* **Sản phẩm bàn giao**: 01 Video Short 60s hoàn chỉnh chuẩn điện ảnh hoạt hình (9:16 - 1080x1920).
* **Tập phim thực hiện**: **Tập 00: Tiếng Súng Lạ Ở Bãi Dài Phú Quốc (Đêm 03/5/1975)** (hoặc Tập 01: Lệnh Kiềm Chế 1976).
* **Thành phần video**:
  1. Hình ảnh hoạt hình 2D Anime Semi-realistic (nhân vật diễn xuất, cử chỉ, biểu cảm).
  2. Mini-Map Widget bản đồ Việt Nam góc phải trên có radar nhấp nháy tại Phú Quốc.
  3. Lồng tiếng đối thoại 2 nhân vật (Anh Cả Thạch & Út Hưng) qua TTS Vieneu (ngắt nghỉ cảm xúc).
  4. Hiệu ứng âm thanh Foley (tiếng sóng, tiếng súng đanh thép, tiếng lên đạn).
  5. Phụ đề tiếng Việt chuẩn vùng an toàn (Safe Zone).
  6. Mẫu Description & Tri ân sẵn sàng xuất bản.

---

### II. TIẾN ĐỘ THỰC HIỆN THEO TỪNG NGÀY

```
    THỨ TƯ (MAI)                     THỨ NĂM                         THỨ SÁU (DEADLINE)
┌───────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐
│ CỐ ĐỊNH NHÂN VẬT      │   │ SẢN XUẤT AUDIO & VISUAL   │   │ HAIZFLOW RENDER & QA      │
│ • Model Sheet Anh Cả  │──>│ • Sinh 5 Scene Storyboard │──>│ • Ghép Timeline 60s      │
│ • Model Sheet Út Hưng │   │ • Tạo TTS Vieneu 2 giọng  │   │ • Gắn Mini-Map góc phải   │
│ • Chốt Visual Prompts │   │ • Gắn SFX tiếng động      │   │ • Xuất MP4 1080x1920      │
└───────────────────────┘   └───────────────────────────┘   └───────────────────────────┘
```

#### 📅 NGÀY 1: THỨ TƯ – THIẾT KẾ & ĐỒNG BỘ NHÂN VẬT (CHARACTER DESIGN)
- [ ] Thiết lập Prompt Model Sheet cho **Anh Cả Thạch** (30t, nghiêm nghị, dạn dày sương gió, áo Tô Châu nón cối).
- [ ] Thiết lập Prompt Model Sheet cho **Út Hưng** (18-19t, thư sinh, trong sáng, lính mới).
- [ ] Khóa cố định nét mặt, kiểu tóc và trang phục để đảm bảo nhân vật không bị biến dạng giữa các cảnh (Character Visual Consistency).
- [ ] Lưu trữ profile ảnh mẫu vào `02_CHARACTER_PROFILES/`.

#### 📅 NGÀY 2: THỨ NĂM – SẢN XUẤT ASSET HÌNH ẢNH & THOẠI TRÊN HAIZFLOW
- [ ] Sinh 5 khung hình chính (Scene 1 đến Scene 5) theo kịch bản Tập 00:
  - Cảnh 1: Bãi cát Bãi Dài đêm trăng, lá cờ trên nóc đồn, bóng xuồng máy rẽ sóng.
  - Cảnh 2: Anh Cả soi ống nhòm thấy 4 bóng lính áo đen nhảy xuống mép nước.
  - Cảnh 3: Bắn pháo hiệu cảnh cáo và nổ súng đánh bật toán quân xâm lấn.
  - Cảnh 4: Nhặt lại bức thư nhà lấm cát, ánh mắt nhìn ra biển đêm.
  - Cảnh 5: Bình minh rực sáng trên đỉnh đảo ngọc Phú Quốc.
- [ ] Tạo file audio đối thoại qua engine TTS Vieneu của HaizFlow:
  - Giọng Anh Cả Thạch: Bắc / Bắc Trung Bộ đĩnh đạc, ấm, uy lực chỉ huy.
  - Giọng Út Hưng: Sài Gòn trẻ, trong, xúc động.
- [ ] Chuẩn bị tiếng động SFX (sóng biển vỗ rì rào, tiếng lách cách lên đạn, tràng đạn AK).

#### 📅 NGÀY 3: THỨ SÁU – GHÉP TIMELINE, GẮN MINI-MAP & RENDER HOÀN THIỆN
- [ ] Nạp kịch bản vào cấu hình dự án HaizFlow (`05_HAIZFLOW_PROJECTS/`).
- [ ] Gắn lớp overlay `mini_map_ep00_phuquoc.svg` vào góc trên bên phải (`X=860, Y=70`).
- [ ] Đồng bộ nhịp thoại với phụ đề tự động (Subturn synchronization).
- [ ] Chạy lệnh Render video dọc chuẩn 1080 x 1920 MP4.
- [ ] Thực hiện kiểm tra 6 tiêu chí Harness Checklist (chính trị, âm thanh, pháp lý, chính tả).
- [ ] Lưu video hoàn thiện vào `06_RENDERED_SHORTS/` sẵn sàng phát hành cuối tuần!
