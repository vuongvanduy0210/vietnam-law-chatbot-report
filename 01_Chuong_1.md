# CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI VÀ CƠ SỞ LÝ THUYẾT

## 1.1. Tổng quan về chatbot

### 1.1.1. Khái niệm chatbot

Chatbot hay tác nhân hội thoại là một hệ thống phần mềm được thiết kế để mô phỏng cuộc hội thoại với người dùng thông qua giao diện văn bản hoặc giọng nói. Mục tiêu cốt lõi của chatbot là tự động hoá quy trình giao tiếp, cho phép người dùng truy xuất thông tin hoặc thực hiện tác vụ một cách hiệu quả mà không cần sự can thiệp trực tiếp từ con người. Việc ứng dụng chatbot mang lại nhiều lợi ích đáng kể, bao gồm: nâng cao hiệu quả vận hành, giảm chi phí nhân sự cho các tác vụ lặp lại, cung cấp dịch vụ liên tục (24/7) và cải thiện trải nghiệm người dùng.

Dựa trên công nghệ lõi, chatbot có thể được phân loại thành hai nhóm chính: chatbot truyền thống và chatbot ứng dụng trí tuệ nhân tạo.

Các hệ thống chatbot truyền thống là những hệ thống sử dụng phương pháp tập luật, hoạt động dựa trên một tập hợp các quy tắc và kịch bản được lập trình sẵn. Điểm yếu cố hữu của phương pháp này là sự thiếu linh hoạt. Hệ thống phụ thuộc hoàn toàn vào cơ sở tri thức do người thiết kế xây dựng và chỉ có thể xử lý các câu hỏi tuân thủ đúng kịch bản. Khi người dùng đặt câu hỏi bằng những cấu trúc ngữ pháp hoặc từ vựng khác biệt, chatbot truyền thống thường không thể hiểu và đưa ra phản hồi phù hợp.

Để khắc phục những hạn chế của chatbot truyền thống, các thế hệ chatbot hiện đại tích hợp những thành tựu của trí tuệ nhân tạo, đặc biệt là trong lĩnh vực Xử lý ngôn ngữ tự nhiên (NLP) và các Mô hình ngôn ngữ lớn (LLMs). Thay vì chỉ bám vào các quy tắc cứng, AI chatbot có khả năng "hiểu" ý định đằng sau câu hỏi của người dùng, cho phép chúng xử lý các truy vấn đa dạng và phức tạp hơn, đồng thời tạo ra các phản hồi tự nhiên, linh hoạt.

Một trong những công nghệ tiên tiến được sử dụng để xây dựng AI chatbot hiện nay là nền tảng kiến trúc AI Agent. AI Agent không chỉ dừng lại ở việc trả lời dựa trên tập dữ liệu được huấn luyện trước mà còn có khả năng suy luận và sử dụng các công cụ bên ngoài, cho phép chatbot tương tác với các hệ thống khác như cơ sở dữ liệu, API tìm kiếm web,… Trong phạm vi đồ án này, hướng tiếp cận được lựa chọn là xây dựng một AI chatbot tư vấn pháp luật dựa trên kiến trúc AI Agent nhằm khai thác tối đa khả năng tương tác với dữ liệu pháp luật liên quan.

### 1.1.2. Tiềm năng ứng dụng chatbot trong lĩnh vực tư vấn pháp luật tại Việt Nam

#### 1.1.2.1. Thực trạng tra cứu pháp luật và nhu cầu ứng dụng chatbot

Hệ thống văn bản quy phạm pháp luật của Việt Nam là một trong những hệ thống pháp luật có quy mô lớn và được cập nhật liên tục tại khu vực Đông Nam Á. Theo dữ liệu thực nghiệm thu thập trong quá trình thực hiện đề tài, hệ thống đã số hoá và nạp vào cơ sở dữ liệu nội bộ tổng cộng **46.047 văn bản pháp luật** với **528.620 điều luật**, trải dài **82 năm** từ 1945 đến 2026 và bao quát hơn **62.000 chủ đề pháp lý** khác nhau.

Người dùng thông thường gặp nhiều rào cản khi tự tra cứu pháp luật:

- Truy cập thông tin nhanh chóng 24/7: Người dân và doanh nghiệp cần tra cứu quy định pháp luật mà không phụ thuộc vào giờ làm việc của cơ quan nhà nước hay văn phòng luật sư. Nhu cầu này đặc biệt cao trong các thời điểm cần xử lý gấp thủ tục hành chính, hợp đồng hay tranh chấp.
- Giảm rào cản thuật ngữ chuyên ngành: Ngôn ngữ pháp luật mang tính trang trọng với nhiều thuật ngữ đặc thù như "phạm vi điều chỉnh", "đối tượng áp dụng", "hiệu lực thi hành" — khiến người dân không có nền tảng pháp lý khó tiếp cận trực tiếp. Chatbot AI có thể diễn giải các thuật ngữ này thành ngôn ngữ tự nhiên, dễ hiểu.
- Đối chiếu thông tin phân mảnh: Một quy định cụ thể thường được đề cập rải rác trong nhiều văn bản (luật gốc, nghị định hướng dẫn, thông tư sửa đổi). Chatbot có thể tự động tổng hợp thông tin từ nhiều nguồn và đưa ra câu trả lời đầy đủ, kèm dẫn nguồn rõ ràng.
- Phát hiện xung đột thời gian hiệu lực: Pháp luật Việt Nam thường xuyên được sửa đổi — riêng năm 2025 đã có hàng chục nghìn điều luật được ban hành mới hoặc sửa đổi. Chatbot AI có thể cảnh báo khi hai văn bản mâu thuẫn nhau, giúp người dùng áp dụng đúng quy định đang có hiệu lực.

Các giải pháp hiện có như `thuvienphapluat.vn`, `luatvietnam.vn`, `vbpl.vn` chủ yếu cung cấp công cụ tìm kiếm theo từ khoá và liệt kê văn bản — người dùng vẫn phải tự đọc, tự đối chiếu và tự suy luận. Đây chính là khoảng trống mà hệ thống Vietnam Law Chatbot hướng tới lấp đầy.

#### 1.1.2.2. Lợi ích của chatbot AI đối với các đối tượng sử dụng

Bên cạnh lợi ích đối với người dân và doanh nghiệp, hệ thống chatbot AI tư vấn pháp luật cũng mang lại nhiều lợi ích rõ rệt cho các đối tượng sử dụng khác:

Tiết kiệm thời gian trong việc giải đáp câu hỏi lặp lại: Các cán bộ, công chức thường nhận được nhiều câu hỏi trùng lặp từ người dân như: thời hạn nộp hồ sơ, thủ tục đăng ký, mức phạt vi phạm,... Chatbot có thể thay thế việc trả lời những câu hỏi này một cách nhanh chóng và chính xác, giúp cán bộ tập trung vào các công việc phức tạp và chuyên môn hơn.

Hỗ trợ tra cứu tức thời khi soạn thảo văn bản: Khi được tích hợp với hệ thống quản lý văn bản, chatbot có thể cung cấp thông tin tức thời như các điều luật liên quan, tiền lệ, quy định hiện hành — giúp cán bộ soạn thảo quyết định hành chính nhanh chóng và chính xác hơn.

Cải thiện chất lượng dịch vụ công: Nhờ có chatbot xử lý các yêu cầu cơ bản, cán bộ có thêm thời gian để tương tác sâu hơn với người dân trong các vấn đề phức tạp — góp phần nâng cao chất lượng phục vụ và sự hài lòng của người dân.

Thúc đẩy chuyển đổi số trong lĩnh vực pháp luật: Xây dựng chatbot pháp luật đúng tinh thần Quyết định 749/QĐ-TTg ngày 03/6/2020 của Thủ tướng Chính phủ về Chương trình Chuyển đổi số quốc gia — đưa dịch vụ pháp lý lên nền tảng số, giúp người dân tiếp cận thông tin pháp luật bình đẳng và thuận tiện hơn.

## 1.2. Một số phương pháp xây dựng chatbot tư vấn pháp luật

Việc phát triển chatbot tư vấn pháp luật dựa trên nhiều phương pháp luận khác nhau, mỗi phương pháp đều sở hữu những đặc điểm, ưu và nhược điểm riêng biệt, phản ánh sự tiến hoá của ngành khoa học máy tính và xử lý ngôn ngữ tự nhiên. Về cơ bản, các phương pháp xây dựng chatbot hiện nay có thể được phân thành ba nhóm chính: chatbot dựa trên các tập luật, chatbot dựa trên các mô hình LLMs và RAG, chatbot dựa trên AI Agent.

### 1.2.1. Chatbot dựa trên tập luật

Phương pháp xây dựng chatbot dựa trên tập luật là cách tiếp cận sơ khai và nền tảng nhất. Hoạt động của các chatbot này hoàn toàn phụ thuộc vào một kịch bản và một bộ quy tắc được lập trình sẵn. Các nhà phát triển phải dự đoán các câu hỏi, từ khoá có thể có từ người dùng và xây dựng một cây quyết định logic để đưa ra câu trả lời tương ứng.

[IMG:image2.png]
*Hình 1.1. Chatbot dựa trên tập luật khi câu hỏi nằm ngoài kịch bản định sẵn*

Mặc dù phương pháp này đảm bảo tính nhất quán và có thể kiểm soát hoàn toàn luồng hội thoại, nó bộc lộ nhiều hạn chế. Hệ thống thiếu đi sự linh hoạt, không có khả năng xử lý các câu hỏi phức tạp, sai chính tả hoặc các truy vấn không nằm trong kịch bản định sẵn. Với lĩnh vực pháp luật Việt Nam — nơi có hàng trăm nghìn điều luật và vô số cách diễn đạt câu hỏi — phương pháp này hoàn toàn không khả thi.

### 1.2.2. Chatbot dựa trên LLMs và RAG

Để khắc phục những giới hạn của cách tiếp cận dựa trên luật, các phương pháp dựa trên học máy đã được nghiên cứu và ứng dụng rộng rãi. Thay vì các quy tắc cứng, chatbot học máy được huấn luyện trên các tập dữ liệu lớn để tự nhận dạng mẫu, hiểu ý định và thực thể trong câu nói của người dùng.

Trong các chatbot này, nổi bật hơn cả là các chatbot với nền tảng là mô hình sinh ngôn ngữ, điển hình là các Mô hình ngôn ngữ lớn, có khả năng tự tạo ra câu trả lời mới hoàn toàn, mang lại các cuộc hội thoại tự nhiên và linh hoạt hơn. Tuy nhiên, khi áp dụng vào lĩnh vực pháp luật, cần phải khắc phục một số vấn đề:

- **Non-Specific domain:** Các mô hình LLM được đào tạo giải quyết đa dạng các vấn đề, không thể giải quyết chuyên sâu bài toán pháp luật Việt Nam với đặc thù riêng.
- **Non-access private datas:** Các mô hình LLM không thể hiểu những dữ liệu văn bản pháp luật nội bộ của hệ thống. Đồng thời, vì lý do bảo mật, hệ thống không được phép đào tạo với dữ liệu riêng tư. Tuy nhiên, việc không thể sử dụng dữ liệu nội bộ lại khiến chatbot không có khả năng thấu hiểu và giải quyết các vấn đề pháp lý cụ thể của người dùng.
- **Hiện tượng ảo giác (Hallucination):** Khi không được đào tạo kiến thức liên quan phần dữ liệu pháp luật nội bộ, các mô hình LLM có xu hướng "bịa" ra những thông tin này để trả lời — ví dụ, tự đặt ra số hiệu nghị định không tồn tại, tự bịa mức phạt không có căn cứ — dẫn đến hậu quả pháp lý nghiêm trọng cho người dùng.

Để giải quyết những bài toán này, kỹ thuật **Truy xuất tạo sinh tăng cường (RAG — Retrieval-Augmented Generation)** thường được áp dụng nhằm tìm kiếm và bổ sung thêm ngữ cảnh từ cơ sở dữ liệu pháp luật, cho phép LLM trả lời câu hỏi với những dữ liệu cụ thể, liên quan trực tiếp đến câu hỏi của người dùng.

[IMG:image3.jpeg]
*Hình 1.2. Mô hình RAG — kết hợp truy xuất tài liệu và tổng hợp câu trả lời*

Cách tiếp cận này giải quyết triệt để các vấn đề đã nêu ở phần trước:

- **Vượt qua giới hạn về miền kiến thức và dữ liệu riêng tư:** Bằng cách kết nối LLM với cơ sở dữ liệu pháp luật bên ngoài, chatbot có thể truy cập và sử dụng nguồn dữ liệu riêng tư của hệ thống một cách an toàn và hiệu quả mà không cần tái huấn luyện toàn bộ mô hình tốn kém.
- **Giảm thiểu hiện tượng ảo giác:** Vì LLM được yêu cầu phải trả lời dựa trên thông tin thực tế được cung cấp trong prompt, khả năng "bịa" ra thông tin sai lệch bị triệt tiêu đáng kể. Câu trả lời được "neo" vào điều luật cụ thể trong cơ sở dữ liệu, từ đó tăng cường độ tin cậy và chính xác.

Mặc dù vậy, chatbot dựa trên LLM và RAG cơ bản (Naive RAG) vẫn còn bị hạn chế: chỉ thực hiện một lần tìm kiếm cố định, không xử lý được câu hỏi đa chiều đòi hỏi tổng hợp từ nhiều văn bản, không có cơ chế tự đánh giá chất lượng kết quả, và không phát hiện được xung đột thời gian hiệu lực giữa các văn bản pháp luật.

### 1.2.3. Xây dựng hệ thống chatbot dựa trên AI Agent

Phương pháp xây dựng chatbot dựa trên AI Agent là một kiến trúc tiên tiến, ra đời như sự kết hợp của những phương pháp xây dựng chatbot khác cùng với khả năng tự suy luận, chủ động tương tác với người dùng.

AI Agent là kiến trúc bao gồm các thành phần suy luận, tạo sinh, thành phần tương tác với các công cụ bên ngoài (cơ sở dữ liệu pháp luật, API tìm kiếm web,…). Nhờ đó, AI Agent có khả năng thấu hiểu câu hỏi người dùng, lên kế hoạch tra cứu, sử dụng công cụ, tự đánh giá và điều chỉnh chiến lược qua nhiều bước — tương tự cách một chuyên gia pháp lý thực thụ làm việc.

[IMG:image4.jpeg]
*Hình 1.3. AI Agent bao gồm nhiều thành phần tư duy, truy vấn và tương tác*

Như vậy, mô hình AI Agent không chỉ tận dụng được sức mạnh ngôn ngữ của LLM mà còn khắc phục được những điểm yếu chí mạng của chúng, tạo ra một thế hệ chatbot thông minh, am hiểu sâu sắc về lĩnh vực pháp luật và đáng tin cậy cho người dùng. Sự kết hợp giữa AI Agent và RAG tạo ra **Agentic RAG** — kiến trúc được lựa chọn cho hệ thống Vietnam Law Chatbot của đề tài này.

## 1.3. Tìm hiểu về mô hình ngôn ngữ lớn

### 1.3.1. Khái niệm mô hình ngôn ngữ lớn

Mô hình ngôn ngữ lớn (Large Language Models — LLM) là những mô hình AI được thiết kế để xử lý và tạo sinh ngôn ngữ tự nhiên. Được xây dựng dựa trên kiến trúc mạng nơ-ron sâu, đặc biệt là mô hình Transformer, LLM được đào tạo trên lượng dữ liệu khổng lồ và cho ra mô hình lên tới hàng chục tỷ tham số. Nhờ đó, LLM có khả năng hiểu ngôn ngữ tự nhiên, trả lời các câu hỏi, dịch văn bản, lập luận logic,…

LLM không chỉ học cách xử lý các mẫu ngôn ngữ phức tạp mà còn nắm bắt được ngữ cảnh, ngữ nghĩa, và cả bối cảnh văn hoá trong nhiều ngôn ngữ khác nhau. Nhờ khả năng tạo sinh ngôn ngữ tự nhiên mạnh mẽ, LLM mở ra tiềm năng vô hạn cho các ứng dụng AI, điển hình trong đó là các ứng dụng chatbot tư vấn pháp luật.

Để LLM có thể đưa ra output chính xác, chúng hoạt động dựa trên mạng nơ-ron sâu, thường là kiến trúc Transformer. Quá trình này bao gồm các bước chính:

- **Mã hoá đầu vào (Input Encoding / Embedding Layer):** Khi nhận văn bản đầu vào, LLM chuyển đổi các từ (tokens) thành các biểu diễn số học dưới dạng vector, gọi là "embedding". Lớp nhúng này nắm bắt ý nghĩa ngữ nghĩa và cú pháp của từ.
- **Xử lý qua các lớp Transformer:** Dữ liệu sau khi nhúng đi qua các lớp của kiến trúc Transformer.
- **Lớp truyền tiếp (Feedforward Layers):** Thực hiện các biến đổi phi tuyến tính trên các vector embedding, giúp mô hình học và tạo ra các liên kết phức tạp giữa dữ liệu đầu vào và đầu ra.
- **Cơ chế chú ý (Attention Mechanism):** Đây là thành phần cốt lõi, cho phép mô hình tập trung có chọn lọc vào các phần quan trọng nhất của văn bản đầu vào khi thực hiện dự đoán.
- **Dự đoán đầu ra (Output Prediction):** Dựa trên thông tin đã được xử lý và hiểu biết về ngữ cảnh, LLM dự đoán từ hoặc chuỗi từ tiếp theo để tạo thành câu trả lời.

Bên cạnh kiến trúc và dữ liệu huấn luyện, việc kiểm soát cách LLM tạo ra output cũng rất quan trọng. Các tham số cấu hình như "temperature", "top-k sampling" và "top-p sampling" có thể thay đổi đáng kể kết quả đầu ra:

- **Temperature:** Điều chỉnh mức độ ngẫu nhiên. Giá trị thấp (0.0–0.3) cho phản hồi tập trung, nhất quán — phù hợp với tác vụ pháp luật đòi hỏi độ chính xác cao.
- **Top-k sampling:** Giới hạn lựa chọn từ tiếp theo trong k từ có xác suất cao nhất, loại bỏ các từ có xác suất rất thấp.
- **Top-p (nucleus) sampling:** Chọn tập nhỏ nhất các từ sao cho tổng xác suất đạt ngưỡng p. Giá trị p càng nhỏ, câu trả lời càng tập trung hơn.

### 1.3.2. Khái niệm Chat LLMs

Chat LLMs là những ứng dụng chat dựa trên LLM, cho phép người dùng tương tác với các mô hình ngôn ngữ lớn dưới dạng các đoạn hội thoại gần gũi. Nhờ cách tương tác tiện dụng, Chat LLMs cho phép người dùng phổ thông dễ dàng sử dụng, đồng thời có thể triển khai rộng rãi trên nhiều loại thiết bị khác nhau. Các Chat LLMs nổi bật hiện nay bao gồm: ChatGPT (OpenAI), Claude (Anthropic), Gemini (Google), Copilot (Microsoft).

**Ưu điểm:**

- Khả năng giao tiếp tự nhiên: LLM có thể hiểu và tạo ra văn bản giống như con người, giúp tương tác trở nên trực quan và dễ dàng hơn.
- Truy cập thông tin nhanh chóng: Có thể xử lý và tóm tắt lượng lớn thông tin từ nhiều nguồn khác nhau, cung cấp câu trả lời nhanh cho nhiều loại câu hỏi.
- Hỗ trợ đa dạng các tác vụ: Viết lách, dịch thuật, tóm tắt văn bản, lập trình, phân tích dữ liệu và nhiều công việc khác.
- Thao tác với đa dạng tài nguyên: LLM có thể thao tác với chữ viết, hình ảnh, âm thanh, video (các mô hình đa phương thức).

**Nhược điểm:**

- Hiện tượng ảo giác (Hallucination): LLM có thể "bịa" ra thông tin không chính xác nhưng lại trình bày một cách rất thuyết phục. Điều này đặc biệt nguy hiểm khi ứng dụng trong lĩnh vực pháp luật.
- Giới hạn knowledge cutoff: Mô hình không có thông tin về các văn bản pháp luật mới ban hành sau thời điểm huấn luyện.
- Nguy cơ lạm dụng: LLM có thể bị sử dụng để tạo nội dung sai lệch hoặc thao túng thông tin pháp luật.
- Phụ thuộc chất lượng prompt: Kết quả phụ thuộc nhiều vào cách người dùng đặt câu hỏi.

### 1.3.3. Lựa chọn mô hình LLM cho đề tài

Hiện nay có ba nhóm LLM thương mại dẫn đầu thị trường: OpenAI GPT-4/GPT-5, Anthropic Claude, và Google Gemini. Bảng 1.1 so sánh các tiêu chí phù hợp với yêu cầu của đề tài.

| Tiêu chí | OpenAI GPT-4/GPT-5 | Anthropic Claude | Google Gemini |
|---|---|---|---|
| Hỗ trợ tiếng Việt | Tốt | Tốt | Rất tốt |
| Function calling (native) | Có | Có | Có |
| Context window | 128k – 200k | 200k – 1M | 1M – 2M |
| Vision API (parse PDF) | Có | Có | Có |
| Chi phí (per 1M tokens) | Cao | Trung bình | Thấp hơn |
| Multi API-key rotation | Không | Không | Có |

*Bảng 1.1. So sánh các LLM thương mại theo tiêu chí phù hợp với đề tài*

Sau khi cân nhắc, đề tài lựa chọn **Google Gemini** làm LLM chính vì bốn lý do chính:

1. Gemini có hỗ trợ tiếng Việt rất tốt nhờ lợi thế từ hệ sinh thái Google Translate và kho dữ liệu đa ngôn ngữ của Google.
2. Hai phiên bản `gemini-2.5-flash` và `gemini-2.5-pro` bổ sung lẫn nhau — Flash nhanh, chi phí thấp phù hợp cho Agent và pipeline RAG; Pro suy luận sâu hơn phù hợp cho Verifier kiểm chứng cuối.
3. Gemini hỗ trợ native function calling và Vision API — cần thiết cho kiến trúc Agent gọi tool và pipeline parse PDF có hình ảnh.
4. Google cho phép đăng ký nhiều API key, giúp triển khai cơ chế xoay vòng key để tránh giới hạn tốc độ khi demo và thực nghiệm.

| Vai trò trong hệ thống | Mô hình | Lý do |
|---|---|---|
| Guardrail, Query Analysis | `gemini-2.5-flash` | Tốc độ cao, chi phí thấp |
| Agent (reasoning + tool calling) | `gemini-2.5-flash` | Cân bằng tốc độ và chất lượng |
| Verifier (kiểm chứng hallucination) | `gemini-2.5-pro` | Suy luận sâu, đối chiếu từng claim |
| Parse PDF (Vision) | `gemini-2.5-flash` | Vision API hỗ trợ tốt tài liệu tiếng Việt |

*Bảng 1.2. Phân tầng sử dụng mô hình Gemini trong hệ thống Vietnam Law Chatbot*

## 1.4. Tìm hiểu về AI Agent

### 1.4.1. Khái niệm AI Agent

Một tác tử (Agent) là bất cứ thứ gì có khả năng nhận thức được môi trường xung quanh và hành động theo môi trường đó. Cuốn sách *Artificial Intelligence: A Modern Approach* (1995) định nghĩa một tác tử là bất cứ thứ gì có thể nhận thức (perceive) môi trường của nó thông qua các cảm biến (sensor) và tác động lên môi trường đó thông qua các bộ truyền động (actuators). "Bộ truyền động" là khái niệm chỉ bất kỳ cách thức, công cụ, biện pháp nào giúp Agent tác động lên môi trường xung quanh nó.

Một Agent được đặc trưng bởi môi trường mà nó hoạt động và tập hợp các hành động mà Agent có thể tác động lên môi trường đó. Ví dụ, một Agent được xây dựng để hỗ trợ tra cứu pháp luật thì "hệ thống pháp luật Việt Nam" (bao gồm CSDL nội bộ và web) sẽ là môi trường của Agent và tác động của Agent lên môi trường sẽ là các hành động "tìm kiếm điều luật", "đối chiếu văn bản", "tổng hợp câu trả lời".

**AI Agent** là Agent được xây dựng trên nền tảng các kỹ thuật AI. Môi trường của AI Agent là bối cảnh, yêu cầu, tài liệu,… được đưa vào bởi người dùng hoặc các tài nguyên hệ thống khác. Các tác động của AI Agent lên môi trường được tăng cường bởi các công cụ mà nó có quyền truy cập.

AI Agent đại diện cho sự phát triển đáng kể trong AI, thể hiện sự thay đổi mô hình trong cách các hệ thống thông minh tương tác với môi trường, đưa ra quyết định và đạt được các mục tiêu phức tạp. Hình sau đây mô tả một AI Agent có tên là SWE-Agent, được xây dựng trên nền tảng mô hình GPT-4. Môi trường của Agent này là máy vi tính với hệ thống tập tin, công cụ dòng lệnh. Tập hành động bao gồm các thao tác lưu trữ, duyệt, xem tập tin.

[IMG:image5.png]
*Hình 1.4. Mô hình SWE AI Agent*

Khi áp dụng vào xây dựng chatbot pháp luật, AI Agent cho phép chatbot thấu hiểu ngữ cảnh câu hỏi và đưa ra những hành động cụ thể để thực hiện yêu cầu — tra cứu điều luật liên quan, đối chiếu văn bản cũ mới, xác minh tính chính xác — trước khi trả lời người dùng.

### 1.4.2. Các thành phần của AI Agent

Kiến trúc của AI Agent đại diện cho sự tích hợp tinh vi của nhiều thành phần cho phép Agent có khả năng nhận thức, tư duy, lên kế hoạch và thực hiện hành động.

AI Agent bao gồm các thành phần sau đây.

[IMG:image6.png]
*Hình 1.5. Sơ đồ kiến trúc các thành phần của AI Agent*

#### 1.4.2.1. Cơ chế nhận thức – Perception

Cơ chế nhận thức là giao diện cho phép thu thập và xử lý thông tin bên ngoài từ môi trường. Trong các Agent dựa trên ngôn ngữ, nhận thức chủ yếu bao gồm các mô-đun hiểu ngôn ngữ tự nhiên (NLU), trích xuất các thực thể và ý định liên quan, chuyển đổi các văn bản phi cấu trúc thành các đối tượng có cấu trúc để xử lý tiếp.

Trong hệ thống Vietnam Law Chatbot, Perception nhận câu hỏi pháp luật từ người dùng, trích xuất các thực thể quan trọng (loại vi phạm, loại văn bản, thời gian áp dụng) và chuyển thành trạng thái đầu vào cho đồ thị LangGraph.

#### 1.4.2.2. Hệ thống biểu diễn tri thức – Knowledge Representation

Hệ thống biểu diễn tri thức cung cấp các cấu trúc và cơ chế để lưu trữ, tổ chức và truy xuất thông tin bên trong Agent. Chúng kết hợp các biểu diễn ký hiệu và phân tán, đồng thời lưu trữ tri thức khai báo, thủ tục, tình tiết và siêu tri thức.

Một Agent hiệu quả cần phải đảm bảo phân biệt giữa nhiều dạng tri thức khác nhau bao gồm:

- **Context:** Sự thật về câu hỏi hiện tại và lịch sử hội thoại.
- **Task:** Các nhiệm vụ cụ thể cần thực hiện trong lượt trả lời này.
- **Steps:** Các bước thủ tục đã và chưa hoàn thành trong kế hoạch.
- **Experiments:** Kết quả từ các lần gọi tool trước đó trong cùng vòng lặp.
- **Meta data:** Siêu tri thức — tự nhận thức về vai trò, khả năng và hạn chế của chính Agent.

#### 1.4.2.3. Mô-đun suy luận và ra quyết định – Reasoning & Decision Making

Các mô-đun suy luận và ra quyết định cho phép Agent xử lý thông tin có sẵn, đánh giá các phương án thay thế và lựa chọn hành động phù hợp. Các mô-đun này có nhiệm vụ lập kế hoạch để Agent thực hiện. Trong đề tài, LLM `gemini-2.5-flash` đảm nhận vai trò này — phân tích tình huống, lập kế hoạch tra cứu và ra quyết định gọi tool phù hợp.

#### 1.4.2.4. Thành phần thực thi – Action

Action là các thành phần chuyển đổi các quyết định thành các hành vi cụ thể tác động đến môi trường. Action có thể bao gồm:

- Tạo phản hồi pháp luật gửi đến người dùng qua SSE streaming.
- Gọi tool tra cứu CSDL pháp luật nội bộ (`retrieve_internal_law`).
- Gọi tool tìm kiếm web (`search_web_for_law`) qua Tavily và Google Grounding API.
- Đặt câu hỏi làm rõ bối cảnh cho người dùng khi câu hỏi chưa đủ thông tin.

#### 1.4.2.5. Các thành phần khác

Ngoài các thành phần chính, AI Agent hiện đại thường bao gồm một số mô-đun và công cụ khác như:

- **Mô-đun quản lý bộ nhớ:** Duy trì thông tin qua nhiều tương tác — trong đề tài, lịch sử hội thoại được lưu trong trường `messages` của AgentState với reducer `add_messages`, đảm bảo chuỗi Thought-Act-Observation được tích luỹ xuyên suốt nhiều node.
- **Thành phần tự phản chiếu (Reflection) và sửa lỗi:** Cho phép Agent đánh giá hiệu suất của chính mình, nhận ra các hạn chế và điều chỉnh phương pháp tiếp cận. Trong đề tài, node Verifier (`gemini-2.5-pro`) đảm nhận vai trò này — đối chiếu từng khẳng định với điều luật đã truy xuất, loại bỏ nội dung không có căn cứ.
- **Cơ chế an toàn và điều chỉnh:** Đảm bảo hành vi Agent nằm trong giới hạn phù hợp — trong đề tài, node Guardrail lọc câu hỏi ngoài phạm vi pháp luật trước khi vào vòng lặp ReAct.

### 1.4.3. Tool trong Agent

Một Agent không nhất thiết truy cập vào các công cụ bên ngoài. Tuy nhiên, nếu không có các công cụ bên ngoài, khả năng của Agent sẽ bị hạn chế. Bản thân một mô hình LLM thường chỉ có thể thực hiện một hành động — một LLM có thể tạo văn bản. Các công cụ bên ngoài làm cho Agent có khả năng hơn rất nhiều, cho phép vừa tạo văn bản vừa truy cập vào các dữ liệu pháp luật nội bộ và web.

Các công cụ giúp Agent vừa nhận biết môi trường vừa hành động dựa trên nó. Các hành động cho phép Agent nhận biết môi trường là hành động đọc, trong khi các hành động cho phép Agent tác động lên môi trường là hành động ghi.

Ví dụ: Một Agent tư vấn pháp luật có thể có tool để truy cập vào ChromaDB nhằm lấy các điều luật liên quan (đọc), vừa truy cập vào tool tìm kiếm web Tavily để lấy văn bản pháp luật mới ban hành (đọc), vừa tổng hợp và streaming kết quả về giao diện người dùng (ghi).

Các tác nhân thường lựa chọn công cụ để sử dụng trong quá trình lên kế hoạch thực hiện. Trong đề tài, hai tool chính được định nghĩa: **`retrieve_internal_law(query)`** tra cứu CSDL pháp luật nội bộ qua ChromaDB với chiến lược Two-stage Retrieval; và **`search_web_for_law(query)`** tìm kiếm pháp luật mới ban hành trên internet.

### 1.4.4. Planning trong Agent

Planning là cốt lõi của một AI Agent tốt. Các AI Agent có thể phải giải quyết những nhiệm vụ rất phức tạp, ví dụ: *"Mức phạt vượt đèn đỏ bằng xe máy theo quy định hiện hành là bao nhiêu và có thay đổi so với Nghị định 100/2019 không?"*. Một nhiệm vụ được xác định bởi mục tiêu và các ràng buộc của nó. Trong ví dụ trên, mục tiêu là thông tin về mức phạt và sự thay đổi theo thời gian, ràng buộc là loại phương tiện và văn bản pháp luật cụ thể.

Các nhiệm vụ phức tạp đòi hỏi phải lập kế hoạch. Đầu ra của quá trình lập kế hoạch là một kế hoạch, tức là một lộ trình vạch ra các bước cần thiết để hoàn thành nhiệm vụ. Đối với một nhiệm vụ bất kỳ, để lập kế hoạch tốt, cần thực hiện:

1. Hiểu nhiệm vụ cần thực hiện.
2. Xem xét tài nguyên và công cụ có sẵn.
3. Lập ra các hướng giải quyết khác nhau và lựa chọn hướng đi tốt nhất.

Đối với AI Agent cũng tương tự, Agent sẽ thực hiện:

1. Hiểu các nhiệm vụ cần thực hiện.
2. Xem xét các Tool và Knowledge có sẵn.
3. Lựa chọn plan tốt nhất.

Tuy nhiên, trong quá trình Planning, Agent hoàn toàn có thể mắc sai lầm và đưa ra kế hoạch không đạt được mục đích. Do đó, việc lập kế hoạch thường được tách riêng ra khỏi việc thực thi và sau khi thực thi một số bước, AI Agent cần có bước đánh giá tình hình và tiến hành **re-planning** nếu cần thiết:

- Nếu kế hoạch là hợp lý và có thể thực hiện tiếp: tiếp tục thực thi.
- Nếu kế hoạch không còn hợp lý: tiến hành lập kế hoạch lại dựa trên dữ liệu thu hoạch được từ các bước thực thi trước đó.

[IMG:image7.png]
*Hình 1.6. Mô hình quá trình Planning và Re-planning của Agent*

Trong hình minh hoạ trên, Agent có quá trình Planner dựa trên đầu vào Query. Plan đã tạo sẽ được đánh giá, sau đó tiến hành thực hiện với các Tool và sau mỗi bước sử dụng Tool, ta sẽ lập kế hoạch lại và tiếp tục chu trình cho đến khi thu được kết quả cuối cùng.

### 1.4.5. Tự đánh giá và sửa lỗi

Như đã trình bày ở mục trước, ngay cả những kế hoạch tốt nhất cũng cần được đánh giá và điều chỉnh liên tục để tối đa hoá độ chính xác của kết quả. Quá trình tự đánh giá hay tự nhìn nhận này được gọi là **Reflection**. Trong lĩnh vực pháp luật, bước kiểm chứng này là thiết yếu vì thông tin sai có thể dẫn đến hậu quả pháp lý nghiêm trọng.

Mặc dù Reflection không hoàn toàn cần thiết để một Agent hoạt động, nhưng nó lại cần thiết để Agent đạt được độ chính xác cao nhất. Có nhiều thời điểm trong quá trình thực hiện tác vụ mà việc tự đánh giá có thể hữu ích:

- Sau khi nhận được truy vấn của người dùng: đánh giá xem yêu cầu có khả thi và trong phạm vi không.
- Sau khi tạo kế hoạch ban đầu: đánh giá xem kế hoạch có hợp lý không.
- Sau mỗi bước thực thi: đánh giá xem nó có đi đúng hướng không, kết quả tìm kiếm có đủ chất lượng không.
- Sau khi toàn bộ kế hoạch đã được thực thi: xác định xem tác vụ đã hoàn thành chưa, câu trả lời có trung thực với tài liệu nguồn không.

Tự nhìn nhận và sửa lỗi là hai cơ chế khác nhau nhưng đi đôi với nhau. Tự nhìn nhận tạo ra những hiểu biết sâu sắc giúp phát hiện ra các lỗi cần sửa. Việc tự nhìn nhận có thể được thực hiện bởi cùng một Agent với các lời nhắc tự phê bình. Nó cũng có thể được thực hiện bởi một thành phần riêng biệt — trong đề tài, `gemini-2.5-pro` đảm nhận vai trò Verifier độc lập.

Lần đầu tiên được đề xuất trong bài báo *"ReAct: Synergizing Reasoning and Acting in Language Models"* (Yao et al., ICLR 2023), việc xen kẽ giữa suy luận (reasoning) và hành động (action) đã trở thành một khuôn mẫu phổ biến cho các Agent. Ở mỗi bước, Agent được yêu cầu giải thích suy nghĩ của mình (lập kế hoạch), thực hiện hành động, sau đó phân tích các kết quả đạt được (tự nhìn nhận). Các AI Agent thường được viết Prompt để tạo ra các output có dạng như sau:

```
Thought 1: [Suy luận về tình huống hiện tại]
Act 1:     [Thực thi hành động cụ thể — gọi tool tra cứu pháp luật]
Observation 1: [Quan sát kết quả trả về từ CSDL]
...
[Lặp lại cho đến khi đủ thông tin]
...
Thought N: [Suy luận cuối — tổng hợp câu trả lời]
Act N:     Finish [Câu trả lời pháp luật hoàn chỉnh kèm dẫn nguồn]
```

[IMG:image8.png]
*Hình 1.7. Ví dụ áp dụng ReAct Agent để trả lời câu hỏi*

Đây cũng là cơ sở cho tính năng **ThinkingPanel** trên ứng dụng di động của hệ thống — hiển thị 5 bước xử lý của pipeline theo thời gian thực, giúp người dùng hiểu được quá trình Agent đang suy luận để đưa ra câu trả lời.

### 1.4.6. Tích hợp RAG vào AI Agent — Agentic RAG

Sự kết hợp giữa kiến trúc RAG và AI Agent tạo ra **Agentic RAG** — bước tiến quan trọng so với Naive RAG. Thay vì một pipeline cố định (Encode → Retrieve → Generate), Agentic RAG giao quyền kiểm soát luồng xử lý cho Agent: Agent tự quyết định khi nào cần tra cứu, tra cứu nguồn nào (CSDL nội bộ hay web), có cần tra cứu thêm không, và khi nào đủ điều kiện để sinh câu trả lời cuối.

| Tiêu chí | Naive RAG | Agentic RAG |
|---|---|---|
| Cấu trúc luồng | Pipeline tuyến tính cố định | Đồ thị có vòng lặp động |
| Số lần truy xuất | Đúng một lần | Từ 0 đến N lần (Agent quyết định) |
| Nguồn dữ liệu | Chỉ CSDL nội bộ | CSDL nội bộ + tìm kiếm Web |
| Câu hỏi đa bước | Không hỗ trợ | Hỗ trợ qua multi-hop reasoning |
| Phát hiện xung đột văn bản | Không | Có (Temporal Conflict Resolution) |
| Tự đánh giá kết quả | Không | Có (thông qua Verifier) |
| Độ trễ phản hồi | ~2 giây | 5–15 giây tuỳ câu hỏi |

*Bảng 1.3. So sánh Naive RAG và Agentic RAG*

Trong đề tài, Agentic RAG được triển khai thông qua framework LangGraph với đồ thị gồm 4 node: **Guardrail → Query Analysis → Agent (ReAct loop) → Verifier**. Kiến trúc cụ thể được trình bày chi tiết ở Chương 2.

## 1.5. Các công nghệ hỗ trợ phát triển hệ thống

### 1.5.1. Ngôn ngữ lập trình Python

Python là một ngôn ngữ lập trình bậc cao, được Guido van Rossum phát triển và phát hành lần đầu vào năm 1991. Python nổi tiếng với cú pháp rõ ràng và dễ đọc, giúp lập trình viên dễ dàng viết và duy trì mã nguồn.

Đặc điểm nổi bật của Python:

- **Cú pháp đơn giản và dễ hiểu:** Python có cú pháp ngắn gọn, dễ học, dễ đọc. Cú pháp của Python gần gũi với ngôn ngữ tự nhiên, giúp người học lập trình nhanh chóng nắm bắt.
- **Thư viện AI/ML phong phú:** Phần lớn các SDK LLM chính thức (Google Gemini, OpenAI, Anthropic, LangChain, LangGraph, Hugging Face Transformers) đều ưu tiên Python, tạo ra hệ sinh thái đồng bộ cho đề tài.
- **Đa nền tảng:** Python có thể chạy trên nhiều hệ điều hành như Windows, macOS, Linux.
- **Cộng đồng lớn mạnh:** Python có cộng đồng lập trình viên lớn mạnh, liên tục cập nhật thư viện mới.

**Ưu điểm:**

- Ngôn ngữ hàng đầu trong lĩnh vực AI/ML và xử lý ngôn ngữ tự nhiên.
- Hỗ trợ async/await native — phù hợp cho các endpoint SSE streaming.
- Tích hợp trực tiếp với toàn bộ công cụ AI của đề tài mà không cần adapter.

**Nhược điểm:**

- Tốc độ thực thi chậm hơn các ngôn ngữ biên dịch như Go hay C++.
- GIL (Global Interpreter Lock) hạn chế xử lý đa luồng CPU-bound thực sự.

Đề tài sử dụng **Python 3.11+** làm ngôn ngữ backend chính cho toàn bộ pipeline Agentic RAG và API service.

### 1.5.2. LangGraph Framework

#### 1.5.2.1. Khái niệm LangGraph

**LangChain** là framework Python mã nguồn mở được phát triển từ tháng 10 năm 2022, cung cấp các abstraction chuẩn hoá để kết nối LLM với nguồn dữ liệu và công cụ bên ngoài. Tuy nhiên, LangChain Chains chỉ hỗ trợ luồng xử lý tuyến tính (Directed Acyclic Graph — DAG): dữ liệu đi một chiều từ đầu đến cuối, không thể quay lại. Đây phù hợp với Naive RAG, nhưng lại không đủ cho AI Agent cần thực hiện vòng lặp ReAct.

**LangGraph** là một framework được phát hành năm 2024, xây dựng trên nền tảng LangChain, chuyên dụng cho bài toán Agent có vòng lặp. LangGraph cung cấp khả năng xây dựng, quản lý các quy trình làm việc AI Agent phức tạp dưới dạng đồ thị có chu trình.

**Ưu điểm:**

- Hỗ trợ chu trình (cycles) — cho phép Agent quay lại node trước tuỳ theo kết quả quan sát.
- Quản lý trạng thái tập trung — toàn bộ đồ thị chia sẻ một State duy nhất.
- Hỗ trợ streaming output (SSE) từng sự kiện realtime về client.
- Dễ gỡ lỗi — trạng thái tập trung cho phép xem đầy đủ diễn biến Agent tại mỗi node.

**Nhược điểm:**

- Đường cong học tập dốc hơn so với LangChain thuần.
- Framework còn trẻ, một số tính năng nâng cao còn thiếu tài liệu chi tiết.

#### 1.5.2.2. Các node và các cạnh trong LangGraph

Về bản chất, LangGraph sử dụng sức mạnh của các kiến trúc dựa trên đồ thị để mô hình hoá và quản lý các mối quan hệ phức tạp giữa các thành phần trong quy trình làm việc của AI Agent.

Thay vì sử dụng cấu trúc chain tuyến tính truyền thống, LangGraph cho phép thiết kế luồng hoạt động phức tạp hơn, tương tự như một mạng lưới với các node (nút) và edge (cạnh):

- **Nodes:** Đại diện cho các bước hoặc giai đoạn trong quá trình hoạt động của Agent. Mỗi node có thể là một task, state hoặc action cụ thể mà Agent cần thực hiện. Ví dụ: Guardrail, Query Analysis, Agent ReAct, Verifier.
- **Edges:** Đại diện cho các kết nối giữa các node, xác định luồng di chuyển của Agent. Edges có thể là direct (trực tiếp) hoặc conditional (có điều kiện): "nếu câu hỏi hợp lệ thì đi đến Query Analysis, ngược lại trả về thông báo từ chối".
- **Conditional Edges:** Đại diện cho những cạnh rẽ nhánh đến các Node khác nhau dựa trên State của Agent. Conditional Edges là thành phần quan trọng giúp quyết định điều hướng Agent và giúp Agent tránh khỏi vòng lặp vĩnh cửu.

[IMG:image9.png]
*Hình 1.8. Mô phỏng các Nút và các Cạnh trong LangGraph*

Tính năng quan trọng nhất của LangGraph là khả năng tạo ra cycles (vòng lặp). Khác với chain truyền thống chỉ đi theo một chiều, LangGraph cho phép Agent quay lại các node đã truy cập, thực hiện lại các bước, tự điều chỉnh dựa trên kết quả và lặp lại cho đến khi đạt được mục tiêu.

#### 1.5.2.3. Quản lý trạng thái trong LangGraph

LangGraph làm sáng tỏ các quy trình trong luồng công việc AI, cho phép minh bạch hoàn toàn trạng thái (State) của tác nhân. Trong LangGraph, tính năng State đóng vai trò như một ngân hàng bộ nhớ ghi lại và theo dõi tất cả thông tin có giá trị được hệ thống AI xử lý.

State có thể là một chuỗi các tin nhắn, một mảng các số, một cấu trúc dữ liệu phức tạp,… State đóng vai trò như công cụ truyền đạt thông tin giữa các Node của Agent. State này được cập nhật khi Agent chạy qua các Node, mỗi Node sẽ xử lý với State là đầu vào và cập nhật State ở đầu ra.

[IMG:image10.png]
*Hình 1.9. Ví dụ State trong Graph của một Agent về thông tin thời tiết*

Dưới đây là ví dụ State được sử dụng trong đồ thị LangGraph của hệ thống Vietnam Law Chatbot:

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query_analysis: str
    is_valid_query: bool
    rejection_reason: str
    iteration_count: int
```

Trường `messages` được chú thích với reducer `add_messages`: thay vì ghi đè danh sách tin nhắn, mỗi node khi trả về tin nhắn mới sẽ được framework tự động append vào danh sách hiện có — đảm bảo chuỗi Thought-Act-Observation được tích luỹ xuyên suốt nhiều node mà không mất thông tin.

State là công cụ mạnh mẽ, truyền đạt ý chí, kế hoạch, yêu cầu, dữ liệu xuyên suốt quá trình hoạt động của Agent. Quản lý State là công việc quan trọng trong phát triển AI Agent với LangGraph. Quản lý trạng thái cũng rất hữu ích khi gỡ lỗi vì nó cho phép tập trung trạng thái của ứng dụng, rút ngắn toàn bộ quy trình debug.

#### 1.5.2.4. Các bước xây dựng AI Agent với LangGraph

Để xây dựng một AI Agent, ta sẽ đi qua các bước sau:

- **Bước 1:** Xác định tính chất Agent: Môi trường, vai trò, đối tượng người dùng, dữ liệu có thể truy cập, giới hạn tri thức, tập hành động.
- **Bước 2:** Lên kế hoạch luồng hoạt động: Từ input đến output cần trải qua những bước gì, các trường hợp có thể xảy ra trong quá trình thực hiện.
- **Bước 3:** Xác định các Node từ workflow đã phân tích.
- **Bước 4:** Xác định các Edge và Conditional Edge dựa trên điều kiện rẽ nhánh.
- **Bước 5:** Xây dựng State bằng `TypedDict` với các trường thông tin cần lưu chuyển.
- **Bước 6:** Xây dựng các Tool cho Agent (hàm Python được đánh dấu `@tool`).
- **Bước 7:** Triển khai và compile đồ thị — chạy qua `compiled.invoke()` (đồng bộ) hoặc `compiled.stream()` (streaming SSE realtime).

### 1.5.3. FastAPI Framework

FastAPI là framework phát triển API dựa trên ngôn ngữ Python, được xây dựng trên Starlette và Pydantic. Framework này hỗ trợ lập trình bất đồng bộ, khai báo kiểu dữ liệu rõ ràng và tự động kiểm tra dữ liệu đầu vào, do đó phù hợp với các hệ thống backend có nhiều luồng xử lý đồng thời.

Trong đề tài, FastAPI được sử dụng để xây dựng hai dịch vụ backend chính là `main-service` và `rag-service`. `main-service` đảm nhận các chức năng nghiệp vụ như xác thực người dùng, quản lý hội thoại, tra cứu thư viện pháp luật và tải lên văn bản. Trong khi đó, `rag-service` phụ trách các tác vụ liên quan đến Agentic RAG, truy xuất vector, gọi mô hình ngôn ngữ lớn và kiểm chứng câu trả lời.

Việc lựa chọn FastAPI phù hợp với kiến trúc của hệ thống vì các thao tác trong backend chủ yếu là tác vụ I/O-bound như truy vấn cơ sở dữ liệu, gọi dịch vụ RAG, kết nối ChromaDB và truyền phản hồi theo thời gian thực qua SSE. Ngoài ra, khả năng tự sinh tài liệu OpenAPI từ khai báo schema giúp quá trình tích hợp giữa backend, ứng dụng di động và trang quản trị được nhất quán hơn.

### 1.5.4. Next.js 16 — Web Admin Dashboard

Next.js là framework phát triển ứng dụng web dựa trên React, hỗ trợ tổ chức giao diện theo cấu trúc route rõ ràng và tích hợp tốt với TypeScript. Trong đề tài, Next.js 16 được sử dụng để xây dựng trang quản trị hệ thống, phục vụ các chức năng như đăng nhập quản trị, tải lên văn bản pháp luật, theo dõi tiến trình xử lý dữ liệu và quan sát các chỉ số thống kê.

Đặc điểm phù hợp của Next.js trong hệ thống là khả năng tổ chức các màn hình quản trị thành những module độc lập như dashboard, danh sách tài liệu, chi tiết tài liệu và trang upload. Cách tổ chức này giúp mã nguồn giao diện dễ mở rộng, đồng thời phù hợp với đặc thù của một hệ thống quản trị dữ liệu pháp luật có nhiều nhóm chức năng khác nhau.

Bên cạnh đó, trang quản trị cần hiển thị trạng thái xử lý tài liệu theo thời gian thực thông qua WebSocket. Next.js kết hợp với React, TailwindCSS và shadcn/ui cho phép xây dựng giao diện có khả năng hiển thị bảng dữ liệu, biểu đồ thống kê, thanh tiến trình và thông báo trạng thái một cách thống nhất. Điều này phù hợp với yêu cầu vận hành và giám sát quy trình cập nhật tri thức pháp luật trong hệ thống.

### 1.5.5. Kotlin Multiplatform + Compose Multiplatform — Ứng dụng di động

Kotlin Multiplatform (KMP) là công nghệ cho phép chia sẻ mã nguồn Kotlin giữa nhiều nền tảng, đặc biệt là Android và iOS. Compose Multiplatform là framework giao diện khai báo, kế thừa tư tưởng thiết kế của Jetpack Compose, cho phép xây dựng giao diện người dùng bằng cùng một ngôn ngữ và cùng một mô hình lập trình.

Trong đề tài, KMP và Compose Multiplatform được sử dụng để phát triển ứng dụng Vietnam Law Chatbot trên thiết bị di động. Việc lựa chọn công nghệ này phù hợp với mục tiêu xây dựng ứng dụng đa nền tảng, trong khi vẫn giữ được sự thống nhất về tầng nghiệp vụ, tầng giao tiếp API, quản lý trạng thái và cách tổ chức giao diện.

Các thành phần như gọi API bằng Ktor, lưu trữ token, xử lý luồng SSE, render câu trả lời dạng Markdown, quản lý trạng thái theo mô hình MVI và điều hướng giữa các màn hình có thể được chia sẻ trong cùng một codebase. Nhờ đó, các chức năng trọng tâm như hỏi đáp pháp luật, tư vấn có hướng dẫn, tra cứu thư viện văn bản và tìm kiếm ngữ nghĩa được triển khai đồng nhất trên cả Android và iOS.

Compose Multiplatform cũng phù hợp với đặc thù giao diện của ứng dụng vì nhiều màn hình có trạng thái thay đổi liên tục, chẳng hạn như quá trình nhận câu trả lời theo dòng sự kiện, bảng hiển thị tiến trình suy luận, danh sách hội thoại và bộ lọc văn bản pháp luật. Mô hình giao diện khai báo giúp trạng thái dữ liệu và giao diện được liên kết chặt chẽ hơn, phù hợp với kiến trúc MVI được áp dụng trong ứng dụng.

Trong đề tài, hệ thống sử dụng Kotlin 2.3.0 và Compose Multiplatform 1.10.0. Lựa chọn này giúp đồ án triển khai ứng dụng di động đa nền tảng nhưng vẫn giữ được sự nhất quán về kiến trúc, ngôn ngữ lập trình và cách tổ chức mã nguồn.

### 1.5.6. Hệ thống cơ sở dữ liệu đa mô hình (Polyglot Persistence)

Hệ thống Vietnam Law Chatbot áp dụng chiến lược **Polyglot Persistence**, tức là sử dụng nhiều loại cơ sở dữ liệu trong cùng một hệ thống. Cách tiếp cận này phù hợp với đề tài vì dữ liệu của hệ thống không đồng nhất: dữ liệu người dùng và hội thoại có tính giao dịch cao, dữ liệu văn bản pháp luật có cấu trúc tài liệu linh hoạt, còn dữ liệu phục vụ RAG lại cần lưu trữ và truy vấn vector embedding.

Thay vì cố gắng lưu toàn bộ dữ liệu vào một hệ quản trị duy nhất, hệ thống lựa chọn PostgreSQL, MongoDB và ChromaDB cho ba nhóm dữ liệu khác nhau. Mỗi cơ sở dữ liệu đảm nhận một vai trò rõ ràng, từ đó giúp kiến trúc lưu trữ vừa đảm bảo tính nhất quán cho nghiệp vụ người dùng, vừa đáp ứng được yêu cầu truy xuất văn bản pháp luật và tìm kiếm ngữ nghĩa.

#### 1.5.6.1. PostgreSQL — Dữ liệu giao dịch

PostgreSQL là hệ quản trị cơ sở dữ liệu quan hệ, phù hợp với các dữ liệu có cấu trúc rõ ràng, có quan hệ khóa ngoại và yêu cầu đảm bảo tính toàn vẹn. Trong hệ thống, PostgreSQL được sử dụng để lưu các dữ liệu giao dịch gồm `users`, `conversations`, `messages`, `document_tasks` và `refresh_tokens`.

Nhóm dữ liệu này cần đảm bảo các thao tác như đăng ký, đăng nhập, làm mới token, lưu hội thoại và ghi nhận tiến trình xử lý tài liệu được thực hiện nhất quán. Ví dụ, một tin nhắn phải gắn với đúng hội thoại, một refresh token phải gắn với đúng người dùng, và một tác vụ xử lý tài liệu phải có trạng thái rõ ràng trong suốt quá trình upload, parse và ingest. Do đó, mô hình quan hệ của PostgreSQL phù hợp để biểu diễn các ràng buộc dữ liệu này.

Bên cạnh đó, PostgreSQL hỗ trợ giao dịch ACID và truy vấn SQL mạnh, giúp hệ thống dễ dàng lọc, sắp xếp và thống kê dữ liệu nghiệp vụ. Trong đề tài, backend sử dụng SQLAlchemy 2.0 kết hợp với `asyncpg` để làm việc với PostgreSQL theo hướng bất đồng bộ, phù hợp với kiến trúc FastAPI của Main Service.

#### 1.5.6.2. MongoDB — Kho văn bản pháp luật

MongoDB là cơ sở dữ liệu NoSQL theo mô hình tài liệu, phù hợp với dữ liệu có cấu trúc linh hoạt và kích thước nội dung lớn. Trong hệ thống, MongoDB được sử dụng để lưu toàn văn các điều luật trong collection `VietnamLawDB.articles`.

Dữ liệu pháp luật không phải lúc nào cũng có cấu trúc đồng nhất. Mỗi điều luật có thể có tiêu đề, nội dung, số văn bản, năm ban hành, chủ đề, từ khóa, tóm tắt và các metadata khác nhau tùy theo loại văn bản. Mô hình document của MongoDB cho phép lưu mỗi điều luật như một tài liệu độc lập, trong đó phần nội dung và metadata có thể mở rộng linh hoạt mà không cần thay đổi schema quan hệ phức tạp.

Theo dữ liệu thực tế của đề tài, MongoDB đang lưu **528.620 điều luật** trải dài từ năm 1945 đến năm 2026. Kho dữ liệu này phục vụ các chức năng duyệt thư viện pháp luật, xem chi tiết điều luật, tìm kiếm theo từ khóa, lọc theo năm ban hành và chủ đề. Driver `motor` được sử dụng để truy vấn MongoDB theo hướng bất đồng bộ, giúp Main Service xử lý tốt các thao tác đọc dữ liệu văn bản lớn.

#### 1.5.6.3. ChromaDB — Kho vector embedding

ChromaDB là cơ sở dữ liệu vector, được sử dụng để lưu trữ embedding của các đoạn văn bản pháp luật sau khi đã được chia nhỏ. Đây là thành phần cần thiết cho các chức năng dựa trên tìm kiếm ngữ nghĩa, đặc biệt là Agentic RAG và AI-Powered Search.

Trong hệ thống, toàn văn điều luật từ MongoDB không được đưa trực tiếp vào mô hình ngôn ngữ lớn. Thay vào đó, văn bản được chia thành các đoạn nhỏ, mã hóa thành vector bằng mô hình embedding tiếng Việt và lưu trong collection `vietnamese_law` của ChromaDB. Khi người dùng đặt câu hỏi, hệ thống mã hóa câu hỏi thành vector và tìm các đoạn luật có ngữ nghĩa gần nhất thông qua cosine similarity.

Collection `vietnamese_law` hiện chứa **690.360 chunks**, mỗi vector có 768 chiều và đi kèm metadata như `law_id`, `article_id`, `year`, `topics`, `keywords`. Các metadata này giúp hệ thống vừa truy xuất theo ngữ nghĩa, vừa giữ được liên kết ngược về văn bản pháp luật gốc để phục vụ trích dẫn nguồn. ChromaDB phù hợp với đồ án vì có thể triển khai cục bộ bằng Docker, tích hợp thuận tiện với Python/FastAPI và hỗ trợ chỉ mục HNSW cho truy vấn vector tốc độ cao.

## 1.6. Tổng kết chương 1

Chương 1 đã trình bày một cách tổng quan về hệ thống chatbot tư vấn pháp luật và các nền tảng lý thuyết cần thiết để hiểu kiến trúc của hệ thống Vietnam Law Chatbot. Nội dung chính bao gồm phần giới thiệu tổng quan về chatbot và tiềm năng ứng dụng trong lĩnh vực pháp luật Việt Nam, các phương pháp xây dựng chatbot từ tập luật đến LLMs+RAG và AI Agent. Bên cạnh đó, chương 1 đã trình bày chi tiết về Mô hình ngôn ngữ lớn (LLM) và cách lựa chọn mô hình phù hợp, về AI Agent với kiến trúc đầy đủ gồm Perception, Knowledge, Reasoning, Action và các cơ chế Planning, ReAct, Verifier — cùng khái niệm Agentic RAG kết hợp sức mạnh của cả hai.

Trong chương tiếp theo, báo cáo sẽ trình bày chi tiết phương pháp xây dựng hệ thống Vietnam Law Chatbot với AI Agent và Agentic RAG — bao gồm đồ thị LangGraph 4 node (Guardrail → Query Analysis → Agent → Verifier), thuật toán Two-stage Retrieval với Temporal Conflict Resolution phát hiện xung đột văn bản cũ/mới, và luồng Tư vấn có hướng dẫn (Guided Consultation) với SSE streaming.
