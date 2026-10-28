# QUY TRÌNH KỸ THUẬT & SẢN XUẤT VỚI HAIZFLOW
## BORDER WAR SW 779 x HAIZFLOW PIPELINE

---

### I. MÔ HÌNH VẬN HÀNH 5 BƯỚC HÀNG TUẦN

```
     [Thứ 2 - Thứ 3]                 [Thứ 4]                  [Thứ 5]                 [Thứ 6]            [Thứ 7 - CN]
┌─────────────────────────┐   ┌───────────────────┐   ┌─────────────────────┐   ┌──────────────────┐   ┌──────────────┐
│  Thẩm định tư liệu &    │──>│  Sinh Visual &    │──>│  Ghép Multi-speaker │──>│  Render HaizFlow │──>│  Phát sóng & │
│  Viết kịch bản thoại    │   │  Tạo hình nhân vật│   │  TTS & Hiệu ứng SFX │   │  & Kiểm duyệt QA │   │  Tương tác   │
│  (Theo Harness 3 Đúng)  │   │  (Prompt chuẩn)   │   │  (Vieneu Profile)   │   │  (9:16 Vertical) │   │  Cộng đồng   │
└─────────────────────────┘   └───────────────────┘   └─────────────────────┘   └──────────────────┘   └──────────────┘
```

---

### II. TÍCH HỢP TÍNH NĂNG ĐẶC THÙ TRÊN HAIZFLOW

1. **Speaker Identity & Subturns (test_speaker_identity.py / test_speaker_subturns.py)**:
   - Cấu hình từng nhân vật trong file kịch bản thành các turn thoại rõ ràng (`speaker: ba_binh`, `speaker: ut_hung`, `speaker: anh_ca`).
   - Sử dụng cơ chế ngắt nhịp (pause responsiveness) để tạo sự kịch tính: những khoảng lặng 0.5s - 1.2s trước khi nhân vật nói để tạo độ sâu cảm xúc (tiếng thở, tiếng nuốt nghẹn).

2. **Hệ thống giọng đọc (TTS Vieneu / Voice Cloning / Runtime)**:
   - Gán Voice Profile cố định cho từng nhân vật để đảm bảo tính nhất quán (character voice consistency) qua 100 tập:
     + `voice_ba_binh`: Giọng Nam Bộ phong trần, độ tuổi 20-25.
     + `voice_ut_hung`: Giọng Nam Sài Gòn trẻ, trong, cảm xúc.
     + `voice_anh_ca`: Giọng Bắc/Bắc Trung Bộ đĩnh đạc, ấm áp.
     + `voice_outro_narrator`: Giọng đọc phim tài liệu chuẩn, hào sảng, trang nghiêm.

3. **Slide / Timeline Composer & Subtitle Alignment (test_timeline_render.py)**:
   - Tỷ lệ khung hình: **9:16 Vertical (1080 x 1920)** chuẩn YouTube Shorts.
   - Subtitle: Phông chữ sans-serif hiện đại, viền đậm tương phản cao, định vị ở vùng an toàn (Safe Zone) 25% phía dưới màn hình để không bị thanh công cụ YouTube Shorts / TikTok che khuất.
   - Nhạc nền: Bộ thư viện nhạc hào hùng, hoài niệm, âm sắc nhạc cụ dân tộc (đàn bầu, sáo trúc, trống Paranưng) với âm lượng ducking tự động khi nhân vật cất tiếng thoại.

---

### III. BẢNG CHECKLIST KIỂM DUYỆT (QA HARNESS AUDIT TRƯỚC KHI RENDER)

Trước khi xuất file video cuối cùng, bắt buộc kiểm tra 6 tiêu chí:

- [ ] **1. Tên gọi & Thuật ngữ**: Không dùng từ ngữ miệt thị sắc tộc; dùng đúng "Quân tình nguyện Việt Nam", "Tập đoàn phản động Pol Pot".
- [ ] **2. Tinh thần chủ đạo**: Có nêu bật được tính tự vệ chính đáng hoặc tinh thần quốc tế vô tư cứu bạn không?
- [ ] **3. Chi tiết lịch sử**: Ngày tháng, địa danh (Ba Chúc, Vĩnh Tế, Mặt trận 779, Snuol, Phnom Penh) có chính xác với sử liệu quân sự không?
- [ ] **4. Hình ảnh bạo lực**: Có yếu tố máu me ghê rợn vi phạm nguyên tắc cộng đồng YouTube hoặc gây phản cảm không? (Chỉ dùng ẩn dụ nghệ thuật).
- [ ] **5. Nhịp điệu kịch bản**: Có giữ đúng cấu trúc kịch tính 60s (Hook -> Diễn biến đối thoại -> Cao trào nhân văn -> Thông điệp kết)?
- [ ] **6. Chất lượng kỹ thuật**: Âm thanh thoại rõ chữ, không bị nhạc nền lấn át, phụ đề khớp 100% từng từ.
