# Hướng dẫn chụp ảnh cho Chương 4

## Nguyên tắc chung

- **Chế độ sáng (Light mode)** nếu app hỗ trợ — in đẹp hơn light mode
- **Dữ liệu thực tế**: dùng câu hỏi/văn bản thật, không để empty state
- **Không chụp thông tin nhạy cảm**: email thật, API key, token
- **Độ phân giải**: Mobile ≥ 1080×1920 (dùng emulator hoặc thiết bị thật), Web ≥ 1440×900
- **Format file**: PNG, không JPG (tránh nén mất chất lượng)
- **Đặt tên file**: theo đúng danh sách bên dưới để script tự nhận

---

## PHẦN A — Mobile App (8 ảnh)

### A1 — Màn hình Đăng nhập
- **File**: `mobile_login.png`
- **Nội dung cần thấy**: Form email + password, nút Đăng nhập, logo/tên app
- **Lưu ý**: Dùng email fake như `demo@lawchat.vn`

### A2 — Màn hình Thư viện văn bản (Library)
- **File**: `mobile_library.png`
- **Nội dung cần thấy**: Danh sách văn bản pháp luật, có thể có filter/search bar
- **Lưu ý**: Cần có ít nhất 5–6 item trong danh sách

### A3 — Màn hình Chat — ThinkingPanel đang chạy *(QUAN TRỌNG NHẤT)*
- **File**: `mobile_chat_thinking.png`
- **Nội dung cần thấy**: ThinkingPanel với 5 bước đang animated (ít nhất 2–3 bước đã lit up)
- **Câu hỏi gợi ý để trigger**: *"Mức phạt lái xe ô tô có nồng độ cồn vượt mức theo quy định mới nhất là bao nhiêu?"*
- **Lưu ý**: Chụp ngay khi panel đang hiển thị, trước khi có câu trả lời

### A4 — Màn hình Chat — Câu trả lời hoàn chỉnh có citation
- **File**: `mobile_chat_answer.png`
- **Nội dung cần thấy**: Câu trả lời đã stream xong, phần "Nguồn tham khảo" với tên văn bản/điều khoản
- **Câu hỏi gợi ý**: cùng câu với A3

### A5 — Màn hình Chat — Temporal Conflict (ký hiệu ⛔/✅)
- **File**: `mobile_chat_conflict.png`
- **Nội dung cần thấy**: Câu trả lời có 2 nguồn: một nguồn đánh dấu ⛔ (văn bản cũ), một ✅ (văn bản mới)
- **Câu hỏi gợi ý**: *"Mức xử phạt vi phạm nồng độ cồn khi lái xe theo NĐ 100/2019 và NĐ 168/2024 khác nhau như thế nào?"*
- **Lưu ý**: Nếu UI chưa hiển thị ký hiệu này, bỏ qua ảnh này

### A6 — Màn hình Guided Consultation — Bước 1 (Clarify)
- **File**: `mobile_guided_step1.png`
- **Nội dung cần thấy**: Câu hỏi gốc + các câu hỏi trắc nghiệm làm rõ
- **Câu hỏi gợi ý**: *"Tôi muốn biết về quyền nghỉ phép hàng năm"*

### A7 — Màn hình Guided Consultation — Bước 2 (Answer)
- **File**: `mobile_guided_step2.png`
- **Nội dung cần thấy**: Câu trả lời đang stream hoặc đã hoàn chỉnh sau khi người dùng chọn đáp án bước 1
- **Lưu ý**: Chụp khi đang stream (cursor blink) hoặc lúc vừa done

### A8 — Màn hình Danh sách hội thoại
- **File**: `mobile_conversations.png`
- **Nội dung cần thấy**: List các cuộc hội thoại đã có, tiêu đề auto-generated, timestamps
- **Lưu ý**: Cần ít nhất 4–5 conversations

---

## PHẦN B — Admin Web (6 ảnh)

### B1 — Trang Login
- **File**: `admin_login.png`
- **Nội dung cần thấy**: Form đăng nhập admin, clean background
- **Lưu ý**: Crop browser chrome, chỉ lấy phần nội dung trang

### B2 — Dashboard
- **File**: `admin_dashboard.png`
- **Nội dung cần thấy**: BarChart thống kê + các card số liệu (tổng văn bản, điều khoản, vector)
- **Lưu ý**: Cần có dữ liệu thực trong chart (không empty)

### B3 — Danh sách tài liệu (Documents list)
- **File**: `admin_documents.png`
- **Nội dung cần thấy**: Table/list các DocumentTask với cột: tên file, status (completed/processing/failed), law_id, article_count, ngày tạo
- **Lưu ý**: Cần có ít nhất 5–6 rows, mix các status

### B4 — Upload — Đang xử lý *(QUAN TRỌNG)*
- **File**: `admin_upload_processing.png`
- **Nội dung cần thấy**: Progress bar đang chạy, current_step hiển thị ("Đang parse PDF...", "Đang embed..."), % tiến trình
- **Lưu ý**: Upload file PDF thật và chụp trong lúc đang xử lý

### B5 — Upload — Hoàn thành
- **File**: `admin_upload_done.png`
- **Nội dung cần thấy**: Status "Completed", article_count, thông báo thành công

### B6 — Chi tiết tài liệu (Document detail)
- **File**: `admin_document_detail.png`
- **Nội dung cần thấy**: Danh sách các điều khoản đã được parse (article_id, title, preview text)

---

## Checklist cuối

| # | File | Bắt buộc | Ghi chú |
|---|---|---|---|
| A1 | mobile_login.png | ✅ | |
| A2 | mobile_library.png | ✅ | |
| A3 | mobile_chat_thinking.png | ✅ *(must have)* | ThinkingPanel |
| A4 | mobile_chat_answer.png | ✅ | Có citation |
| A5 | mobile_chat_conflict.png | ⚠️ nếu có | Temporal conflict |
| A6 | mobile_guided_step1.png | ✅ | |
| A7 | mobile_guided_step2.png | ✅ | |
| A8 | mobile_conversations.png | ✅ | |
| B1 | admin_login.png | ✅ | |
| B2 | admin_dashboard.png | ✅ | Có data |
| B3 | admin_documents.png | ✅ | |
| B4 | admin_upload_processing.png | ✅ *(must have)* | Đang chạy |
| B5 | admin_upload_done.png | ✅ | |
| B6 | admin_document_detail.png | ✅ | |

**Tổng: 14 ảnh** (13 bắt buộc + 1 nếu có)

Sau khi chụp xong, đặt tất cả vào thư mục:
`Bao_Cao/sample_images/chapter4/`
