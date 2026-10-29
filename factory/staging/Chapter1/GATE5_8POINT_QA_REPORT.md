# BIÊN BẢN KIỂM DUYỆT CUỐI (GATE 5: 8-POINT FINAL QA AUDIT)
## TẬP 01: ĐÊM ĐẦU THÁNG 5 Ở PHÚ QUỐC (v6.0 – 60 GIÂY: THẾ KẸT ĐỘC ĐẠO)

- **File Video Kiểm duyệt (Staging MP4)**: [`factory/staging/Chapter1/EP01_DemDauThang5_PhuQuoc_v6_60s_staging.mp4`](file:///c:/projects/borderWarSW779/factory/staging/Chapter1/EP01_DemDauThang5_PhuQuoc_v6_60s_staging.mp4)
- **Dung lượng**: `36.35 MB`
- **Thông số Kỹ thuật**: `1080 x 1920` (Vertical 9:16) | `30.0 fps` (`1.800 frames`) | `H.264 (yuv420p)` | `AAC 192kbps / 48kHz Stereo` | Thời lượng: `60.00s`
- **Trạng thái Tổng thể Gate 5**: ✅ **ĐẠT TUYỆT ĐỐI (8/8 PASS) – ĐỦ ĐIỀU KIỆN CHUYỂN SANG GATE 6 (PRODUCTION)**

---

### BẢNG KIỂM DUYỆT 8 TIÊU CHÍ BẮT BUỘC (8-POINT FINAL QA GATE)

| Tiêu chí Kiểm duyệt | Trạng thái | Bằng chứng & Thông số Xác thực |
| :--- | :---: | :--- |
| **1. Ẩn danh nhân thân (Identity Rule)** | ✅ **PASS** | 0 tên thật / phiên hiệu đơn vị chưa xác minh trong kịch bản, giọng đọc và phụ đề (chỉ dùng 3 hình tượng: Lão chài, Người chài trẻ, Người trực đêm). |
| **2. Không bản đồ (Zero Map Policy)** | ✅ **PASS** | 0 file .svg bản đồ trong assets/ và staging/; Nhịp 4 dùng góc máy điện ảnh từ trên cao (Cinematic High-Angle Shot). |
| **3. Sạch từ khóa thuật toán (ASR & OCR Safety)** | ✅ **PASS** | Đã quét 11 từ khóa nhạy cảm (giết, chết, chém, máu, sát hại...): phát hiện 0 từ vi phạm. |
| **4. Không hình ảnh máu me (Visual Safety)** | ✅ **PASS** | 5/5 phân cảnh hoàn toàn không có máu, vết thương hở hay bạo lực trực diện. |
| **5. Chuẩn mực chính trị ('3 Đúng - 3 Không')** | ✅ **PASS** | Tôn vinh sự mưu trí của ngư dân và thế trận phòng thủ chủ động của bộ đội giữ đảo; không kích động hằn thù dân tộc. |
| **6. Chất lượng âm thanh & Khớp khung hình (Audio Mix & Sync)** | ✅ **PASS** | Master 60.0s đạt Peak -1.02 dBFS, RMS -20.12 dBFS; tiếng BỐP (11.20s), ÙM (12.50s), đập cửa (21.0s), kẻng (26.5s) khớp chính xác chuyển động hình. |
| **7. Chuẩn vùng hiển thị (Safe Zone & Disclaimer)** | ✅ **PASS** | 7/7 tấm đồ họa chữ nằm gọn trong vùng X=[80..920], Y<=1390 (<1420); có đủ bảng Disclaimer (57.0–60.0s), logo VCH (trên-trái) và watermark VẠN CHUYỆN (dưới-phải). |
| **8. Nhịp điệu 60 giây & Text Hook mở đầu (Pacing & Hook)** | ✅ **PASS** | Thời lượng chuẩn 60.00s (1.800 frames @ 30fps); Text Hook hiển thị rõ từ giây 0.6–6.5; kết thúc êm với hòa tấu Đàn Bầu & Sáo Trúc. |
