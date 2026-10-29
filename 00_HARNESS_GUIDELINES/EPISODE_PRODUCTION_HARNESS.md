# HARNESS QUY TRÌNH SẢN XUẤT HOÀN THIỆN MỘT TẬP PHIM (EPISODE PRODUCTION HARNESS)
## QUY CHUẨN THỰC THI TỪ KHI CHỐT KHÂU CHUẨN BỊ ĐẾN KHI XUẤT BẢN MP4 (CHUẨN v6.0)
*Mã quy chuẩn: HRN-PROD-V6 | Áp dụng bắt buộc cho toàn bộ các tập Short 9:16 thuộc dự án Border War SW 779*

---

### I. MỤC ĐÍCH, KIẾN TRÚC 3 TẦNG THƯ MỤC & NGUYÊN TẮC VẬN HÀNH

Tài liệu này là **Đường ray Sản xuất Chuẩn (Standard Production Harness)**. Toàn bộ quá trình sản xuất một tập phim được phân bổ rõ ràng vào **3 tầng thư mục trong `factory/`** tương ứng với **6 Cổng kiểm soát (Gate 0 $\rightarrow$ Gate 6)**:

1. **`factory/materialAndDraft/ChapterX/` (Nơi lưu trữ toàn bộ tư liệu & Output của Gate 0, Gate 1, Gate 2, Gate 3)**:
   - Chứa hồ sơ nguồn (`source/`), thẩm định (`clearance/`), kịch bản chuẩn `v6` (`script/`), bộ ảnh phân cảnh đã duyệt/retouch (`assets/`), cấu hình chuyển động (`motion_plan.json`), giọng thoại (`audio/tts/`), tiếng động/nhạc nền (`audio/sfx/`, `audio/bgm/`) và bản trộn âm thanh 60s (`audio/mix/`).
2. **`factory/staging/ChapterX/` (Nơi thực thi & lưu trữ Output của Gate 4, Gate 5)**:
   - Chứa script dựng hình/timeline, file phụ đề/overlay Safe Zone (Zero Map), bản render kiểm duyệt MP4 `1080x1920` và biên bản kiểm định 8 tiêu chí cuối (`8-Point QA Audit`).
3. **`factory/production/ChapterX/` (Nơi lưu trữ Output hoàn chỉnh của Gate 6)**:
   - Chứa bản phát hành chính thức (`Final Master MP4`), gói Metadata/Description chuẩn đăng tải, hướng dẫn tích nhãn AI và hồ sơ lưu trữ xuất bản.

```
[TẦNG 1: factory/materialAndDraft/ChapterX/] ──► GATE 0, GATE 1, GATE 2, GATE 3
  │
  ├──► GATE 0 (ENTRY GATE): Kịch bản v6 + Clearance PASS + 5 Ảnh Scene 9:16
  ├──► GATE 1 (VISUAL QA & MOTION): Retouch lỗi AI + Xuất motion_plan.json
  ├──► GATE 2 (TTS VOICE & QA): Sinh 2–4 câu thoại ngắn + Nghe duyệt âm sắc
  └──► GATE 3 (SFX, BGM & MIX): Tổng hợp Ambience, Foley, BGM & Master Audio 60s
         │
         ▼
[TẦNG 2: factory/staging/ChapterX/] ───────────► GATE 4, GATE 5
  │
  ├──► GATE 4 (TIMELINE 60S & SAFE ZONE): Ghép hình + tiếng + Phụ đề/Hook (Zero Map)
  └──► GATE 5 (RENDER & 8-POINT QA): Xuất MP4 1080x1920 & Duyệt 8 tiêu chí cuối
         │
         ▼
[TẦNG 3: factory/production/ChapterX/] ────────► GATE 6
  │
  └──► GATE 6 (PACKAGING & RELEASE): Bản Final MP4 + Description phóng tác + Nhãn AI
```

---

### II. CỔNG ĐẦU VÀO (GATE 0): XÁC NHẬN KHÂU CHUẨN BỊ TẠI `materialAndDraft/ChapterX/`

Trước khi kích hoạt quy trình sản xuất (Gate 1 $\rightarrow$ Gate 6), tập phim tại `factory/materialAndDraft/ChapterX/` phải đạt đủ **5 điều kiện đầu vào**:

- [ ] **1. Hồ sơ Nguồn (`source/`)**: Đã lưu trữ tư liệu gốc nội bộ và phân loại mức độ xác thực (đa nguồn / đơn nguồn / hư cấu nghệ thuật).
- [ ] **2. Hồ sơ Thẩm định (`clearance/TAPXX_CLEARANCE.md`)**: Đã đạt trạng thái **ĐẠT (PASS)** theo chuẩn `v6.0`.
- [ ] **3. Kịch bản Chuẩn `v6` (`script/`)**: Thời lượng 60s chia 5 nhịp rõ ràng, tối đa 2–4 câu thoại siêu ngắn (~15–25 từ), nhân vật ẩn danh theo hình tượng (`Archetypes`), áp dụng **Zero Map Policy**.
- [ ] **4. Bộ Hình Phân Cảnh (`assets/scene1..5.jpg`)**: Đã render đủ các khung hình dọc `9:16` (`1080x1920`) theo đúng [`CORE_CHARACTERS.md`](file:///c:/projects/borderWarSW779/02_CHARACTER_PROFILES/CORE_CHARACTERS.md).
- [ ] **5. Đồng bộ Kế hoạch (`INDEX.md` & `plan/`)**: Đã thống nhất mã tập và thông số `v6.0`.

---

### III. CHI TIẾT 6 BƯỚC SẢN XUẤT CHUẨN (PRODUCTION GATES)

#### 🔹 BƯỚC 1 (GATE 1): KIỂM ĐỊNH THỊ GIÁC & TIỀN KỲ CHUYỂN ĐỘNG (VISUAL QA & MOTION PREP)
Mục tiêu: Đảm bảo 100% ảnh phân cảnh không có "sạn" AI trước khi đưa vào dựng video.

1. **Rà soát 5 tiêu chí thị giác trên từng bức ảnh (`scene1` $\rightarrow$ `scene5`)**:
   - **Đồng nhất nhân vật (Consistency)**: Khuôn mặt, độ tuổi, màu áo bà ba, khăn rằn, nón lá, mũ cối của *Lão chài*, *Người chài trẻ*, *Người trực đêm* có khớp nhau qua các cảnh không?
   - **Logic không gian & quân sự**: Có nhân vật thừa đứng sai vị trí không? (VD: người dân đứng giữa bãi cát khi đang bị bao vây, mũi tàu quay ngược hướng di chuyển, cầm súng sai tư thế).
   - **Thuần Việt & Lịch sử**: Tuyệt đối không lẫn kiến trúc, tàu thuyền, trang phục kiểu Nhật Bản/phương Tây hiện đại.
   - **An toàn nền tảng (No Gore)**: Không có vết máu đỏ tươi, vết thương hở hay cảnh bạo lực trực diện.
   - **Không bản đồ (Zero Map)**: Không có hình vẽ bản đồ hay đường biên giới trên ảnh.
2. **Xử lý & Thiết lập chuyển động (Motion Plan)**:
   - Nếu ảnh có lỗi nhỏ: Thực hiện **Inpaint / Retouch** hoặc dùng khung cắt (Crop/Zoom) để loại bỏ vùng lỗi.
   - Thiết lập kịch bản chuyển động camera cho từng nhịp (bằng Ken Burns trên HaizFlow/FFmpeg hoặc AI Image-to-Video):
     + *Nhịp 1 (`00:00–00:10`)*: Zoom-in rất chậm (tạo sự căng thẳng ngầm).
     + *Nhịp 2 (`00:10–00:20`)*: Camera Shake (rung nhẹ tại thời điểm cú quật *BỐP!*) + Pan nhanh theo đà nhảy.
     + *Nhịp 3 (`00:20–00:30`)*: Handheld motion (chuyển động gấp gáp theo nhịp thở và tiếng đập cửa).
     + *Nhịp 4 (`00:30–00:46`)*: Slow Pan từ trên cao xuống (mô phỏng góc nhìn toàn cảnh thế kẹt địa hình).
     + *Nhịp 5 (`00:46–00:60`)*: Slow Zoom-out mở rộng ra đường chân trời bình minh.

---

#### 🔹 BƯỚC 2 (GATE 2): SẢN XUẤT GIỌNG THOẠI TỐI GIẢN (TTS GENERATION & VOICE QA)
Mục tiêu: Tạo giọng đọc có hồn, đúng chất giọng vùng miền, không bị "rô-bốt" (giải quyết ràng buộc `C3` trong [`CONSTRAINTS_AND_RISK_REGISTER.md`](file:///c:/projects/borderWarSW779/CONSTRAINTS_AND_RISK_REGISTER.md)).

1. **Cấu hình Voice Profile theo Hình tượng (Archetypes)**:
   - `voice_lao_chai`: Giọng Nam Bộ lớn tuổi (50–55 tuổi), trầm, khàn, từng trải.
   - `voice_nguoi_chai_tre`: Giọng Nam Bộ trẻ (22–26 tuổi), rắn rỏi, nhịp nhanh, gấp gáp khi báo tin.
   - `voice_nguoi_truc_dem`: Giọng bộ đội đanh gọn, điềm tĩnh, dứt khoát.
2. **Quy tắc sinh Audio & Ngắt nhịp (Subturn Pauses)**:
   - Chèn khoảng nghỉ tự nhiên (`0.4s – 0.8s`) ở dấu ba chấm `...` để tạo tiếng lấy hơi hoặc sự nghẹn lời.
   - Xuất file âm thanh định dạng `.wav` hoặc `.mp3` chất lượng cao (`44.1kHz / 48kHz`) lưu vào `factory/materialAndDraft/ChapterX/audio/tts/`.
3. **Kiểm tra nghe thử bắt buộc (Human Audio QA)**:
   - Nghe trực tiếp từng câu: Có bị đọc sai dấu thanh tiếng Việt không? Có đúng cảm xúc tình huống (thở dốc / đanh thép / nhẹ nhõm) không? Nếu chưa đạt, sinh lại (re-roll) hoặc chỉnh tốc độ/cao độ trước khi qua Bước 3.

---

#### 🔹 BƯỚC 3 (GATE 3): THIẾT KẾ TIẾNG ĐỘNG HIỆN TRƯỜNG & NHẠC NỀN (FOLEY/SFX & BGM MIXING)
Mục tiêu: Vì thoại chỉ chiếm ~15 từ/60s, **âm thanh hiện trường (SFX) chiếm 80% sức nặng kịch tính** của tập phim.

1. **Chuẩn bị 3 lớp âm thanh chuẩn tại `factory/materialAndDraft/ChapterX/audio/` (`sfx/`, `bgm/`, `mix/`)**:
   - **Lớp 1 – Ambience (Âm thanh môi trường xuyên suốt từng cảnh)**:
     + Cảnh biển đêm: Tiếng sóng vỗ mạn gỗ, tiếng gió biển rít, tiếng máy ghe đuôi tôm *tạch... tạch...*
     + Cảnh trạm gác / rừng đêm: Tiếng côn trùng đêm, tiếng gió lùa tán dừa.
     + Cảnh bình minh: Tiếng sóng êm, tiếng gió nhẹ.
   - **Lớp 2 – Action Foley (Tiếng động điểm nhấn khớp khung hình)**:
     + Đặt chính xác đến từng phần mười giây (frame-accurate): Tiếng gậy gỗ đập *BỐP!*, tiếng nhảy xuống nước *ÙM!*, tiếng súng AK điểm xạ xa dần, tiếng chân chạy bùn lầy, tiếng đập cửa gỗ *Cộc! Cộc! Cộc!*, tiếng kẻng báo động *Keng! Keng!*, tiếng còi tàu xa xăm.
   - **Lớp 3 – Nhạc nền (BGM)**:
     + Nửa đầu (00–45s): Drone trầm căng thẳng hoặc nhịp trống rất khẽ (không lấn át tiếng động hiện trường).
     + Nửa cuối (46–60s): Giai điệu sáo trúc, đàn bầu hoặc guitar acoustic mộc mạc, sâu lắng.
2. **Cân bằng âm lượng (Audio Leveling & Auto-Ducking)**:
   - Giọng thoại (TTS): Đạt chuẩn `-6dB` đến `-3dB` (rõ nhất).
   - Tiếng động điểm nhấn (Action Foley): `-9dB` đến `-6dB` (không đè lên chữ đang nói).
   - Ambience & BGM: `-18dB` đến `-15dB` (tự động hạ xuống `-22dB` khi có giọng nhân vật).

---

#### 🔹 BƯỚC 4 (GATE 4): DỰNG TIMELINE 60S, ĐỒ HỌA CHỮ & PHỤ ĐỀ TẠI `staging/ChapterX/` (TIMELINE ASSEMBLY)
Mục tiêu: Ghép hoàn chỉnh hình, tiếng, chữ trên khung dọc `9:16` (`1080x1920`) tại `factory/staging/ChapterX/`, tuân thủ tuyệt đối quy chuẩn hiển thị Shorts/Reels/TikTok.

1. **Khớp thời lượng 5 nhịp trên Timeline (Tổng = 60.0s)**:
   - Nhịp 1 (`00:00 – 00:10`): 10 giây
   - Nhịp 2 (`00:10 – 00:20`): 10 giây
   - Nhịp 3 (`00:20 – 00:30`): 10 giây
   - Nhịp 4 (`00:30 – 00:46`): 16 giây
   - Nhịp 5 (`00:46 – 00:60`): 14 giây
   *(Dùng chuyển cảnh Cross-dissolve ngắn `0.3s` giữa các nhịp đêm và Fade-to-light `0.5s` khi sang cảnh bình minh Nhịp 5).*
2. **Thực thi Chính sách Không Bản Đồ (Zero Map Policy)**:
   - Kiểm tra toàn bộ các track video/overlay: **Tuyệt đối không gắn** `mini_map_*.svg` hay bất kỳ hình ảnh bản đồ nào.
3. **Đặt Chữ trên màn hình (Text Overlay), Phụ đề & Nhận diện Kênh (Channel Branding) trong Vùng An Toàn (Safe Zone)**:
   - **Vùng an toàn (Safe Zone)**: Cách đáy màn hình tối thiểu `25%` (`Y < 1440px`), cách lề phải `15%` để không bị giao diện tên kênh/nút Like/Share của YouTube Shorts & TikTok che khuất.
   - **4 lớp đồ họa bắt buộc**:
     1. *Nhận diện kênh xuyên suốt (00–60s)*: Logo badge đỏ chữ trắng **`VCH`** ở góc trên bên trái và watermark mờ **`VẠN CHUYỆN`** ở góc dưới bên phải (đồng bộ chuẩn nhận diện HaizFlow).
     2. *Text Hook mở đầu (giây `0.6–6.5`)*: Hiển thị đủ lâu (~6 giây) để khán giả đọc trọn mốc thời gian và địa điểm (VD: `VÙNG BIỂN ĐẢO TÂY NAM — Đêm đầu tháng 5/1975`).
     3. *Phụ đề thoại (Subtitles)*: Xuất hiện đúng lúc nhân vật nói, phông chữ Sans-serif đậm, chữ trắng/vàng viền đen rõ nét, không chứa từ khóa nhạy cảm.
     4. *Disclaimer cuối video (giây `57–60`)*: Hiển thị rõ dòng chữ:
        > *"Phóng tác từ lời kể của một cựu chiến binh. Nhân vật và tình tiết đã được hư cấu hóa."*

---

#### 🔹 BƯỚC 5 (GATE 5): RENDER MP4 & KIỂM DUYỆT 8 TIÊU CHÍ CUỐI TẠI `staging/ChapterX/` (FINAL RENDER & QA AUDIT)
Mục tiêu: Xuất file video chất lượng cao tại `factory/staging/ChapterX/` và vượt qua bộ lọc kiểm duyệt 8 tiêu chí trước khi chuyển sang `production/ChapterX/`.

1. **Thông số Render chuẩn**:
   - Độ phân giải: `1080 x 1920` (Vertical 9:16).
   - Tốc độ khung hình: `30 fps` (hoặc `60 fps`), Video Codec: `H.264 (MP4)`, Audio: `AAC 192kbps / 48kHz`.
   - Đường dẫn xuất file kiểm duyệt (Staging): `factory/staging/ChapterX/EPXX_<TenTap>_v6_60s_staging.mp4`.
2. **Bảng Kiểm Duyệt 8 Điểm Bắt Buộc (8-Point Final QA Gate)**:
   Xem lại toàn bộ video MP4 từ giây 00 đến 60 và tích đủ 8 mục:
   - [ ] **1. Ẩn danh nhân thân (Identity Rule)**: Không có bất kỳ tên thật, phiên hiệu đơn vị chưa xác minh hay chức danh cá nhân nào trong hình, thoại và chữ.
   - [ ] **2. Không bản đồ (Zero Map Policy)**: Không xuất hiện bất kỳ widget hay hình vẽ bản đồ nào.
   - [ ] **3. Sạch từ khóa thuật toán (ASR & OCR Safety)**: Không chứa các từ *giết, chết, chém, máu, sát hại, xác...* trong cả giọng đọc lẫn phụ đề (đối chiếu [`POLITICAL_LEGAL_HARNESS.md`](file:///c:/projects/borderWarSW779/00_HARNESS_GUIDELINES/POLITICAL_LEGAL_HARNESS.md#L50-L72)).
   - [ ] **4. Không hình ảnh máu me (Visual Safety)**: Không có cảnh thương tích ghê rợn.
   - [ ] **5. Chuẩn mực chính trị ("3 Đúng - 3 Không")**: Tôn vinh sự mưu trí của nhân dân và bản lĩnh người lính giữ đảo; không kích động hằn thù sắc tộc.
   - [ ] **6. Chất lượng âm thanh (Audio Mix)**: 3 câu thoại nghe rõ từng chữ; tiếng động *BỐP!*, *ÙM!*, tiếng đập cửa, tiếng kẻng khớp đúng hành động trên hình.
   - [ ] **7. Chuẩn vùng hiển thị (Safe Zone & Disclaimer)**: Phụ đề không bị tràn lề; có đủ dòng chữ *"Phóng tác từ lời kể..."* ở 3 giây cuối.
   - [ ] **8. Nhịp điệu 60 giây (Pacing & Hook)**: Mở đầu gây tò mò ngay trong 3 giây đầu, kết thúc gọn ở giây 60, không bị đen hình hay cụt âm thanh cuối video.

---

#### 🔹 BƯỚC 6 (GATE 6): ĐÓNG GÓI XUẤT BẢN & LƯU TRỮ TẠI `production/ChapterX/` (PACKAGING, PUBLISHING & ARCHIVAL)
Mục tiêu: Đóng gói bản phát hành chính thức tại `factory/production/ChapterX/` (và bản sao tại `06_RENDERED_SHORTS/`), đảm bảo an toàn pháp lý và thuật toán khi đưa video lên nền tảng công khai.

1. **Chuyển giao Bản Phát Hành Chính Thức & Đóng gói Metadata chuẩn**:
   - Sao chép file video đã vượt qua Gate 5 sang `factory/production/ChapterX/EPXX_<TenTap>_v6_60s.mp4` (đồng bộ vào `06_RENDERED_SHORTS/`).
   - Tạo file gói xuất bản `factory/production/ChapterX/PUBLISH_PACKAGE_EPXX.md` chứa nguyên văn **Description chuẩn đăng tải** và **Bình luận ghim** từ file kịch bản `v6` (có nhãn `🎬 ĐÂY LÀ PHIM HOẠT HÌNH PHÓNG TÁC` và `🤖 Hình ảnh và âm thanh được hỗ trợ sản xuất bởi công cụ AI`).
2. **Khai báo AI trên nền tảng**:
   - Khi tải lên YouTube Shorts / TikTok / Facebook Reels, bắt buộc tích chọn ô **Khai báo nội dung tổng hợp / có sử dụng AI (Altered or synthetic content)** (giải quyết mục `B6`, `D3` trong [`CONSTRAINTS_AND_RISK_REGISTER.md`](file:///c:/projects/borderWarSW779/CONSTRAINTS_AND_RISK_REGISTER.md)).
3. **Kiểm tra điều kiện ngoại vi trước khi bấm Công khai (Public)**:
   - Đối chiếu mục `B3` (liên hệ/xin phép nguồn lời kể khi cần thiết) và mục `B7` (có người thật kiểm tra chéo sử liệu & pháp lý).
4. **Cập nhật Hồ sơ Dự án**:
   - Cập nhật trạng thái tập phim trong `factory/materialAndDraft/ChapterX/INDEX.md` và [`CONSTRAINTS_AND_RISK_REGISTER.md`](file:///c:/projects/borderWarSW779/CONSTRAINTS_AND_RISK_REGISTER.md) sang `✅ ĐÃ HOÀN THÀNH SẢN XUẤT (PRODUCED)`.

---

### IV. PHIẾU THỰC THI NHANH CHO TỪNG TẬP (QUICK RUNBOOK TEMPLATE)

*(Mỗi khi chốt xong khâu chuẩn bị của một tập mới, tạo file `PRODUCTION_RUNBOOK_EPXX.md` tại `factory/materialAndDraft/ChapterX/` để theo dõi xuyên suốt 6 cổng)*:

```markdown
## PHIẾU THỰC THI SẢN XUẤT – TẬP [XX]: [TÊN TẬP PHIM] (CHUẨN v6.0)
- **Tầng 1 (Gate 0, 1, 2, 3)**: `factory/materialAndDraft/Chapter[X]/`
- **Tầng 2 (Gate 4, 5)**: `factory/staging/Chapter[X]/`
- **Tầng 3 (Gate 6)**: `factory/production/Chapter[X]/`

### Tiến độ 6 Cổng Sản Xuất (Production Gates)
- [ ] **GATE 0 (Entry – `materialAndDraft/Chapter[X]`)**: Đã khóa kịch bản v6 + Clearance PASS + Đủ 5 ảnh phân cảnh 9:16.
- [ ] **GATE 1 (Visual QA & Motion – `materialAndDraft/Chapter[X]`)**: Đã duyệt 5 ảnh & chốt `motion_plan.json`.
- [ ] **GATE 2 (TTS Voice – `materialAndDraft/Chapter[X]`)**: Đã sinh đủ các câu thoại ngắn tại `audio/tts/` & nghe thử đạt yêu cầu.
- [ ] **GATE 3 (SFX & BGM – `materialAndDraft/Chapter[X]`)**: Đã ghép đủ Ambience + Action Foley + BGM & trộn `master_audio` tại `audio/mix/`.
- [ ] **GATE 4 (Timeline 60s – `staging/Chapter[X]`)**: Đã ghép hình + tiếng + Text Hook (1–3s) + Phụ đề + Disclaimer (57–60s) trong Safe Zone (Zero Map).
- [ ] **GATE 5 (Render & 8-Point QA – `staging/Chapter[X]`)**: Đã xuất MP4 `1080x1920` và vượt qua 8 tiêu chí kiểm duyệt cuối.
- [ ] **GATE 6 (Packaging & Release – `production/Chapter[X]`)**: Đã đóng gói bản Final MP4, Description phóng tác, bật nhãn AI và cập nhật `INDEX.md`.
```

