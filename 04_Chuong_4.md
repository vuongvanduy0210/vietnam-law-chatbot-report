# CHƯƠNG 4. TRIỂN KHAI VÀ THỰC NGHIỆM

Chương này trình bày kết quả triển khai thực tế của hệ thống Vietnam Law Chatbot, bao gồm môi trường vận hành, giao diện người dùng trên hai nền tảng Mobile và Web, cùng với quá trình thực nghiệm và đánh giá định lượng hiệu quả của giải pháp Agentic RAG đề xuất. Qua đó, em rút ra những nhận xét về ưu điểm, hạn chế và hướng phát triển tiếp theo của hệ thống.

---

## 4.1. Môi trường triển khai

### 4.1.1. Môi trường phát triển

Hệ thống được phát triển và kiểm thử trên môi trường sau:

*Bảng 4.1. Cấu hình môi trường phát triển*

| Thành phần | Phiên bản / Cấu hình |
|---|---|
| Hệ điều hành | macOS 14 / Ubuntu 22.04 LTS |
| CPU | Apple M-series / Intel Core i7 |
| RAM | 16 GB |
| Python | 3.12.x |
| JDK | 17 (Android) / 21 (backend) |
| Node.js | 20.x LTS |
| IDE | Android Studio Meerkat / VS Code |
| Docker Desktop | 4.x |

### 4.1.2. Kiến trúc triển khai

Hệ thống gồm bốn thành phần chính chạy song song: **Main Service** (port 8000) đảm nhận xử lý API công khai và xác thực người dùng; **RAG Service** (port 8001) phụ trách toàn bộ luồng AI bao gồm Agentic RAG, embedding và ingestion; **ChromaDB** (port 8002) lưu trữ vector; **PostgreSQL** (port 5432) quản lý dữ liệu người dùng và phiên làm việc. Ngoài ra, **MongoDB** được kết nối qua Atlas Cloud hoặc instance local để lưu trữ 528.620 điều khoản pháp luật.

Trong giai đoạn phát triển, ba cơ sở dữ liệu (PostgreSQL, ChromaDB, MongoDB) được container hóa bằng Docker Compose, trong khi hai backend service chạy trực tiếp (native) trên máy host để thuận tiện cho việc debug và hot-reload. Cấu hình Docker Compose cho lớp dữ liệu như sau:

*Bảng 4.2. Cấu hình Docker Compose lớp dữ liệu*

| Container | Image | Port | Volume |
|---|---|---|---|
| postgres | postgres:16-alpine | 5432:5432 | pg-data |
| chromadb | chromadb/chroma:latest | 8002:8000 | chroma-data |
| mongo | mongo:7.0 | 27017:27017 | mongo-data |

Các service backend giao tiếp với nhau qua hai lớp xác thực: JWT Bearer token cho luồng Client → Main Service, và X-API-Key nội bộ cho luồng Main Service → RAG Service, đảm bảo RAG Service không bao giờ tiếp xúc trực tiếp với internet.

### 4.1.3. Biến môi trường và bảo mật

Mỗi service được cấu hình qua file `.env` riêng biệt, không được commit vào source control. Các biến môi trường quan trọng bao gồm: chuỗi GEMINI_API_KEY (hỗ trợ rotation nhiều key), TAVILY_API_KEY, JWT_SECRET_KEY, X_API_KEY_SECRET, và connection string cho từng cơ sở dữ liệu. Cơ chế rotation API key được kích hoạt tự động khi phát hiện lỗi HTTP 429 (rate limit) hoặc 503 (service unavailable) từ Gemini API, đảm bảo tính liên tục của dịch vụ trong giờ cao điểm.

---

## 4.2. Giao diện ứng dụng Mobile

Ứng dụng Mobile được phát triển theo kiến trúc Kotlin Multiplatform (KMP) với Compose Multiplatform, cho phép triển khai đồng thời trên Android và iOS từ một codebase duy nhất. Giao diện tuân theo Material Design 3, được tối ưu cho màn hình điện thoại với kích thước từ 5 đến 6.7 inch. Các màn hình chính gồm có Đăng nhập, Thư viện pháp luật, Chi tiết văn bản, Chat Agentic RAG, AI-Powered Search, Guided Consultation và Quản lý hội thoại.

### 4.2.1. Đăng nhập và xác thực

[IMG:mobile_login.png]
*Hình 4.1. Màn hình đăng nhập ứng dụng Mobile*

Màn hình đăng nhập cung cấp form xác thực với email và mật khẩu, tích hợp kiểm tra hợp lệ theo thời gian thực. Sau khi xác thực thành công, JWT access token và refresh token được lưu trữ mã hóa vào KSafe (sử dụng Android Keystore / iOS Keychain). Ktor HTTP client được cấu hình với plugin `Auth { bearer { refreshTokens } }` để tự động làm mới token hết hạn mà không yêu cầu người dùng đăng nhập lại, đảm bảo trải nghiệm liên tục.

### 4.2.2. Thư viện văn bản pháp luật

[IMG:mobile_library.png]
*Hình 4.2. Màn hình thư viện văn bản pháp luật*

Màn hình Thư viện cho phép người dùng duyệt và tìm kiếm trong kho 46.047 văn bản pháp luật, với các bộ lọc theo chủ đề, năm ban hành và cơ quan ban hành. Danh sách điều khoản được tải theo phân trang (pagination) để tối ưu hiệu năng, với lazy loading tích hợp sẵn trong Compose Multiplatform.

[IMG:mobile_detail_law.png]
*Hình 4.3. Màn hình chi tiết văn bản pháp luật*

Khi chọn một văn bản, người dùng chuyển sang màn hình Chi tiết hiển thị toàn bộ nội dung điều khoản theo cấu trúc phân cấp (chương → điều → khoản → điểm). Nội dung được render với định dạng rich text, hỗ trợ cuộn dài và tìm kiếm trong văn bản, giúp người dùng tra cứu trực tiếp nội dung pháp luật gốc mà không cần rời ứng dụng.

### 4.2.3. Chat Agentic RAG và ThinkingPanel

[IMG:mobile_chat_thinking.png]
*Hình 4.4. Màn hình Chat với ThinkingPanel đang hiển thị các bước xử lý của pipeline*

Đây là tính năng trọng tâm của ứng dụng. Giao diện Chat sử dụng SSE (Server-Sent Events) streaming để hiển thị câu trả lời theo từng token, tạo cảm giác phản hồi thời gian thực với hiệu ứng con trỏ nhấp nháy (TypingBubble). Điểm nổi bật là **ThinkingPanel** — một component hiển thị tiến trình xử lý của pipeline AI theo 5 bước tuần tự: Guardrail, Query Analysis, Agent, Tool Calls, và Verifier. Mỗi bước được animate theo trạng thái (đang xử lý / hoàn thành / bỏ qua), giúp người dùng hiểu hệ thống đang làm gì trong khi chờ câu trả lời.

[IMG:mobile_chat_answer_1.png]
*Hình 4.5. Câu trả lời Agentic RAG — phần đầu với trích dẫn điều khoản cụ thể*

[IMG:mobile_chat_answer_2.png]
*Hình 4.6. Câu trả lời Agentic RAG — phần tiếp theo với phân tích chi tiết*

[IMG:mobile_chat_answer_3.png]
*Hình 4.7. Câu trả lời Agentic RAG — phần cuối với danh sách nguồn tham chiếu*

Sau khi pipeline hoàn tất, câu trả lời được hiển thị dưới dạng Markdown với danh sách nguồn tham chiếu rõ ràng, bao gồm tên văn bản pháp luật, số điều khoản và năm ban hành. Khi hệ thống phát hiện xung đột thời gian giữa hai văn bản cùng điều chỉnh một vấn đề, nguồn cũ được đánh dấu ⛔ và nguồn mới được đánh dấu ✅, giúp người dùng nhận biết ngay quy định nào đang còn hiệu lực.

### 4.2.4. AI-Powered Search (Tìm kiếm theo ngữ nghĩa)

[IMG:mobile_chat_search_ai.png]
*Hình 4.8. Tính năng AI-Powered Search — tìm kiếm văn bản pháp luật theo ngữ nghĩa*

Tính năng AI-Powered Search cho phép người dùng tìm kiếm văn bản pháp luật bằng ngôn ngữ tự nhiên thay vì từ khóa cứng. Truy vấn người dùng được embedding bằng mô hình `vietnamese-bi-encoder` (768 chiều), sau đó ChromaDB thực hiện truy vấn cosine similarity để tìm các điều khoản ngữ nghĩa gần nhất. Kết quả trả về được sắp xếp theo độ liên quan, kèm tên văn bản, số điều khoản và đoạn trích ngữ cảnh, giúp người dùng định vị nhanh văn bản pháp lý cần tham chiếu mà không cần biết chính xác tên văn bản hay số điều.

### 4.2.5. Guided Consultation (Tư vấn có hướng dẫn)

[IMG:mobile_guided_step1.png]
*Hình 4.9. Guided Consultation — bước 1: câu hỏi gốc và gợi ý câu hỏi làm rõ ngữ cảnh*

Tính năng Guided Consultation được thiết kế cho các câu hỏi pháp lý thiếu ngữ cảnh. Ở bước đầu tiên, người dùng nhập câu hỏi và hệ thống hiển thị đồng thời các gợi ý câu hỏi bổ trợ (multiple-choice) nhằm làm rõ hoàn cảnh cụ thể — ví dụ: loại hợp đồng lao động, lĩnh vực doanh nghiệp, vùng địa lý.

[IMG:mobile_guided_step2.png]
*Hình 4.10. Guided Consultation — bước 2: câu hỏi thu thập thông tin chi tiết*

Bước hai hệ thống thu thập thêm thông tin chi tiết từ người dùng thông qua các câu hỏi trắc nghiệm có cấu trúc, nhằm xác định chính xác khung pháp lý áp dụng cho tình huống. Các câu hỏi được Planning Node tạo ra theo cơ chế deterministic (không dùng LLM) bằng cách ghép template từ kết quả phân tích bước 1, tiết kiệm đáng kể chi phí token và giảm latency so với phương pháp planning bằng LLM.

[IMG:mobile_guided_step3.png]
*Hình 4.11. Guided Consultation — bước 3: hệ thống đang suy nghĩ và tổng hợp*

Sau khi thu thập đủ ngữ cảnh, hệ thống chạy Guided Graph (START → planning → agent → verifier → END) để tổng hợp câu trả lời. Trạng thái "đang suy nghĩ" được hiển thị với animation tương tự ThinkingPanel, phản ánh quá trình Agent gọi tool retrieve và Verifier kiểm chứng kết quả.

[IMG:mobile_guided_step4.png]
*Hình 4.12. Guided Consultation — bước 4: kết quả tư vấn chuyên sâu theo ngữ cảnh*

Bước cuối trả về câu trả lời chuyên sâu được tùy chỉnh hoàn toàn theo tình huống cụ thể của người dùng, kèm trích dẫn điều khoản và tên văn bản pháp lý liên quan. Nhờ thu thập đủ ngữ cảnh trước khi truy vấn, kết quả chính xác hơn so với câu hỏi mở thông thường, đặc biệt với các tình huống pháp lý có nhiều ngoại lệ theo từng đối tượng hoặc ngành nghề.

### 4.2.6. Quản lý hội thoại

[IMG:mobile_conversations.png]
*Hình 4.13. Màn hình danh sách hội thoại*

Ứng dụng lưu trữ toàn bộ lịch sử hội thoại theo tài khoản người dùng. Tiêu đề mỗi cuộc hội thoại được tự động tạo bởi LLM từ câu hỏi đầu tiên. Người dùng có thể ghim (pin) các cuộc hội thoại quan trọng, lưu trữ (archive) hoặc xóa các cuộc hội thoại không cần thiết.

---

## 4.3. Giao diện Admin Web

Admin Web được xây dựng bằng Next.js 16.1.6 với App Router, React 19.2.3, TailwindCSS 4 và thư viện UI shadcn/ui 3.8. Đây là giao diện quản trị nội bộ dành cho người quản lý hệ thống, cung cấp các chức năng theo dõi và vận hành nội dung pháp luật trong hệ thống.

### 4.3.1. Đăng nhập quản trị

[IMG:admin_login.png]
*Hình 4.14. Trang đăng nhập Admin Web*

Trang đăng nhập admin yêu cầu tài khoản có quyền `role=admin` được cấp từ hệ thống. JWT token sau khi đăng nhập thành công được lưu trong httpOnly cookie với thời hạn phiên làm việc theo cấu hình server.

### 4.3.2. Dashboard tổng quan

[IMG:admin_dashboard.png]
*Hình 4.15. Dashboard tổng quan với BarChart và các card thống kê*

Dashboard hiển thị tổng quan trạng thái hệ thống theo thời gian thực thông qua kết nối WebSocket. Giao diện gồm các card thống kê nhanh (tổng số văn bản, tổng số điều khoản, số vector trong ChromaDB) và biểu đồ cột (BarChart, thư viện Recharts) thể hiện số lượng tài liệu được tải lên theo từng tháng. Khi có tài liệu mới hoàn thành xử lý, các chỉ số được cập nhật tức thì mà không cần tải lại trang.

### 4.3.3. Quản lý tài liệu

[IMG:admin_document_detail.png]
*Hình 4.16. Chi tiết tài liệu — danh sách điều khoản đã được trích xuất*

Trang Documents hiển thị danh sách tất cả tác vụ xử lý tài liệu (DocumentTask), bao gồm các thông tin: tên file PDF, mã văn bản pháp luật (law_id) được trích xuất tự động, số điều khoản đã parse, trạng thái (pending / processing / completed / failed), và thời gian tạo. Khi xem chi tiết từng tác vụ, admin có thể kiểm tra toàn bộ danh sách điều khoản đã được trích xuất — bao gồm số điều, tiêu đề và nội dung — để đối chiếu với văn bản PDF gốc và phát hiện các trường hợp parse sai hoặc thiếu.

### 4.3.4. Upload và theo dõi tiến trình

[IMG:admin_upload_processing.png]
*Hình 4.17. Giao diện Upload PDF đang trong quá trình xử lý*

Trang Upload hỗ trợ kéo-thả (drag-and-drop) file PDF hoặc chọn file thông thường. Sau khi upload, hệ thống khởi chạy pipeline ingestion với các bước: tải lên Cloudinary (lưu trữ file gốc), parse nội dung bằng Gemini Vision API, lưu điều khoản vào MongoDB, embedding và lưu vector vào ChromaDB. Tiến trình được phản hồi thời gian thực qua WebSocket với thanh tiến trình (progress bar) và thông báo bước hiện tại.

Một tính năng đáng chú ý là khả năng **phục hồi sau reload trang** (resume): task_id được lưu vào localStorage, khi người dùng tải lại trình duyệt, hệ thống tự động tra trạng thái qua `GET /documents/tasks/{id}` và khôi phục thanh tiến trình đúng giai đoạn. Điều này ngăn tình trạng mất thông tin tiến trình khi mạng chập chờn hoặc trình duyệt bị đóng.

[IMG:admin_upload_done.png]
*Hình 4.18. Trạng thái hoàn thành sau khi xử lý tài liệu thành công*

---

## 4.4. Đánh giá hệ thống

### 4.4.1. Thiết kế thực nghiệm

Để đánh giá hiệu quả của giải pháp Agentic RAG đề xuất, em thiết kế thực nghiệm tập trung vào hai mục tiêu: (1) đánh giá chất lượng câu trả lời trên bộ dữ liệu kiểm thử đa dạng theo các chỉ số định lượng, và (2) đo lường hiệu năng pipeline để xác định tính khả dụng trong điều kiện thực tế.

**Bộ dữ liệu kiểm thử**

Em xây dựng hai tập câu hỏi độc lập với tổng cộng 60 câu, phủ rộng các lĩnh vực pháp luật thực tế bao gồm giao thông đường bộ, lao động, doanh nghiệp, đất đai & nhà ở và hình sự & dân sự:

*Bảng 4.3. Cấu trúc bộ dữ liệu kiểm thử*

| Tập | Loại | Số câu | Mô tả |
|---|---|---|---|
| **N1** | Factual | 30 | Câu hỏi có đáp án xác định (số liệu, điều khoản cụ thể). Đánh giá tự động bằng so khớp kết quả; trong đó 3 câu chuyên biệt kiểm tra Temporal Conflict (NĐ 100/2019 vs NĐ 168/2024) |
| **N2** | Open/Reasoning | 30 | Câu hỏi mở, tình huống thực tế, cần tổng hợp nhiều nguồn. Đánh giá bằng LLM-judge theo thang 1-5 |

Câu hỏi tập N1 được tham chiếu với các văn bản pháp luật cụ thể để có thể so khớp tự động về nội dung trả lời, nguồn trích dẫn và khả năng nhận diện xung đột giữa văn bản cũ - mới. Câu hỏi tập N2 được sử dụng để đánh giá khả năng suy luận, tổng hợp và diễn giải tư vấn của hệ thống trong các tình huống pháp lý mở.

### 4.4.2. Các chỉ số đánh giá

Em sử dụng năm chỉ số đánh giá, được phân nhóm theo mục tiêu đo lường:

*Bảng 4.5. Bộ chỉ số đánh giá hệ thống*

| Chỉ số | Áp dụng | Mô tả | Phương pháp đo |
|---|---|---|---|
| **Accuracy@1** | N1 | Tỷ lệ câu trả lời đầu tiên chứa đúng thông tin factual kỳ vọng | So khớp tự động với bộ từ khóa kỳ vọng |
| **Answer Quality** | N2 | Chất lượng tổng thể câu trả lời (độ đầy đủ, chính xác, có trích dẫn) | LLM-judge (1–5) |
| **Citation Accuracy** | N1 | Tỷ lệ nguồn được trích dẫn khớp với văn bản pháp luật chứa đáp án | So khớp tự động |
| **Temporal Conflict OK** | Subset 3 câu N1 | Tỷ lệ nhận diện đúng văn bản hiện hành khi tồn tại luật cũ và luật mới | So khớp tự động |

Ngoài các chỉ số về chất lượng, phần thực nghiệm cũng đo độ trễ phản hồi, tính từ thời điểm gửi câu hỏi đến khi quá trình trả lời hoàn tất, theo phân vị P50 và P95 trên 60 lượt truy vấn. Chỉ số P50 phản ánh độ trễ trung vị, còn P95 cho biết thời gian phản hồi trong nhóm câu hỏi chậm hơn, qua đó giúp đánh giá tính khả dụng của hệ thống trong điều kiện thực tế.

### 4.4.3. Kết quả thực nghiệm

Thực nghiệm được tiến hành trên bộ 60 câu hỏi (30 N1 + 30 N2) chạy tự động qua API chatbot. Toàn bộ 60 câu hoàn thành không có lỗi. Điểm N1 được chấm theo phương pháp so khớp từ khóa tự động: mỗi câu hỏi được gán tập từ khóa factual trích từ văn bản pháp luật gốc, câu trả lời được tính đúng khi chứa đúng thông tin kỳ vọng. Điểm N2 được chấm bằng LLM-judge theo thang 1-5 với tiêu chí: 5 = đầy đủ, chính xác, có trích dẫn điều khoản; 4 = đúng hướng, thiếu vài điểm phụ; 3 = đúng phần lớn nhưng thiếu thông tin quan trọng; 2 = lẫn thông tin đúng và sai; 1 = sai hoàn toàn.

*Bảng 4.6. Kết quả đánh giá hệ thống Agentic RAG*

| Chỉ số | Kết quả | Ghi chú |
|---|---|---|
| **Accuracy@1** (N1, 30 câu) | **90,0%** (27/30) | 3 câu sai do thiếu số liệu điều khoản cụ thể trong câu trả lời |
| **Citation Accuracy** (N1) | **86,7%** (26/30) | Tỷ lệ nguồn trích dẫn đúng đạt mức cao; các lỗi còn lại chủ yếu xuất hiện ở một số câu có nhiều văn bản liên quan hoặc truy hồi nhầm văn bản gần nghĩa |
| **Temporal Conflict OK** (3 câu ★) | **3/3 (100%)** | Hệ thống xác định đúng NĐ 168/2024 thay thế NĐ 100/2019 |
| **Answer Quality** (N2, LLM-judge) | **4,07/5,0** | Phân bố: 5★×6, 4★×20, 3★×4, 2★×0, 1★×0 |
| **Latency P50** (full response) | **65,16s** | Bao gồm toàn bộ pipeline: Guardrail → Query Analysis → Agent → Verifier |
| **Latency P95** (full response) | **96,46s** | Trường hợp câu hỏi phức tạp, Agent thực hiện nhiều vòng lặp ReAct |

**Nhận xét tổng hợp**

Kết quả thực nghiệm cho thấy Agentic RAG đạt chất lượng câu trả lời tốt với Accuracy@1 = 90,0%, Citation Accuracy = 86,7% và Answer Quality = 4,07/5,0. Các kết quả này cho thấy hệ thống không chỉ trả lời đúng nội dung factual trong phần lớn trường hợp, mà còn duy trì được nguồn trích dẫn tương đối đáng tin cậy và chất lượng tư vấn tốt trên nhóm câu hỏi mở.

*Thứ nhất*, **Temporal Conflict Detection đạt 100% (3/3)**. Đây là tính năng đặc thù của hệ thống, không có ở các chatbot RAG thông thường. Trong cả ba câu hỏi kiểm tra xung đột thời gian giữa NĐ 100/2019 và NĐ 168/2024, hệ thống xác định đúng văn bản đang có hiệu lực, trình bày so sánh rõ ràng và không trích dẫn sai văn bản đã hết hiệu lực. Kết quả này chứng minh logic Temporal Conflict dựa trên năm trong số hiệu văn bản, loại văn bản và metadata chủ đề hoạt động đúng trong các tình huống kiểm thử.

*Thứ hai*, **Citation Accuracy đạt 86,7% (26/30)**, cho thấy cơ chế truy hồi, xếp hạng lại và đóng gói nguồn luật đã hoạt động tương đối ổn định. Một số lỗi còn lại chủ yếu xuất hiện ở các câu hỏi có nhiều văn bản liên quan gần nghĩa hoặc khi đoạn truy hồi chứa thông tin đúng nhưng chưa khớp hoàn toàn với nguồn kỳ vọng. Điều này cho thấy hệ thống đã cải thiện đáng kể khả năng cung cấp căn cứ pháp lý, tuy nhiên vẫn cần tiếp tục tối ưu dữ liệu vector và chiến lược reranking để giảm các trường hợp trích dẫn nhầm văn bản gần chủ đề.

*Về Answer Quality (N2)*, điểm trung bình 4,07/5,0 phản ánh hệ thống trả lời tốt ở phần lớn câu hỏi tình huống mở. Các câu trả lời thường có cấu trúc rõ ràng, nêu được căn cứ pháp lý và đưa ra hướng tư vấn phù hợp với bối cảnh người dùng. Những điểm còn hạn chế chủ yếu nằm ở các câu hỏi yêu cầu phân biệt nhiều ngoại lệ hoặc cần diễn giải sâu về trình tự xử lý, khi câu trả lời vẫn có thể thiếu một số chi tiết phụ.

*Về latency*, P50 = 65,16s và P95 = 96,46s là thời gian phản hồi còn cao so với một chatbot thông thường. Nguyên nhân chủ yếu đến từ việc mỗi câu hỏi phải đi qua nhiều bước xử lý tuần tự như kiểm tra đầu vào, phân tích truy vấn, truy hồi dữ liệu, gọi công cụ, kiểm chứng và sinh câu trả lời cuối cùng. Trong bối cảnh tư vấn pháp luật, nơi độ chính xác và căn cứ trích dẫn quan trọng hơn tốc độ phản hồi tức thời, đây là mức đánh đổi có thể chấp nhận được ở giai đoạn thử nghiệm, nhưng vẫn cần tối ưu trong phiên bản triển khai thực tế.

### 4.4.4. Phân tích case study

Để minh họa cụ thể hiệu quả của hệ thống, em phân tích một case study điển hình thể hiện tính năng Temporal Conflict Resolution.

**Case study: Phát hiện xung đột mức phạt vi phạm nồng độ cồn**

*Câu hỏi*: "Hiện nay lái xe ô tô có nồng độ cồn 0.35mg/L khí thở bị phạt bao nhiêu?"

Đây là câu hỏi có xung đột thời gian điển hình: hệ thống CSDL chứa cả NĐ 100/2019/NĐ-CP (quy định mức phạt cũ 30–40 triệu đồng, tước GPLX 16–18 tháng) và NĐ 168/2024/NĐ-CP (thay thế một phần NĐ 100/2019 từ ngày 01/01/2025, quy định mức phạt 30–40 triệu đồng, tước GPLX 22–24 tháng với mức vi phạm tương đương).

Nếu dùng phương pháp RAG không có Temporal Conflict Detection, việc retrieve chunk có thể trả về thông tin từ văn bản cũ hoặc mới mà không phân biệt, dẫn đến câu trả lời mơ hồ hoặc sai. Agentic RAG xử lý theo luồng:

1. **Query Analysis** xác định đây là câu hỏi về mức xử phạt giao thông, cần tìm kiếm theo từ khóa "nồng độ cồn" + "xe ô tô" + kết hợp metadata `year`
2. **Tool retrieve_internal_law** thực hiện Two-Stage Retrieval, Temporal Conflict Detection phát hiện hai văn bản có cùng `metadata.topics` và `metadata.keywords` nhưng khác `metadata.year` → đánh dấu cặp xung đột
3. **Agent** nhận observation có cặp xung đột, lấy cả hai nguồn vào context kèm annotation
4. **Verifier** kiểm tra và xác nhận câu trả lời chỉ trích dẫn NĐ 168/2024 là văn bản đang có hiệu lực, đồng thời giải thích rằng NĐ 100/2019 đã được thay thế

Kết quả: câu trả lời chính xác, minh bạch, hiển thị cả hai nguồn để người dùng tham khảo.

### 4.4.5. Đánh giá hiệu năng hệ thống

*Bảng 4.7. Chỉ số hiệu năng hệ thống*

| Chỉ số | Giá trị đo được |
|---|---|
| ChromaDB query top-60 (cosine, HNSW) | < 200ms |
| Two-Stage Reranking (top-60 → top-20) | < 500ms |
| Agentic RAG full response (P50) | **65,16 giây** (đo thực nghiệm, 60 câu) |
| Agentic RAG full response (P95) | **96,46 giây** (đo thực nghiệm) |
| Ingestion pipeline (PDF 50 điều, ~30 trang) | 3–5 phút |
| Embedding batch 100 chunks | < 10 giây |

Về mặt tài nguyên, RAG Service tiêu thụ khoảng 500–800 MB RAM trong điều kiện bình thường, tăng lên 1–1.5 GB khi embedding batch lớn. ChromaDB với 690.360 vector chiều 768 chiếm khoảng 3.5 GB lưu trữ trên đĩa. Các thông số này nằm trong giới hạn hoạt động bình thường của một máy chủ phổ thông với 8 GB RAM.

---

## 4.5. Tổng kết chương 4

Chương 4 đã trình bày toàn diện kết quả triển khai hệ thống Vietnam Law Chatbot trên cả ba phương diện: môi trường vận hành thực tế, giao diện người dùng trực quan trên hai nền tảng Mobile (KMP) và Web Admin (Next.js), cùng với kết quả thực nghiệm định lượng đánh giá hiệu quả phương pháp Agentic RAG đề xuất.

Kết quả thực nghiệm cho thấy việc bổ sung các cơ chế Guardrail, Two-Stage Reranking, ReAct Agent Loop và Verifier giúp cải thiện chất lượng câu trả lời, đặc biệt trong việc hạn chế hiện tượng sinh thông tin không có căn cứ và xử lý xung đột pháp luật theo thời gian. Hệ thống đạt Accuracy@1 = 90,0%, Citation Accuracy = 86,7% và Answer Quality = 4,07/5,0, cho thấy khả năng kết hợp giữa truy hồi nguồn luật và sinh câu trả lời tư vấn tương đối ổn định. Hạn chế chính của quy trình hiện tại là độ trễ còn cao (P50 = 65,16 giây, P95 = 96,46 giây), tuy nhiên mức đánh đổi này phù hợp hơn với bối cảnh tư vấn pháp lý, nơi độ chính xác được ưu tiên hơn tốc độ.
