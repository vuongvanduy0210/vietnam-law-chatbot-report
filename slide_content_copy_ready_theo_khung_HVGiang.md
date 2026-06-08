# Nội dung slide copy-ready theo khung HVGiang

Tài liệu này chia nội dung theo đúng 4 phần lớn của bài mẫu `Final Project Presentation_HVGiang.pptx`:

1. Phát biểu bài toán
2. Cơ sở lý thuyết
3. Xây dựng hệ thống
4. Thực nghiệm và kết luận

Mỗi slide bên dưới gồm **tiêu đề** và **nội dung có thể copy trực tiếp vào Canva**.

---

## Phần 1. Phát biểu bài toán

### Slide 1. Trang bìa

**Tiêu đề slide**

Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số

**Nội dung slide**

Báo cáo đồ án tốt nghiệp đại học  
Sinh viên thực hiện: Vương Văn Duy  
Chuyên ngành: Công nghệ thông tin  
Định hướng: Trợ lý pháp luật, Agentic RAG, kho tri thức pháp luật

---

### Slide 2. Nội dung trình bày

**Tiêu đề slide**

Nội dung trình bày

**Nội dung slide**

1. Phát biểu bài toán  
2. Cơ sở lý thuyết  
3. Xây dựng hệ thống  
4. Thực nghiệm và kết luận

Trọng tâm bài báo cáo là cách hệ thống xây dựng kho tri thức pháp luật, truy hồi bằng RAG và kiểm chứng câu trả lời trước khi phản hồi người dùng.

---

### Slide 3. Slide chuyển phần

**Tiêu đề slide**

1. Phát biểu bài toán

**Nội dung slide**

Phần này trình bày bối cảnh, lý do lựa chọn đề tài và mục tiêu xây dựng hệ thống trợ lý ảo pháp luật trong quá trình chuyển đổi số.

---

### Slide 4. Lý do chọn đề tài

**Tiêu đề slide**

1.1. Lý do chọn đề tài

**Nội dung slide**

Văn bản pháp luật có khối lượng lớn, cấu trúc phức tạp và thường xuyên thay đổi theo thời gian.

Người dùng phổ thông thường gặp khó khăn khi xác định văn bản nào đang còn hiệu lực, điều khoản nào phù hợp với tình huống của mình và nên tra cứu bằng từ khóa nào.

Các LLMs thuần có khả năng trả lời linh hoạt, nhưng vẫn có nguy cơ đưa ra thông tin thiếu căn cứ, trích dẫn sai hoặc không thể kiểm chứng nguồn.

Vì vậy, cần xây dựng một hệ thống trợ lý pháp luật có khả năng truy hồi nguồn, tổng hợp câu trả lời và kiểm chứng kết quả trước khi phản hồi.

---

### Slide 5. Mục tiêu đề tài

**Tiêu đề slide**

1.2. Mục tiêu đề tài

**Nội dung slide**

Xây dựng hệ thống trợ lý ảo pháp luật hỗ trợ người dùng tra cứu và đặt câu hỏi bằng ngôn ngữ tự nhiên.

Cung cấp câu trả lời có căn cứ, có nguồn tham chiếu và phù hợp với ngữ cảnh pháp lý của người dùng.

Tổ chức kho tri thức pháp luật để hệ thống có thể tìm kiếm, truy hồi và cập nhật dữ liệu khi có văn bản mới.

Triển khai sản phẩm hoàn chỉnh gồm ứng dụng cho người dùng cuối và trang quản trị cho quản trị viên.

Đánh giá khả năng trả lời, độ tin cậy và các hạn chế của hệ thống thông qua quá trình thử nghiệm.

---

## Phần 2. Cơ sở lý thuyết

### Slide 6. Slide chuyển phần

**Tiêu đề slide**

2. Cơ sở lý thuyết

**Nội dung slide**

Phần này trình bày các khái niệm nền tảng về chatbot, LLMs, AI Agent và LangGraph trước khi đi vào thiết kế hệ thống.

---

### Slide 7. Chatbot

**Tiêu đề slide**

2.1. Chatbot

**Nội dung slide**

Chatbot là hệ thống phần mềm được thiết kế để mô phỏng cuộc hội thoại với người dùng thông qua giao diện văn bản hoặc giọng nói.

Chatbot có thể tiếp nhận câu hỏi, phân tích nội dung đầu vào và tự động sinh phản hồi phù hợp với yêu cầu của người dùng.

Trong các hệ thống hiện đại, chatbot thường được kết hợp với mô hình ngôn ngữ lớn và các nguồn dữ liệu riêng để tăng khả năng hiểu ngữ cảnh.

Đối với bài toán tư vấn pháp luật, chatbot cần không chỉ trả lời tự nhiên mà còn phải gắn câu trả lời với thông tin có căn cứ.

---

### Slide 8. Một số phương pháp xây dựng chatbot

**Tiêu đề slide**

2.2. Một số phương pháp xây dựng chatbot

**Nội dung slide**

Chatbot dựa trên kịch bản hoặc tập luật hoạt động theo các luồng được chuẩn bị trước, dễ kiểm soát nhưng thiếu linh hoạt khi câu hỏi thay đổi.

Chatbot dựa trên LLMs có khả năng hiểu ngôn ngữ tự nhiên tốt hơn, trả lời linh hoạt hơn và phù hợp với nhiều cách diễn đạt khác nhau của người dùng.

Tuy nhiên, nếu chỉ dùng LLMs thuần, hệ thống có thể sinh ra thông tin không chính xác hoặc không dựa trên dữ liệu nội bộ.

Hướng tiếp cận AI Agent cho phép chatbot sử dụng thêm công cụ, truy vấn dữ liệu và lập kế hoạch xử lý để trả lời tốt hơn các yêu cầu phức tạp.

---

### Slide 9. LLMs, AI Agent và LangGraph

**Tiêu đề slide**

2.3. LLMs, AI Agent và LangGraph

**Nội dung slide**

LLMs là các mô hình ngôn ngữ lớn có khả năng xử lý, hiểu và tạo sinh ngôn ngữ tự nhiên.

AI Agent là hệ thống có khả năng nhận yêu cầu, phân tích trạng thái hiện tại, lựa chọn hành động phù hợp và sử dụng công cụ để đạt mục tiêu.

Trong các hệ thống chatbot hiện đại, LLMs thường đóng vai trò là thành phần lập luận chính của Agent.

LangGraph là framework hỗ trợ xây dựng AI Agent dưới dạng đồ thị, trong đó các node biểu diễn bước xử lý, các edge biểu diễn hướng di chuyển và state lưu trạng thái xuyên suốt quá trình thực hiện.

---

## Phần 3. Xây dựng hệ thống

### Slide 10. Slide chuyển phần

**Tiêu đề slide**

3. Xây dựng hệ thống

**Nội dung slide**

Phần này trình bày cách xác định môi trường của Agent, mô hình tổng quan hệ thống chatbot, luồng xử lý tin nhắn, đồ thị LangGraph, cách xây dựng các node và các chức năng chính của toàn hệ thống.

---

### Slide 11. Xác định môi trường của Agent

**Tiêu đề slide**

3.1. Xác định môi trường của Agent cho bài toán pháp luật

**Nội dung slide**

Trong bài toán pháp luật, môi trường của Agent gồm câu hỏi người dùng, lịch sử hội thoại, kho dữ liệu pháp luật nội bộ, nguồn thông tin cập nhật bên ngoài và trạng thái xử lý hiện tại.

Agent cần có khả năng truy hồi điều luật liên quan, kiểm tra thông tin theo thời gian và tổng hợp câu trả lời dễ hiểu cho người dùng phổ thông.

Tập hành động chính của Agent gồm: phân tích câu hỏi, tạo truy vấn tìm kiếm, gọi công cụ truy hồi, tổng hợp bằng chứng và chuyển câu trả lời sang bước kiểm chứng.

Kết quả cuối cùng của Agent không chỉ là một đoạn văn trả lời, mà còn phải kèm căn cứ pháp lý và nguồn tham chiếu phù hợp.

---

### Slide 12. Mô hình tổng quan của hệ thống chatbot

**Tiêu đề slide**

3.2. Mô hình tổng quan của hệ thống chatbot

**Nội dung slide**

Người dùng tương tác với hệ thống thông qua Mobile App, còn quản trị viên sử dụng Web Admin để quản lý và cập nhật dữ liệu pháp luật.

Main Service đóng vai trò cổng nghiệp vụ, xử lý xác thực, hội thoại, upload văn bản và điều phối request giữa client với các service phía sau.

RAG Service là lõi xử lý AI, phụ trách LangGraph, Agentic RAG, embedding, truy hồi vector và kiểm chứng câu trả lời.

PostgreSQL lưu dữ liệu người dùng và hội thoại; MongoDB lưu điều luật có cấu trúc; ChromaDB lưu vector chunks phục vụ tìm kiếm ngữ nghĩa.

---

### Slide 13. Luồng xử lý tin nhắn của người dùng

**Tiêu đề slide**

3.3. Luồng xử lý tin nhắn của người dùng

**Nội dung slide**

Khi người dùng gửi câu hỏi, Mobile App chuyển tin nhắn đến Main Service để xác thực, lưu hội thoại và tạo request xử lý.

Main Service gọi RAG Service để chạy luồng Agentic RAG, trong đó câu hỏi được kiểm tra, phân tích và chuyển thành các truy vấn phù hợp.

Agent gọi các công cụ để truy hồi bằng chứng từ kho luật nội bộ và nguồn thông tin cập nhật khi cần.

Sau khi có câu trả lời nháp, Verifier kiểm tra lại tính đúng đắn, nguồn dẫn và sự nhất quán trước khi kết quả được trả về giao diện người dùng.

---

### Slide 14. Đồ thị của hệ thống

**Tiêu đề slide**

3.4. Đồ thị của hệ thống

**Nội dung slide**

Đồ thị xử lý của hệ thống được xây dựng bằng LangGraph, gồm các node chính: Guardrail, Query Analysis, Agent, Tools và Verifier.

Guardrail kiểm tra câu hỏi đầu vào; Query Analysis phân tích ý định và tạo truy vấn; Agent quyết định công cụ cần gọi; Tools thực hiện truy hồi; Verifier kiểm chứng câu trả lời.

Các cạnh trong graph biểu diễn hướng di chuyển giữa các bước xử lý. Một số cạnh là cạnh điều kiện, cho phép hệ thống quyết định tiếp tục gọi tool, chuyển sang kiểm chứng hoặc kết thúc luồng.

**Hướng dẫn vẽ trên slide**

Vẽ tương tự slide 3.3 trong bài mẫu: đặt các node theo chiều từ trên xuống hoặc trái sang phải, dùng khung bo tròn cho từng node, mũi tên liền cho luồng chính và mũi tên vòng lặp giữa Agent và Tools.

Sơ đồ gợi ý: START → Guardrail → Query Analysis → Agent ↔ Tools → Verifier → END.

---

### Slide 15. Xây dựng các node trong hệ thống

**Tiêu đề slide**

3.5. Xây dựng các node trong hệ thống

**Nội dung slide**

Mỗi node trong graph được thiết kế như một bước xử lý độc lập, có đầu vào, logic điều khiển và đầu ra rõ ràng.

`Guardrail`
Input: câu hỏi hiện tại của người dùng.
Prompt trích trong code: “Bạn là một bộ lọc kiểm duyệt cực kỳ nghiêm ngặt cho Hệ thống AI Tư vấn Luật pháp Việt Nam.”
Logic chính trích trong code: “Hãy chỉ trả về ĐÚNG MỘT TỪ: - "PASS" nếu câu hỏi hợp lệ và thuộc phạm trù luật pháp, đời sống dân sự hành chính. - "REJECT" nếu câu hỏi vi phạm các nguyên tắc trên hoặc hoàn toàn lạc đề.”
Output: trạng thái `PASS` để xử lý tiếp hoặc `REJECT` kèm lý do từ chối.

`Query Analysis`
Input: câu hỏi đã qua kiểm tra.
Prompt trích trong code: “Bạn là chuyên gia phân tích pháp luật Việt Nam. Nhiệm vụ: Phân tích câu hỏi pháp lý của người dùng và tạo ra các truy vấn tìm kiếm TỐI ƯU cho 2 hệ thống khác nhau.”
Logic chính: tạo JSON gồm `legal_topic`, `legal_domain`, `relevant_laws`, `internal_search_query`, `web_search_query`, `key_legal_terms`, `analysis_summary`.
Output: `internal_search_query`, `web_search_query`, các thuật ngữ pháp lý chính và tóm tắt nhu cầu tra cứu.

`Agent`
Input: lịch sử hội thoại, kết quả phân tích truy vấn và kết quả từ các công cụ nếu đã có.
Prompt trích trong code: “Bạn là một Luật sư Tư vấn Pháp luật Việt Nam cấp cao với hơn 20 năm kinh nghiệm hành nghề. Bạn đang tư vấn trực tiếp cho thân chủ.”
Logic chính trích trong code: “QUY TRÌNH BẮT BUỘC: 1. BƯỚC 1 - TRA CỨU NGUYÊN VĂN: Gọi `retrieve_internal_law` để lấy nội dung điều khoản gốc (dữ liệu đến 2026). 2. BƯỚC 2 - XÁC MINH VÀ CẬP NHẬT: BẮT BUỘC gọi `search_web_for_law` để tìm quy định hiện hành. Kết quả bao gồm cả Google Search realtime và cổng pháp luật chính thức.”
Output: yêu cầu gọi công cụ hoặc câu trả lời nháp có cấu trúc.

`Tools`
Input: truy vấn tối ưu do node Query Analysis tạo ra.
Mô tả tool nội bộ trích trong code: “Sử dụng công cụ này ĐẦU TIÊN để tìm kiếm các quy định pháp luật Việt Nam trong cơ sở dữ liệu nội bộ (tất cả văn bản hiện hành đến năm 2026).”
Mô tả tool web trích trong code: “Tra cứu văn bản pháp luật Việt Nam HIỆN HÀNH, xác minh hiệu lực và tìm quy định mới nhất.”
Output: nội dung điều luật, metadata pháp lý, độ liên quan và nguồn tham chiếu.

`Verifier`
Input: câu trả lời nháp của Agent và toàn bộ kết quả công cụ đã sử dụng.
Prompt trích trong code: “Kiểm tra câu trả lời pháp luật có bịa đặt không. Ngày hiện tại: {today}. Văn bản hiệu lực ≤ hôm nay = ĐÃ CÓ HIỆU LỰC (không phải bịa).”
Logic chính: kiểm tra số hiệu, nội dung chi tiết, từng con số cụ thể, quan hệ văn bản và việc sử dụng luật cũ - luật mới.
Output: `PASS` nếu câu trả lời hợp lệ hoặc bản trả lời đã được sửa bằng cách loại bỏ phần thiếu căn cứ.

**Ý thuyết trình**

Thiết kế này giúp tách rõ trách nhiệm giữa các bước. `Query Analysis` không trực tiếp trả lời mà chỉ tối ưu hướng tìm kiếm; `Agent` chịu trách nhiệm suy luận và điều phối công cụ; còn `Verifier` là lớp kiểm tra cuối để hạn chế câu trả lời thiếu căn cứ. Nhờ vậy, luồng xử lý không phụ thuộc hoàn toàn vào một lần sinh câu trả lời của LLMs.

---

### Slide 16. Xử lý State và cạnh điều kiện

**Tiêu đề slide**

3.6. Xử lý State và cạnh điều kiện

**Nội dung slide**

State là vùng lưu trữ trạng thái dùng chung giữa các node trong graph, giúp hệ thống theo dõi toàn bộ quá trình xử lý một câu hỏi.

State lưu các thông tin quan trọng như tin nhắn hội thoại, kết quả phân tích câu hỏi, tài liệu đã truy hồi, số vòng lặp xử lý và trạng thái hợp lệ của truy vấn.

Mỗi node đọc một phần state, thực hiện nhiệm vụ của mình và cập nhật lại state để node sau tiếp tục sử dụng.

Các cạnh điều kiện giúp graph quyết định hướng đi tiếp theo, ví dụ kết thúc sớm khi câu hỏi không hợp lệ, quay lại Agent khi chưa đủ bằng chứng hoặc chuyển sang Verifier khi đã có dữ liệu cần thiết.

---

### Slide 17. Xây dựng luồng RAG nội bộ

**Tiêu đề slide**

3.7.1. Xây dựng luồng RAG truy hồi dữ liệu pháp luật nội bộ

**Nội dung slide**

Luồng RAG nội bộ bắt đầu từ tập dữ liệu pháp luật dạng JSON, trước khi được đưa vào MongoDB và ChromaDB.

Dữ liệu ban đầu thường chỉ có nội dung văn bản và thông tin điều luật ở dạng còn thô:

```json
{
  "law_id": "100/2015/QH13",
  "article": "Điều 173. Tội trộm cắp tài sản",
  "content": "Người nào trộm cắp tài sản của người khác..."
}
```

Sau bước làm sạch và chuẩn hóa, dữ liệu được tách rõ thành từng điều luật và gắn thêm metadata:

```json
{
  "law_id": "100/2015/QH13",
  "article_id": "173",
  "title": "Điều 173. Tội trộm cắp tài sản",
  "text": "Người nào trộm cắp tài sản của người khác...",
  "metadata": {
    "year": "2015",
    "topics": ["Hình sự"],
    "keywords": ["trộm cắp tài sản", "khung hình phạt"],
    "summary": "Quy định về tội trộm cắp tài sản."
  }
}
```

MongoDB lưu dữ liệu điều luật đầy đủ để quản lý và tra cứu văn bản.

ChromaDB lưu các vector chunks được tạo từ dữ liệu đã chuẩn hóa để phục vụ truy hồi ngữ nghĩa cho `retrieve_internal_law`.

**Ý thuyết trình**

Điểm cần nhấn mạnh là hệ thống không đưa dữ liệu thô trực tiếp vào RAG. Dữ liệu ban đầu phải đi qua bước làm sạch, chuẩn hóa theo đơn vị điều luật và gắn metadata trước. Nhờ vậy, mỗi chunk sau này không chỉ có nội dung văn bản mà còn có thông tin pháp lý đi kèm, giúp Agent trích dẫn và Verifier kiểm tra nguồn dễ hơn.

---

### Slide 18. Chunking, Embedding và lưu trữ ChromaDB

**Tiêu đề slide**

3.7.2. Chunking, Embedding và lưu trữ ChromaDB

**Nội dung slide**

Hệ thống sử dụng chiến thuật chunking lai: điều luật ngắn được giữ nguyên, điều luật dài mới được chia nhỏ.

Ngưỡng chia được cấu hình tối đa 1000 từ cho một chunk, với overlap 150 từ giữa các chunk liền kề.

Khi chia nhỏ, hệ thống ưu tiên cắt tại dấu câu gần nhất để hạn chế làm đứt mạch nội dung pháp lý.

Mỗi chunk được ghép thêm tiêu đề điều luật ở đầu nội dung trước khi tạo embedding.

Sau đó, mỗi chunk được chuyển thành vector embedding bằng mô hình bi-encoder tiếng Việt.

ChromaDB lưu đồng thời `id`, `document`, `embedding` và `metadata` của từng chunk.

`metadata` chứa thông tin pháp lý như `law_id`, `article_id`, `title`, `chunk_index`, `total_chunks`, `year`, `topics`, `keywords`, `summary`.

**Ý thuyết trình**

Chiến thuật này cân bằng giữa tính toàn vẹn của điều luật và độ chính xác khi truy hồi. Nếu chunk quá ngắn, quy định có thể bị tách khỏi điều kiện áp dụng; nếu chunk quá dài, embedding khó biểu diễn trọng tâm. Việc gắn tiêu đề và metadata giúp mỗi chunk vẫn giữ được ngữ cảnh pháp lý khi được truy hồi.

---

### Slide 19. Retrieve, Rerank và đóng gói Context

**Tiêu đề slide**

3.7.3. Retrieve, Rerank và đóng gói Context

**Nội dung slide**

Truy vấn đầu vào của `retrieve_internal_law` là `internal_search_query` đã được tối ưu từ node Query Analysis.

Bước đầu tiên, hệ thống encode truy vấn thành vector và tìm kiếm trong ChromaDB bằng độ tương đồng vector.

ChromaDB trả về tập ứng viên ban đầu gồm các chunk gần nghĩa nhất với câu hỏi.

Sau đó, cross-encoder rerank lại các ứng viên bằng cách chấm điểm trực tiếp từng cặp query - chunk.

Sau khi rerank, hệ thống lọc kết quả đạt ngưỡng liên quan và chọn tối đa 10 văn bản cho Agent.

Mỗi kết quả được đóng gói gồm: độ tin cậy, số hiệu văn bản, điều khoản, tên điều, năm ban hành, lĩnh vực và nội dung nguyên văn.

Kết quả được bọc bằng marker `[VĂN BẢN ... BẮT ĐẦU]` và `[VĂN BẢN ... KẾT THÚC]` để Agent nhận biết ranh giới nguồn.

Hệ thống cũng phát hiện xung đột luật cũ - luật mới để hạn chế việc sử dụng nhầm quy định đã hết hiệu lực.

**Ý thuyết trình**

Vector search giúp lấy nhanh các ứng viên trên tập dữ liệu lớn, còn cross-encoder giúp chọn lại các chunk có mức liên quan cao hơn. ChromaDB không đưa vector trực tiếp cho LLMs; vector chỉ dùng để tìm kiếm. Context cuối cùng đưa cho Agent là văn bản pháp luật đã truy hồi, kèm metadata và marker kiểm soát nguồn.

---

### Slide 20. Chức năng chính của toàn hệ thống

**Tiêu đề slide**

3.8. Các chức năng chính của hệ thống

**Nội dung slide**

Mobile App hỗ trợ chat tư vấn pháp luật, hiển thị tiến trình xử lý và nguồn tham chiếu cho câu trả lời.

Luồng tư vấn có hướng dẫn giúp người dùng bổ sung thông tin khi câu hỏi ban đầu còn thiếu ngữ cảnh.

Tính năng tra cứu văn bản cho phép tìm kiếm pháp luật bằng ngôn ngữ tự nhiên thay vì chỉ dựa vào từ khóa cứng.

Web Admin hỗ trợ dashboard, quản lý văn bản pháp luật, upload PDF và theo dõi trạng thái cập nhật dữ liệu vào kho tri thức.

---

## Phần 4. Thực nghiệm và kết luận

### Slide 21. Slide chuyển phần

**Tiêu đề slide**

4. Thực nghiệm và kết luận

**Nội dung slide**

Phần này trình bày phương pháp đánh giá hệ thống, kết quả thực nghiệm, các hạn chế còn tồn tại và hướng phát triển tiếp theo.

---

### Slide 22. Kết quả đánh giá hệ thống

**Tiêu đề slide**

4.1. Kết quả đánh giá hệ thống

**Nội dung slide**

Bộ kiểm thử gồm 60 câu hỏi, được dùng để đánh giá độ chính xác, chất lượng câu trả lời, khả năng xử lý luật cũ - luật mới và độ trễ phản hồi.

Hệ thống đạt Accuracy@1 là 90,0% trên nhóm câu hỏi factual.

Answer Quality đạt 3,67/5,0, cho thấy câu trả lời nhìn chung đáp ứng được yêu cầu tư vấn.

Temporal Conflict OK đạt 3/3, thể hiện hệ thống xử lý đúng nhóm câu hỏi có xung đột giữa luật cũ và luật mới.

Citation Accuracy đạt 56,7% và Latency P50 là 65,5 giây, đây là hai điểm cần tiếp tục cải thiện.

---

### Slide 23. Kết luận, hạn chế và hướng phát triển

**Tiêu đề slide**

4.2. Kết luận và hướng phát triển

**Nội dung slide**

Đề tài đã xây dựng được hệ thống trợ lý ảo pháp luật có kho tri thức vector, luồng Agentic RAG và bước kiểm chứng câu trả lời.

Hệ thống hỗ trợ các luồng chính gồm chat tư vấn pháp luật, tư vấn có hướng dẫn, tra cứu văn bản và cập nhật văn bản mới phía Admin.

Hạn chế hiện tại nằm ở độ trễ của pipeline Agentic RAG và độ chính xác nguồn trích dẫn nội bộ.

Trong hướng phát triển tiếp theo, hệ thống cần tối ưu thời gian phản hồi, mở rộng kho dữ liệu pháp luật, cải thiện chất lượng trích dẫn và xây dựng bộ benchmark đánh giá lớn hơn.

---

### Slide 24. Cảm ơn

**Tiêu đề slide**

Cảm ơn Thầy/Cô đã lắng nghe

**Nội dung slide**

Em xin trân trọng cảm ơn Quý Thầy/Cô đã lắng nghe phần trình bày.

Em rất mong nhận được các góp ý của Hội đồng để tiếp tục hoàn thiện đề tài.

---

## Gợi ý rút gọn xuống 18-20 slide

Nếu cần rút ngắn, có thể gộp:

- Slide 8 và Slide 9 thành một slide: Phương pháp chatbot, LLMs và AI Agent.
- Slide 15 và Slide 16 thành một slide: Node, State và cạnh điều kiện.
- Slide 17 đến Slide 19 thành 2 slide nếu cần rút thêm: Xây dựng dữ liệu - Chunking và Retrieve - Rerank.
- Slide 23 và Slide 24 thành một slide: Kết luận và cảm ơn.

Không nên cắt các slide về môi trường Agent, mô hình tổng quan, luồng xử lý tin nhắn, đồ thị hệ thống và xây dựng CSDL phục vụ Internal Retrieve vì đây là các phần trọng tâm của đồ án.
