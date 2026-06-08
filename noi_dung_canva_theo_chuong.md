# Cấu trúc nội dung theo phần lớn cho Canva AI

Tài liệu này dùng để đưa cho Canva AI hoặc dùng làm khung dựng lại slide báo cáo bảo vệ. Thay vì chia cứng theo từng slide, nội dung được tổ chức thành 5 phần lớn. Canva có thể tự tách mỗi phần thành 2-5 slide tùy bố cục template, miễn là tổng số slide nằm trong khoảng 15-20 slide và thời gian trình bày khoảng 12-15 phút.

Trọng tâm của bài báo cáo là Chương 2 trong báo cáo đồ án: xây dựng kho dữ liệu vector pháp luật ban đầu, cơ chế truy hồi RAG, luồng chat chính với LangGraph, luồng cập nhật văn bản mới phía Admin và luồng tư vấn có hướng dẫn.

---

## Phần 1. Mở đầu: bối cảnh, vấn đề và mục tiêu đề tài

**Số slide gợi ý:** 3-4 slide

**Vai trò của phần này**

Phần mở đầu cần giúp Hội đồng hiểu vì sao bài toán có ý nghĩa và đề tài cần giải quyết vấn đề gì. Nội dung nên đi từ bối cảnh chuyển đổi số trong lĩnh vực pháp luật, khó khăn khi người dùng tra cứu văn bản pháp luật, đến mục tiêu xây dựng một trợ lý pháp luật có khả năng trả lời dựa trên nguồn và có kiểm chứng.

**Nội dung cần trình bày**

- Tên đề tài: Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số.
- Bối cảnh: văn bản pháp luật nhiều, dài, có cấu trúc phức tạp và thường xuyên thay đổi.
- Vấn đề của người dùng phổ thông: khó biết phải tra cứu ở đâu, dùng từ khóa nào, văn bản nào đang còn hiệu lực.
- Hạn chế của chatbot hoặc LLMs thuần: có thể trả lời nghe hợp lý nhưng thiếu căn cứ, sai điều khoản hoặc không dẫn nguồn kiểm chứng.
- Mục tiêu đề tài: xây dựng hệ thống trợ lý pháp luật tiếng Việt có khả năng truy hồi nguồn, tổng hợp câu trả lời, kiểm chứng kết quả và hỗ trợ cập nhật văn bản mới.

**Thông điệp chính cần nhấn mạnh**

Bài toán không chỉ là xây dựng một chatbot hỏi đáp, mà là xây dựng một hệ thống tư vấn pháp luật có căn cứ, có kiểm chứng và có khả năng cập nhật tri thức.

**Gợi ý visual**

- Slide bìa sáng, hiện đại, có biểu tượng pháp luật kết hợp AI/chatbot.
- Một slide agenda ngắn liệt kê các phần chính của bài báo cáo.
- Một slide problem statement với 3-4 thẻ vấn đề: dữ liệu lớn, hiệu lực thay đổi, khó tra cứu, rủi ro trả lời sai.
- Một slide mục tiêu đề tài dạng 4-5 goal cards.

**Ghi chú thuyết trình**

Ở phần này nên trình bày ngắn, không đi sâu kỹ thuật. Mục tiêu là tạo nền cho phần giải pháp phía sau: vì pháp luật yêu cầu độ chính xác và căn cứ rõ ràng, hệ thống cần kết hợp LLMs với kho dữ liệu pháp luật, cơ chế truy hồi và bước kiểm chứng.

---

## Phần 2. Phương án giải quyết và kiến trúc tổng quan

**Số slide gợi ý:** 3-4 slide

**Vai trò của phần này**

Phần này giải thích hướng tiếp cận kỹ thuật của đồ án và cách hệ thống được tổ chức. Cần làm rõ vì sao dùng Agentic RAG, các công nghệ chính được chọn theo vai trò nào, và các service/dữ liệu trong hệ thống liên kết với nhau ra sao.

**Nội dung cần trình bày**

- So sánh ngắn ba hướng tiếp cận:
  - LLMs thuần: trả lời linh hoạt nhưng khó kiểm chứng.
  - RAG cơ bản: có truy hồi tài liệu nhưng chưa kiểm soát tốt luật cũ - luật mới.
  - Agentic RAG: Agent điều phối công cụ truy hồi, thu thập bằng chứng và đưa câu trả lời qua Verifier.
- Công nghệ sử dụng theo vai trò:
  - FastAPI và Python cho backend.
  - LangGraph cho điều phối luồng Agentic RAG.
  - PostgreSQL cho dữ liệu tài khoản, xác thực và hội thoại.
  - MongoDB cho dữ liệu điều luật có cấu trúc linh hoạt.
  - ChromaDB cho kho vector phục vụ tìm kiếm ngữ nghĩa.
  - Kotlin Multiplatform cho Mobile App.
  - Next.js cho Web Admin.
- Kiến trúc tổng quan:
  - Mobile App và Web Admin gọi Main Service qua API có xác thực.
  - Main Service xử lý nghiệp vụ chính, tài khoản, hội thoại, upload và điều phối request.
  - RAG Service là service nội bộ phụ trách Agentic RAG, embedding, truy hồi vector và ingestion.
  - RAG Service kết nối MongoDB, ChromaDB, LLMs và nguồn tìm kiếm ngoài khi cần.

**Thông điệp chính cần nhấn mạnh**

LLMs trong hệ thống không được xem là nguồn pháp luật độc lập, mà là thành phần lập luận trên bằng chứng được truy hồi và kiểm chứng.

**Gợi ý visual**

- Một slide so sánh 3 cột: LLMs thuần, RAG cơ bản, Agentic RAG có kiểm chứng.
- Một slide tech stack theo nhóm vai trò, tránh liệt kê logo quá dày.
- Một slide kiến trúc khối: Mobile App/Web Admin → Main Service → RAG Service → PostgreSQL/MongoDB/ChromaDB/LLMs/Web Search.
- Có thể dùng màu khác nhau cho client, backend service, database và external services.

**Ghi chú thuyết trình**

Điểm cần giải thích rõ là việc tách Main Service và RAG Service. Main Service xử lý nghiệp vụ thông thường, còn RAG Service chứa workload AI nặng hơn như embedding model, vector search và LangGraph. Cách tách này giúp hệ thống dễ mở rộng và dễ kiểm soát tài nguyên hơn.

---

## Phần 3. Xây dựng kho dữ liệu vector pháp luật và cơ chế truy hồi

**Số slide gợi ý:** 4-5 slide

**Vai trò của phần này**

Đây là một trong các phần quan trọng nhất của bài báo cáo. Cần trình bày rõ rằng hệ thống phải xây dựng kho dữ liệu vector pháp luật ban đầu trước, sau đó Agentic RAG mới có nền tảng để truy hồi khi người dùng đặt câu hỏi. Phần này cũng cần làm rõ chiến lược chunking, metadata, embedding và reranking.

**Nội dung cần trình bày**

- Dữ liệu pháp luật ban đầu được chuẩn hóa thành các article có metadata.
- MongoDB lưu khoảng **528.620 điều luật** để phục vụ tra cứu, quản lý và liên kết nguồn.
- Các điều luật được chia chunk, tạo embedding và lưu vào ChromaDB.
- ChromaDB collection `vietnamese_law` lưu khoảng **690.360 vector chunks**.
- Mỗi vector có **768 chiều**, phục vụ tìm kiếm ngữ nghĩa.
- Chiến lược chunking:
  - Điều luật ngắn được giữ gần như nguyên vẹn để không mất ý nghĩa pháp lý.
  - Điều luật dài được chia thành chunk tối đa **1.000 từ**.
  - Overlap **150 từ** giúp giữ ngữ cảnh ở ranh giới giữa các chunk.
  - Naming convention giúp truy ngược từ chunk về article gốc.
- Metadata quan trọng:
  - `law_id`, `article_id`, `title`, `year`, `topics`, `keywords`, `summary`.
  - Metadata giúp truy hồi đúng nguồn, hiển thị trích dẫn và phân biệt văn bản cũ - mới.
- Cơ chế truy hồi:
  - Query của người dùng được mã hóa thành vector.
  - ChromaDB thực hiện vector search để lấy tập ứng viên ban đầu.
  - Hệ thống lấy **top-60 chunks** để tăng khả năng không bỏ sót nguồn liên quan.
  - Cross-encoder reranking chấm lại tối đa **40 ứng viên** có triển vọng.
  - Blended score và ngưỡng tin cậy được dùng để chọn nguồn đưa vào Agent.

**Thông điệp chính cần nhấn mạnh**

Chất lượng câu trả lời của Agentic RAG phụ thuộc trực tiếp vào chất lượng kho dữ liệu, cách chia chunk, metadata và cơ chế truy hồi. Với văn bản pháp luật, chunking không chỉ để giảm độ dài văn bản, mà còn để giữ đúng ngữ cảnh pháp lý.

**Gợi ý visual**

- Một pipeline dữ liệu: dữ liệu pháp luật → article/metadata → chunking → embedding → ChromaDB.
- Một slide số liệu lớn: 528.620 articles, 690.360 vector chunks, 768 dimensions.
- Một visual minh họa một điều luật dài được chia thành nhiều chunk có overlap.
- Một pipeline retrieval: Query → Vector Search → Top-60 Candidates → Cross-encoder Reranking → Blended Score → Top Sources.
- Có thể dùng visual dạng "lọc rộng trước, chấm sâu sau" để giải thích vector search và reranking.

**Ghi chú thuyết trình**

Nên nhấn mạnh rằng kho vector ban đầu là nền tảng của hệ thống, không phải kết quả phụ của luồng upload Admin. Luồng upload Admin chỉ là cơ chế cập nhật sau này. Khi người dùng đặt câu hỏi, Agent không đọc toàn bộ kho luật, mà truy hồi những chunk liên quan nhất từ ChromaDB, sau đó reranking để chọn nguồn tốt hơn trước khi tổng hợp câu trả lời.

---

## Phần 4. Các luồng xử lý trọng tâm của hệ thống

**Số slide gợi ý:** 5-6 slide

**Vai trò của phần này**

Đây là phần trọng tâm nhất khi bảo vệ vì thể hiện cách hệ thống thật sự hoạt động. Nội dung cần đi vào ba luồng chính: luồng chat LangGraph, xử lý luật cũ - luật mới, luồng upload văn bản mới của Admin và luồng tư vấn có hướng dẫn.

**Nội dung cần trình bày**

### Luồng chat chính với LangGraph

- LangGraph tổ chức pipeline chat thành đồ thị có trạng thái.
- Luồng tổng quát: START → Guardrail → Query Analysis → Agent ↔ Tools → Verifier → END.
- Guardrail kiểm soát câu hỏi đầu vào trước khi xử lý sâu hơn.
- Query Analysis phân tích câu hỏi và tạo truy vấn phù hợp cho từng nguồn tìm kiếm.
- Agent gọi công cụ để thu thập bằng chứng pháp luật.
- Tools gồm truy hồi kho luật nội bộ và tìm kiếm nguồn cập nhật khi cần.
- Verifier kiểm tra điều khoản, số liệu, nguồn dẫn và tính nhất quán của câu trả lời cuối cùng.

### Xử lý luật cũ và luật mới

- Một chủ đề pháp luật có thể xuất hiện trong nhiều văn bản ở các năm khác nhau.
- Vector search có thể trả về cả văn bản cũ và văn bản mới vì nội dung gần nghĩa.
- Hệ thống sử dụng metadata như năm ban hành, chủ đề và từ khóa để phát hiện nhóm có khả năng xung đột.
- Văn bản mới hơn được ưu tiên khi có dấu hiệu thay thế hoặc cập nhật quy định.
- Verifier kiểm tra lại để tránh dùng nhầm con số hoặc căn cứ từ văn bản cũ.
- Ví dụ minh họa: NĐ 100/2019 và NĐ 168/2024 trong nhóm câu hỏi về xử phạt giao thông.

### Luồng upload văn bản mới phía Admin

- Admin upload file PDF văn bản pháp luật trên Web Admin.
- Main Service tạo task xử lý để theo dõi trạng thái.
- Hệ thống trích xuất nội dung, cấu trúc hóa thành các điều luật.
- MongoDB lưu article đầy đủ để quản lý và tra cứu.
- RAG Service chunk, embedding và upsert dữ liệu vào ChromaDB.
- Nếu lỗi ở các bước cuối, hệ thống rollback để tránh lệch dữ liệu giữa MongoDB và ChromaDB.

### Luồng tư vấn có hướng dẫn

- Nhiều câu hỏi pháp luật ban đầu thường thiếu dữ kiện quan trọng.
- Hệ thống chủ động hỏi làm rõ bằng các lựa chọn cụ thể.
- Người dùng bổ sung thông tin như loại phương tiện, độ tuổi, tình huống, giấy tờ hoặc vai trò liên quan.
- Câu hỏi sau khi làm rõ được đưa vào pipeline RAG để truy hồi và kiểm chứng.
- Cách làm này giảm suy đoán và giúp câu trả lời sát tình huống hơn.

**Thông điệp chính cần nhấn mạnh**

Điểm mạnh của hệ thống nằm ở việc kiểm soát luồng xử lý: câu hỏi được phân tích, nguồn được truy hồi, Agent thu thập bằng chứng và Verifier kiểm chứng trước khi trả lời.

**Gợi ý visual**

- Graph LangGraph: START → Guardrail → Query Analysis → Agent ↔ Tools → Verifier → END.
- Một slide card giải thích vai trò từng node: Guardrail, Query Analysis, Agent, Tools, Verifier.
- Timeline luật cũ - luật mới: 2019 → 2024, có lớp Verifier ở cuối.
- Pipeline Admin upload: Upload PDF → Create Task → Parse/Structure → Save MongoDB → Chunk/Embedding → Upsert ChromaDB → Complete/Failed.
- Flow tư vấn có hướng dẫn: câu hỏi ban đầu → hỏi làm rõ → người dùng bổ sung → truy hồi theo ngữ cảnh → câu trả lời có căn cứ.

**Ghi chú thuyết trình**

Phần này nên dành nhiều thời gian nhất. Khi trình bày, không cần đi quá sâu vào tên hàm hoặc tên file code, nhưng cần giải thích được vì sao từng bước tồn tại. Guardrail giúp kiểm soát đầu vào, Query Analysis giúp truy vấn tốt hơn, Agent dùng công cụ thay vì tự trả lời cảm tính, Verifier giúp giảm rủi ro hallucination, còn guided consultation giúp hệ thống không phải suy đoán khi câu hỏi thiếu dữ kiện.

---

## Phần 5. Sản phẩm demo, đánh giá và kết luận

**Số slide gợi ý:** 3-4 slide

**Vai trò của phần này**

Phần cuối cần chứng minh hệ thống đã được triển khai thành sản phẩm có thể sử dụng, có kết quả đánh giá và có hướng phát triển rõ ràng. Nội dung nên ngắn gọn, tập trung vào kết quả đạt được và các hạn chế còn tồn tại.

**Nội dung cần trình bày**

### Sản phẩm demo

- Mobile App hỗ trợ chat tư vấn pháp luật, hiển thị tiến trình xử lý và nguồn tham chiếu.
- Luồng tư vấn có hướng dẫn giúp người dùng bổ sung ngữ cảnh trước khi nhận câu trả lời.
- Tính năng tra cứu văn bản giúp tìm kiếm pháp luật bằng ngôn ngữ tự nhiên.
- Web Admin hỗ trợ dashboard, quản lý văn bản, upload PDF và theo dõi trạng thái xử lý.

### Kết quả đánh giá

- Bộ kiểm thử gồm **60 câu hỏi**.
- **Accuracy@1: 90,0%** trên nhóm câu hỏi factual.
- **Answer Quality: 3,67/5,0** theo đánh giá chất lượng câu trả lời.
- **Temporal Conflict OK: 3/3**, hệ thống xử lý đúng nhóm luật cũ - luật mới.
- **Citation Accuracy: 56,7%**, phản ánh hạn chế về nguồn trích dẫn nội bộ.
- **Latency P50: 65,5s**, **P95: 100,6s** cho toàn bộ pipeline trả lời.

### Kết luận

- Đề tài đã xây dựng kho tri thức pháp luật phục vụ truy hồi ngữ nghĩa.
- Đề tài đã thiết kế luồng chat Agentic RAG có bước kiểm chứng.
- Hệ thống có cơ chế xử lý luật cũ - luật mới trong truy hồi.
- Hệ thống hỗ trợ cập nhật văn bản mới từ Web Admin và đồng bộ vào kho dữ liệu.
- Sản phẩm demo gồm Mobile App và Web Admin, thể hiện được các luồng chính.

### Hướng phát triển

- Tối ưu độ trễ của pipeline trả lời.
- Mở rộng và cập nhật đầy đủ hơn kho dữ liệu pháp luật.
- Cải thiện độ chính xác nguồn trích dẫn.
- Mở rộng bộ benchmark đánh giá theo nhiều nhóm câu hỏi pháp lý.

**Thông điệp chính cần nhấn mạnh**

Kết quả cho thấy hướng Agentic RAG phù hợp với bài toán tư vấn pháp luật, nhưng hệ thống vẫn cần tiếp tục tối ưu độ trễ, mở rộng dữ liệu và cải thiện độ chính xác trích dẫn.

**Gợi ý visual**

- Một slide demo ghép 3 ảnh/mockup: Mobile chat, guided consultation, Web Admin upload/dashboard.
- Một slide metric cards: Accuracy@1, Answer Quality, Temporal Conflict OK, Citation Accuracy, Latency P50/P95.
- Một slide kết luận 2 cột: kết quả đạt được và hướng phát triển.
- Slide cuối có thể dùng lời cảm ơn và Q&A.

**Ghi chú thuyết trình**

Khi trình bày phần đánh giá, nên nói thẳng cả điểm mạnh và hạn chế. Accuracy@1 và Temporal Conflict OK cho thấy hướng thiết kế có hiệu quả, còn Citation Accuracy và latency là các vấn đề cần cải thiện trong phiên bản tiếp theo. Cách trình bày này giúp phần bảo vệ khách quan hơn.

---

## Gợi ý phân bổ thành 18 slide

Canva AI có thể tự tách nội dung thành khoảng 18 slide theo phân bổ sau:

- Phần 1: 4 slide.
- Phần 2: 3 slide.
- Phần 3: 4 slide.
- Phần 4: 5 slide.
- Phần 5: 2 slide chính và 1 slide cảm ơn/Q&A.

Nếu cần rút xuống 15-16 slide, có thể gộp phần công nghệ với kiến trúc, gộp demo với đánh giá, hoặc gộp kết luận với hướng phát triển. Không nên cắt bớt phần kho dữ liệu vector, truy hồi, LangGraph, upload văn bản mới và tư vấn có hướng dẫn vì đây là các nội dung trọng tâm của đồ án.

---

## Prompt ngắn có thể đưa cho Canva AI

Hãy tạo một bộ slide báo cáo bảo vệ đồ án tốt nghiệp khoảng 18 slide, theme sáng, hiện đại và chuyên nghiệp, dựa trên 5 phần nội dung lớn sau: mở đầu bài toán trợ lý pháp luật; phương án Agentic RAG và kiến trúc hệ thống; xây dựng kho dữ liệu vector pháp luật và cơ chế truy hồi; các luồng xử lý trọng tâm gồm LangGraph chat flow, luật cũ - luật mới, upload văn bản mới và tư vấn có hướng dẫn; cuối cùng là demo, đánh giá, kết luận và hướng phát triển. Slide cần ít chữ, nhiều sơ đồ khối, pipeline, metric cards và mockup sản phẩm; tránh đưa tên class/file code hoặc tên model cụ thể.
