# CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

Chương này chuyển từ góc nhìn "phương pháp" (chương 2) sang góc nhìn "phân tích và thiết kế" — trả lời câu hỏi: hệ thống cần làm *gì*, cần lưu trữ *gì* và giao tiếp *như thế nào*. Chương bao gồm đặc tả yêu cầu, biểu đồ use case, biểu đồ tuần tự, thiết kế cơ sở dữ liệu và thiết kế API.

---

## 3.1. Đặc tả yêu cầu hệ thống

### 3.1.1. Yêu cầu về hình thức sản phẩm

Hệ thống Vietnam Law Chatbot bao gồm 4 thành phần triển khai độc lập:

| Thành phần | Nền tảng | Người dùng |
|---|---|---|
| Mobile App (Vietnam Law Chatbot) | Android + iOS (Kotlin Multiplatform) | Người dùng cuối |
| Web Admin (Vietnam Law Admin) | Trình duyệt (Next.js 16) | Quản trị viên |
| Main Service | Server/Docker Container | — (backend) |
| RAG Service | Server/Docker Container | — (backend) |

### 3.1.2. Yêu cầu chức năng cho người dùng cuối (Mobile App)

**Bảng 3.1. Danh sách yêu cầu chức năng — Người dùng cuối**

| Mã | Chức năng | Mô tả ngắn | Ưu tiên |
|---|---|---|---|
| F-01 | Đăng ký tài khoản | Tạo tài khoản bằng email + mật khẩu | Cao |
| F-02 | Đăng nhập / Đăng xuất | Xác thực JWT, lưu token encrypted | Cao |
| F-03 | Đổi mật khẩu | Xác thực mật khẩu cũ trước khi đổi | Trung |
| F-04 | Quản lý hội thoại | CRUD hội thoại, pin, archive, đổi tên | Cao |
| F-05 | Chat AI với streaming | Gửi câu hỏi, nhận trả lời SSE với ThinkingPanel | Cao |
| F-06 | Suggested Questions | Xem và chọn câu hỏi gợi ý sau mỗi trả lời | Trung |
| F-07 | Tư vấn có hướng dẫn | Trắc nghiệm làm rõ + Answer SSE | Cao |
| F-08 | Duyệt thư viện pháp luật | Xem danh sách văn bản, lọc year/topic | Cao |
| F-09 | Tìm kiếm văn bản | Tìm theo keyword/topic/năm ban hành | Cao |
| F-10 | Tìm kiếm AI ngữ nghĩa | Semantic search toàn văn điều luật | Cao |
| F-11 | Xem chi tiết điều luật | Xem nội dung đầy đủ từng điều | Cao |

### 3.1.3. Yêu cầu chức năng cho Quản trị viên (Admin Web)

**Bảng 3.2. Danh sách yêu cầu chức năng — Quản trị viên**

| Mã | Chức năng | Mô tả ngắn | Ưu tiên |
|---|---|---|---|
| F-12 | Đăng nhập Admin | Xác thực role=admin | Cao |
| F-13 | Upload PDF văn bản | Drag-drop, có AbortController, resume sau reload | Cao |
| F-14 | Theo dõi xử lý PDF | Realtime qua WebSocket, hiển thị % tiến trình | Cao |
| F-15 | Quản lý văn bản | Danh sách, paginate, tìm kiếm, xem chi tiết, xoá | Cao |
| F-16 | Dashboard thống kê | Tổng số users, conversations, messages, documents | Trung |

### 3.1.4. Yêu cầu phi chức năng

**Bảng 3.3. Yêu cầu phi chức năng**

| Nhóm | Yêu cầu | Mức độ |
|---|---|---|
| **Hiệu năng** | Latency toàn pipeline Agentic RAG < 15 giây | Bắt buộc |
| | Latency Simple RAG < 5 giây | Khuyến nghị |
| | Thời gian TTF (Time-To-First-Token) SSE < 3 giây | Khuyến nghị |
| | Tìm kiếm vector (ChromaDB) < 500ms | Bắt buộc |
| **Bảo mật** | Mật khẩu hash bằng bcrypt (cost factor ≥ 10) | Bắt buộc |
| | JWT access token expire 15 phút, refresh 30 ngày | Bắt buộc |
| | Refresh token rotation (thu hồi khi sử dụng) | Bắt buộc |
| | RAG Service chỉ nhận kết nối qua X-API-Key | Bắt buộc |
| **Đa nền tảng** | Mobile: Android + iOS từ 1 codebase KMP | Bắt buộc |
| | Web admin: Chrome, Firefox, Safari mới nhất | Bắt buộc |
| **Mở rộng** | Docker Compose — dễ scale từng service | Khuyến nghị |
| | Stateless REST API (có thể load balance) | Bắt buộc |
| **Khả dụng** | Fault tolerance qua compensating transaction | Bắt buộc |
| | Multi-API-key rotation chống rate limit | Bắt buộc |
| **Trải nghiệm** | SSE streaming hiển thị typing animation | Bắt buộc |
| | WebSocket realtime task tracking | Bắt buộc |
| | SSE ThinkingPanel 5 bước tiến trình | Khuyến nghị |

---

## 3.2. Phân tích hệ thống — Biểu đồ Use Case

### 3.2.1. Biểu đồ Use Case tổng quát

*(Tham khảo Hình 3.1 trong phụ lục sơ đồ)*

Hệ thống có hai tác nhân chính:
- **Người dùng (User)**: người dân, sinh viên, cán bộ — sử dụng Mobile App.
- **Quản trị viên (Admin)**: nhân viên quản trị hệ thống — sử dụng Admin Web.

Hai tác nhân chia sẻ một số chức năng (duyệt thư viện, xem chi tiết điều luật) nhưng có tập use case chủ yếu hoàn toàn khác nhau.

### 3.2.2. Đặc tả chi tiết các Use Case quan trọng

#### UC-01: Đăng ký tài khoản

**Bảng 3.4. Đặc tả UC-01 — Đăng ký tài khoản**

| Trường | Nội dung |
|---|---|
| **Tên use case** | Đăng ký tài khoản |
| **Mã** | UC-01 |
| **Tác nhân** | Người dùng chưa có tài khoản |
| **Mô tả** | Người dùng mới tạo tài khoản bằng email và mật khẩu để sử dụng hệ thống |
| **Tiền điều kiện** | Người dùng chưa có tài khoản với email này |
| **Luồng cơ bản** | 1. Người dùng mở ứng dụng, chọn "Đăng ký". 2. Nhập email, mật khẩu (≥8 ký tự), họ tên. 3. Nhấn "Đăng ký". 4. Hệ thống kiểm tra email chưa tồn tại. 5. Hash mật khẩu bằng bcrypt. 6. Tạo bản ghi user, tạo access + refresh token. 7. Trả về token, chuyển vào màn hình chính. |
| **Luồng thay thế** | 4a. Email đã tồn tại → hiển thị lỗi "Email này đã được đăng ký". |
| | 2a. Mật khẩu < 8 ký tự → validation ngay trên UI trước khi gửi. |
| **Hậu điều kiện** | Tài khoản mới được tạo trong PostgreSQL. Người dùng đã đăng nhập. |

#### UC-02: Đăng nhập / Đăng xuất

**Bảng 3.5. Đặc tả UC-02 — Đăng nhập / Đăng xuất**

| Trường | Nội dung |
|---|---|
| **Tên use case** | Đăng nhập / Đăng xuất |
| **Mã** | UC-02 |
| **Tác nhân** | Người dùng đã có tài khoản |
| **Mô tả** | Xác thực người dùng bằng email/mật khẩu, nhận JWT token. Đăng xuất thu hồi refresh token. |
| **Tiền điều kiện** | Tài khoản tồn tại và `is_active = true` |
| **Luồng cơ bản (Đăng nhập)** | 1. Nhập email + mật khẩu. 2. Hệ thống tra cứu user theo email. 3. So sánh mật khẩu với bcrypt.verify. 4. Tạo access token (15 phút) + refresh token (30 ngày). 5. Lưu refresh token vào PostgreSQL. 6. Lưu token vào KSafe (encrypted storage) trên thiết bị. 7. Chuyển vào màn hình chính. |
| **Luồng cơ bản (Đăng xuất)** | 1. Người dùng nhấn "Đăng xuất". 2. Gọi API revoke refresh token. 3. Xoá token khỏi KSafe. 4. Chuyển về màn hình đăng nhập. |
| **Luồng thay thế** | 3a. Mật khẩu sai → lỗi "Email hoặc mật khẩu không đúng". |
| | 5a. is_active = false → lỗi "Tài khoản bị khoá". |
| **Luồng ngoại lệ (Auto-refresh)** | Khi access token hết hạn (401): Ktor Auth plugin tự động gọi POST /auth/refresh với refresh token → nhận access + refresh token mới (rotation) → retry request gốc. |
| **Hậu điều kiện** | (Đăng nhập) Token lưu local, user `last_login_at` cập nhật. (Đăng xuất) Refresh token bị thu hồi. |

#### UC-04: Quản lý hội thoại

**Bảng 3.6. Đặc tả UC-04 — Quản lý hội thoại**

| Trường | Nội dung |
|---|---|
| **Tên use case** | Quản lý hội thoại |
| **Mã** | UC-04 |
| **Tác nhân** | Người dùng đã đăng nhập |
| **Mô tả** | Người dùng tạo, xem, đổi tên, pin, archive và xoá các hội thoại với AI |
| **Tiền điều kiện** | Đã đăng nhập (có access token hợp lệ) |
| **Luồng cơ bản** | 1. Người dùng vào màn hình "Hội thoại". 2. Danh sách hội thoại hiển thị, sắp xếp: pinned trước, sau đó theo `last_message_at` giảm dần. 3. Nhấn "+" tạo hội thoại mới → tiêu đề tự động (cập nhật sau câu đầu tiên). 4. Nhấn giữ hội thoại → menu: Đổi tên, Pin/Unpin, Archive, Xoá. |
| **Luồng thay thế** | 4a. Pin hội thoại → hội thoại luôn xuất hiện đầu danh sách. |
| | 4b. Archive hội thoại → ẩn khỏi danh sách mặc định, có thể khôi phục. |
| **Hậu điều kiện** | Thay đổi được lưu vào PostgreSQL, danh sách cập nhật realtime. |

#### UC-05: Gửi tin nhắn AI — Streaming SSE

**Bảng 3.7. Đặc tả UC-05 — Gửi tin nhắn AI với Streaming SSE**

| Trường | Nội dung |
|---|---|
| **Tên use case** | Gửi tin nhắn AI — Streaming SSE |
| **Mã** | UC-05 |
| **Tác nhân** | Người dùng đã đăng nhập |
| **Mô tả** | Người dùng gửi câu hỏi pháp luật và nhận câu trả lời từ Agentic RAG qua SSE streaming, với ThinkingPanel hiển thị tiến trình 5 bước |
| **Tiền điều kiện** | Đã đăng nhập, đang trong một hội thoại |
| **Luồng cơ bản** | 1. Nhập câu hỏi vào TextField. 2. Nhấn nút Gửi. 3. ThinkingPanel xuất hiện, hiển thị từng bước pipeline: Bước 1 (Kiểm tra) → Bước 2 (Phân tích) → Bước 3 (Tra cứu CSDL) → Bước 4 (Tìm kiếm web) → Bước 5 (Kiểm chứng). 4. ChatBubble nhận câu trả lời theo từng token (typing animation). 5. Câu trả lời hoàn tất, hiển thị citation (nguồn tham chiếu). 6. Suggested Questions chips xuất hiện bên dưới. |
| **Luồng thay thế** | 1a. Câu hỏi off-topic → Guardrail từ chối, hiển thị thông báo lịch sự. |
| | 3a. Không tìm thấy tài liệu liên quan → Agent tự động chuyển sang web search. |
| **Luồng ngoại lệ** | Mất kết nối giữa stream → SSEClient phát hiện, hiển thị lỗi, cho phép retry. |
| **Hậu điều kiện** | Cặp tin nhắn (user + assistant) lưu vào PostgreSQL với `sources` JSONB. Tiêu đề hội thoại tự cập nhật theo topic của câu trả lời đầu tiên. |

#### UC-07: Tư vấn có Hướng dẫn (Guided Consultation)

**Bảng 3.8. Đặc tả UC-07 — Tư vấn có Hướng dẫn**

| Trường | Nội dung |
|---|---|
| **Tên use case** | Tư vấn có Hướng dẫn |
| **Mã** | UC-07 |
| **Tác nhân** | Người dùng đã đăng nhập |
| **Mô tả** | Quy trình 2 bước: hệ thống hỏi làm rõ ngữ cảnh trước, sau đó chạy pipeline AI với thông tin đầy đủ |
| **Tiền điều kiện** | Đã đăng nhập |
| **Luồng cơ bản** | 1. Người dùng mở màn hình "Tư vấn có hướng dẫn". 2. Nhập câu hỏi ngắn (VD: "Vượt đèn đỏ phạt bao nhiêu?"). 3. Nhấn "Bắt đầu". 4. Hệ thống phân tích, hiển thị câu hỏi trắc nghiệm (VD: "Phương tiện: [Ô tô / Xe máy / Xe đạp]"). 5. Người dùng chọn đáp án. 6. Nhấn "Tiếp tục". 7. ThinkingPanel + stream trả lời (tương tự UC-05). 8. Hiển thị câu trả lời chuyên sâu theo ngữ cảnh đã chọn. |
| **Luồng thay thế** | 4a. Câu hỏi đã đủ ngữ cảnh → hệ thống không sinh câu hỏi làm rõ, chuyển thẳng sang Bước 6. |
| **Hậu điều kiện** | Câu trả lời chính xác theo loại phương tiện/tình huống cụ thể của người dùng. |

#### UC-10: Tìm kiếm AI ngữ nghĩa (AI-Powered Search)

**Bảng 3.9. Đặc tả UC-10 — Tìm kiếm AI ngữ nghĩa**

| Trường | Nội dung |
|---|---|
| **Tên use case** | Tìm kiếm AI ngữ nghĩa |
| **Mã** | UC-10 |
| **Tác nhân** | Người dùng đã đăng nhập |
| **Mô tả** | Tìm kiếm điều luật theo ngữ nghĩa (semantic search) thay vì chỉ khớp từ khoá, sử dụng embedding vector |
| **Tiền điều kiện** | Đã đăng nhập, đang ở màn hình Thư viện pháp luật |
| **Luồng cơ bản** | 1. Nhập mô tả ngữ nghĩa vào ô tìm kiếm (VD: "Quy định về bảo vệ người tố giác tham nhũng"). 2. Nhấn "Tìm kiếm AI". 3. Hệ thống mã hoá query → ChromaDB cosine search → cross-encoder rerank. 4. Hiển thị top-20 kết quả, sắp xếp theo relevance score, kèm badge score. 5. Nhấn vào kết quả → xem chi tiết điều luật. |
| **Luồng thay thế** | 3a. Không tìm thấy kết quả nào trên ngưỡng 0.60 → hiển thị "Không tìm thấy kết quả phù hợp". |
| **Hậu điều kiện** | Người dùng có danh sách điều luật liên quan ngữ nghĩa nhất với câu truy vấn. |

#### UC-13: Upload PDF văn bản pháp luật

**Bảng 3.10. Đặc tả UC-13 — Upload PDF**

| Trường | Nội dung |
|---|---|
| **Tên use case** | Upload PDF văn bản pháp luật |
| **Mã** | UC-13 |
| **Tác nhân** | Quản trị viên |
| **Mô tả** | Admin upload file PDF để hệ thống tự động parse thành điều luật, embed và đưa vào CSDL |
| **Tiền điều kiện** | Đã đăng nhập với role = admin |
| **Luồng cơ bản** | 1. Truy cập trang "Upload văn bản". 2. Kéo file PDF vào DropZone hoặc nhấn chọn file. 3. Hệ thống validate (định dạng PDF, kích thước). 4. Nhấn "Upload". 5. Hiển thị ProgressBar, `task_id` lưu vào localStorage. 6. WebSocket cập nhật tiến trình realtime. 7. Khi hoàn tất: toast thành công + số điều luật đã thêm. |
| **Luồng thay thế** | 4a. Người dùng nhấn Huỷ (AbortController) → upload dừng, task vẫn lưu `task_id`. |
| | 7a. Sau khi reload trang: hệ thống detect `task_id` trong localStorage, query `GET /tasks/{id}` để tiếp tục theo dõi. |
| **Luồng ngoại lệ** | 6a. Gemini Vision parse lỗi → DocumentTask status = FAILED, hiển thị error message. |
| **Hậu điều kiện** | Văn bản pháp luật mới xuất hiện trong thư viện (nếu thành công). |

#### UC-14: Theo dõi tiến trình qua WebSocket

**Bảng 3.11. Đặc tả UC-14 — Theo dõi tiến trình WebSocket**

| Trường | Nội dung |
|---|---|
| **Tên use case** | Theo dõi tiến trình xử lý PDF qua WebSocket |
| **Mã** | UC-14 |
| **Tác nhân** | Quản trị viên |
| **Mô tả** | Admin theo dõi tiến trình xử lý PDF realtime qua WebSocket mà không cần refresh trang |
| **Tiền điều kiện** | Đã upload file (UC-13), WebSocket đã kết nối |
| **Luồng cơ bản** | 1. Ngay khi upload, WebSocket tự kết nối `wss://main-service/documents/ws`. 2. Nhận events: `UPLOAD_PROGRESS {progress: 0→100%}` → cập nhật ProgressBar. 3. Nhận event: `UPLOAD_STATUS {status: COMPLETED, article_count: N}` → toast thành công. 4. WebSocket tự ngắt khi navigate khỏi trang. |
| **Luồng thay thế** | 2a. Mất kết nối WebSocket → tự reconnect sau 3 giây (exponential backoff). |
| **Luồng ngoại lệ** | 3a. `UPLOAD_STATUS {status: FAILED}` → toast lỗi, hiển thị `error_message`. |
| **Hậu điều kiện** | Admin biết kết quả xử lý mà không cần refresh trang. |

#### UC-16: Xem Dashboard thống kê

**Bảng 3.12. Đặc tả UC-16 — Dashboard thống kê**

| Trường | Nội dung |
|---|---|
| **Tên use case** | Xem Dashboard thống kê |
| **Mã** | UC-16 |
| **Tác nhân** | Quản trị viên |
| **Mô tả** | Admin xem tổng quan thống kê hệ thống: số lượng người dùng, hội thoại, tin nhắn, văn bản pháp luật |
| **Tiền điều kiện** | Đã đăng nhập với role = admin |
| **Luồng cơ bản** | 1. Truy cập `/dashboard`. 2. Hiển thị 4 card số liệu: Users, Conversations, Messages, Documents. 3. BarChart top-10 chủ đề pháp luật theo số điều luật. 4. Danh sách 5 task upload gần nhất. 5. Dashboard tự refresh khi có task mới hoàn tất (qua WebSocket). |
| **Hậu điều kiện** | Admin nắm được tình trạng hoạt động của hệ thống. |

---

## 3.3. Biểu đồ tuần tự (Sequence Diagrams)

*(Tất cả biểu đồ tuần tự xem tại phụ lục sơ đồ — Hình 3.6 đến 3.13)*

### SD-01 — Đăng ký + Đăng nhập + JWT Auto-refresh

*(Hình 3.6)*

Luồng này minh hoạ cơ chế xác thực JWT 2 token (access + refresh). Điểm đặc trưng là **JWT Auto-refresh** được xử lý hoàn toàn tự động bởi Ktor `Auth { bearer { refreshTokens } }` plugin ở phía mobile: khi nhận 401, plugin tự động gọi `POST /auth/refresh`, nhận token mới và retry request gốc mà người dùng không cần đăng nhập lại. Cơ chế **token rotation** (mỗi lần refresh, token cũ bị thu hồi, token mới được cấp) ngăn chặn token bị đánh cắp sử dụng lại.

### SD-02 — Luồng Chat Agentic RAG + SSE Streaming (Quan trọng nhất)

*(Hình 3.7)*

Đây là luồng phức tạp và quan trọng nhất của hệ thống. Điểm đáng chú ý:

1. **SSE bridging**: Main Service không xử lý AI mà đóng vai trò proxy — nhận SSE stream từ RAG Service và forward về mobile, cho phép pipeline AI nặng chạy độc lập.

2. **5-step ThinkingPanel**: Mỗi node trong LangGraph tương ứng với 1 event `thinking` gửi về mobile. ThinkingPanel cập nhật realtime theo từng bước: Kiểm tra → Phân tích → Tra cứu CSDL → Tìm kiếm web (optional) → Kiểm chứng.

3. **Dual-source retrieval**: Agent bắt buộc gọi cả `retrieve_internal_law` và `search_web_for_law` để đảm bảo câu trả lời dựa trên cả nguyên văn nội bộ và hiệu lực pháp lý hiện hành.

4. **Verifier correction**: Gemini 2.5 Pro kiểm chứng câu trả lời trước khi stream về — nếu phát hiện hallucination, tự động sửa trước khi người dùng nhìn thấy.

5. **Suggested Questions**: Sau khi `done` event nhận được, mobile tự động gọi `GET /messages/{id}/suggested-questions` để hiển thị 3 gợi ý câu hỏi tiếp theo.

### SD-03 — Guided Consultation (Clarify + Answer SSE)

*(Hình 3.8)*

Luồng 2 bước: Bước 1 (Clarify) nhẹ và nhanh (~500ms) — chỉ phân tích câu hỏi để sinh trắc nghiệm. Bước 2 (Answer) nặng hơn và dùng SSE stream. Điểm đặc biệt là **Planning Node (deterministic)** — không gọi LLM để lập kế hoạch, giảm latency và chi phí token.

### SD-04 — AI-Powered Search

*(Hình 3.9)*

Khác với chat thông thường, AI Search chạy pipeline retrieval trực tiếp (không qua LangGraph) và trả về danh sách kết quả có score. Mobile hiển thị kết quả theo dạng list với badge score màu sắc (xanh lá = ≥ 0.85, vàng = 0.75-0.85, đỏ = < 0.75).

### SD-05 — Document Ingestion (Concurrent + Compensating Transaction)

*(Hình 3.10)*

Luồng này thể hiện hai kỹ thuật quan trọng: (1) **Concurrent processing** — Cloudinary upload và Gemini Vision parse chạy song song, tiết kiệm 5-10 giây. (2) **Compensating Transaction** — nếu ChromaDB lỗi sau khi MongoDB đã ghi, MongoDB được rollback để đảm bảo nhất quán dữ liệu.

### SD-06 — WebSocket Task Tracking

*(Hình 3.11)*

WebSocket kết nối tự động khi Admin vào trang Documents, ngắt khi rời trang (`useEffect` cleanup). Hệ thống broadcast `UPLOAD_PROGRESS` và `UPLOAD_STATUS` events. Auto-reconnect với exponential backoff xử lý trường hợp mất kết nối tạm thời.

### SD-07 — Suggested Questions

*(Hình 3.12)*

Sau khi nhận `done` event từ SSE, mobile tự động gọi API gợi ý câu hỏi. Gemini Flash sinh 3 câu hỏi liên quan dựa trên context cuộc hội thoại. Mobile render dưới dạng clickable chips — khi nhấn, câu hỏi tự điền vào TextField và tự động gửi.

### SD-08 — Browse + View Article

*(Hình 3.13)*

Duyệt thư viện dùng MongoDB aggregation pipeline để group by `law_id`, lấy thông tin tóm tắt. Xem chi tiết điều luật là một query MongoDB đơn giản `findOne`. Không qua RAG Service — thuần CRUD từ MongoDB qua Main Service.

---

## 3.4. Thiết kế cơ sở dữ liệu

### 3.4.1. Lý do chọn Polyglot Persistence

Hệ thống sử dụng 3 loại cơ sở dữ liệu khác nhau — mỗi loại được chọn dựa trên tính chất dữ liệu cần lưu:

**Bảng 3.13. Lý do lựa chọn từng loại CSDL**

| CSDL | Loại | Dữ liệu lưu trữ | Lý do chọn |
|---|---|---|---|
| **PostgreSQL** | Relational | Users, conversations, messages | Cần ACID, foreign key, JOIN phức tạp |
| **MongoDB** | Document | Articles (điều luật, 528K+ bản ghi) | Schema linh hoạt, aggregation mạnh, không cần JOIN |
| **ChromaDB** | Vector | Embedding chunks (690K+ vectors) | Chuyên biệt cho nearest-neighbor search, tích hợp HNSW |

### 3.4.2. Thiết kế PostgreSQL — 5 bảng

*(Tham khảo Hình 3.4 — ER Diagram)*

#### Bảng `users`

**Bảng 3.14. Schema bảng users**

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT uuid4 | Khoá chính tự sinh |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Email đăng nhập |
| `hashed_password` | VARCHAR(255) | NOT NULL | Mật khẩu đã hash bcrypt |
| `full_name` | VARCHAR(255) | NULL | Họ và tên |
| `phone_number` | VARCHAR(20) | NULL, INDEX | Số điện thoại |
| `role` | VARCHAR(50) | DEFAULT 'user', INDEX | 'user' hoặc 'admin' |
| `is_active` | BOOLEAN | DEFAULT true, INDEX | Trạng thái kích hoạt |
| `last_login_at` | TIMESTAMPTZ | NULL | Lần đăng nhập cuối |
| `password_changed_at` | TIMESTAMPTZ | NULL | Lần đổi mật khẩu cuối |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Thời điểm tạo |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW(), ON UPDATE NOW() | Thời điểm cập nhật |

#### Bảng `conversations`

**Bảng 3.15. Schema bảng conversations**

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | UUID | PK | — |
| `user_id` | UUID | FK → users.id (CASCADE) | Chủ sở hữu |
| `title` | VARCHAR(500) | NOT NULL | Tiêu đề hội thoại |
| `is_pinned` | BOOLEAN | DEFAULT false | Ghim lên đầu |
| `is_archived` | BOOLEAN | DEFAULT false | Ẩn khỏi danh sách chính |
| `message_count` | INTEGER | DEFAULT 0 | Đếm số tin nhắn (tránh COUNT query) |
| `last_message_at` | TIMESTAMPTZ | NULL | Thời điểm tin nhắn cuối |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | — |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | — |

#### Bảng `messages`

**Bảng 3.16. Schema bảng messages**

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | UUID | PK | — |
| `conversation_id` | UUID | FK → conversations.id (CASCADE), INDEX | Hội thoại chứa tin nhắn |
| `question_id` | UUID | FK → messages.id (SET NULL), NULL | Self-reference: ID của câu hỏi tương ứng (Q&A pair) |
| `role` | VARCHAR(20) | NOT NULL | 'user' hoặc 'assistant' |
| `content` | TEXT | NOT NULL | Nội dung tin nhắn |
| `sources` | JSONB | NULL | Danh sách nguồn citation (law_id, article_id, score, ...) |
| `metadata` | JSONB | NULL | Thông tin bổ sung (topic, query_analysis, ...) |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | — |

> **Ghi chú thiết kế**: Cặp (câu hỏi, câu trả lời) được liên kết qua `question_id` tự tham chiếu. Khi AI trả lời message ID=X, `answer.question_id = X`. Điều này cho phép truy vấn "câu trả lời của câu hỏi này" mà không cần JOIN phức tạp.

> **Ghi chú JSONB**: Trường `sources` lưu dạng JSONB thay vì bảng riêng để tránh JOIN phức tạp khi truy vấn danh sách messages. Ví dụ:
> ```json
> [{"law_id": "168/2024/nd-cp", "article_id": "7", "title": "Điều 7...", 
>   "score": 0.92, "year": "2024", "source_url": "https://..."}]
> ```

#### Bảng `document_tasks`

**Bảng 3.17. Schema bảng document_tasks**

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | UUID | PK, INDEX | — |
| `user_id` | UUID | FK → users.id (SET NULL), NULL, INDEX | Admin tạo task |
| `filename` | VARCHAR | INDEX | Tên file gốc |
| `file_size_bytes` | BIGINT | NULL | Kích thước file |
| `status` | ENUM | INDEX | `pending`, `processing`, `completed`, `failed`, `cancelled` |
| `progress` | INTEGER | DEFAULT 0 | 0–100% |
| `current_step` | VARCHAR | NULL | Bước đang xử lý: 'uploading', 'parsing', 'embedding', ... |
| `law_id` | VARCHAR | NULL, INDEX | Mã văn bản pháp luật (sau parse) |
| `article_count` | INTEGER | DEFAULT 0 | Số điều luật đã ingest |
| `error_message` | TEXT | NULL | Mô tả lỗi (nếu FAILED) |
| `created_at` | DATETIME | DEFAULT NOW() | — |
| `completed_at` | DATETIME | NULL | Thời điểm hoàn thành |

#### Bảng `refresh_tokens`

**Bảng 3.18. Schema bảng refresh_tokens**

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | UUID | PK | — |
| `user_id` | UUID | FK → users.id (CASCADE), INDEX | Chủ sở hữu token |
| `token` | VARCHAR | UNIQUE | Token đã hash (bcrypt) |
| `expires_at` | TIMESTAMPTZ | NOT NULL | Thời điểm hết hạn |
| `is_revoked` | BOOLEAN | DEFAULT false | Đã thu hồi chưa |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | — |

**Quan hệ giữa các bảng** (xem Hình 3.4):
- `users` 1—* `conversations`: mỗi user có nhiều hội thoại.
- `users` 1—* `refresh_tokens`: mỗi user có nhiều refresh token (đa thiết bị).
- `conversations` 1—* `messages`: mỗi hội thoại có nhiều tin nhắn.
- `messages` 1—0..1 `messages` (self): mỗi câu trả lời tham chiếu về câu hỏi gốc.

### 3.4.3. Thiết kế MongoDB — Collection articles

**Cấu trúc document** (collection `VietnamLawDB.articles`):

```json
{
  "_id": "168/2024/nd-cp_7",
  "law_id": "168/2024/nd-cp",
  "article_id": "7",
  "title": "Điều 7. Xử phạt người điều khiển xe mô tô, xe gắn máy...",
  "text": "1. Phạt tiền từ 100.000 đồng đến 200.000 đồng đối với người...",
  "source_url": "https://res.cloudinary.com/...",
  "full_content_search": "Điều 7. Xử phạt...\n1. Phạt tiền...",
  "metadata": {
    "topics": ["Xử phạt giao thông", "Xe mô tô"],
    "keywords": ["nồng độ cồn", "mức phạt", "tước GPLX"],
    "summary": "Quy định mức xử phạt vi phạm giao thông cho xe máy",
    "year": "2024"
  }
}
```

**Bảng 3.19. Các trường trong MongoDB article document**

| Trường | Kiểu | Mô tả |
|---|---|---|
| `_id` | String | `{law_id}_{article_id}` — khoá duy nhất cho mỗi điều luật |
| `law_id` | String | Mã văn bản pháp luật (VD: `168/2024/nd-cp`) |
| `article_id` | String | Số thứ tự điều luật (VD: `"7"`) |
| `title` | String | Tiêu đề đầy đủ điều luật |
| `text` | String | Nội dung toàn văn |
| `source_url` | String | URL file PDF gốc trên Cloudinary |
| `full_content_search` | String | Ghép title + text cho full-text search index |
| `metadata.topics` | Array[String] | Danh sách chủ đề pháp lý |
| `metadata.keywords` | Array[String] | Từ khoá chuyên ngành |
| `metadata.summary` | String | Tóm tắt ngắn gọn điều luật |
| `metadata.year` | String | Năm ban hành văn bản |

**Index** được tạo trên MongoDB:
- Text index trên `full_content_search` (full-text search).
- B-tree index trên `law_id`, `article_id`, `metadata.year`, `metadata.topics`.

**Aggregation pipelines chính**:

| Pipeline | Mục đích |
|---|---|
| `get_laws()` | Group by `law_id`, đếm số điều, lấy năm/topic/summary. Kết quả: danh sách văn bản |
| `get_law_detail()` | Lấy tất cả articles của một `law_id`, sort theo `article_id` |
| `get_all_topics()` | Distinct tất cả topics có trong CSDL |
| `get_all_years()` | Distinct tất cả năm ban hành |
| `search()` | Full-text search + metadata filter |

### 3.4.4. Thiết kế ChromaDB — Collection vietnamese_law

ChromaDB lưu trữ **vector embeddings** của các chunks được chia từ articles.

**Bảng 3.20. Cấu trúc một entry trong ChromaDB**

| Trường | Kiểu | Ví dụ | Mô tả |
|---|---|---|---|
| `id` | String | `168/2024/nd-cp_7_chunk0` | `{law_id}_{article_id}_chunk{index}` |
| `document` | String | `"Điều 7. Xử phạt...\n\n1. Phạt tiền..."` | `title + "\n\n" + chunk_text` |
| `embedding` | float[768] | `[0.231, -0.045, ...]` | Vector từ bi-encoder |
| `metadata.law_id` | String | `168/2024/nd-cp` | — |
| `metadata.article_id` | String | `7` | — |
| `metadata.title` | String | `Điều 7...` | Tiêu đề điều luật |
| `metadata.chunk_index` | Integer | `0` | Thứ tự chunk trong article |
| `metadata.total_chunks` | Integer | `1` | Tổng số chunks của article |
| `metadata.year` | String | `2024` | Dùng để year boost |
| `metadata.topics` | String (JSON) | `'["Giao thông", "Xe máy"]'` | JSON string do ChromaDB chỉ lưu scalar |
| `metadata.keywords` | String (JSON) | `'["nồng độ cồn", "mức phạt"]'` | JSON string |
| `metadata.summary` | String | `"Quy định mức phạt..."` | Tóm tắt |

> **Ghi chú quan trọng**: ChromaDB metadata chỉ hỗ trợ kiểu scalar (string, int, float, bool). Do đó `topics` và `keywords` phải lưu dưới dạng **JSON string** (không phải array). Khi đọc ra cần `json.loads()` để convert lại array.

**Cấu hình HNSW**:

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `distance_metric` | cosine | Độ đo khoảng cách vector |
| `ef_construction` | 100 | Số ứng viên duyệt khi build index |
| `ef_search` | 100 | Số ứng viên duyệt khi query |
| `max_neighbors (M)` | 16 | Số kết nối mỗi node trong HNSW graph |

### 3.4.5. Sơ đồ quan hệ giữa 3 cơ sở dữ liệu

*(Tham khảo Hình 3.5)*

Tuy 3 CSDL độc lập về mặt kỹ thuật, chúng liên kết với nhau qua **application-level references** (không phải foreign key):

1. **MongoDB ↔ ChromaDB**: 1 article (`law_id + article_id`) → 1..N chunks trong ChromaDB. Khoá liên kết: `{law_id}_{article_id}` là prefix của `chunk_id`.

2. **PostgreSQL ↔ ChromaDB**: `messages.sources` (JSONB) chứa `chunk_id` để truy hồi citation khi người dùng muốn xem nguồn chi tiết.

3. **PostgreSQL ↔ MongoDB**: `document_tasks.law_id` liên kết task upload với articles trong MongoDB. Admin có thể xem task và biết bao nhiêu điều luật của law_id đó đã được ingest.

---

## 3.5. Thiết kế API

Hệ thống cung cấp hai nhóm API:
- **Main Service** (`/api/v1`) — public, xác thực JWT.
- **RAG Service** (`/api/v1`) — internal, xác thực X-API-Key.

Dưới đây đặc tả 20 API quan trọng nhất.

### 3.5.1. Auth APIs

**Bảng 3.21. API POST /auth/register — Đăng ký**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `POST /api/v1/auth/register` |
| **Authentication** | Không yêu cầu |
| **Request Body** | `{"email": "user@example.com", "password": "password123", "full_name": "Nguyễn Văn A"}` |
| **Response 201** | `{"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer", "user": {...}}` |
| **Response 400** | Email không hợp lệ / mật khẩu quá ngắn |
| **Response 409** | Email đã tồn tại |

**Bảng 3.22. API POST /auth/login — Đăng nhập**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `POST /api/v1/auth/login` |
| **Authentication** | Không yêu cầu |
| **Request Body** | `{"email": "user@example.com", "password": "password123"}` |
| **Response 200** | `{"access_token": "...", "refresh_token": "...", "user": {"id", "email", "role", ...}}` |
| **Response 401** | Email hoặc mật khẩu sai |
| **Response 403** | Tài khoản bị khoá |

**Bảng 3.23. API POST /auth/refresh — Làm mới token**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `POST /api/v1/auth/refresh` |
| **Request Body** | `{"refresh_token": "eyJ..."}` |
| **Response 200** | `{"access_token": "...", "refresh_token": "..."}` (token rotation) |
| **Response 401** | Refresh token hết hạn hoặc đã bị thu hồi |

### 3.5.2. Chat APIs

**Bảng 3.24. API POST /chat/messages/stream — Gửi tin nhắn AI**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `POST /api/v1/chat/messages/stream` |
| **Authentication** | JWT Bearer |
| **Request Body** | `{"conversation_id": "uuid", "content": "Vượt đèn đỏ phạt bao nhiêu?"}` |
| **Response** | `Content-Type: text/event-stream` (SSE) |
| **SSE Events** | `event: thinking` `{"step": 1-5, "message": "..."}` → `event: answer` `{"chunk": "..."}` → `event: done` `{"sources": [...]}` |
| **Response 401** | Token không hợp lệ |
| **Response 404** | Conversation không tồn tại |

**Bảng 3.25. API GET /chat/messages/{id}/suggested-questions — Gợi ý câu hỏi**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `GET /api/v1/chat/messages/{message_id}/suggested-questions` |
| **Authentication** | JWT Bearer |
| **Response 200** | `{"suggestions": [{"question": "..."}, {"question": "..."}, {"question": "..."}]}` |
| **Response 404** | Message không tồn tại |

### 3.5.3. Laws APIs

**Bảng 3.26. API GET /laws — Danh sách văn bản**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `GET /api/v1/laws` |
| **Authentication** | JWT Bearer |
| **Query Params** | `page` (int, default=1), `limit` (int, default=20, max=100), `q` (string, tìm kiếm), `year` (string), `topics` (array string) |
| **Response 200** | `{"items": [{law_id, year, article_count, summary, topics}], "total", "page", "limit"}` |

**Bảng 3.27. API POST /laws/ai-search — Tìm kiếm AI ngữ nghĩa**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `POST /api/v1/laws/ai-search` |
| **Authentication** | JWT Bearer |
| **Request Body** | `{"query": "bảo vệ người tố giác tham nhũng", "top_k": 20}` |
| **Response 200** | `{"results": [{"law_id", "article_id", "title", "text", "score", "year", "topics"}], "query_time_ms"}` |

**Bảng 3.28. API GET /laws/{law_id}/articles — Chi tiết điều luật**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `GET /api/v1/laws/{law_id}/articles` |
| **Authentication** | JWT Bearer |
| **Query Params** | `page` (int), `limit` (int) |
| **Response 200** | `{"items": [{article_id, title, text, metadata}], "total", "page"}` |

### 3.5.4. Documents APIs

**Bảng 3.29. API POST /documents/upload — Upload PDF**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `POST /api/v1/documents/upload` |
| **Authentication** | JWT Bearer (role=admin) |
| **Request Body** | `multipart/form-data` với field `file` (PDF) |
| **Response 202** | `{"task_id": "uuid", "status": "pending", "message": "Upload đã bắt đầu xử lý"}` |
| **Response 400** | File không phải PDF |
| **Response 403** | Không có quyền admin |

**Bảng 3.30. API GET /documents/tasks/{task_id} — Trạng thái task**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `GET /api/v1/documents/tasks/{task_id}` |
| **Authentication** | JWT Bearer |
| **Response 200** | `{"id", "filename", "status", "progress", "current_step", "law_id", "article_count", "error_message"}` |

**Bảng 3.31. API WebSocket /documents/ws — Tracking realtime**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `WS /api/v1/documents/ws` |
| **Authentication** | JWT Bearer (qua query param `token`) |
| **Event UPLOAD_PROGRESS** | `{"type": "UPLOAD_PROGRESS", "task_id": "uuid", "progress": 60, "current_step": "embedding"}` |
| **Event UPLOAD_STATUS** | `{"type": "UPLOAD_STATUS", "task_id": "uuid", "status": "completed", "article_count": 47}` |

### 3.5.5. Guided Consultation APIs

**Bảng 3.32. API POST /guided/clarify — Bước 1 Guided Consultation**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `POST /api/v1/guided/clarify` |
| **Authentication** | JWT Bearer |
| **Request Body** | `{"query": "Vượt đèn đỏ phạt bao nhiêu?"}` |
| **Response 200** | `{"detected_topic": "Giao thông", "clarify_questions": [{"question": "...", "options": [...]}]}` |

**Bảng 3.33. API POST /guided/answer/stream — Bước 2 Guided Consultation**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `POST /api/v1/guided/answer/stream` |
| **Authentication** | JWT Bearer |
| **Request Body** | `{"original_query": "...", "detected_topic": "...", "clarify_context": "Phương tiện: Xe máy"}` |
| **Response** | `Content-Type: text/event-stream` (SSE, format giống chat stream) |

### 3.5.6. Dashboard API

**Bảng 3.34. API GET /dashboard/stats — Thống kê tổng quan**

| Trường | Nội dung |
|---|---|
| **Endpoint** | `GET /api/v1/dashboard/stats` |
| **Authentication** | JWT Bearer (role=admin) |
| **Response 200** | `{"total_users", "total_conversations", "total_messages", "total_documents", "top_topics": [...], "recent_tasks": [...]}` |
| **Cache** | Server-side cache 60 giây, invalidate khi có task mới hoàn tất |

---

## 3.6. Tổng kết chương 3

Chương 3 đã hoàn thành việc phân tích và thiết kế toàn bộ hệ thống Vietnam Law Chatbot từ góc độ chức năng và dữ liệu. Hệ thống gồm **16 use case chính** phục vụ 2 nhóm tác nhân với **20+ API endpoint** được thiết kế theo chuẩn RESTful, kết hợp với SSE streaming và WebSocket cho các tính năng real-time.

Ba điểm thiết kế quan trọng cần nhấn mạnh: (1) **Mô hình Q&A pair** trong bảng `messages` (self-reference `question_id`) cho phép truy vấn linh hoạt cặp câu hỏi-trả lời mà không cần JOIN phức tạp; (2) **Polyglot persistence** — sử dụng đúng loại CSDL cho từng nhu cầu giúp tối ưu cả hiệu năng lẫn linh hoạt; (3) **JSONB sources** trong `messages` cho phép lưu citation có cấu trúc mà không cần bảng phụ.

Chương 4 tiếp theo sẽ trình bày kết quả triển khai thực tế và đánh giá hệ thống theo các tiêu chí đã đặt ra.
