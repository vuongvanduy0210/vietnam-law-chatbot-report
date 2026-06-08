# Nội dung cụ thể cho 18 slide báo cáo bảo vệ

Tài liệu này dùng để nhập nội dung vào Canva hoặc làm kịch bản dựng lại slide từ template hiện có. Nội dung được bám theo báo cáo đồ án, tập trung vào Chương 2 và các luồng kỹ thuật trọng tâm: kho dữ liệu vector ban đầu, truy hồi RAG, luồng chat LangGraph, cập nhật văn bản mới phía Admin và tư vấn có hướng dẫn.

Nguyên tắc khi đưa lên slide:

- Mỗi slide chỉ giữ 1 thông điệp chính.
- Text trên slide nên ngắn; phần giải thích dài hơn đặt trong ghi chú thuyết trình.
- Không ghi tên model cụ thể nếu không cần; dùng "LLMs", "Agent model" hoặc "Verifier" để tổng quát.
- Không đưa tên class/file code lên slide, trừ khi cần giải thích kỹ thuật trong phần hỏi đáp.

---

## Slide 1. Trang bìa

**Mục đích slide**

Giới thiệu đề tài, người thực hiện và tạo ấn tượng ban đầu về hướng nghiên cứu: trợ lý pháp luật kết hợp AI, RAG và chuyển đổi số.

**Tiêu đề đưa lên slide**

NGHIÊN CỨU PHÁT TRIỂN TRỢ LÝ ẢO PHÁP LUẬT CHO CHUYỂN ĐỔI SỐ

**Nội dung đưa lên slide**

- Báo cáo đồ án tốt nghiệp đại học
- Sinh viên thực hiện: Vương Văn Duy
- Chuyên ngành: Công nghệ thông tin
- Định hướng: Trợ lý pháp luật, Agentic RAG, kho tri thức vector

**Gợi ý visual/layout**

Sử dụng bố cục cover sáng, ít chữ. Nền trắng hoặc xám rất nhạt, có một cụm visual gồm biểu tượng cán cân pháp luật, khung chat và mạng vector/AI. Tiêu đề nên là thành phần lớn nhất trên slide.

**Ghi chú thuyết trình**

Kính thưa Hội đồng, đề tài của em tập trung nghiên cứu và phát triển một hệ thống trợ lý ảo pháp luật. Mục tiêu không chỉ là tạo chatbot trả lời câu hỏi, mà là xây dựng một luồng tư vấn có căn cứ pháp lý, có truy hồi nguồn và có bước kiểm chứng trước khi trả lời người dùng.

---

## Slide 2. Nội dung trình bày

**Mục đích slide**

Giúp Hội đồng nắm trước cấu trúc bài báo cáo và biết phần trọng tâm sẽ nằm ở đâu.

**Tiêu đề đưa lên slide**

Nội dung trình bày

**Nội dung đưa lên slide**

1. Lý do chọn bài toán và mục tiêu đề tài
2. Phương án giải quyết và công nghệ sử dụng
3. Kiến trúc tổng quan hệ thống
4. Xây dựng kho dữ liệu vector pháp luật ban đầu
5. Luồng chat chính với LangGraph và Agentic RAG
6. Cập nhật văn bản mới và tư vấn có hướng dẫn
7. Demo, đánh giá và kết luận

**Câu nhấn mạnh trên slide**

Trọng tâm bài trình bày là cách hệ thống xây dựng tri thức pháp luật, truy hồi bằng RAG và kiểm chứng câu trả lời.

**Gợi ý visual/layout**

Dùng dạng agenda/timeline dọc gồm 7 mục. Có thể nhóm màu nhẹ: phần bối cảnh, phần giải pháp, phần kỹ thuật trọng tâm, phần đánh giá. Không nên để quá nhiều icon, chỉ cần số thứ tự rõ và khoảng trắng tốt.

**Ghi chú thuyết trình**

Phần đầu bài trình bày sẽ giới thiệu bài toán và hướng giải quyết. Phần trọng tâm nằm ở các slide về kho dữ liệu vector, luồng LangGraph, cơ chế truy hồi và cập nhật văn bản mới. Cuối cùng, em trình bày demo, kết quả đánh giá và hướng phát triển của hệ thống.

---

## Slide 3. Lý do chọn bài toán

**Mục đích slide**

Làm rõ vì sao bài toán tư vấn pháp luật cần một cách tiếp cận khác so với chatbot thông thường.

**Tiêu đề đưa lên slide**

Vì sao cần một trợ lý pháp luật đáng tin cậy?

**Nội dung đưa lên slide**

- Văn bản pháp luật nhiều, dài và có cấu trúc phức tạp.
- Quy định có thể thay đổi theo thời gian, văn bản mới thay thế hoặc sửa đổi văn bản cũ.
- Người dùng phổ thông khó biết phải tra cứu ở đâu và tra cứu theo từ khóa nào.
- LLMs thuần có nguy cơ trả lời thiếu căn cứ, sai điều khoản hoặc không dẫn nguồn kiểm chứng.

**Câu nhấn mạnh trên slide**

Bài toán không chỉ là hỏi đáp, mà là trả lời có căn cứ và có kiểm chứng.

**Gợi ý visual/layout**

Dùng 3-4 problem cards: "Dữ liệu lớn", "Hiệu lực thay đổi", "Khó tra cứu", "Rủi ro trả lời sai". Có thể đặt một icon cảnh báo nhỏ ở card về LLMs thuần.

**Ghi chú thuyết trình**

Trong lĩnh vực pháp luật, một câu trả lời đúng cần dựa trên nguồn văn bản cụ thể. Nếu hệ thống chỉ dựa vào khả năng sinh văn bản của LLMs thì rất khó đảm bảo độ tin cậy, đặc biệt với các quy định mới hoặc các trường hợp có luật cũ và luật mới cùng tồn tại trong kết quả tìm kiếm.

---

## Slide 4. Mục tiêu đề tài

**Mục đích slide**

Nêu rõ sản phẩm và phạm vi chính của đồ án.

**Tiêu đề đưa lên slide**

Mục tiêu của đề tài

**Nội dung đưa lên slide**

- Xây dựng trợ lý ảo pháp luật tiếng Việt có khả năng trả lời dựa trên nguồn.
- Thiết kế luồng Agentic RAG để truy hồi, tổng hợp và kiểm chứng câu trả lời.
- Xây dựng kho dữ liệu vector pháp luật phục vụ tìm kiếm ngữ nghĩa.
- Phát triển ứng dụng Mobile cho người dùng và Web Admin cho quản trị viên.
- Hỗ trợ cập nhật văn bản pháp luật mới vào kho tri thức của hệ thống.

**Gợi ý visual/layout**

Sử dụng 5 goal cards hoặc sơ đồ vòng tròn xoay quanh mục tiêu trung tâm "Trợ lý pháp luật có kiểm chứng". Mỗi card nên có icon: chat, search, database, mobile, admin.

**Ghi chú thuyết trình**

Đề tài được triển khai theo hướng có sản phẩm hoàn chỉnh. Phía người dùng có ứng dụng di động để chat và tư vấn có hướng dẫn. Phía quản trị có web admin để cập nhật văn bản mới. Ở giữa là lõi RAG, kho vector và quy trình kiểm chứng câu trả lời.

---

## Slide 5. Phương án giải quyết tổng quan

**Mục đích slide**

Giải thích vì sao đồ án chọn Agentic RAG thay vì chỉ dùng LLMs hoặc RAG cơ bản.

**Tiêu đề đưa lên slide**

Phương án giải quyết: Agentic RAG có kiểm chứng

**Nội dung đưa lên slide**

| Cách tiếp cận | Đặc điểm | Hạn chế |
| --- | --- | --- |
| LLMs thuần | Trả lời linh hoạt bằng ngôn ngữ tự nhiên | Dễ thiếu nguồn, khó kiểm chứng |
| RAG cơ bản | Truy hồi tài liệu trước khi trả lời | Chưa kiểm soát tốt luật cũ - luật mới |
| Agentic RAG | Agent gọi công cụ, truy hồi đa nguồn, qua Verifier | Phức tạp hơn nhưng phù hợp domain pháp luật |

**Câu nhấn mạnh trên slide**

LLMs đóng vai trò lập luận trên bằng chứng, không phải nguồn pháp luật độc lập.

**Gợi ý visual/layout**

Dùng layout 3 cột so sánh. Cột Agentic RAG nên được nhấn màu chủ đạo để thể hiện đây là phương án chính của đồ án.

**Ghi chú thuyết trình**

Điểm khác biệt của hệ thống là câu trả lời không được sinh ra trực tiếp ngay sau khi người dùng hỏi. Trước đó, hệ thống phải phân tích câu hỏi, truy hồi nguồn pháp luật, có thể kiểm tra nguồn cập nhật bên ngoài, rồi mới đưa câu trả lời qua một bước Verifier để giảm rủi ro sai căn cứ.

---

## Slide 6. Công nghệ sử dụng và vai trò trong hệ thống

**Mục đích slide**

Trình bày công nghệ theo vai trò, tránh biến slide thành danh sách công nghệ rời rạc.

**Tiêu đề đưa lên slide**

Công nghệ sử dụng theo vai trò

**Nội dung đưa lên slide**

- **Backend nghiệp vụ**: FastAPI, Python, JWT authentication.
- **Điều phối AI/RAG**: LangGraph, Agentic RAG, tool calling, Verifier.
- **Lưu trữ dữ liệu**: PostgreSQL cho tài khoản và hội thoại; MongoDB cho điều luật; ChromaDB cho vector chunks.
- **Ứng dụng người dùng**: Kotlin Multiplatform cho Mobile App.
- **Trang quản trị**: Next.js cho Web Admin, dashboard và upload văn bản.
- **Tích hợp ngoài**: LLMs, web search, cloud storage.

**Gợi ý visual/layout**

Chia thành 5 nhóm ngang hoặc dạng stack: Client, Backend, AI/RAG, Database, External Services. Mỗi nhóm có 2-3 logo/icon nhỏ, không cần quá nhiều text.

**Ghi chú thuyết trình**

Các công nghệ được lựa chọn theo đúng vai trò dữ liệu và nghiệp vụ. PostgreSQL phù hợp dữ liệu quan hệ như người dùng, phiên đăng nhập và hội thoại; MongoDB phù hợp lưu điều luật có cấu trúc linh hoạt; ChromaDB phục vụ truy hồi ngữ nghĩa bằng embedding.

---

## Slide 7. Kiến trúc tổng quan hệ thống

**Mục đích slide**

Cho Hội đồng thấy cách các thành phần chính kết nối với nhau trước khi đi sâu vào từng luồng.

**Tiêu đề đưa lên slide**

Kiến trúc tổng quan hệ thống

**Nội dung đưa lên slide**

- Mobile App và Web Admin giao tiếp với Main Service qua API có xác thực.
- Main Service xử lý nghiệp vụ, tài khoản, hội thoại, upload và điều phối request.
- RAG Service là service nội bộ, phụ trách Agentic RAG, embedding, truy hồi và ingestion.
- PostgreSQL, MongoDB và ChromaDB được tách theo từng loại dữ liệu.
- LLMs và nguồn tìm kiếm ngoài được gọi qua RAG Service khi cần bổ sung bằng chứng.

**Sơ đồ gợi ý trên slide**

Mobile App / Web Admin  
→ Main Service  
→ RAG Service  
→ PostgreSQL / MongoDB / ChromaDB / LLMs / Web Search

**Gợi ý visual/layout**

Vẽ sơ đồ khối từ trái sang phải. Client ở bên trái, hai service ở giữa, database và nguồn ngoài ở bên phải. Nhấn rõ rằng client không gọi trực tiếp RAG Service.

**Ghi chú thuyết trình**

Kiến trúc được tách thành Main Service và RAG Service để cô lập phần nghiệp vụ thông thường với workload AI. RAG Service có nhu cầu tài nguyên riêng vì phải tải embedding model, kết nối vector database và chạy luồng Agentic RAG.

---

## Slide 8. Xây dựng kho dữ liệu vector pháp luật ban đầu

**Mục đích slide**

Nhấn mạnh kho vector ban đầu là nền tảng trước khi xây dựng Agentic RAG và các tính năng chat.

**Tiêu đề đưa lên slide**

Xây dựng kho dữ liệu vector pháp luật ban đầu

**Nội dung đưa lên slide**

- Dữ liệu pháp luật ban đầu được chuẩn hóa thành các article có metadata.
- MongoDB lưu khoảng **528.620 điều luật** để phục vụ tra cứu và quản lý nội dung.
- Các điều luật được chia chunk, tạo embedding và lưu vào ChromaDB.
- ChromaDB collection `vietnamese_law` lưu khoảng **690.360 vector chunks**.
- Mỗi vector có **768 chiều**, phục vụ tìm kiếm ngữ nghĩa cho RAG.

**Pipeline đưa lên slide**

Dữ liệu pháp luật → Chuẩn hóa article/metadata → Chunking → Embedding → ChromaDB

**Gợi ý visual/layout**

Dùng pipeline ngang 5 bước, mỗi bước là một icon. Ở góc phải có 2 số liệu lớn: 528.620 articles và 690.360 chunks.

**Ghi chú thuyết trình**

Kho vector này được xây dựng từ đầu, trước khi hệ thống vận hành luồng chat. Đây là nguồn tri thức nội bộ để Agent có thể truy hồi quy định pháp luật khi người dùng đặt câu hỏi. Sau này, luồng upload văn bản mới của Admin chỉ là cơ chế cập nhật mở rộng cho kho dữ liệu đã có.

---

## Slide 9. Chiến lược chunking và metadata cho văn bản pháp luật

**Mục đích slide**

Giải thích vì sao xử lý văn bản pháp luật không thể chỉ tách đoạn tùy ý.

**Tiêu đề đưa lên slide**

Chunking và metadata cho văn bản pháp luật

**Nội dung đưa lên slide**

- Điều luật ngắn được giữ gần như nguyên vẹn để không mất ý nghĩa pháp lý.
- Điều luật dài được chia thành chunk tối đa **1.000 từ**.
- Overlap **150 từ** giúp giữ ngữ cảnh ở ranh giới giữa hai chunk.
- Mỗi chunk được gắn metadata như `law_id`, `article_id`, `title`, `year`, `topics`, `keywords`, `summary`.
- Metadata giúp truy hồi đúng nguồn, hiển thị trích dẫn và phân biệt văn bản cũ - mới.

**Câu nhấn mạnh trên slide**

Chunk không chỉ để giảm độ dài văn bản, mà còn để giữ đúng ngữ cảnh pháp lý khi truy hồi.

**Gợi ý visual/layout**

Hiển thị một điều luật dài được chia thành 3 chunk, phía dưới mỗi chunk có các tag metadata nhỏ. Dùng màu nhấn nhẹ cho phần overlap giữa các chunk.

**Ghi chú thuyết trình**

Nếu chunk quá ngắn, hệ thống có thể mất điều kiện áp dụng hoặc mức xử phạt đi kèm. Nếu chunk quá dài, embedding sẽ kém đặc trưng và kết quả tìm kiếm dễ nhiễu. Vì vậy, chiến lược chunking phải cân bằng giữa độ đầy đủ ngữ cảnh và độ chính xác khi truy hồi.

---

## Slide 10. Cơ chế truy hồi trong kho vector

**Mục đích slide**

Trình bày cách hệ thống chọn nguồn pháp luật trước khi Agent tổng hợp câu trả lời.

**Tiêu đề đưa lên slide**

Cơ chế truy hồi trong kho vector

**Nội dung đưa lên slide**

- Query của người dùng được mã hóa thành vector để tìm kiếm theo ngữ nghĩa.
- ChromaDB thực hiện vector search và lấy tập ứng viên ban đầu.
- Hệ thống lấy **top-60 chunks** để tăng khả năng không bỏ sót nguồn liên quan.
- Cross-encoder reranking chấm lại tối đa **40 ứng viên** có triển vọng.
- Blended score và ngưỡng tin cậy được dùng để chọn nguồn đưa vào Agent.

**Pipeline đưa lên slide**

Query → Vector Search → Top-60 Candidates → Cross-encoder Reranking → Blended Score → Top Sources

**Gợi ý visual/layout**

Dùng pipeline dạng "lọc rộng trước, chấm sâu sau". Bước Vector Search có phễu lớn, bước Reranking thu nhỏ lại còn vài nguồn tốt nhất.

**Ghi chú thuyết trình**

Vector search giúp tìm nhanh trong hàng trăm nghìn chunks, nhưng kết quả có thể còn nhiễu. Cross-encoder chấm lại cặp query-document kỹ hơn, nhờ đó tăng độ chính xác của nguồn trước khi câu trả lời được sinh ra.

---

## Slide 11. Luồng chat chính với LangGraph

**Mục đích slide**

Mô tả luồng trọng tâm nhất của hệ thống: người dùng hỏi, Agent truy hồi, Verifier kiểm chứng.

**Tiêu đề đưa lên slide**

Luồng chat chính với LangGraph

**Nội dung đưa lên slide**

- LangGraph tổ chức pipeline chat thành đồ thị có trạng thái.
- Guardrail kiểm tra câu hỏi đầu vào trước khi xử lý sâu hơn.
- Query Analysis tạo truy vấn phù hợp cho từng nguồn tìm kiếm.
- Agent gọi công cụ để thu thập bằng chứng pháp luật.
- Verifier kiểm chứng câu trả lời cuối cùng trước khi trả về người dùng.

**Graph đưa lên slide**

START → Guardrail → Query Analysis → Agent ↔ Tools → Verifier → END

**Gợi ý visual/layout**

Vẽ graph ở giữa slide. Vòng lặp Agent ↔ Tools nên nổi bật vì đây là điểm khác biệt so với pipeline tuyến tính.

**Ghi chú thuyết trình**

LangGraph giúp hệ thống kiểm soát rõ từng bước thay vì để LLMs tự xử lý toàn bộ trong một prompt. State của graph lưu lại câu hỏi, kết quả phân tích, tài liệu truy hồi, số vòng lặp và trạng thái kiểm tra, từ đó các node có thể phối hợp với nhau nhất quán.

---

## Slide 12. Các node quan trọng trong LangGraph

**Mục đích slide**

Giải thích trách nhiệm của từng node để người nghe hiểu vì sao luồng chat đáng tin hơn.

**Tiêu đề đưa lên slide**

Vai trò từng node trong Agentic RAG

**Nội dung đưa lên slide**

- **Guardrail**: kiểm soát câu hỏi ngoài phạm vi hoặc không phù hợp.
- **Query Analysis**: phân tích ý định và tạo truy vấn tối ưu cho từng nguồn.
- **Agent**: quyết định gọi công cụ nào để thu thập bằng chứng.
- **Tools**: truy hồi kho luật nội bộ và tìm nguồn cập nhật khi cần.
- **Verifier**: kiểm tra điều khoản, số liệu, nguồn dẫn và tính nhất quán của câu trả lời.

**Câu nhấn mạnh trên slide**

Agent tạo câu trả lời, nhưng Verifier mới là lớp kiểm tra cuối cùng trước khi phản hồi.

**Gợi ý visual/layout**

Dùng 5 card theo thứ tự xử lý. Card Verifier nên dùng icon check/shield để thể hiện vai trò kiểm chứng.

**Ghi chú thuyết trình**

Điểm quan trọng là hệ thống không chỉ dựa vào một lần sinh câu trả lời. Agent phải làm việc với công cụ truy hồi, còn Verifier kiểm tra lại câu trả lời dựa trên nguồn. Thiết kế này phù hợp với domain pháp luật vì câu trả lời cần đúng căn cứ, không chỉ nghe hợp lý.

---

## Slide 13. Xử lý luật cũ và luật mới

**Mục đích slide**

Làm nổi bật bài toán đặc thù của pháp luật: quy định thay đổi theo thời gian.

**Tiêu đề đưa lên slide**

Xử lý xung đột giữa luật cũ và luật mới

**Nội dung đưa lên slide**

- Một chủ đề pháp luật có thể xuất hiện trong nhiều văn bản ở các năm khác nhau.
- Vector search có thể trả về cả văn bản cũ và văn bản mới vì nội dung gần nghĩa.
- Hệ thống sử dụng metadata như năm ban hành, chủ đề và từ khóa để phát hiện nhóm có khả năng xung đột.
- Văn bản mới hơn được ưu tiên khi có dấu hiệu thay thế hoặc cập nhật quy định.
- Verifier kiểm tra lại để tránh dùng nhầm con số hoặc căn cứ từ văn bản cũ.

**Ví dụ ngắn trên slide**

NĐ 100/2019 và NĐ 168/2024 trong nhóm câu hỏi về xử phạt giao thông.

**Câu nhấn mạnh trên slide**

Tìm đúng chủ đề chưa đủ; hệ thống phải ưu tiên đúng quy định hiện hành.

**Gợi ý visual/layout**

Dùng timeline 2019 → 2024. Văn bản cũ dùng màu xám/cam nhạt; văn bản mới dùng màu chủ đạo. Đặt Verifier ở cuối timeline như lớp xác nhận.

**Ghi chú thuyết trình**

Trong thử nghiệm, nhóm câu hỏi về xung đột luật cũ - luật mới là nhóm rất quan trọng. Nếu chỉ sắp xếp theo semantic score, văn bản cũ có thể vẫn được xếp cao. Vì vậy, hệ thống bổ sung xử lý theo thời gian và kiểm chứng lại trước khi trả lời.

---

## Slide 14. Luồng upload văn bản mới của Admin

**Mục đích slide**

Trình bày cách hệ thống cập nhật tri thức mới sau khi đã có kho vector ban đầu.

**Tiêu đề đưa lên slide**

Luồng cập nhật văn bản mới phía Admin

**Nội dung đưa lên slide**

- Admin upload file PDF văn bản pháp luật trên Web Admin.
- Main Service tạo task xử lý để theo dõi trạng thái.
- Hệ thống trích xuất nội dung, cấu trúc hóa thành các điều luật.
- MongoDB lưu article đầy đủ để quản lý và tra cứu.
- RAG Service chunk, embedding và upsert dữ liệu vào ChromaDB.
- Nếu lỗi ở các bước cuối, hệ thống rollback để tránh lệch dữ liệu giữa MongoDB và ChromaDB.

**Pipeline đưa lên slide**

Upload PDF → Create Task → Parse/Structure → Save MongoDB → Chunk/Embedding → Upsert ChromaDB → Complete/Failed

**Gợi ý visual/layout**

Dùng pipeline dạng document processing. Nên có hai database ở cuối: MongoDB cho article, ChromaDB cho vector chunks. Trạng thái task đặt ở phía dưới pipeline.

**Ghi chú thuyết trình**

Luồng upload Admin không thay thế kho dữ liệu ban đầu, mà là cơ chế mở rộng và cập nhật tri thức. Một văn bản chỉ được xem là xử lý thành công khi nội dung đã có trong MongoDB, vector đã có trong ChromaDB và trạng thái quản trị được cập nhật nhất quán.

---

## Slide 15. Luồng tư vấn có hướng dẫn

**Mục đích slide**

Giải thích tính năng giúp người dùng phổ thông cung cấp đủ ngữ cảnh trước khi hệ thống trả lời.

**Tiêu đề đưa lên slide**

Luồng tư vấn có hướng dẫn

**Nội dung đưa lên slide**

- Nhiều câu hỏi pháp luật ban đầu thường thiếu dữ kiện quan trọng.
- Hệ thống chủ động hỏi làm rõ bằng các lựa chọn cụ thể.
- Người dùng bổ sung thông tin như loại phương tiện, độ tuổi, tình huống, giấy tờ hoặc vai trò liên quan.
- Câu hỏi sau khi làm rõ được đưa vào pipeline RAG để truy hồi và kiểm chứng.
- Cách làm này giảm suy đoán và giúp câu trả lời sát tình huống hơn.

**Flow đưa lên slide**

Câu hỏi ban đầu → Hỏi làm rõ → Người dùng bổ sung → Truy hồi theo ngữ cảnh → Câu trả lời có căn cứ

**Ví dụ ngắn trên slide**

"Vượt đèn đỏ phạt bao nhiêu?" cần làm rõ loại phương tiện và tình huống vi phạm.

**Gợi ý visual/layout**

Dùng layout hội thoại 3 bước hoặc mockup mobile. Có thể đặt câu hỏi gốc bên trái, câu hỏi làm rõ ở giữa, câu trả lời cuối cùng bên phải.

**Ghi chú thuyết trình**

Guided Consultation phù hợp với người dùng không biết mình cần cung cấp thông tin gì. Thay vì trả lời chung chung, hệ thống hỏi lại để thu thập dữ kiện quyết định, sau đó mới truy hồi và tổng hợp câu trả lời.

---

## Slide 16. Demo giao diện và tính năng chính

**Mục đích slide**

Cho thấy hệ thống đã được triển khai thành sản phẩm có giao diện người dùng và trang quản trị.

**Tiêu đề đưa lên slide**

Demo giao diện và tính năng chính

**Nội dung đưa lên slide**

- **Mobile App**: chat tư vấn pháp luật, hiển thị tiến trình xử lý và nguồn tham chiếu.
- **Tư vấn có hướng dẫn**: hỏi làm rõ trước khi đưa ra câu trả lời.
- **Tra cứu văn bản**: tìm kiếm văn bản pháp luật theo ngôn ngữ tự nhiên.
- **Web Admin**: dashboard, quản lý văn bản, upload PDF và theo dõi trạng thái xử lý.

**Gợi ý visual/layout**

Ghép 3 ảnh/mockup chính:

- Màn hình chat hoặc ThinkingPanel.
- Màn hình tư vấn có hướng dẫn.
- Màn hình Web Admin upload/dashboard.

Nên đặt ảnh trong mockup điện thoại/laptop, hạn chế text dài.

**Ghi chú thuyết trình**

Sản phẩm được triển khai ở cả phía người dùng cuối và phía quản trị. Người dùng có thể chat, tra cứu và dùng luồng tư vấn có hướng dẫn; quản trị viên có thể cập nhật văn bản mới để mở rộng kho tri thức cho hệ thống.

---

## Slide 17. Đánh giá hệ thống

**Mục đích slide**

Tóm tắt kết quả đánh giá, đồng thời thể hiện khách quan các hạn chế còn tồn tại.

**Tiêu đề đưa lên slide**

Đánh giá hệ thống

**Nội dung đưa lên slide**

- Bộ kiểm thử gồm **60 câu hỏi**.
- **Accuracy@1: 90,0%** trên nhóm câu hỏi factual.
- **Answer Quality: 3,67/5,0** theo đánh giá chất lượng câu trả lời.
- **Temporal Conflict OK: 3/3**, hệ thống xử lý đúng nhóm luật cũ - luật mới.
- **Citation Accuracy: 56,7%**, phản ánh hạn chế về nguồn trích dẫn nội bộ.
- **Latency P50: 65,5s**, **P95: 100,6s** cho toàn bộ pipeline trả lời.

**Câu kết trên slide**

Kết quả cho thấy hướng Agentic RAG phù hợp, nhưng cần tiếp tục tối ưu độ trễ và chất lượng trích dẫn.

**Gợi ý visual/layout**

Dùng metric cards. Các chỉ số tốt dùng xanh/teal; hạn chế về citation và latency dùng vàng/cam để thể hiện còn cần cải thiện.

**Ghi chú thuyết trình**

Kết quả nổi bật là hệ thống đạt Accuracy@1 90,0% và xử lý đúng toàn bộ nhóm xung đột luật cũ - luật mới trong bộ kiểm thử. Tuy nhiên Citation Accuracy và latency vẫn là hai điểm cần cải thiện, nhất là khi kho dữ liệu nội bộ chưa index đầy đủ mọi văn bản mới hoặc pipeline Agentic RAG phải chạy nhiều bước kiểm chứng.

---

## Slide 18. Kết luận và hướng phát triển

**Mục đích slide**

Khép lại bài trình bày bằng đóng góp chính và định hướng phát triển tiếp theo.

**Tiêu đề đưa lên slide**

Kết luận và hướng phát triển

**Nội dung đưa lên slide**

**Kết quả đạt được**

- Xây dựng kho tri thức pháp luật phục vụ truy hồi ngữ nghĩa.
- Thiết kế luồng chat Agentic RAG có bước kiểm chứng.
- Bổ sung cơ chế xử lý luật cũ - luật mới trong truy hồi.
- Xây dựng luồng Admin upload văn bản mới và đồng bộ vào kho dữ liệu.
- Hoàn thiện sản phẩm demo gồm Mobile App và Web Admin.

**Hướng phát triển**

- Tối ưu độ trễ của pipeline trả lời.
- Mở rộng và cập nhật đầy đủ hơn kho dữ liệu pháp luật.
- Cải thiện độ chính xác nguồn trích dẫn.
- Mở rộng bộ benchmark đánh giá theo nhiều nhóm câu hỏi pháp lý.

**Gợi ý visual/layout**

Dùng 2 cột: "Đã thực hiện" và "Phát triển tiếp". Cuối slide có dòng "Em xin trân trọng cảm ơn Quý Thầy/Cô đã lắng nghe".

**Ghi chú thuyết trình**

Tổng kết lại, đồ án đã xây dựng được một hệ thống trợ lý pháp luật theo hướng Agentic RAG, có nguồn dữ liệu nội bộ, có truy hồi vector, có kiểm chứng câu trả lời và có cơ chế cập nhật tri thức mới. Trong thời gian tiếp theo, em sẽ tập trung tối ưu hiệu năng, mở rộng dữ liệu và nâng cao chất lượng trích dẫn để hệ thống phù hợp hơn với triển khai thực tế.

---

## Gợi ý phân bổ thời gian 12-15 phút

- Slide 1-4: khoảng 2-3 phút.
- Slide 5-7: khoảng 2-3 phút.
- Slide 8-15: khoảng 7-8 phút, đây là phần trọng tâm.
- Slide 16: khoảng 1 phút.
- Slide 17-18: khoảng 2 phút.

Nếu cần rút ngắn khi trình bày, có thể nói nhanh slide 6 và slide 16. Không nên cắt ngắn các slide 8-15 vì đây là phần giải thích kỹ thuật chính của đồ án.
