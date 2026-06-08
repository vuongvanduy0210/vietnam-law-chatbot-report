# Thiết kế lại nội dung slide theo khung bài mẫu HVGiang

Tài liệu này thiết kế lại bài trình bày dựa theo khung sườn của file `Final Project Presentation_HVGiang.pptx`. Deck mẫu có nhịp trình bày theo 4 phần lớn:

1. Phát biểu bài toán
2. Cơ sở lý thuyết
3. Xây dựng hệ thống
4. Thực nghiệm và kết luận

Với đồ án "Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số", nên giữ đúng logic 4 phần này để bài trình bày giống phong cách báo cáo mẫu, nhưng nội dung bên trong cần tập trung vào các điểm mạnh riêng của đề tài: kho dữ liệu vector pháp luật, Agentic RAG với LangGraph, truy hồi và kiểm chứng nguồn, cập nhật văn bản mới phía Admin, tư vấn có hướng dẫn và đánh giá hệ thống.

---

## 1. Khung bài mẫu cần học theo

Deck mẫu không trình bày theo kiểu liệt kê tính năng ngay từ đầu. Bài mẫu đi theo mạch:

- Mở đầu bằng lý do chọn đề tài và mục tiêu.
- Sau đó trình bày cơ sở lý thuyết đủ để người nghe hiểu các khái niệm chính.
- Phần lớn thời lượng dành cho xây dựng hệ thống: môi trường của Agent, mô hình tổng quan, đồ thị xử lý, các node/thành phần, chức năng hệ thống.
- Cuối cùng là demo, thực nghiệm, kết luận, hạn chế và hướng phát triển.

Điểm nên áp dụng cho bài của bạn:

- Có slide chia chương rõ ràng, giống dạng "1. PHÁT BIỂU BÀI TOÁN", "2. CƠ SỞ LÝ THUYẾT".
- Không mở đầu bằng quá nhiều chi tiết code.
- Cơ sở lý thuyết chỉ trình bày khái niệm cần thiết để dẫn vào hệ thống.
- Phần xây dựng hệ thống là phần dài nhất, có nhiều sơ đồ.
- Phần thực nghiệm cần có bộ dữ liệu đánh giá, chỉ số, kết quả và nhận xét.

Điểm cần điều chỉnh so với bài mẫu:

- Deck mẫu có 51 slide, quá dài cho thời lượng 12-15 phút. Bài của bạn nên nằm trong khoảng 18-20 slide.
- Không nên đưa quá nhiều slide giải thích từng node nhỏ như bài mẫu, vì hệ thống của bạn có nhiều luồng trọng tâm hơn.
- Không nên đưa các placeholder như "MAJOR: INTERIOR DESIGN"; khi dùng Canva cần thay toàn bộ bằng nhận diện của Học viện/Khoa/đề tài.
- Không nên trình bày tên model cụ thể nếu không cần; dùng LLMs, Agent model hoặc Verifier cho tổng quát.

---

## 2. Cấu trúc đề xuất theo 4 phần lớn

### Phần 1. Phát biểu bài toán

**Số slide gợi ý:** 4 slide

**Mục tiêu phần này**

Giúp Hội đồng hiểu bài toán xuất phát từ nhu cầu thực tế nào, vì sao lĩnh vực pháp luật khó xử lý bằng chatbot thông thường và đề tài đặt ra mục tiêu gì.

**Nội dung nên có**

- Trang bìa.
- Nội dung trình bày.
- Lý do chọn đề tài.
- Mục tiêu đề tài.

**Thông điệp chính**

Người dùng cần một công cụ hỗ trợ tra cứu và tư vấn pháp luật dễ tiếp cận, nhưng câu trả lời pháp luật phải có căn cứ, có nguồn và có khả năng xử lý thay đổi của văn bản pháp luật theo thời gian.

**Nội dung chi tiết**

Lý do chọn đề tài nên nhấn vào 4 vấn đề:

- Hệ thống văn bản pháp luật có khối lượng lớn, cấu trúc dài và nhiều điều khoản.
- Một quy định có thể thay đổi, bị thay thế hoặc được cập nhật bởi văn bản mới.
- Người dùng phổ thông khó xác định văn bản nào đang còn hiệu lực và khó chọn từ khóa tra cứu đúng.
- LLMs thuần có thể trả lời linh hoạt nhưng vẫn có nguy cơ thiếu căn cứ, trích dẫn sai hoặc tạo câu trả lời khó kiểm chứng.

Mục tiêu đề tài nên trình bày theo 5 ý tổng quan:

- Xây dựng hệ thống hỗ trợ người dùng tra cứu và tư vấn pháp luật bằng ngôn ngữ tự nhiên.
- Cung cấp câu trả lời có căn cứ, có nguồn tham chiếu và phù hợp với ngữ cảnh câu hỏi.
- Tổ chức kho tri thức pháp luật để hệ thống có thể tìm kiếm, truy hồi và cập nhật dữ liệu.
- Triển khai sản phẩm ở cả phía người dùng cuối và phía quản trị viên.
- Đánh giá khả năng trả lời, độ tin cậy và các hạn chế của hệ thống trong quá trình thử nghiệm.

**Gợi ý visual**

- Slide bìa: tên đề tài lớn, visual pháp luật + AI/chatbot + vector network.
- Slide nội dung: 4 phần lớn giống bài mẫu.
- Slide lý do: 4 problem cards.
- Slide mục tiêu: 5 goal cards hoặc sơ đồ mục tiêu trung tâm.

---

### Phần 2. Cơ sở lý thuyết

**Số slide gợi ý:** 4 slide

**Mục tiêu phần này**

Giới thiệu ngắn gọn các khái niệm nền tảng giống cách trình bày trong bài mẫu. Phần này chưa cần đi sâu vào nội dung chính của hệ thống, mà chỉ cần tạo nền để người nghe hiểu chatbot, LLMs, AI Agent và LangGraph là gì.

**Nội dung nên có**

- Khái niệm chatbot.
- Một số phương pháp xây dựng chatbot.
- LLMs và vai trò trong chatbot hiện đại.
- AI Agent và khả năng sử dụng công cụ.
- LangGraph và đồ thị có trạng thái.

**Thông điệp chính**

Các hệ thống chatbot hiện đại không chỉ phản hồi theo kịch bản cố định, mà có thể kết hợp LLMs, AI Agent và graph xử lý để hiểu yêu cầu, lập luận và điều phối công cụ.

**Nội dung chi tiết**

Slide về chatbot:

- Chatbot là hệ thống phần mềm mô phỏng hội thoại với người dùng thông qua văn bản hoặc giọng nói.
- Chatbot có thể tiếp nhận câu hỏi, phân tích đầu vào và tự động sinh phản hồi.
- Trong các hệ thống hiện đại, chatbot thường được kết hợp với mô hình ngôn ngữ lớn hoặc nguồn dữ liệu riêng để tăng khả năng hiểu ngữ cảnh.

Slide về các phương pháp xây dựng chatbot:

- Chatbot dựa trên luật/kịch bản: dễ kiểm soát nhưng thiếu linh hoạt.
- Chatbot dựa trên LLMs: hiểu ngôn ngữ tự nhiên tốt hơn và trả lời linh hoạt hơn.
- Chatbot theo hướng AI Agent: có thể sử dụng công cụ, truy vấn dữ liệu và lập kế hoạch xử lý để trả lời các yêu cầu phức tạp hơn.

Slide về LLMs và AI Agent:

- LLMs là các mô hình ngôn ngữ lớn có khả năng xử lý, hiểu và tạo sinh ngôn ngữ tự nhiên.
- AI Agent là hệ thống có khả năng nhận yêu cầu, phân tích trạng thái hiện tại, lựa chọn hành động phù hợp và sử dụng công cụ để đạt mục tiêu.
- Trong chatbot hiện đại, LLMs thường đóng vai trò là thành phần lập luận chính của Agent.

Slide về LangGraph:

- LangGraph cho phép mô hình hóa luồng xử lý thành graph gồm node, edge và state.
- Node tương ứng với từng bước xử lý.
- Edge thể hiện hướng di chuyển giữa các node.
- State lưu thông tin xuyên suốt quá trình xử lý của Agent.
- Conditional edge giúp kiểm soát hướng đi của graph theo điều kiện.

**Gợi ý visual**

- Slide định nghĩa chatbot, có minh họa người dùng trò chuyện với hệ thống.
- Slide so sánh các hướng: rule-based chatbot, LLMs chatbot và AI Agent chatbot.
- Sơ đồ AI Agent tổng quát: yêu cầu đầu vào → LLMs suy luận → công cụ/dữ liệu → câu trả lời.
- Sơ đồ LangGraph đơn giản gồm node, edge, state và conditional edge, chưa cần đưa toàn bộ luồng hệ thống.

---

### Phần 3. Xây dựng hệ thống

**Số slide gợi ý:** 8-9 slide

**Mục tiêu phần này**

Đây là phần trọng tâm, tương đương phần "Xây dựng hệ thống" trong bài mẫu. Mạch trình bày nên đi theo hướng của AI Agent: xác định môi trường của Agent, mô hình tổng quan chatbot, hành trình một tin nhắn đi qua hệ thống, đồ thị xử lý, cách xây dựng node/state/edge, sau đó mới liệt kê các chức năng chính của toàn app.

**Nội dung nên có**

- Xác định môi trường của Agent cho bài toán pháp luật.
- Mô hình tổng quan của hệ thống chatbot.
- Mô hình chi tiết xử lý tin nhắn của người dùng.
- Đồ thị của hệ thống bằng LangGraph.
- Xây dựng các node chính trong graph.
- Xử lý state và cạnh điều kiện.
- Công cụ và nguồn dữ liệu của Agent.
- Các chức năng chính của toàn hệ thống.

**Thông điệp chính**

Hệ thống được xây dựng như một AI Agent phục vụ bài toán pháp luật: Agent nhận câu hỏi, quan sát môi trường dữ liệu, gọi công cụ truy hồi, cập nhật state qua từng node và chỉ trả lời sau khi đã có bước kiểm chứng.

**Nội dung chi tiết**

Xác định môi trường của Agent:

- Môi trường của Agent gồm câu hỏi người dùng, lịch sử hội thoại, kho dữ liệu pháp luật nội bộ, nguồn thông tin cập nhật bên ngoài và trạng thái xử lý hiện tại.
- Agent cần có khả năng truy hồi điều luật liên quan, kiểm tra thông tin theo thời gian và tổng hợp câu trả lời dễ hiểu cho người dùng phổ thông.
- Tập hành động chính của Agent gồm phân tích câu hỏi, tạo truy vấn tìm kiếm, gọi công cụ truy hồi, tổng hợp bằng chứng và chuyển câu trả lời sang bước kiểm chứng.
- Kết quả cuối cùng cần có câu trả lời, căn cứ pháp lý và nguồn tham chiếu phù hợp.

Mô hình tổng quan của hệ thống chatbot:

- Mobile App là giao diện chính cho người dùng cuối.
- Web Admin là giao diện cho quản trị viên quản lý và cập nhật dữ liệu pháp luật.
- Main Service xử lý nghiệp vụ, xác thực, hội thoại, upload văn bản và điều phối request.
- RAG Service xử lý LangGraph, Agentic RAG, embedding, truy hồi vector và kiểm chứng câu trả lời.
- PostgreSQL lưu dữ liệu người dùng và hội thoại.
- MongoDB lưu điều luật có cấu trúc.
- ChromaDB lưu vector chunks phục vụ tìm kiếm ngữ nghĩa.

Mô hình chi tiết xử lý tin nhắn:

- Người dùng gửi câu hỏi từ Mobile App.
- Main Service xác thực request, lưu hội thoại và gọi RAG Service.
- RAG Service chạy graph Agentic RAG.
- Guardrail kiểm tra tính hợp lệ của câu hỏi.
- Query Analysis phân tích câu hỏi và tạo truy vấn tìm kiếm.
- Agent gọi tools để truy hồi bằng chứng.
- Verifier kiểm chứng câu trả lời nháp.
- Main Service nhận kết quả và trả về giao diện người dùng.

Đồ thị của hệ thống:

- Đồ thị gồm các node chính: Guardrail, Query Analysis, Agent, Tools và Verifier.
- Luồng chính: START → Guardrail → Query Analysis → Agent ↔ Tools → Verifier → END.
- Mũi tên liền biểu diễn luồng xử lý chính.
- Vòng lặp Agent ↔ Tools biểu diễn quá trình Agent gọi công cụ để thu thập bằng chứng.
- Cạnh điều kiện quyết định kết thúc sớm, tiếp tục gọi tool hoặc chuyển sang Verifier.

Hướng dẫn vẽ đồ thị tương tự slide 3.3 trong bài mẫu:

- Dùng slide trắng hoặc nền rất nhạt.
- Đặt tên mục ở góc trên: `3.4. Đồ thị của hệ thống`.
- Dùng các box bo tròn hoặc capsule cho node, tương tự phong cách slide mẫu.
- Dùng mũi tên đen mảnh-vừa, rõ hướng đi.
- Node `Agent` đặt ở trung tâm vì đây là node điều phối.
- Node `Tools` đặt dưới hoặc bên cạnh Agent, nối bằng mũi tên hai chiều để thể hiện vòng lặp.
- Node `Verifier` đặt gần cuối luồng, trước `END`.
- Không đưa quá nhiều chữ trong box; mỗi box chỉ nên ghi tên node.
- Các ghi chú nhỏ có thể đặt bên cạnh mũi tên: `valid`, `need evidence`, `verified`.

Xây dựng các node chính:

- Guardrail kiểm tra câu hỏi ngoài phạm vi hoặc không phù hợp.
- Query Analysis phân tích ý định và tạo truy vấn tìm kiếm phù hợp.
- Agent điều phối quá trình gọi công cụ và thu thập bằng chứng.
- Tools thực hiện truy hồi kho luật nội bộ hoặc tìm kiếm nguồn cập nhật khi cần.
- Verifier kiểm tra căn cứ pháp lý, số liệu, nguồn trích dẫn và tính nhất quán.

Xử lý state và cạnh điều kiện:

- State lưu thông tin dùng chung giữa các node trong graph.
- State gồm tin nhắn hội thoại, kết quả phân tích câu hỏi, tài liệu truy hồi, số vòng lặp và trạng thái hợp lệ của truy vấn.
- Mỗi node đọc một phần state, xử lý nhiệm vụ của mình và cập nhật state cho node tiếp theo.
- Cạnh điều kiện giúp graph quyết định hướng đi: kết thúc sớm, quay lại Agent hoặc chuyển sang Verifier.

Công cụ và nguồn dữ liệu của Agent:

- Công cụ truy hồi nội bộ tìm điều luật trong kho dữ liệu đã vector hóa.
- Kho dữ liệu ban đầu gồm khoảng **528.620 điều luật** trong MongoDB và khoảng **690.360 vector chunks** trong ChromaDB.
- Vector search lấy tập ứng viên liên quan, sau đó hệ thống xếp hạng lại để chọn nguồn phù hợp hơn.
- Nguồn tìm kiếm bên ngoài được dùng khi cần bổ sung hoặc đối chiếu thông tin mới.

Các chức năng chính:

- Chat tư vấn pháp luật.
- Tư vấn có hướng dẫn.
- Tra cứu văn bản pháp luật bằng ngôn ngữ tự nhiên.
- Quản lý hội thoại và nguồn tham chiếu.
- Web Admin dashboard.
- Upload PDF và cập nhật kho tri thức.
- Theo dõi tiến trình xử lý văn bản mới.

**Gợi ý visual**

- Slide môi trường Agent: Agent ở trung tâm, xung quanh là User Query, Chat History, ChromaDB, MongoDB, Web Search, Admin Knowledge Update.
- Slide mô hình tổng quan: Mobile App/Web Admin → Main Service → RAG Service → PostgreSQL/MongoDB/ChromaDB/LLMs/Web Search.
- Slide luồng tin nhắn: User → Mobile App → Main Service → RAG Service → LangGraph → Main Service → Response.
- Slide đồ thị hệ thống: START → Guardrail → Query Analysis → Agent ↔ Tools → Verifier → END, phong cách box bo tròn giống slide mẫu.
- Slide node: 5 card cho Guardrail, Query Analysis, Agent, Tools, Verifier.
- Slide state/edge: một khối State ở giữa, các node xung quanh đọc/ghi state; cạnh điều kiện thể hiện các nhánh xử lý.
- Slide chức năng: chia thành Mobile App và Web Admin.

**Ghi chú thuyết trình**

Phần này nên chiếm nhiều thời gian nhất, khoảng 7-8 phút. Khi trình bày, nên đi theo câu chuyện của Agent: Agent hoạt động trong môi trường nào, nhận tin nhắn ra sao, graph điều phối như thế nào, state được cập nhật qua từng node ra sao và cuối cùng hệ thống cung cấp những chức năng nào cho người dùng và quản trị viên.

---

### Phần 4. Thực nghiệm và kết luận

**Số slide gợi ý:** 4-5 slide

**Mục tiêu phần này**

Phần này cần chứng minh hệ thống đã được triển khai, có demo, có đánh giá định lượng và có nhận xét khách quan về kết quả.

**Nội dung nên có**

- Demo các chức năng.
- Bộ dữ liệu và phương pháp đánh giá.
- Kết quả thực nghiệm.
- Kết luận, hạn chế và hướng phát triển.
- Lời cảm ơn/Q&A.

**Thông điệp chính**

Kết quả thực nghiệm cho thấy hướng Agentic RAG phù hợp với bài toán tư vấn pháp luật, đặc biệt ở nhóm câu hỏi cần xử lý luật cũ - luật mới; tuy nhiên hệ thống vẫn cần cải thiện độ trễ và chất lượng trích dẫn nguồn.

**Nội dung chi tiết**

Demo chức năng:

- Mobile App: chat tư vấn pháp luật, hiển thị tiến trình xử lý và nguồn tham chiếu.
- Tư vấn có hướng dẫn: hỏi làm rõ trước khi trả lời.
- Tra cứu văn bản: tìm kiếm pháp luật bằng ngôn ngữ tự nhiên.
- Web Admin: dashboard, quản lý văn bản, upload PDF và theo dõi trạng thái xử lý.

Bộ dữ liệu và phương pháp đánh giá:

- Bộ kiểm thử gồm **60 câu hỏi**.
- Nhóm câu hỏi factual dùng để đo Accuracy@1 và Citation Accuracy.
- Nhóm câu hỏi đánh giá chất lượng câu trả lời dùng thang điểm Answer Quality.
- Nhóm câu hỏi luật cũ - luật mới dùng để kiểm tra Temporal Conflict.
- Độ trễ được đo theo P50 và P95 cho toàn bộ pipeline trả lời.

Kết quả thực nghiệm:

- **Accuracy@1: 90,0%** trên nhóm câu hỏi factual.
- **Answer Quality: 3,67/5,0**.
- **Temporal Conflict OK: 3/3**, hệ thống xử lý đúng nhóm luật cũ - luật mới.
- **Citation Accuracy: 56,7%**, phản ánh hạn chế về nguồn trích dẫn nội bộ.
- **Latency P50: 65,5s**, **P95: 100,6s**.

Kết luận:

- Đề tài đã xây dựng được kho tri thức pháp luật phục vụ truy hồi ngữ nghĩa.
- Đề tài đã thiết kế luồng chat Agentic RAG có bước kiểm chứng.
- Hệ thống có cơ chế xử lý luật cũ - luật mới.
- Hệ thống hỗ trợ cập nhật văn bản mới từ Web Admin và đồng bộ vào kho dữ liệu.
- Sản phẩm demo gồm Mobile App và Web Admin, thể hiện được các luồng chính.

Hạn chế và hướng phát triển:

- Cần tối ưu độ trễ của pipeline Agentic RAG.
- Cần mở rộng và cập nhật đầy đủ hơn kho dữ liệu pháp luật.
- Cần cải thiện độ chính xác nguồn trích dẫn.
- Cần mở rộng bộ benchmark đánh giá theo nhiều nhóm câu hỏi pháp lý.

**Gợi ý visual**

- Slide demo: 3 mockup gồm Mobile chat, Guided Consultation và Web Admin.
- Slide đánh giá: metric cards.
- Slide kết luận: hai cột "Kết quả đạt được" và "Hướng phát triển".
- Slide cảm ơn: thiết kế đơn giản, có Q&A.

---

## 3. Phân bổ thành deck 18-20 slide

Dưới đây là phương án cụ thể để Canva dựng deck theo đúng khung bài mẫu nhưng không quá dài.

### Phần 1. Phát biểu bài toán

1. Trang bìa
2. Nội dung trình bày
3. Slide chuyển phần: 1. PHÁT BIỂU BÀI TOÁN
4. Lý do chọn đề tài
5. Mục tiêu đề tài

### Phần 2. Cơ sở lý thuyết

6. Slide chuyển phần: 2. CƠ SỞ LÝ THUYẾT
7. Chatbot
8. Một số phương pháp xây dựng chatbot
9. LLMs, AI Agent và LangGraph

### Phần 3. Xây dựng hệ thống

10. Slide chuyển phần: 3. XÂY DỰNG HỆ THỐNG
11. Xác định môi trường của Agent
12. Mô hình tổng quan của hệ thống chatbot
13. Luồng xử lý tin nhắn của người dùng
14. Đồ thị của hệ thống
15. Xây dựng các node trong hệ thống
16. Xử lý State và cạnh điều kiện
17. Công cụ và nguồn dữ liệu của Agent
18. Các chức năng chính của hệ thống

### Phần 4. Thực nghiệm và kết luận

19. Slide chuyển phần: 4. THỰC NGHIỆM VÀ KẾT LUẬN
20. Kết quả đánh giá hệ thống
21. Kết luận, hạn chế và hướng phát triển
22. Cảm ơn/Q&A

Nếu bắt buộc giữ trong 18 slide, có thể gộp:

- Slide 8 và 9 thành một slide "Phương pháp chatbot, LLMs và AI Agent".
- Slide 15 và 16 thành một slide "Node, State và cạnh điều kiện".
- Slide 21 và 22 thành một slide cuối "Kết luận và cảm ơn".

Khi đó deck sẽ có 18-19 slide nhưng vẫn giữ đúng khung sườn bài mẫu.

---

## 4. Nội dung có thể copy trực tiếp vào slide

Phần này viết theo dạng ngắn gọn để có thể copy nhanh vào Canva. Khi dựng slide, chỉ cần giữ lại các câu chính, không cần đưa toàn bộ ghi chú giải thích lên slide.

### Slide 1. Trang bìa

**Tiêu đề**

Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số

**Nội dung phụ**

Báo cáo đồ án tốt nghiệp đại học  
Sinh viên thực hiện: Vương Văn Duy  
Chuyên ngành: Công nghệ thông tin  
Định hướng: Agentic RAG, kho dữ liệu vector pháp luật, trợ lý tư vấn pháp luật

### Slide 2. Nội dung trình bày

**Tiêu đề**

Nội dung trình bày

**Nội dung**

1. Phát biểu bài toán  
2. Cơ sở lý thuyết  
3. Xây dựng hệ thống  
4. Thực nghiệm và kết luận

**Câu nhấn**

Trọng tâm bài báo cáo là cách hệ thống xây dựng kho tri thức pháp luật, truy hồi bằng RAG và kiểm chứng câu trả lời trước khi phản hồi người dùng.

### Slide 3. Phát biểu bài toán

**Tiêu đề**

1. Phát biểu bài toán

**Nội dung**

Phần này trình bày lý do lựa chọn đề tài và mục tiêu xây dựng hệ thống trợ lý ảo pháp luật trong bối cảnh chuyển đổi số.

### Slide 4. Lý do chọn đề tài

**Tiêu đề**

1.1. Lý do chọn đề tài

**Nội dung**

Văn bản pháp luật có khối lượng lớn, cấu trúc phức tạp và thường xuyên thay đổi theo thời gian.

Người dùng phổ thông thường gặp khó khăn khi xác định văn bản nào đang còn hiệu lực, điều khoản nào phù hợp với tình huống của mình và nên tra cứu bằng từ khóa nào.

Các LLMs thuần có khả năng trả lời linh hoạt, nhưng vẫn có nguy cơ đưa ra thông tin thiếu căn cứ, trích dẫn sai hoặc không thể kiểm chứng nguồn.

Vì vậy, cần xây dựng một hệ thống trợ lý pháp luật có khả năng truy hồi nguồn, tổng hợp câu trả lời và kiểm chứng kết quả trước khi phản hồi.

### Slide 5. Mục tiêu đề tài

**Tiêu đề**

1.2. Mục tiêu đề tài

**Nội dung**

Xây dựng hệ thống trợ lý ảo pháp luật hỗ trợ người dùng tra cứu và đặt câu hỏi bằng ngôn ngữ tự nhiên.

Cung cấp câu trả lời có căn cứ, có nguồn tham chiếu và phù hợp với ngữ cảnh pháp lý của người dùng.

Tổ chức kho tri thức pháp luật để hệ thống có thể tìm kiếm, truy hồi và cập nhật dữ liệu khi có văn bản mới.

Triển khai sản phẩm hoàn chỉnh gồm ứng dụng cho người dùng cuối và trang quản trị cho quản trị viên.

Đánh giá khả năng trả lời, độ tin cậy và các hạn chế của hệ thống thông qua quá trình thử nghiệm.

### Slide 6. Cơ sở lý thuyết

**Tiêu đề**

2. Cơ sở lý thuyết

**Nội dung**

Phần này trình bày các khái niệm nền tảng về chatbot, LLMs, AI Agent và LangGraph trước khi đi vào thiết kế hệ thống.

### Slide 7. Chatbot

**Tiêu đề**

2.1. Chatbot

**Nội dung**

Chatbot là hệ thống phần mềm được thiết kế để mô phỏng cuộc hội thoại với người dùng thông qua giao diện văn bản hoặc giọng nói.

Chatbot có thể tiếp nhận câu hỏi, phân tích nội dung đầu vào và tự động sinh phản hồi phù hợp với yêu cầu của người dùng.

Trong các hệ thống hiện đại, chatbot thường được kết hợp với mô hình ngôn ngữ lớn và các nguồn dữ liệu riêng để tăng khả năng hiểu ngữ cảnh.

Đối với bài toán tư vấn pháp luật, chatbot cần không chỉ trả lời tự nhiên mà còn phải gắn câu trả lời với thông tin có căn cứ.

### Slide 8. Một số phương pháp xây dựng chatbot

**Tiêu đề**

2.2. Một số phương pháp xây dựng chatbot

**Nội dung**

Chatbot dựa trên kịch bản hoặc tập luật hoạt động theo các luồng được chuẩn bị trước, dễ kiểm soát nhưng thiếu linh hoạt khi câu hỏi thay đổi.

Chatbot dựa trên LLMs có khả năng hiểu ngôn ngữ tự nhiên tốt hơn, trả lời linh hoạt hơn và phù hợp với nhiều cách diễn đạt khác nhau của người dùng.

Tuy nhiên, nếu chỉ dùng LLMs thuần, hệ thống có thể sinh ra thông tin không chính xác hoặc không dựa trên dữ liệu nội bộ.

Hướng tiếp cận AI Agent cho phép chatbot sử dụng thêm công cụ, truy vấn dữ liệu và lập kế hoạch xử lý để trả lời tốt hơn các yêu cầu phức tạp.

### Slide 9. LLMs, AI Agent và LangGraph

**Tiêu đề**

2.3. LLMs, AI Agent và LangGraph

**Nội dung**

LLMs là các mô hình ngôn ngữ lớn có khả năng xử lý, hiểu và tạo sinh ngôn ngữ tự nhiên.

AI Agent là hệ thống có khả năng nhận yêu cầu, phân tích trạng thái hiện tại, lựa chọn hành động phù hợp và sử dụng công cụ để đạt mục tiêu.

Trong các hệ thống chatbot hiện đại, LLMs thường đóng vai trò là thành phần lập luận chính của Agent.

LangGraph là framework hỗ trợ xây dựng AI Agent dưới dạng đồ thị, trong đó các node biểu diễn bước xử lý, các edge biểu diễn hướng di chuyển và state lưu trạng thái xuyên suốt quá trình thực hiện.

### Slide 10. Slide chuyển phần

**Tiêu đề**

3. Xây dựng hệ thống

**Nội dung**

Phần này trình bày cách xác định môi trường của Agent, mô hình tổng quan hệ thống chatbot, luồng xử lý tin nhắn, đồ thị LangGraph, cách xây dựng các node và các chức năng chính của toàn hệ thống.

---

### Slide 11. Xác định môi trường của Agent

**Tiêu đề**

3.1. Xác định môi trường của Agent cho bài toán pháp luật

**Nội dung**

Trong bài toán pháp luật, môi trường của Agent gồm câu hỏi người dùng, lịch sử hội thoại, kho dữ liệu pháp luật nội bộ, nguồn thông tin cập nhật bên ngoài và trạng thái xử lý hiện tại.

Agent cần có khả năng truy hồi điều luật liên quan, kiểm tra thông tin theo thời gian và tổng hợp câu trả lời dễ hiểu cho người dùng phổ thông.

Tập hành động chính của Agent gồm: phân tích câu hỏi, tạo truy vấn tìm kiếm, gọi công cụ truy hồi, tổng hợp bằng chứng và chuyển câu trả lời sang bước kiểm chứng.

Kết quả cuối cùng của Agent không chỉ là một đoạn văn trả lời, mà còn phải kèm căn cứ pháp lý và nguồn tham chiếu phù hợp.

---

### Slide 12. Mô hình tổng quan của hệ thống chatbot

**Tiêu đề**

3.2. Mô hình tổng quan của hệ thống chatbot

**Nội dung**

Người dùng tương tác với hệ thống thông qua Mobile App, còn quản trị viên sử dụng Web Admin để quản lý và cập nhật dữ liệu pháp luật.

Main Service đóng vai trò cổng nghiệp vụ, xử lý xác thực, hội thoại, upload văn bản và điều phối request giữa client với các service phía sau.

RAG Service là lõi xử lý AI, phụ trách LangGraph, Agentic RAG, embedding, truy hồi vector và kiểm chứng câu trả lời.

PostgreSQL lưu dữ liệu người dùng và hội thoại; MongoDB lưu điều luật có cấu trúc; ChromaDB lưu vector chunks phục vụ tìm kiếm ngữ nghĩa.

---

### Slide 13. Luồng xử lý tin nhắn của người dùng

**Tiêu đề**

3.3. Luồng xử lý tin nhắn của người dùng

**Nội dung**

Khi người dùng gửi câu hỏi, Mobile App chuyển tin nhắn đến Main Service để xác thực, lưu hội thoại và tạo request xử lý.

Main Service gọi RAG Service để chạy luồng Agentic RAG, trong đó câu hỏi được kiểm tra, phân tích và chuyển thành các truy vấn phù hợp.

Agent gọi các công cụ để truy hồi bằng chứng từ kho luật nội bộ và nguồn thông tin cập nhật khi cần.

Sau khi có câu trả lời nháp, Verifier kiểm tra lại tính đúng đắn, nguồn dẫn và sự nhất quán trước khi kết quả được trả về giao diện người dùng.

---

### Slide 14. Đồ thị của hệ thống

**Tiêu đề**

3.4. Đồ thị của hệ thống

**Nội dung**

Đồ thị xử lý của hệ thống được xây dựng bằng LangGraph, gồm các node chính: Guardrail, Query Analysis, Agent, Tools và Verifier.

Guardrail kiểm tra câu hỏi đầu vào; Query Analysis phân tích ý định và tạo truy vấn; Agent quyết định công cụ cần gọi; Tools thực hiện truy hồi; Verifier kiểm chứng câu trả lời.

Các cạnh trong graph biểu diễn hướng di chuyển giữa các bước xử lý. Một số cạnh là cạnh điều kiện, cho phép hệ thống quyết định tiếp tục gọi tool, chuyển sang kiểm chứng hoặc kết thúc luồng.

**Hướng dẫn vẽ trên slide**

Vẽ tương tự slide 3.3 trong bài mẫu: đặt các node theo chiều từ trên xuống hoặc trái sang phải, dùng khung bo tròn cho từng node, mũi tên liền cho luồng chính và mũi tên vòng lặp giữa Agent và Tools.

Sơ đồ gợi ý: START → Guardrail → Query Analysis → Agent ↔ Tools → Verifier → END.

---

### Slide 15. Xây dựng các node trong hệ thống

**Tiêu đề**

3.5. Xây dựng các node trong hệ thống

**Nội dung**

Node Guardrail có nhiệm vụ kiểm tra câu hỏi đầu vào, loại bỏ các yêu cầu không phù hợp hoặc nằm ngoài phạm vi tư vấn pháp luật.

Node Query Analysis phân tích câu hỏi của người dùng, xác định ý định truy vấn và tạo các truy vấn tìm kiếm phù hợp cho từng nguồn dữ liệu.

Node Agent điều phối quá trình thu thập bằng chứng, quyết định khi nào cần gọi công cụ truy hồi nội bộ hoặc tìm kiếm nguồn cập nhật.

Node Verifier kiểm tra câu trả lời cuối cùng về căn cứ pháp lý, số liệu, nguồn trích dẫn và tính nhất quán trước khi phản hồi người dùng.

---

### Slide 16. Xử lý State và cạnh điều kiện

**Tiêu đề**

3.6. Xử lý State và cạnh điều kiện

**Nội dung**

State là vùng lưu trữ trạng thái dùng chung giữa các node trong graph, giúp hệ thống theo dõi toàn bộ quá trình xử lý một câu hỏi.

State lưu các thông tin quan trọng như tin nhắn hội thoại, kết quả phân tích câu hỏi, tài liệu đã truy hồi, số vòng lặp xử lý và trạng thái hợp lệ của truy vấn.

Mỗi node đọc một phần state, thực hiện nhiệm vụ của mình và cập nhật lại state để node sau tiếp tục sử dụng.

Các cạnh điều kiện giúp graph quyết định hướng đi tiếp theo, ví dụ kết thúc sớm khi câu hỏi không hợp lệ, quay lại Agent khi chưa đủ bằng chứng hoặc chuyển sang Verifier khi đã có dữ liệu cần thiết.

---

### Slide 17. Các công cụ và nguồn dữ liệu của Agent

**Tiêu đề**

3.7. Công cụ và nguồn dữ liệu của Agent

**Nội dung**

Công cụ truy hồi nội bộ giúp Agent tìm kiếm các điều luật liên quan trong kho dữ liệu pháp luật đã được vector hóa.

Kho dữ liệu ban đầu gồm khoảng 528.620 điều luật trong MongoDB và khoảng 690.360 vector chunks trong ChromaDB.

Cơ chế truy hồi sử dụng vector search để lấy tập ứng viên, sau đó xếp hạng lại để chọn nguồn phù hợp hơn cho câu trả lời.

Nguồn tìm kiếm bên ngoài được sử dụng khi Agent cần bổ sung hoặc đối chiếu thông tin mới, đặc biệt với các quy định có thể thay đổi theo thời gian.

---

### Slide 18. Chức năng chính của toàn hệ thống

**Tiêu đề**

3.8. Các chức năng chính của hệ thống

**Nội dung**

Mobile App hỗ trợ chat tư vấn pháp luật, hiển thị tiến trình xử lý và nguồn tham chiếu cho câu trả lời.

Luồng tư vấn có hướng dẫn giúp người dùng bổ sung thông tin khi câu hỏi ban đầu còn thiếu ngữ cảnh.

Tính năng tra cứu văn bản cho phép tìm kiếm pháp luật bằng ngôn ngữ tự nhiên thay vì chỉ dựa vào từ khóa cứng.

Web Admin hỗ trợ dashboard, quản lý văn bản pháp luật, upload PDF và theo dõi trạng thái cập nhật dữ liệu vào kho tri thức.

---

### Slide 19. Thực nghiệm và kết luận

**Tiêu đề**

4. Thực nghiệm và kết luận

**Nội dung**

Phần này trình bày cách đánh giá hệ thống, kết quả thực nghiệm, các hạn chế còn tồn tại và hướng phát triển tiếp theo.

### Slide 20. Kết quả đánh giá hệ thống

**Tiêu đề**

4.1. Kết quả đánh giá hệ thống

**Nội dung**

Bộ kiểm thử gồm 60 câu hỏi, được dùng để đánh giá độ chính xác, chất lượng câu trả lời, khả năng xử lý luật cũ - luật mới và độ trễ phản hồi.

Hệ thống đạt Accuracy@1 là 90,0% trên nhóm câu hỏi factual.

Answer Quality đạt 3,67/5,0, cho thấy câu trả lời nhìn chung đáp ứng được yêu cầu tư vấn.

Temporal Conflict OK đạt 3/3, thể hiện hệ thống xử lý đúng nhóm câu hỏi có xung đột giữa luật cũ và luật mới.

Citation Accuracy đạt 56,7% và Latency P50 là 65,5 giây, đây là hai điểm cần tiếp tục cải thiện.

### Slide 21. Kết luận, hạn chế và hướng phát triển

**Tiêu đề**

4.2. Kết luận và hướng phát triển

**Nội dung**

Đề tài đã xây dựng được hệ thống trợ lý ảo pháp luật có kho tri thức vector, luồng Agentic RAG và bước kiểm chứng câu trả lời.

Hệ thống hỗ trợ các luồng chính gồm chat tư vấn pháp luật, tư vấn có hướng dẫn, tra cứu văn bản và cập nhật văn bản mới phía Admin.

Hạn chế hiện tại nằm ở độ trễ của pipeline Agentic RAG và độ chính xác nguồn trích dẫn nội bộ.

Trong hướng phát triển tiếp theo, hệ thống cần tối ưu thời gian phản hồi, mở rộng kho dữ liệu pháp luật, cải thiện chất lượng trích dẫn và xây dựng bộ benchmark đánh giá lớn hơn.

### Slide 22. Cảm ơn

**Tiêu đề**

Cảm ơn Thầy/Cô đã lắng nghe

**Nội dung**

Em xin trân trọng cảm ơn Quý Thầy/Cô đã lắng nghe phần trình bày.  
Em rất mong nhận được các góp ý của Hội đồng để tiếp tục hoàn thiện đề tài.

## 5. Prompt đưa cho Canva AI

Hãy tạo một bộ slide báo cáo bảo vệ đồ án tốt nghiệp bằng tiếng Việt, theme sáng, hiện đại, chuyên nghiệp, dựa theo khung sườn 4 phần giống bài báo cáo mẫu: 1. Phát biểu bài toán, 2. Cơ sở lý thuyết, 3. Xây dựng hệ thống, 4. Thực nghiệm và kết luận. Chủ đề là "Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số". Nội dung cần tập trung vào bài toán tư vấn pháp luật có căn cứ, phương án Agentic RAG, kho dữ liệu vector pháp luật ban đầu, chunking và metadata, truy hồi bằng ChromaDB, luồng chat chính với LangGraph, xử lý luật cũ - luật mới, luồng Admin upload văn bản mới, tư vấn có hướng dẫn, demo sản phẩm và kết quả đánh giá. Deck khoảng 18-20 slide, có các slide chuyển phần rõ ràng, nhiều sơ đồ khối/pipeline/metric cards/mockup, ít chữ trên mỗi slide, không đưa tên class/file code và không ghi tên model cụ thể.

---

## 6. Lưu ý khi dựng trong Canva

- Giữ các slide chuyển phần giống bài mẫu: số chương lớn + tên chương, ít chi tiết.
- Các slide nội dung nên có tiêu đề dạng mục số, ví dụ `1.1. Lý do chọn đề tài`, `2.2. Một số phương pháp xây dựng chatbot`, `3.4. Luồng chat chính với LangGraph`.
- Phần "Xây dựng hệ thống" phải là phần dài nhất.
- Slide lý thuyết cần ngắn, chỉ đủ để dẫn vào thiết kế hệ thống.
- Không biến slide thành bản sao báo cáo Word; mỗi slide chỉ nên có một thông điệp chính.
- Với các sơ đồ kỹ thuật, ưu tiên đường nét đơn giản, chữ lớn, nhiều khoảng trắng.
- Nên dùng màu chủ đạo sáng: trắng/xám nhạt, xanh dương hoặc teal; dùng cam/vàng cho cảnh báo, hạn chế hoặc luật cũ.
- Nếu template có các placeholder ngành khác, phải thay toàn bộ bằng nhận diện phù hợp với đề tài pháp luật và Học viện.
