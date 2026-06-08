# Brief cho Canva AI tạo slide báo cáo đồ án tốt nghiệp

Tài liệu này dùng để đưa cho AI của Canva đọc và tạo slide báo cáo bảo vệ đồ án tốt nghiệp. Mục tiêu là tạo một bộ slide hiện đại, dễ trình bày trong 12-15 phút, tập trung vào bài toán, giải pháp, kiến trúc hệ thống, các tính năng chính, thuật toán trọng tâm và kết quả đánh giá.

Nguồn nội dung bắt buộc cần bám sát:

**File báo cáo chính:** `Vương Văn Duy_CT060411_NGHIÊN CỨU PHÁT TRIỂN TRỢ LÝ ẢO PHÁP LUẬT CHO CHUYỂN ĐỔI SỐ.docx`

**Bản PDF tương ứng để đối chiếu khi gửi cho Canva/giảng viên:** `Vương Văn Duy_CT060411_NGHIÊN CỨU PHÁT TRIỂN TRỢ LÝ ẢO PHÁP LUẬT CHO CHUYỂN ĐỔI SỐ.pdf`

Khi tạo slide, hãy coi file báo cáo chính là nguồn nội dung duy nhất đáng tin cậy. Slide chỉ được rút gọn, trực quan hóa và sắp xếp lại thông tin đã có trong báo cáo; không tự thêm tính năng, số liệu, thuật toán hoặc kết luận ngoài báo cáo. Nếu cần làm gọn, hãy ưu tiên giữ đúng luận điểm và thuật ngữ của báo cáo hơn là viết lại theo cách quá sáng tạo.

---

## 1. Vai trò của Canva AI

Bạn là một AI thiết kế slide chuyên nghiệp. Hãy tạo một bộ slide bảo vệ đồ án tốt nghiệp bằng tiếng Việt, có phong cách hiện đại, sáng, rõ ràng, phù hợp với báo cáo kỹ thuật về hệ thống AI/RAG. Slide cần dễ đọc khi trình chiếu, không quá nhiều chữ, ưu tiên sơ đồ, timeline, card thông tin, biểu đồ luồng và các khối ý chính.

Bộ slide dùng cho sinh viên bảo vệ trước hội đồng trong khoảng 12-15 phút. Vì vậy, số lượng slide nên nằm trong khoảng 15-18 slide, tối đa 20 slide. Không tạo slide quá dày nội dung. Mỗi slide chỉ nên có một thông điệp chính.

Yêu cầu quan trọng về độ chính xác nội dung:

- Bám sát cấu trúc và nội dung trong file báo cáo chính đã gửi cho giảng viên phản biện.
- Không tự tạo thêm số liệu đánh giá, tên model, tên tính năng hoặc kết quả mới.
- Không đổi bản chất phương pháp từ **Agentic RAG có kiểm chứng** sang chatbot LLM thông thường.
- Không đảo sai quan hệ giữa các thành phần: Mobile App/Web Admin gọi Main Service; Main Service điều phối sang RAG Service; RAG Service xử lý AI/RAG và truy hồi dữ liệu.
- Không mô tả kho vector như phần phát sinh sau cùng của admin upload. Theo báo cáo, kho vector pháp luật ban đầu là nền tảng được xây dựng trước để phục vụ Agentic RAG; pipeline upload PDF của Admin là cơ chế cập nhật tri thức về sau.

---

## 1A. Mapping nội dung slide theo file báo cáo chính

Canva AI cần bám theo tuyến nội dung sau trong báo cáo:

### Lời nói đầu và Chương 1

Dùng để lấy phần bối cảnh, lý do chọn bài toán và cơ sở lý thuyết. Các ý cần giữ:

- Nhu cầu ứng dụng chatbot trong tư vấn pháp luật tại Việt Nam.
- Hạn chế của chatbot dựa trên tập luật.
- Lợi ích và rủi ro khi dùng LLMs trong bài toán pháp luật.
- Vai trò của RAG, AI Agent, Tool, Planning và cơ chế tự kiểm chứng.
- Các công nghệ nền tảng: Python, LangGraph, FastAPI, Next.js, Kotlin Multiplatform, PostgreSQL, MongoDB và ChromaDB.

### Chương 2 - Phương pháp xây dựng hệ thống

Đây là chương quan trọng nhất để xây dựng phần nội dung kỹ thuật của slide. Thứ tự ý trong slide nên bám theo logic chương 2 hiện tại:

1. **2.1. Kiến trúc tổng quan hệ thống Vietnam Law Chatbot**: Microservices, Main Service, RAG Service, kênh giao tiếp giữa các thành phần.
2. **2.2. Xây dựng kho dữ liệu vector pháp luật ban đầu**: cấu trúc dữ liệu pháp luật đầu vào, metadata, chunking, embedding và lưu vào ChromaDB. Đây là nền tảng cho Agentic RAG.
3. **2.3. Xác định tính chất AI Agent**: vai trò, phạm vi, nguồn dữ liệu và tập hành động của Agent.
4. **2.4. Nguồn tri thức và cơ chế truy hồi của Agent**: tra cứu kho pháp luật nội bộ và tìm kiếm nguồn cập nhật bên ngoài.
5. **2.5. Luồng Agentic RAG có kiểm chứng**: trạng thái xử lý, đồ thị tổng quan, Guardrail, Query Analysis, Agent thu thập bằng chứng, Verifier kiểm chứng.
6. **2.6. Tối ưu pipeline RAG - truy xuất hai giai đoạn**: tìm kiếm vector, reranking, blended score, ưu tiên văn bản mới, giải quyết mâu thuẫn pháp lý theo thời gian, ngưỡng tin cậy.
7. **2.7. Luồng Tư vấn có Hướng dẫn**: hệ thống hỏi làm rõ ngữ cảnh trước khi trả lời.
8. **2.8. Quy trình cập nhật tri thức từ văn bản pháp luật**: admin upload PDF, trích xuất, cấu trúc hóa, lưu MongoDB, cập nhật ChromaDB và giữ nhất quán dữ liệu.
9. **2.10. Phương pháp xây dựng lớp ứng dụng đa nền tảng**: mobile app, MVI, trải nghiệm chat, admin web, WebSocket cho tiến trình xử lý tài liệu.

### Chương 3 - Phân tích và thiết kế hệ thống

Dùng để lấy các nội dung về yêu cầu, use case, sequence diagram, thiết kế cơ sở dữ liệu và API. Slide không cần đưa nhiều bảng đặc tả use case, nhưng cần thể hiện được:

- Hai nhóm tác nhân chính: người dùng cuối và quản trị viên.
- Các ca sử dụng quan trọng: xác thực, quản lý hội thoại, gửi tin nhắn AI, tư vấn có hướng dẫn, tìm kiếm AI, upload PDF, theo dõi tiến trình, dashboard.
- Thiết kế dữ liệu gồm PostgreSQL, MongoDB và ChromaDB.
- Thiết kế API gồm Auth, Chat, Laws, Documents, Guided Consultation và Dashboard.

### Chương 4 - Triển khai và thực nghiệm

Dùng để lấy phần demo giao diện và đánh giá hệ thống:

- Môi trường triển khai và kiến trúc vận hành.
- Giao diện Mobile: đăng nhập, thư viện văn bản pháp luật, chat Agentic RAG, AI-Powered Search, Guided Consultation, quản lý hội thoại.
- Giao diện Admin Web: đăng nhập, dashboard, quản lý tài liệu, tải lên và theo dõi tiến trình.
- Đánh giá hệ thống với bộ 60 câu hỏi.
- Kết quả: Accuracy@1, Citation Accuracy, Temporal Conflict OK, Answer Quality, Latency P50/P95.

### Kết luận

Dùng cho slide kết luận cuối:

- Hệ thống đã xây dựng được trợ lý ảo pháp luật theo hướng Agentic RAG.
- Câu trả lời có căn cứ, có nguồn và có bước kiểm chứng.
- Hệ thống có sản phẩm demo thực tế trên Mobile App và Web Admin.
- Hạn chế chính nằm ở độ trễ, độ bao phủ dữ liệu và chất lượng nguồn trích dẫn nội bộ.

---

## 1B. Trọng tâm nội dung bắt buộc của bộ slide

Do thời gian trình bày chỉ khoảng 12-15 phút, bộ slide không nên cố gắng tóm tắt toàn bộ báo cáo theo từng chương. Nội dung chính cần tập trung vào **Chương 2 - Phương pháp xây dựng hệ thống**, vì đây là phần thể hiện đóng góp kỹ thuật và phương pháp triển khai của đồ án.

Tỷ trọng nội dung đề xuất:

- Khoảng 65-70% thời lượng: Chương 2, gồm kiến trúc, kho dữ liệu vector, Agentic RAG, cơ chế truy hồi, guided consultation và cập nhật tri thức.
- Khoảng 10-15% thời lượng: Chương 1, dùng để mở bài và giải thích vì sao bài toán cần Agentic RAG.
- Khoảng 10% thời lượng: Chương 3, dùng để nhắc nhanh thiết kế hệ thống, actor, use case/API/CSDL ở mức tổng quan.
- Khoảng 10-15% thời lượng: Chương 4, dùng cho demo giao diện và kết quả đánh giá.

Bốn cụm nội dung bắt buộc phải nổi bật trong slide:

### Cụm 1 - Luồng chat chính với LangGraph

Đây là phần quan trọng nhất. Cần trình bày rõ hệ thống không gửi câu hỏi trực tiếp cho LLMs, mà tổ chức thành graph xử lý có kiểm soát:

```text
Người dùng
→ Main Service
→ RAG Service
→ Guardrail
→ Query Analysis
→ Agent ↔ Tools
→ Verifier
→ Câu trả lời có nguồn
```

Các ý cần nhấn mạnh:

- Main Service xác thực JWT, quản lý hội thoại và lưu tin nhắn.
- RAG Service chạy LangGraph cho luồng Agentic RAG.
- Guardrail kiểm soát câu hỏi đầu vào.
- Query Analysis tạo truy vấn tối ưu cho nội bộ và nguồn cập nhật.
- Agent thu thập bằng chứng thông qua tools.
- Verifier kiểm chứng câu trả lời trước khi trả về.
- Có thể nhắc ngắn việc giao diện hiển thị tiến trình xử lý, nhưng không cần tách riêng thành một nội dung chính.

### Cụm 2 - Xây dựng cơ sở dữ liệu ban đầu cho RAG và cơ chế truy hồi

Phần này phải được đặt trước hoặc ngay sát phần Agentic RAG, vì kho vector ban đầu là nền tảng để Agent truy hồi căn cứ pháp luật.

Nội dung cần có:

```text
Dữ liệu pháp luật đầu vào
→ Chuẩn hóa article/metadata
→ Chunking văn bản pháp luật
→ Tạo embedding
→ Lưu vào ChromaDB
→ Truy hồi bằng vector search + reranking
```

Các ý cần nhấn mạnh:

- Dữ liệu pháp luật được tổ chức theo văn bản và điều luật.
- Metadata giúp giữ liên kết về văn bản gốc, năm ban hành, chủ đề, từ khóa.
- Chunking giúp điều luật dài có thể được truy hồi chính xác hơn.
- Embedding giúp tìm kiếm theo ngữ nghĩa, không chỉ tìm từ khóa.
- ChromaDB collection `vietnamese_law` là kho vector phục vụ Agent.
- Cơ chế truy hồi gồm vector search, reranking, blended score, ưu tiên văn bản mới và xử lý xung đột pháp lý theo thời gian.

### Cụm 3 - Luồng upload văn bản mới của Admin

Phần này thể hiện hệ thống có khả năng cập nhật tri thức, không phải chỉ dùng một kho dữ liệu tĩnh.

Nội dung cần có:

```text
Admin upload PDF
→ Tạo task xử lý
→ Trích xuất và cấu trúc hóa nội dung
→ Lưu MongoDB
→ Chunking + embedding
→ Cập nhật ChromaDB
→ Theo dõi tiến trình qua WebSocket
```

Các ý cần nhấn mạnh:

- Admin nhận task để theo dõi tiến trình.
- MongoDB lưu nội dung điều luật dạng văn bản.
- ChromaDB lưu vector chunks để phục vụ truy hồi.
- WebSocket dùng để cập nhật tiến trình xử lý tài liệu.
- Cơ chế hoàn tác/giữ nhất quán dữ liệu giúp tránh tình trạng MongoDB và ChromaDB lệch nhau khi lỗi xảy ra.

### Cụm 4 - Luồng tư vấn có hướng dẫn

Phần này thể hiện hệ thống không chỉ trả lời câu hỏi trực tiếp, mà còn biết hỏi lại khi câu hỏi thiếu ngữ cảnh.

Nội dung cần có:

```text
Câu hỏi ban đầu
→ Sinh câu hỏi làm rõ
→ Người dùng bổ sung thông tin
→ Trả lời theo ngữ cảnh đã làm rõ
→ Streaming kết quả
```

Các ý cần nhấn mạnh:

- Pháp luật phụ thuộc mạnh vào ngữ cảnh.
- Nếu câu hỏi thiếu dữ kiện, hệ thống không nên suy đoán.
- Guided Consultation giúp thu thập thêm thông tin trước khi tư vấn.
- Thiết kế này phù hợp với các tình huống pháp lý thực tế, nơi cùng một câu hỏi có thể có câu trả lời khác nhau theo đối tượng, hành vi, thời điểm hoặc điều kiện cụ thể.

Các nội dung khác chỉ nên trình bày ngắn:

- Công nghệ sử dụng: chỉ cần một slide tech stack.
- Use case/thiết kế API/CSDL chương 3: chỉ cần dùng làm nền cho slide kiến trúc hoặc tính năng.
- Demo chương 4: chỉ chọn một slide ghép mockup mobile/admin.
- Đánh giá: một slide metric là đủ.

## 2. Thông tin đề tài

Tên đề tài:

**Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số**

Sinh viên thực hiện:

**Vương Văn Duy**

Loại báo cáo:

**Báo cáo đồ án tốt nghiệp đại học**

Lĩnh vực:

- Trợ lý ảo pháp luật
- Chatbot AI
- Agentic RAG
- Hệ thống hỏi đáp có căn cứ
- Ứng dụng mobile và web admin

---

## 3. Bối cảnh và lý do chọn bài toán

Hệ thống được xây dựng từ nhu cầu thực tế trong việc tra cứu và tiếp cận thông tin pháp luật tại Việt Nam. Văn bản pháp luật có số lượng lớn, cấu trúc phức tạp, nhiều điều khoản, nhiều văn bản sửa đổi và thay thế. Người dùng phổ thông thường gặp khó khăn khi tự xác định văn bản nào đang có hiệu lực, điều khoản nào liên quan trực tiếp tới tình huống của mình.

Trong bối cảnh chuyển đổi số, một trợ lý ảo pháp luật có thể hỗ trợ người dân, sinh viên, cán bộ hoặc người không chuyên tiếp cận thông tin pháp luật nhanh hơn. Tuy nhiên, lĩnh vực pháp luật có yêu cầu độ chính xác cao. Nếu chatbot trả lời sai điều khoản, sai mức phạt hoặc trích dẫn văn bản đã hết hiệu lực, câu trả lời có thể gây hiểu nhầm nghiêm trọng.

Vì vậy, vấn đề chính của đề tài không chỉ là xây dựng một chatbot biết nói chuyện tự nhiên. Trọng tâm của đề tài là xây dựng một hệ thống có khả năng:

- Truy hồi căn cứ pháp luật từ kho dữ liệu nội bộ.
- Kiểm tra thông tin với nguồn cập nhật bên ngoài.
- Hạn chế hiện tượng hallucination của LLMs.
- Ưu tiên văn bản pháp luật mới, tránh dùng nhầm quy định đã hết hiệu lực.
- Hiển thị câu trả lời có nguồn tham chiếu rõ ràng.
- Cho phép quản trị viên cập nhật văn bản mới vào kho tri thức.

Thông điệp chính cho phần mở đầu:

**Trong lĩnh vực pháp luật, một câu trả lời đúng không chỉ cần tự nhiên, mà phải có căn cứ, có nguồn và có cơ chế kiểm chứng.**

---

## 4. Mục tiêu của hệ thống

Hệ thống hướng tới bốn mục tiêu chính:

1. Xây dựng trợ lý ảo tư vấn pháp luật tiếng Việt, cho phép người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên.
2. Ứng dụng Agentic RAG để kết hợp LLMs với truy hồi tri thức, công cụ tìm kiếm và bước kiểm chứng câu trả lời.
3. Xây dựng kho dữ liệu pháp luật có khả năng tìm kiếm ngữ nghĩa bằng ChromaDB, embedding và reranking.
4. Triển khai sản phẩm hoàn chỉnh gồm mobile app cho người dùng cuối và web admin cho quản trị viên cập nhật dữ liệu.

---

## 5. Phương án giải quyết

Phương án của đề tài là xây dựng hệ thống theo kiến trúc Agentic RAG.

Không nên trình bày hệ thống như một chatbot LLM thông thường. Điểm quan trọng là LLMs không được dùng như nguồn tri thức độc lập. LLMs được đặt trong một quy trình có kiểm soát gồm các bước:

1. Kiểm tra câu hỏi đầu vào.
2. Phân tích và tối ưu truy vấn.
3. Truy hồi dữ liệu pháp luật từ kho nội bộ.
4. Tra cứu nguồn hiện hành bên ngoài khi cần.
5. Tổng hợp câu trả lời.
6. Kiểm chứng lại câu trả lời trước khi trả về người dùng.

Sơ đồ nên thể hiện rõ:

```text
User Question
→ Guardrail
→ Query Analysis
→ Agent
→ Tools: Internal Law Retrieval + Web Search
→ Verifier
→ Final Answer with Sources
```

Thông điệp chính:

**Agentic RAG giúp hệ thống chuyển từ "LLMs tự trả lời" sang "LLMs lập luận trên bằng chứng đã truy hồi và đã được kiểm chứng".**

---

## 6. Công nghệ sử dụng

Chỉ trình bày công nghệ ở mức vừa đủ, không biến slide thành danh sách dài. Nên chia thành 5 nhóm:

### Backend

- Python
- FastAPI
- LangGraph
- REST API
- WebSocket

Vai trò: xử lý xác thực, hội thoại, upload tài liệu, điều phối RAG và trả kết quả về client.

### AI/RAG

- LLMs
- Agentic RAG
- LangGraph StateGraph
- Tool calling
- Guardrail
- Verifier
- Embedding model
- Cross-encoder reranking

Lưu ý: không cần ghi tên model cụ thể trên slide chính. Nên dùng cách gọi tổng quát như **LLMs**, **Agent model**, **Verifier**, **LLM Judge**, vì mô hình có thể thay đổi.

### Cơ sở dữ liệu

- PostgreSQL: lưu người dùng, hội thoại, tin nhắn, refresh token, tác vụ xử lý tài liệu.
- MongoDB: lưu văn bản pháp luật dạng article, metadata, topics, keywords.
- ChromaDB: lưu vector embeddings phục vụ tìm kiếm ngữ nghĩa.

### Frontend

- Kotlin Multiplatform + Compose Multiplatform: mobile app.
- Next.js + React + TypeScript: web admin.

### Hạ tầng và tích hợp

- Docker Compose.
- JWT authentication.
- Cloud storage cho file tài liệu.
- API key nội bộ giữa Main Service và RAG Service.

---

## 7. Các tính năng chính

Tập trung vào các tính năng quan trọng nhất, không liệt kê quá nhiều.

### 7.1. Chat tư vấn pháp luật

Người dùng đặt câu hỏi pháp luật bằng tiếng Việt. Hệ thống xử lý theo luồng Agentic RAG, trả lời có căn cứ, có nguồn, có giải thích rõ ràng. Slide nên tập trung vào cách hệ thống kiểm soát câu hỏi, truy hồi bằng chứng và kiểm chứng câu trả lời, không cần trình bày cơ chế truyền dữ liệu theo thời gian thực.

### 7.2. Tư vấn có hướng dẫn

Khi câu hỏi của người dùng thiếu thông tin, hệ thống không trả lời vội. Thay vào đó, hệ thống hỏi thêm các câu làm rõ tình huống, sau đó mới lập kế hoạch tra cứu và trả lời. Đây là tính năng phù hợp với lĩnh vực pháp luật vì cùng một câu hỏi có thể có kết luận khác nhau tùy theo đối tượng, thời điểm, hành vi và ngữ cảnh.

### 7.3. Tra cứu văn bản pháp luật

Người dùng có thể xem thư viện văn bản pháp luật, tìm kiếm, lọc theo chủ đề, năm ban hành hoặc xem chi tiết điều luật.

### 7.4. Tìm kiếm AI theo ngữ nghĩa

Thay vì chỉ tìm theo từ khóa, hệ thống hỗ trợ tìm kiếm theo ý nghĩa câu hỏi. Ví dụ, người dùng có thể hỏi bằng ngôn ngữ tự nhiên, hệ thống vẫn tìm được các điều luật liên quan thông qua embedding và vector search.

### 7.5. Admin upload và xử lý văn bản mới

Quản trị viên upload PDF văn bản pháp luật. Hệ thống trích xuất nội dung, cấu trúc hóa thành các điều luật, lưu vào MongoDB, chia chunk, tạo embedding và cập nhật vào ChromaDB. Admin có thể theo dõi tiến trình xử lý qua WebSocket.

### 7.6. Dashboard quản trị

Web admin cung cấp giao diện theo dõi tổng quan tài liệu, trạng thái xử lý, số lượng văn bản, tác vụ thành công/thất bại và các thông tin vận hành chính.

---

## 8. Kiến trúc tổng quan hệ thống

Slide kiến trúc nên là một trong các slide quan trọng nhất. Hãy vẽ sơ đồ theo hướng rõ ràng, ít chữ, có các khối chính:

```text
Mobile App
Web Admin
        ↓ JWT
Main Service
        ↓ X-API-Key nội bộ
RAG Service
        ↓
PostgreSQL / MongoDB / ChromaDB
        ↓
LLMs + Web Search
```

Giải thích vai trò:

- Mobile App: giao diện người dùng cuối, chat AI, tư vấn có hướng dẫn, tra cứu văn bản.
- Web Admin: quản trị văn bản, upload PDF, theo dõi pipeline xử lý.
- Main Service: cổng API chính, xác thực JWT, quản lý hội thoại, lưu tin nhắn, gọi RAG Service.
- RAG Service: lõi AI, chạy Agentic RAG, truy hồi nội bộ, tìm kiếm web, kiểm chứng câu trả lời.
- PostgreSQL: dữ liệu tài khoản, hội thoại, tin nhắn, refresh token, document task.
- MongoDB: kho văn bản pháp luật dạng article.
- ChromaDB: kho vector embedding cho tìm kiếm ngữ nghĩa.

Thông điệp chính:

**Client không gọi trực tiếp RAG Service. Main Service là lớp bảo vệ và điều phối, còn RAG Service là lõi xử lý AI nội bộ.**

---

## 9. Luồng chat chính

Đây là luồng quan trọng nhất cần có trong slide.

Quy trình:

1. Người dùng gửi câu hỏi từ mobile app.
2. Main Service kiểm tra JWT access token.
3. Main Service xác định hoặc tạo hội thoại.
4. Tin nhắn người dùng được lưu vào PostgreSQL.
5. Main Service lấy một phần lịch sử hội thoại gần nhất để làm ngữ cảnh.
6. Main Service gọi RAG Service bằng API key nội bộ.
7. RAG Service chạy graph Agentic RAG.
8. Câu trả lời cuối cùng được lưu lại và trả về cùng nguồn tham chiếu.

Nên thể hiện bằng sơ đồ sequence hoặc flow ngang:

```text
User → Mobile App → Main Service → RAG Service → Tools/DB/Web → Verifier → Response
```

Các điểm cần nhấn mạnh:

- JWT bảo vệ request từ người dùng.
- API key nội bộ bảo vệ RAG Service.
- Lịch sử hội thoại chỉ dùng để hiểu ngữ cảnh, không thay thế nguồn pháp lý.
- Cơ chế hiển thị tiến trình có thể nhắc ngắn ở phần demo, không cần tách thành slide riêng.
- Câu trả lời cuối cùng được lưu cùng metadata và sources.

---

## 10. Thuật toán trọng tâm: Agentic RAG Graph

Nên có một slide riêng cho graph Agentic RAG.

Các node chính:

### Guardrail

Kiểm tra câu hỏi có thuộc phạm vi pháp luật Việt Nam và có an toàn để xử lý không. Nếu câu hỏi lạc đề hoặc độc hại, hệ thống từ chối sớm.

### Query Analysis

Phân tích câu hỏi tự nhiên của người dùng thành truy vấn pháp lý có cấu trúc. Bước này tạo truy vấn tối ưu cho tìm kiếm nội bộ và truy vấn tối ưu cho tìm kiếm web.

### Agent

Đóng vai trò điều phối. Agent quyết định gọi công cụ nào, đọc kết quả trả về và tổng hợp câu trả lời nháp.

### Tools

Gồm hai nhóm công cụ:

- Truy hồi pháp luật nội bộ từ ChromaDB.
- Tìm kiếm nguồn pháp luật hiện hành từ bên ngoài.

### Verifier

Kiểm chứng câu trả lời cuối cùng, đặc biệt là điều khoản, con số, mức phạt, thời điểm hiệu lực và sự phù hợp của nguồn dẫn.

Thông điệp chính:

**Graph không để Agent tự do trả lời ngay. Agent phải đi qua công cụ truy hồi và bước kiểm chứng trước khi phản hồi người dùng.**

---

## 11. Thuật toán trọng tâm: xây dựng kho vector pháp luật

Đây là phần quan trọng vì chất lượng RAG phụ thuộc vào chất lượng kho tri thức.

Quy trình nên trình bày:

```text
JSON/article pháp luật
→ Tiền xử lý
→ Chuẩn hóa metadata
→ Chunking
→ Embedding
→ Lưu ChromaDB
→ Truy hồi khi người dùng hỏi
```

Giải thích:

- Dữ liệu pháp luật ban đầu được tổ chức theo từng văn bản và từng điều luật.
- Mỗi điều luật có các trường như `law_id`, `article_id`, `title`, `text`, `topics`, `keywords`, `summary`, `year`.
- Nội dung dài được chia thành các chunk để truy hồi chính xác hơn.
- Khi chunking, hệ thống giữ overlap để tránh mất ngữ cảnh ở ranh giới giữa các đoạn.
- Trước khi embedding, tiêu đề điều luật được ghép với nội dung chunk để vector giữ được ngữ cảnh pháp lý.
- Embedding được lưu vào ChromaDB cùng metadata phục vụ lọc và hiển thị nguồn.

Thông tin nên đưa vào slide:

- ChromaDB collection: `vietnamese_law`.
- Embedding dimension: 768.
- Kho dữ liệu có khoảng 690.360 vector chunks.
- Metadata trong ChromaDB gồm law_id, article_id, title, chunk_index, total_chunks, year, topics, keywords, summary.

Không cần đưa quá nhiều code lên slide, chỉ nên dùng sơ đồ pipeline.

---

## 12. Thuật toán trọng tâm: truy hồi hai giai đoạn

Nên trình bày bằng sơ đồ pipeline.

```text
Query
→ Vector Search
→ Top-K candidates
→ Cross-Encoder Reranking
→ Blended Score
→ Threshold
→ Top sources
```

Ý nghĩa:

- Vector search giúp tìm nhanh các chunk gần nghĩa trong ChromaDB.
- Bi-encoder phù hợp cho việc tìm kiếm nhanh trong kho dữ liệu lớn.
- Cross-encoder reranking chấm lại mức độ liên quan giữa query và từng document.
- Điểm cuối kết hợp giữa điểm vector và điểm rerank.
- Kết quả có điểm thấp bị loại khỏi context để tránh đưa nguồn yếu vào câu trả lời.

Thông điệp chính:

**Vector search giúp tìm nhanh, cross-encoder giúp chọn chính xác hơn.**

---

## 13. Thuật toán trọng tâm: xử lý luật cũ và luật mới

Đây là điểm đặc thù của bài toán pháp luật, nên cần có slide riêng nếu còn thời gian.

Vấn đề:

Cùng một chủ đề pháp luật có thể xuất hiện trong nhiều văn bản khác nhau ở các năm khác nhau. Văn bản cũ và văn bản mới có thể cùng được truy hồi vì nội dung gần nhau về ngữ nghĩa. Nếu không xử lý, hệ thống có thể trộn lẫn quy định cũ và mới.

Ví dụ:

- Nghị định 100/2019/NĐ-CP.
- Nghị định 168/2024/NĐ-CP.
- Cùng liên quan đến xử phạt giao thông, nhưng văn bản mới cần được ưu tiên khi trả lời câu hỏi hiện hành.

Cách xử lý:

1. Nhóm các kết quả truy hồi theo chủ đề và metadata.
2. Phát hiện các nhóm có nhiều năm ban hành khác nhau.
3. Ưu tiên văn bản mới hơn.
4. Gắn nhãn văn bản cũ để Agent không dùng làm căn cứ chính.
5. Verifier kiểm tra lại câu trả lời để tránh dùng nhầm con số từ văn bản cũ.

Thông điệp chính:

**Trong tư vấn pháp luật, tìm đúng điều khoản chưa đủ; hệ thống còn phải ưu tiên đúng quy định hiện hành.**

---

## 14. Luồng cập nhật văn bản mới phía Admin

Nên có một slide riêng vì đây là tính năng quan trọng chứng minh hệ thống không phải chatbot tĩnh.

Quy trình:

```text
Admin upload PDF
→ Tạo DocumentTask
→ Upload file lên cloud storage
→ Trích xuất nội dung PDF
→ Cấu trúc hóa thành các điều luật
→ Lưu MongoDB
→ Chunking + Embedding
→ Upsert ChromaDB
→ Cập nhật trạng thái qua WebSocket
```

Điểm cần nhấn mạnh:

- Admin nhận `task_id` ngay sau khi upload.
- Hệ thống cập nhật tiến trình xử lý theo thời gian thực.
- MongoDB lưu nội dung pháp luật dạng article.
- ChromaDB lưu vector chunks để phục vụ tìm kiếm.
- Nếu một bước lưu dữ liệu lỗi, hệ thống có cơ chế rollback/compensating transaction để tránh MongoDB và ChromaDB lệch nhau.

Thông điệp chính:

**Kho tri thức của hệ thống có thể được cập nhật thông qua pipeline xử lý tài liệu, không phải nhập dữ liệu thủ công hoàn toàn.**

---

## 15. Đánh giá hệ thống

Nếu có slide đánh giá, nên trình bày ngắn gọn bằng metric cards hoặc biểu đồ.

Bộ đánh giá:

- Tổng cộng 60 câu hỏi.
- N1: 30 câu factual, có đáp án xác định.
- N2: 30 câu mở/tình huống, đánh giá chất lượng câu trả lời.
- Các lĩnh vực gồm giao thông, lao động, doanh nghiệp, đất đai & nhà ở, hình sự & dân sự.

Kết quả:

- Accuracy@1: 90,0% trên tập N1.
- Citation Accuracy: 56,7%.
- Temporal Conflict OK: 3/3, tương đương 100% trên nhóm câu kiểm tra xung đột luật cũ/mới.
- Answer Quality: 3,67/5,0 trên tập N2.
- Latency P50: 65,5 giây.
- Latency P95: 100,6 giây.

Cách trình bày:

- Dùng 4-6 thẻ số liệu lớn.
- Dùng màu xanh cho kết quả tốt.
- Dùng màu vàng/cam cho hạn chế về latency hoặc citation.

Thông điệp chính:

**Hệ thống đạt chất lượng trả lời tốt và xử lý đúng xung đột luật cũ/mới, nhưng còn hạn chế về độ trễ và độ đầy đủ của nguồn trích dẫn nội bộ.**

---

## 16. Hạn chế và hướng phát triển

Hạn chế:

- Độ trễ còn cao do pipeline có nhiều bước gọi LLMs và Verifier.
- Citation Accuracy chưa cao khi kho dữ liệu nội bộ chưa đầy đủ hoặc chưa index kịp văn bản mới.
- Phạm vi dữ liệu pháp luật chưa bao phủ toàn bộ lĩnh vực.
- Bộ đánh giá còn nhỏ so với hệ thống sản xuất thực tế.

Hướng phát triển:

- Tối ưu tốc độ bằng cache, song song hóa một số bước và giảm số lần gọi xử lý tuần tự.
- Mở rộng kho dữ liệu pháp luật.
- Cải thiện embedding/reranking cho miền pháp luật tiếng Việt.
- Xây dựng bộ benchmark pháp luật lớn hơn.
- Bổ sung kiểm thử hồi quy để tránh lỗi khi cập nhật dữ liệu mới.

---

## 17. Đề xuất cấu trúc slide 15-18 slide

Nên tạo **17 slide**. Nếu cần rút gọn xuống 15-16 slide, hãy gộp slide demo và đánh giá; không nên cắt các slide về kho vector ban đầu, LangGraph chat flow, retrieval, admin upload và guided consultation vì đây là các nội dung trọng tâm của Chương 2.

### Slide 1. Trang bìa

Nội dung:

- Tên đề tài: Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số.
- Sinh viên thực hiện: Vương Văn Duy.
- Báo cáo đồ án tốt nghiệp đại học.

Visual:

- Theme sáng, hiện đại.
- Có biểu tượng pháp luật + AI/chatbot.
- Có motif network/vector/RAG nhẹ ở nền.

### Slide 2. Lý do chọn bài toán

Thông điệp:

Văn bản pháp luật khó tra cứu, thường xuyên thay đổi, trong khi LLMs thuần có nguy cơ trả lời thiếu căn cứ.

Visual:

- 3 problem cards: dữ liệu lớn, hiệu lực thay đổi, hallucination.

### Slide 3. Mục tiêu đề tài

Thông điệp:

Xây dựng trợ lý ảo pháp luật có nguồn, có kiểm chứng và có khả năng cập nhật dữ liệu.

Visual:

- 4 goal cards.

### Slide 4. Phương án giải quyết tổng quan

Thông điệp:

Hệ thống dùng Agentic RAG để kết hợp LLMs, kho tri thức pháp luật, công cụ truy hồi và bước kiểm chứng câu trả lời.

Visual:

- So sánh ngắn 3 cột: LLMs thuần, RAG cơ bản, Agentic RAG có kiểm chứng.
- Nhấn mạnh Agentic RAG là phương pháp chính của đồ án.

### Slide 5. Công nghệ sử dụng và vai trò trong hệ thống

Thông điệp:

Các công nghệ được chọn theo vai trò cụ thể: backend, điều phối Agent, lưu trữ dữ liệu, truy hồi vector, mobile app và web admin.

Visual:

- Tech stack chia theo nhóm Backend, AI/RAG, Database, Mobile, Admin.
- Không cần giải thích dài; slide này chỉ làm cầu nối trước khi đi vào Chương 2.

### Slide 6. Kiến trúc tổng quan hệ thống

Thông điệp:

Theo Chương 2, hệ thống được tổ chức theo kiến trúc microservices, trong đó Main Service là cổng nghiệp vụ và RAG Service là lõi AI nội bộ.

Visual:

- Sơ đồ khối: Mobile App/Web Admin → Main Service → RAG Service → PostgreSQL/MongoDB/ChromaDB/LLMs/Web Search.
- Thể hiện rõ client không gọi trực tiếp RAG Service.

### Slide 7. Xây dựng kho dữ liệu vector pháp luật ban đầu

Thông điệp:

Kho dữ liệu vector pháp luật ban đầu là nền tảng để Agentic RAG có căn cứ truy hồi khi người dùng đặt câu hỏi.

Visual:

- Pipeline: dữ liệu pháp luật đầu vào → chuẩn hóa article/metadata → chunking → embedding → ChromaDB.
- Có thể dùng icon document, scissors/chunk, vector, database.

### Slide 8. Chiến lược chunking và metadata cho văn bản pháp luật

Thông điệp:

Văn bản pháp luật cần được chia chunk và giữ metadata để vừa truy hồi chính xác, vừa liên kết ngược được về văn bản gốc.

Visual:

- Một điều luật dài được chia thành nhiều chunk.
- Các thẻ metadata: `law_id`, `article_id`, `title`, `year`, `topics`, `keywords`, `summary`.
- Nhấn mạnh tiêu đề điều luật và metadata giúp chunk không mất ngữ cảnh.

### Slide 9. Cơ chế truy hồi trong kho vector

Thông điệp:

Hệ thống không tìm kiếm toàn văn đơn thuần, mà truy hồi theo ngữ nghĩa rồi xếp hạng lại để chọn nguồn tốt hơn.

Visual:

- Pipeline: Query → Vector Search → Candidate chunks → Cross-encoder Reranking → Blended Score → Top Sources.
- Có thể ghi ngắn: vector search tăng recall, reranking tăng precision.

### Slide 10. Luồng chat chính với LangGraph

Thông điệp:

Luồng chat chính được xây dựng bằng LangGraph để kiểm soát từng bước xử lý, từ kiểm tra đầu vào đến kiểm chứng câu trả lời.

Visual:

- Graph trung tâm: START → Guardrail → Query Analysis → Agent ↔ Tools → Verifier → END.
- Nên vẽ vòng lặp Agent ↔ Tools rõ ràng.

### Slide 11. Các node quan trọng trong LangGraph

Thông điệp:

Mỗi node trong graph đảm nhiệm một trách nhiệm riêng để giảm rủi ro LLMs trả lời thiếu căn cứ.

Visual:

- 4 card chính:
  - Guardrail: kiểm soát đầu vào.
  - Query Analysis: tối ưu truy vấn.
  - Agent: thu thập bằng chứng qua tools.
  - Verifier: kiểm chứng câu trả lời.
- Slide này có thể dùng icon shield, search, agent/network, check.

### Slide 12. Xử lý luật cũ và luật mới

Thông điệp:

Hệ thống phát hiện xung đột pháp lý theo thời gian và ưu tiên văn bản mới để tránh dùng nhầm quy định đã hết hiệu lực.

Visual:

- Timeline 2019 → 2024, nhãn "văn bản cũ" và "văn bản hiện hành".
- Nên dùng một callout: "Tìm đúng điều luật chưa đủ; cần ưu tiên đúng quy định hiện hành."

### Slide 13. Luồng upload văn bản mới của Admin

Thông điệp:

Admin upload PDF, hệ thống trích xuất và cập nhật cả MongoDB lẫn ChromaDB để mở rộng kho tri thức.

Visual:

- Pipeline Document Ingestion: Upload PDF → Task → Parse/Structure → MongoDB → Chunk/Embedding → ChromaDB → WebSocket Progress.
- Nhấn mạnh đây là cơ chế cập nhật tri thức sau khi đã có kho vector ban đầu.

### Slide 14. Luồng tư vấn có hướng dẫn

Thông điệp:

Khi câu hỏi pháp luật thiếu ngữ cảnh, hệ thống hỏi làm rõ trước khi đưa ra câu trả lời cuối cùng.

Visual:

- Flow: Câu hỏi ban đầu → Câu hỏi làm rõ → Người dùng bổ sung → Trả lời theo ngữ cảnh.
- Có thể dùng mockup mobile hoặc card hội thoại.

### Slide 15. Demo giao diện và tính năng chính

Thông điệp:

Sản phẩm đã triển khai được các luồng chính trên Mobile App và Web Admin.

Visual:

- Một slide ghép mockup:
  - Mobile chat Agentic RAG/ThinkingPanel.
  - Guided Consultation.
  - Web Admin dashboard/upload.
- Không cần đưa quá nhiều ảnh; chọn 3 ảnh tiêu biểu.

### Slide 16. Đánh giá hệ thống

Thông điệp:

Hệ thống đạt kết quả tốt trên bộ 60 câu hỏi, xử lý đúng nhóm xung đột luật cũ/mới nhưng còn hạn chế về độ trễ và nguồn trích dẫn nội bộ.

Visual:

- Metric cards: 90,0% Accuracy@1, 3,67/5 Answer Quality, 3/3 Temporal Conflict OK, 65,5s P50 latency.
- Dùng màu cam/vàng cho latency để thể hiện hạn chế cần cải thiện.

### Slide 17. Kết luận và hướng phát triển

Thông điệp:

Đề tài đã xây dựng được hệ thống trợ lý ảo pháp luật theo Agentic RAG, có kho tri thức vector, có luồng chat kiểm chứng, có cơ chế cập nhật văn bản mới và có sản phẩm demo thực tế.

Visual:

- 3 contribution cards:
  - Kho tri thức pháp luật phục vụ RAG.
  - Luồng chat Agentic RAG có kiểm chứng.
  - Mobile App + Web Admin có thể vận hành.
- Kết thúc bằng "Cảm ơn Quý Thầy/Cô đã lắng nghe" hoặc "Q&A".

---

## 18. Yêu cầu thiết kế visual

Phong cách:

- Sáng, hiện đại, chuyên nghiệp.
- Phù hợp với báo cáo kỹ thuật và đồ án tốt nghiệp.
- Không quá màu mè, không dùng nền tối toàn bộ.

Màu chủ đạo:

- Trắng hoặc xám rất nhạt làm nền.
- Xanh teal hoặc xanh dương làm màu nhấn.
- Cam/vàng chỉ dùng để nhấn mạnh cảnh báo, hạn chế hoặc luật cũ.
- Đen/xám đậm cho chữ chính.

Typography:

- Tiêu đề lớn, rõ.
- Nội dung ngắn.
- Không dùng paragraph dài trên slide.
- Mỗi slide chỉ nên có 3-5 bullet hoặc 3-5 card.

Hình ảnh:

- Dùng icon liên quan đến pháp luật, tài liệu, chatbot, AI, database, shield, search, check.
- Dùng sơ đồ khối đơn giản, không quá nhiều đường nối.
- Nếu có screenshot sản phẩm, hãy đặt trong mockup điện thoại/laptop.

Tránh:

- Không dùng quá nhiều text.
- Không dùng template quá trẻ con hoặc quá marketing.
- Không dùng ảnh stock luật sư quá chung chung.
- Không ghi tên model cụ thể nếu không cần; dùng LLMs cho tổng quát.
- Không đưa quá nhiều tên class/file code vào slide.
- Không dùng slide toàn bảng kỹ thuật dày chữ.

---

## 19. Prompt có thể copy trực tiếp vào Canva AI

Hãy tạo một bộ slide PowerPoint tiếng Việt cho báo cáo đồ án tốt nghiệp với chủ đề:

**"Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số"**

Nguồn nội dung bắt buộc: bám sát file báo cáo chính **`Vương Văn Duy_CT060411_NGHIÊN CỨU PHÁT TRIỂN TRỢ LÝ ẢO PHÁP LUẬT CHO CHUYỂN ĐỔI SỐ.docx`** hoặc bản PDF xuất từ báo cáo này. Chỉ rút gọn và trực quan hóa nội dung đã có trong báo cáo, không tự thêm thông tin ngoài báo cáo.

Thời gian trình bày: 12-15 phút. Số lượng slide: khoảng 16-18 slide, tối đa 20 slide.

Phong cách thiết kế: theme sáng, hiện đại, chuyên nghiệp, phù hợp với đề tài công nghệ/AI và báo cáo tốt nghiệp. Nền trắng hoặc xám rất nhạt, màu nhấn xanh teal/xanh dương, chữ đen/xám đậm. Ưu tiên sơ đồ, card thông tin, timeline, flow diagram và mockup giao diện. Không dùng quá nhiều chữ trên slide.

Trọng tâm nội dung: tập trung chủ yếu vào **Chương 2 - Phương pháp xây dựng hệ thống tư vấn pháp luật với Agentic RAG**. Các nội dung ở Chương 1 chỉ dùng để mở bài; Chương 3 và Chương 4 chỉ dùng để hỗ trợ phần thiết kế, demo và đánh giá. Không biến slide thành bản tóm tắt đều cả 4 chương.

Nội dung cần tập trung:

1. Lý do chọn bài toán: văn bản pháp luật lớn, khó tra cứu, thường xuyên thay đổi, LLMs thuần có nguy cơ hallucination.
2. Mục tiêu: xây dựng trợ lý ảo pháp luật tiếng Việt có nguồn, có kiểm chứng và có khả năng cập nhật dữ liệu.
3. Phương án giải quyết: Agentic RAG kết hợp LLMs, truy hồi dữ liệu, công cụ tìm kiếm và Verifier.
4. Công nghệ sử dụng: FastAPI, LangGraph, WebSocket, PostgreSQL, MongoDB, ChromaDB, Kotlin Multiplatform, Next.js.
5. Tính năng chính: chat tư vấn pháp luật, tư vấn có hướng dẫn, thư viện văn bản luật, tìm kiếm AI theo ngữ nghĩa, admin upload PDF, dashboard quản trị.
6. Sơ đồ tổng quan hệ thống: Mobile App và Web Admin gọi Main Service bằng JWT; Main Service gọi RAG Service bằng API key nội bộ; RAG Service kết nối PostgreSQL, MongoDB, ChromaDB, LLMs và Web Search.
7. Xây dựng kho vector pháp luật ban đầu: dữ liệu pháp luật/article → chuẩn hóa metadata → chunking → embedding → ChromaDB collection `vietnamese_law`. Nội dung này phải đứng trước phần Agentic RAG vì đây là nền tảng dữ liệu để Agent truy hồi.
8. Cơ chế truy hồi: Vector Search → Candidate chunks → Cross-Encoder Reranking → Blended Score → Top Sources.
9. Luồng chat chính với LangGraph: User → Main Service → RAG Service → Guardrail → Query Analysis → Agent ↔ Tools → Verifier → Final Answer with Sources.
10. Các node quan trọng trong LangGraph: Guardrail kiểm soát đầu vào, Query Analysis tối ưu truy vấn, Agent thu thập bằng chứng qua tools, Verifier kiểm chứng câu trả lời.
11. Xử lý luật cũ và luật mới: phát hiện văn bản cùng chủ đề nhưng khác năm, ưu tiên quy định mới, Verifier kiểm tra tránh dùng nhầm văn bản cũ.
12. Admin cập nhật văn bản mới: upload PDF → tạo task → trích xuất/cấu trúc hóa → lưu MongoDB → chunking/embedding → upsert ChromaDB → theo dõi tiến trình WebSocket. Đây là cơ chế cập nhật tri thức sau khi hệ thống đã có kho vector ban đầu.
13. Luồng tư vấn có hướng dẫn: câu hỏi ban đầu → hệ thống hỏi làm rõ → người dùng bổ sung thông tin → trả lời theo ngữ cảnh đã làm rõ.
14. Demo giao diện: mobile chat/ThinkingPanel, guided consultation, web admin dashboard/upload.
15. Đánh giá: bộ 60 câu hỏi; Accuracy@1 90,0%; Answer Quality 3,67/5; Temporal Conflict OK 3/3; Latency P50 65,5s; Latency P95 100,6s.
16. Hạn chế và hướng phát triển: tối ưu latency, mở rộng kho dữ liệu, cải thiện embedding/rerank cho pháp luật Việt Nam, xây benchmark lớn hơn.
17. Kết luận: hệ thống đã xây dựng được trợ lý ảo pháp luật theo Agentic RAG, có căn cứ, có kiểm chứng, có khả năng cập nhật tri thức và có sản phẩm demo thực tế.

Đề xuất cấu trúc slide:

1. Trang bìa.
2. Lý do chọn bài toán.
3. Mục tiêu đề tài.
4. Phương án giải quyết.
5. Công nghệ sử dụng.
6. Kiến trúc tổng quan hệ thống.
7. Xây dựng kho dữ liệu vector pháp luật ban đầu.
8. Chiến lược chunking và metadata.
9. Cơ chế truy hồi trong kho vector.
10. Luồng chat chính với LangGraph.
11. Các node quan trọng trong LangGraph.
12. Xử lý luật cũ và luật mới.
13. Luồng upload văn bản mới của Admin.
14. Luồng tư vấn có hướng dẫn.
15. Demo giao diện và tính năng chính.
16. Đánh giá hệ thống.
17. Kết luận và hướng phát triển.

Yêu cầu quan trọng:

- Không viết slide quá dày chữ.
- Không dùng tên model cụ thể, chỉ dùng LLMs, Agent model, Verifier hoặc LLM Judge.
- Không nhắc cơ chế multi-api-key hoặc các chi tiết vận hành nội bộ không được nhấn mạnh trong báo cáo.
- Không đưa tên class/file code vào slide.
- Không dùng bảng lớn; hãy chuyển thành card/diagram.
- Mỗi slide chỉ truyền tải một ý chính.
- Tạo slide dễ chỉnh sửa trong Canva/PowerPoint.
