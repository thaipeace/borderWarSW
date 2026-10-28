# SỔ GHI RÀNG BUỘC & RỦI RO (CONSTRAINTS & RISK REGISTER)
## Ghi ngày 27/10/2026 - sau buổi phản biện. Giải quyết dần, cập nhật cột Trạng thái.

> **Quy ước trạng thái**: `MỞ` (chưa xử lý) | `ĐANG LÀM` | `ĐÃ XONG` | `CHẤP NHẬN RỦI RO` (có ghi lý do)
> **Nguyên tắc**: Mục mức CAO phải xong (hoặc loại bỏ khỏi nội dung) **trước khi đăng tập đầu tiên**.

---

## A. DỮ LIỆU BỊA / CHƯA XÁC MINH TRONG TÀI LIỆU HIỆN TẠI (do AI tạo ra)

> [!CAUTION]
> Toàn bộ mục A là **placeholder do AI viết, chưa có nguồn thật**. Không được đăng bất kỳ Description nào chứa các mục này khi chưa thay bằng nguồn xác minh.

| ID | Nội dung chưa xác minh | Nằm ở file | Mức | Việc cần làm | Trạng thái |
|---|---|---|---|---|---|
| A1 | Tên 7 người kể (Đặng Viết Thọ, Nguyễn Văn Hùng, Lê Minh Cảnh, Trần Văn Thành, Phạm Minh Tuấn, Nguyễn Văn Thuyền, Nguyễn Thị Mai) | SOURCES_AND_DESCRIPTIONS_P1.md, STORYTELLER_ATTRIBUTION_RULE.md, Description trong các kịch bản W00/W01 | **CAO** | Thay bằng `[NGƯỜI KỂ: chưa xác minh]`; chỉ điền khi có video thật + đã xin phép | MỞ |
| A2 | Tên kênh YouTube và tiêu đề video nguồn ("Hồi ức Lính chiến", "Ký ức Người lính", "Ký ức Chiến trường Tây Nam", "Ký ức Người lính Biển", "Lịch sử & Nhân chứng", "Chuyện Kể Người Lính" và các video đi kèm) | Như trên | **CAO** | Như A1; thay bằng URL/kênh thật khi tìm được | MỞ |
| A3 | Chi tiết chiến sự không có nguồn: tàu PCF/PGM, pháo 20mm, "bắn chìm tàu địch quanh Hòn Nhạn" | MICRO_TIMELINE (Tập 03), W00_EP_HaiChienThoChu1975.md | **CAO** | Tìm sử liệu chính thống (Lịch sử Hải quân, Vùng 5) trước khi giữ lại kịch bản hải chiến; nếu không có, hạ xuống kịch bản không nêu chi tiết tàu/vũ khí | MỞ |
| A4 | Phiên hiệu và con số: "Đại đội 20 Trinh sát E2 F9", "12 chiến sĩ Đồn Phú Hội", "4 đợt xung phong", "Trung đoàn 4 QK9", "Tiểu đoàn 47", "Lữ đoàn 126" | MICRO_TIMELINE, SOURCES, kịch bản | **CAO** | Đối chiếu từng phiên hiệu với sử liệu; ghi rõ độ chắc chắn (xác nhận / chưa chắc) | MỞ |
| A5 | Mốc 03 rạng 04/5/1975 và địa điểm Bãi Dài (Phú Quốc) | W00_EP00, MICRO_TIMELINE Tập 01 | TRUNG BÌNH | Nguồn ghi 3, 4 hoặc 6/5 không nhất quán; cần ít nhất 2 nguồn chính thống trước khi chốt ngày | MỞ |
| A6 | Tên cán bộ/liệu sĩ từng nêu trong chat (Mai Năng chỉ huy Thổ Chu, Đinh Công Ngữ, Bùi Văn Vẹn, Nguyễn Văn Nam, Lê Thị Kim Loan, Nguyễn Văn Nhường, Lê Văn Tơ...) | Không còn trong file (đã ghi đè), nhưng từng xuất hiện | TRUNG BÌNH | Không dùng khi chưa có nguồn; nếu dùng thì phải đối chiếu tài liệu chính thống | MỞ |
| A7 | Điều khoản luật trích trong harness (Điều 8 Luật An ninh mạng, các điểm a, b; Luật Báo chí, Luật Xuất bản) | POLITICAL_LEGAL_HARNESS.md | TRUNG BÌNH | Nhờ luật sư hoặc người có chuyên môn kiểm tra lại số điều, nội dung | MỞ |
| A8 | Tên nhân vật hư cấu (Ba Bình, Út Hưng, Anh Cả Thạch...) nhưng một số tập gắn nhân vật với bối cảnh có thật | CORE_CHARACTERS.md, các kịch bản | THẤP | Giữ nhân vật là hình tượng; luôn có dòng "nhân vật hình tượng nghệ thuật" trong Description | MỞ |

---

## B. RỦI RO PHÁP LÝ - CHÍNH TRỊ

| ID | Rủi ro | Mức | Việc cần làm | Trạng thái |
|---|---|---|---|---|
| B1 | **Bản đồ widget do AI tự vẽ** (path chữ S tự tạo, vị trí Hoàng Sa/Trường Sa ước lượng, chưa render kiểm tra; xuất PNG lỗi exit code 1) | **CAO** | Thay bằng bản đồ chuẩn do cơ quan nhà nước công bố; hoặc tạm bỏ widget ở bản MVP đầu. Bản đồ sai nguy hiểm hơn không có bản đồ | MỞ |
| B2 | Chi tiết "săm lốp xe tải Trung Quốc" trong dấu dép (tập 02 và timeline Tập 11) | **CAO** | Bỏ hẳn chi tiết này khỏi kịch bản và timeline (nhạy cảm đối ngoại, không có nguồn) | MỞ |
| B3 | Bản quyền và quyền nhân thân lời kể CCB trên YouTube | **CAO** | Xin phép chủ kênh/người kể bằng văn bản trước khi chuyển thể; lưu bằng chứng cho phép | MỞ |
| B4 | Cách diễn giải "lệnh kiềm chế" là "bản lĩnh vì đại cuộc" | TRUNG BÌNH | Để người có thẩm quyền (Hội CCB, Viện Lịch sử Quân sự hoặc tương đương) duyệt khung diễn giải này | MỞ |
| B5 | Quan hệ hiện nay với Campuchia; khán giả Khmer có thể hiểu sai | TRUNG BÌNH | Luôn phân biệt rõ tập đoàn Pol Pot - Ieng Sary với nhân dân Campuchia; cân nhắc phụ đề/ghi chú song ngữ | MỞ |
| B6 | Chính sách YouTube về nội dung bạo lực/chiến tranh và nội dung do AI tạo | TRUNG BÌNH | Đọc lại chính sách hiện hành; khai báo nội dung tổng hợp (AI) khi đăng | MỞ |
| B7 | Chưa có bước thẩm định bởi người thật (harness hiện chỉ là checklist do AI viết) | **CAO** | Tìm tối thiểu 1 người đối chiếu sử liệu và 1 người xem rủi ro pháp lý trước khi đăng tập đầu | MỞ |

---

## C. KHẢ THI SẢN XUẤT

| ID | Ràng buộc | Mức | Việc cần làm | Trạng thái |
|---|---|---|---|---|
| C1 | Quy mô 350-400 tập, 2 tập/tuần, mỗi tập đều cần đối chiếu nguồn: quá tải cho một người | CAO | Thu hẹp thành 1 mùa nhỏ 8-12 tập, đo kết quả rồi mới mở rộng | MỞ |
| C2 | Nhất quán khuôn mặt/trang phục nhân vật qua nhiều cảnh trong HaizFlow chưa được kiểm chứng | CAO | Dùng bản MVP thứ Sáu làm phép thử; nếu không đạt, giảm số cảnh hoặc dùng ảnh tĩnh có chuyển động | MỞ |
| C3 | Chất lượng TTS đối thoại 2 giọng có cảm xúc chưa nghe thử | TRUNG BÌNH | Nghe thử trước khi cam kết "phim có thoại" | MỞ |
| C4 | Kịch bản 58 giây quá dày thoại, khó đọc kịp cùng phụ đề, lồng tiếng và widget | TRUNG BÌNH | Rút gọn thoại; tối đa khoảng 3-4 câu thoại ngắn mỗi tập MVP | MỞ |

---

## D. HIỆU QUẢ VÀ LAN TỎA

| ID | Vấn đề | Mức | Việc cần làm | Trạng thái |
|---|---|---|---|---|
| D1 | Hook mở đầu yếu (cảnh tĩnh, thì thào), cần gây tò mò trong 2 giây đầu | TRUNG BÌNH | Viết lại hook cho tập MVP | MỞ |
| D2 | Khán giả mục tiêu (35+, lịch sử) có thể ở Facebook/Zalo nhiều hơn YouTube | TRUNG BÌNH | Đăng thử song song và đo giữ chân người xem | MỞ |
| D3 | Rủi ro bị xếp vào nội dung sản xuất hàng loạt bằng AI (inauthentic) khi kiếm tiền | TRUNG BÌNH | Ghi rõ phần AI; thêm giá trị biên tập thật (nguồn, tri ân, hậu trường) | MỞ |
| D4 | Chưa có kênh phân phối ngoài đăng tải thuần túy | THẤP | Cân nhắc hợp tác với hội/kênh CCB, tập "hậu trường nguồn" để tăng độ tin cậy | MỞ |

---

## E. THỨ TỰ XỬ LÝ ĐỀ XUẤT (TRƯỚC KHI ĐĂNG TẬP ĐẦU TIÊN)

1. A1, A2, A3, A4: thay dữ liệu bịa bằng placeholder hoặc nguồn thật.
2. B2: bỏ chi tiết liên quan Trung Quốc.
3. B1: thay hoặc bỏ widget bản đồ tự vẽ.
4. B3: xin phép nguồn lời kể CCB.
5. B7: tìm người thẩm định thật.
6. C2, C3: dùng bản MVP làm phép thử kỹ thuật.
7. Phần còn lại giải quyết dần theo mức độ.

---

## F. NHẬT KÝ GIẢI QUYẾT

| Ngày | ID | Việc đã làm | Ghi chú |
|---|---|---|---|
| | | | |
