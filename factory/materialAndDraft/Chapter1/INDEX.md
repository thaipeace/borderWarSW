# CHAPTER 1: ĐÊM ĐẦU THÁNG 5 Ở PHÚ QUỐC (v6 – 60 GIÂY: THẾ KẸT ĐỘC ĐẠO)
## DANH MỤC TÀI LIỆU & HỒ SƠ GATE 0–3 (MATERIAL & DRAFT MANIFEST)
*Cập nhật: 29/10/2026 | Định vị dự án: Tập 01 mở đầu Chuỗi Hoạt hình Phóng tác Vi mô (Border War SW 779) – Chuẩn v6.0*

---

### I. KIẾN TRÚC 3 TẦNG THƯ MỤC SẢN XUẤT (`FACTORY` 3-TIER ARCHITECTURE)

```
factory/
├── materialAndDraft/Chapter1/                     <-- [GATE 0, 1, 2, 3] Toàn bộ tư liệu gốc, kịch bản, ảnh, audio & bản trộn
│   ├── INDEX.md                                   <-- Bản kiểm soát mục lục này (Chuẩn v6.0)
│   ├── PRODUCTION_RUNBOOK_EP01.md                 <-- Phiếu thực thi & kiểm duyệt 6 cổng sản xuất Tập 01
│   ├── motion_plan.json                           <-- [Output Gate 1] Cấu hình chuyển động camera & mốc thời gian 60s
│   ├── generate_tts_gate2.py                      <-- [Script Gate 2] Tổng hợp & mastering 3 giọng thoại Nam Bộ
│   ├── generate_sfx_bgm_gate3.py                  <-- [Script Gate 3] Tổng hợp SFX/BGM & trộn Master 60s (Auto-Ducking)
│   ├── script/
│   │   └── EP01_DemDauThang5_PhuQuoc_v6_60s.md    <-- [Output Gate 0] Kịch bản chính thức v6.0 (60s, 5 nhịp, Thế Kẹt Độc Đạo)
│   ├── assets/
│   │   ├── scene1_boat_night.jpg                  <-- [Output Gate 0 & 1] Nhịp 1 (00:00–00:10): Hook biển đêm
│   │   ├── scene2_action_tiller.jpg               <-- [Output Gate 0 & 1] Nhịp 2 (00:10–00:20): Cú quật cần lái & thoát hiểm
│   │   ├── scene3_alert_cabin.jpg                 <-- [Output Gate 0 & 1] Nhịp 3 (00:20–00:30): Chạy đêm & đập cửa cấp báo
│   │   ├── scene4_bottleneck_swamp.jpg            <-- [Output Gate 0 & 1] Nhịp 4 (00:30–00:46): Thế kẹt độc đạo (3 nhân vật key + lún bùn)
│   │   └── scene5_sunrise_peace.jpg               <-- [Output Gate 0 & 1] Nhịp 5 (00:46–00:60): Chân trời trống & hòa bình trở lại
│   ├── audio/
│   │   ├── tts/                                   <-- [Output Gate 2] 3 file thoại (.wav/.mp3) + tts_manifest_gate2.json
│   │   ├── sfx/                                   <-- [Output Gate 3] 3 file Ambience + 7 file Action Foley (.mp3 trên Git / .wav local)
│   │   ├── bgm/                                   <-- [Output Gate 3] 2 file BGM (Drone 00-46s & Đàn Bầu/Sáo Trúc 46-60s)
│   │   └── mix/                                   <-- [Output Gate 3] master_audio_ep01_v6_60s.mp3 + audio_manifest_gate3.json
│   ├── source/
│   │   └── ARCHIVE_YOUTUBE_PHUQUOC_03051975.md    <-- Nguồn tư liệu thực địa & phân tầng Oral History (lưu nội bộ)
│   └── clearance/
│       └── TAP01_CLEARANCE.md                     <-- [Output Gate 0] Bản đánh giá sử liệu, pháp lý & rủi ro sản xuất v6.0
│
├── staging/Chapter1/                              <-- [GATE 4, 5] Dựng Timeline 60s, Phụ đề Safe Zone, Render MP4 & 8-Point QA
│   ├── assemble_timeline_gate4.py                 <-- [Script Gate 4] Engine dựng chuyển động camera & đồ họa chữ Safe Zone
│   ├── timeline_manifest_gate4.json               <-- [Output Gate 4] Manifest kiểm định tọa độ Safe Zone & 1.800 frames
│   ├── timeline_video_60s_gate4.mp4               <-- [Output Gate 4] Track hình chuyển động 60.0s (1080x1920 @ 30fps, Zero Map)
│   ├── subtitles/ep01_subtitles.srt               <-- [Output Gate 4] Phụ đề chuẩn .SRT khớp thời lượng thoại Gate 2
│   ├── overlays/                                  <-- [Output Gate 4] 7 tấm đồ họa chữ RGBA (Hook, Subtitles, Disclaimer)
│   ├── preview_frames/                            <-- [Output Gate 4] Bộ ảnh kiểm định trực quan vùng an toàn (Safe Zone QA)
│   ├── render_and_audit_gate5.py                  <-- [Script Gate 5] Ghép Master Audio + Video xuất MP4 & quét 8 tiêu chí QA
│   ├── EP01_DemDauThang5_PhuQuoc_v6_60s_staging.mp4 <-- [Output Gate 5] Bản video hoàn chỉnh 60.0s (1080x1920, H.264 + AAC 48kHz)
│   ├── GATE5_8POINT_QA_REPORT.md                  <-- [Output Gate 5] Biên bản kiểm duyệt 8 tiêu chí cuối (8/8 PASS)
│   └── qa_audit_report_gate5.json                 <-- [Output Gate 5] Dữ liệu JSON kiểm định luồng stream & từ khóa thuật toán
│
└── production/Chapter1/                           <-- [GATE 6] Đóng gói bản Final Master MP4, Metadata/Description & Phát hành
    ├── package_release_gate6.py                   <-- [Script Gate 6] Đóng gói Master MP4, kiểm tra SHA-256 & tạo gói xuất bản
    ├── EP01_DemDauThang5_PhuQuoc_v6_60s.mp4       <-- [Output Gate 6] Bản phát hành chính thức 60.0s (đồng bộ sang 06_RENDERED_SHORTS/)
    ├── EP01_DemDauThang5_PhuQuoc_v6_60s.srt       <-- [Output Gate 6] Phụ đề .SRT rời đính kèm khi đăng tải
    ├── EP01_Thumbnail_9x16.jpg                    <-- [Output Gate 6] Ảnh bìa dọc 9:16 chuẩn Shorts/TikTok/Reels
    ├── PUBLISH_PACKAGE_EP01.md                    <-- [Output Gate 6] Description phóng tác, Bình luận ghim & Checklist bật nhãn AI
    └── release_manifest_gate6.json                <-- [Output Gate 6] Manifest xuất bản chính thức & mã băm SHA-256
```

---

### II. BẢNG ĐỐI CHIẾU: TIẾN HÓA TỪ BẢN THẢO CŨ LÊN CHUẨN v6.0 (AN TOÀN PHÁP LÝ & ĐIỆN ẢNH VI MÔ)

| Hạng mục | Bản thảo cũ (v1–v3: Hư cấu gượng ép hoặc nêu tên thật/bản đồ) ❌ | Bản chuẩn hóa chính thức v6.0 (`EP01_DemDauThang5_PhuQuoc_v6_60s.md`) ✅ | Lý do chuẩn hóa v6.0 |
| :--- | :--- | :--- | :--- |
| **Định danh & Thể loại** | Lẫn lộn "Tập 00/EP00", đóng khung như phim tài liệu lịch sử khẳng định số liệu tuyệt đối | **Tập 01 – Đêm Đầu Tháng 5 Ở Phú Quốc** (*Phóng tác hoạt hình vi mô, nhân vật & tình tiết hư cấu hóa*) | Triệt tiêu rủi ro tranh chấp sử liệu đơn nguồn (chỉ 1 lời kể nhân chứng) và bảo vệ an toàn pháp lý khi đăng tải. |
| **Nhân vật & Danh tính** | Đưa nhầm Út Hưng (v1) hoặc nêu đích danh tên thật Ông Năm Thối, Ông Kế, Bác Đào Hữu Phước trong thoại/hình (v3) | **3 hình tượng ẩn danh thuần Việt**: *Lão chài*, *Người chài trẻ*, *Người trực đêm* (theo [`CORE_CHARACTERS.md`](file:///c:/projects/borderWarSW779/02_CHARACTER_PROFILES/CORE_CHARACTERS.md)) | Bảo vệ quyền nhân thân (mục `A8`, `B3`), tránh rủi ro gắn tên người thật vào hình ảnh do AI tạo. |
| **Chính sách Bản đồ** | Gắn widget `mini_map_ep01_phuquoc.svg` hoặc vẽ bản đồ tác chiến trong cảnh 4 | **Zero Map Policy (Không bản đồ)**: Thay bằng góc máy điện ảnh từ trên cao (`Cinematic High-Angle Shot`) nhìn xuống dải cát & đầm lầy | Giải quyết triệt để rủi ro pháp lý về xuất bản bản đồ và chủ quyền biển đảo (mục `B1` trong Sổ rủi ro). |
| **Điểm nhấn kịch tính** | Kéo pháo 105mm ra mép sóng (v1) hoặc dừng cụt ở cảnh đập cửa / đọc lệnh trên bản đồ (v3–v4) | **Thế Kẹt Độc Đạo (Nhịp 4) & Chân Trời Trống (Nhịp 5)**: Bẫy địa hình tự nhiên (biển sâu – cát hẹp – đầm lầy ngập mặn – chốt chặn độc đạo) khiến đối phương tự rút lui | Khép kín cấu trúc tự sự 60s đầy thuyết phục, giải thích hợp lý vì sao hóa giải được nguy cơ mà không cần cảnh giao tranh máu me. |
| **Thời lượng & Lời thoại** | Thoại dày (~75–120 từ / 58s), nhân vật nói nhiều gây quá tải phụ đề và lộ chất giọng AI | **60 giây / 5 nhịp**, tinh giản còn **3 câu thoại siêu ngắn (~15 từ)**; ưu tiên âm thanh hiện trường (SFX) dẫn dắt cảm xúc | Giải quyết ràng buộc `C3`, `C4`, `D1`: tạo nhịp thở điện ảnh căng thẳng, dễ nghe và giữ chân khán giả ngay từ giây đầu. |
| **Trạng thái Visual & Audio** | Mới dừng ở mức mô tả chữ (Prompt text) | **✅ ĐÃ HOÀN THÀNH SẢN XUẤT (PRODUCED – PASS 6/6 GATES)** | Đã xuất bản Master MP4 chính thức tại [`factory/production/Chapter1/`](file:///c:/projects/borderWarSW779/factory/production/Chapter1/) và [`06_RENDERED_SHORTS/`](file:///c:/projects/borderWarSW779/06_RENDERED_SHORTS/). |

---

### III. TRẠNG THÁI HIỆN TẠI & HỒ SƠ HOÀN TẤT 6 CỔNG SẢN XUẤT (THEO PRODUCTION HARNESS)
> **Quy chuẩn thực thi**: Áp dụng trực tiếp [**EPISODE_PRODUCTION_HARNESS.md (6 Production Gates)**](file:///c:/projects/borderWarSW779/00_HARNESS_GUIDELINES/EPISODE_PRODUCTION_HARNESS.md) cho Tập 01 — **Trạng thái: ✅ ĐÃ HOÀN THÀNH SẢN XUẤT (PRODUCED)**.

- ✅ **GATE 0 (Entry Gate – `materialAndDraft/Chapter1`)**: Đã khóa kịch bản [`EP01_DemDauThang5_PhuQuoc_v6_60s.md`](file:///c:/projects/borderWarSW779/factory/materialAndDraft/Chapter1/script/EP01_DemDauThang5_PhuQuoc_v6_60s.md), duyệt [`TAP01_CLEARANCE.md`](file:///c:/projects/borderWarSW779/factory/materialAndDraft/Chapter1/clearance/TAP01_CLEARANCE.md), dọn sạch file `.svg` bản đồ khỏi `assets/` và hoàn tất 5/5 hình ảnh phân cảnh dọc 9:16 tại [`assets/`](file:///c:/projects/borderWarSW779/factory/materialAndDraft/Chapter1/assets/).
- ✅ **GATE 1 (Visual QA & Motion Prep – `materialAndDraft/Chapter1`)**: Đã hoàn thành rà soát thị giác, sao lưu bản gốc vào `assets/originals_backup/`, nâng cấp `scene4_bottleneck_swamp.jpg` (3 nhân vật key đấu lý giữa bãi cát + lính áo đen lún bùn rễ đước ở mép phải) & `scene5_sunrise_peace.jpg` (xoay đuôi tàu rút ra khơi xa), xuất cấu hình chuyển động [`motion_plan.json`](file:///c:/projects/borderWarSW779/factory/materialAndDraft/Chapter1/motion_plan.json) và phiếu thực thi [`PRODUCTION_RUNBOOK_EP01.md`](file:///c:/projects/borderWarSW779/factory/materialAndDraft/Chapter1/PRODUCTION_RUNBOOK_EP01.md).
- ✅ **GATE 2 (TTS Voice & Audio QA – `materialAndDraft/Chapter1`)**: Đã sinh và kiểm duyệt thính giác 3 câu thoại giọng miền Nam theo đúng 3 nhân vật (*Người chài trẻ* – giọng `Puck`, *Người trực đêm / Chỉ huy bộ đội* – giọng `Fenrir`, *Lão chài* – giọng `Charon`) chuẩn `48kHz PCM_16 .wav` & `192kbps .mp3` (`-3.0 dBFS` peak) tại [`audio/tts/`](file:///c:/projects/borderWarSW779/factory/materialAndDraft/Chapter1/audio/tts/) kèm manifest [`tts_manifest_gate2.json`](file:///c:/projects/borderWarSW779/factory/materialAndDraft/Chapter1/audio/tts/tts_manifest_gate2.json).
- ✅ **GATE 3 (SFX, BGM & 60s Master Mix – `materialAndDraft/Chapter1`)**: Đã tổng hợp và kiểm duyệt thính giác toàn bộ 3 lớp âm thanh (Ambience + 7 file Action Foley nâng cấp độ đanh/ướt cho cú đánh cần lái & nhảy biển + 2 bản BGM Drone & Đàn Bầu/Sáo Trúc ngũ cung Nam Bộ), đồng thời xuất 4 Stems và bản trộn tổng `60.0s` có Auto-Ducking tại [`audio/mix/master_audio_ep01_v6_60s.mp3`](file:///c:/projects/borderWarSW779/factory/materialAndDraft/Chapter1/audio/mix/master_audio_ep01_v6_60s.mp3).
- ✅ **GATE 4 (Timeline 60s & Safe Zone – `staging/Chapter1`)**: Đã kết xuất 1.800 khung hình chuyển động mượt (`1080x1920 @ 30fps`) kèm chuyển cảnh Cross-dissolve (`0.3s`), Fade-to-sunrise (`0.5s`) và 7 tấm đồ họa chữ/phụ đề chuẩn Safe Zone (`X ∈ [80, 920]`, `Y ≤ 1390 < 1420`, tuyệt đối không bản đồ) tại [`factory/staging/Chapter1/timeline_video_60s_gate4.mp4`](file:///c:/projects/borderWarSW779/factory/staging/Chapter1/timeline_video_60s_gate4.mp4).
- ✅ **GATE 5 (Render & 8-Point QA – `staging/Chapter1`)**: Đã ghép hoàn chỉnh video + âm thanh 60.0s xuất file [`EP01_DemDauThang5_PhuQuoc_v6_60s_staging.mp4`](file:///c:/projects/borderWarSW779/factory/staging/Chapter1/EP01_DemDauThang5_PhuQuoc_v6_60s_staging.mp4) (`35.94 MB`, `1080x1920 @ 30fps`, `H.264 + AAC 192kbps/48kHz`) và vượt qua 8/8 tiêu chí kiểm duyệt tại [`GATE5_8POINT_QA_REPORT.md`](file:///c:/projects/borderWarSW779/factory/staging/Chapter1/GATE5_8POINT_QA_REPORT.md).
- ✅ **GATE 6 (Packaging & Release – `production/Chapter1`)**: Đã đóng gói bản phát hành chính thức [`EP01_DemDauThang5_PhuQuoc_v6_60s.mp4`](file:///c:/projects/borderWarSW779/factory/production/Chapter1/EP01_DemDauThang5_PhuQuoc_v6_60s.mp4) (đồng bộ sang [`06_RENDERED_SHORTS/EP01_DemDauThang5_PhuQuoc_v6_60s.mp4`](file:///c:/projects/borderWarSW779/06_RENDERED_SHORTS/EP01_DemDauThang5_PhuQuoc_v6_60s.mp4)), kèm gói xuất bản [`PUBLISH_PACKAGE_EP01.md`](file:///c:/projects/borderWarSW779/factory/production/Chapter1/PUBLISH_PACKAGE_EP01.md) và [`release_manifest_gate6.json`](file:///c:/projects/borderWarSW779/factory/production/Chapter1/release_manifest_gate6.json).
