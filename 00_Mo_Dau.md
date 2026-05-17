# BAN CƠ YẾU CHÍNH PHỦ
# HỌC VIỆN KỸ THUẬT MẬT MÃ
-------------------------

## BÁO CÁO ĐỒ ÁN TỐT NGHIỆP ĐẠI HỌC

**ĐỀ TÀI:**
**NGHIÊN CỨU PHÁT TRIỂN TRỢ LÝ ẢO PHÁP LUẬT CHO CHUYỂN ĐỔI SỐ**

**Sinh viên thực hiện:** Vương Văn Duy
**Giáo viên hướng dẫn:** ThS. Trần Đức Thịnh

Hà Nội, Năm 2026

---

# LỜI CẢM ƠN

Trong suốt quá trình học tập và nghiên cứu tại Học viện Kỹ thuật mật mã, em đã nhận được sự quan tâm, chỉ bảo và giúp đỡ tận tình của các thầy cô giáo, gia đình và bạn bè để hoàn thành tốt khóa học cũng như đồ án tốt nghiệp này.

Trước tiên, em xin gửi lời cảm ơn sâu sắc nhất tới ThS. Trần Đức Thịnh, người đã trực tiếp hướng dẫn, định hướng và tận tình chỉ bảo, truyền đạt những kiến thức quý báu, tạo mọi điều kiện thuận lợi nhất cho em trong suốt thời gian nghiên cứu và thực hiện đồ án.

Em cũng xin trân trọng cảm ơn các thầy cô giáo trong Khoa Công nghệ Thông tin - Học viện Kỹ thuật Mật mã đã trang bị cho em những kiến thức nền tảng vững chắc trong suốt những năm tháng học tập trên giảng đường, làm hành trang quan trọng để em có thể tiếp cận và hoàn thành đề tài nghiên cứu này.

Mặc dù đã có nhiều cố gắng trong quá trình thực hiện, nhưng do hạn chế về mặt thời gian cũng như kinh nghiệm thực tiễn, đồ án chắc chắn không tránh khỏi những thiếu sót. Em rất mong nhận được sự góp ý, chỉ bảo của quý thầy cô và các bạn để đồ án được hoàn thiện hơn, đồng thời giúp em rút ra những bài học kinh nghiệm quý báu cho công việc thực tế sau này.

Em xin chân thành cảm ơn!

Hà Nội, ngày ... tháng ... năm 2026
Sinh viên thực hiện


Vương Văn Duy

---

# LỜI CAM ĐOAN

Em tên là: Vương Văn Duy, sinh viên lớp CT6D, chuyên ngành Phát triển phần mềm di động - Học viện Kỹ thuật Mật mã.
Em xin cam đoan đề tài đồ án tốt nghiệp "Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số" là sản phẩm nghiên cứu của riêng em dưới sự hướng dẫn của ThS. Trần Đức Thịnh. Các nội dung nghiên cứu, thiết kế hệ thống và kết quả đạt được trong đồ án này là trung thực và chưa từng được công bố trong bất kỳ công trình nào khác.

Mọi tài liệu tham khảo, mã nguồn mở sử dụng hoặc kế thừa từ các công trình nghiên cứu khác đều được trích dẫn và ghi rõ nguồn gốc trong phần Tài liệu tham khảo. Hệ thống mã nguồn do em tự phát triển dựa trên việc nghiên cứu tài liệu và áp dụng các công nghệ hiện đại.

Nếu có bất kỳ sự gian lận hay vi phạm quy định nào về tính trung thực của đồ án, em xin chịu hoàn toàn trách nhiệm trước Hội đồng bảo vệ đồ án tốt nghiệp và nhà trường.

Hà Nội, ngày ... tháng ... năm 2026
Sinh viên thực hiện


Vương Văn Duy

---

# LỜI NÓI ĐẦU

Trong bối cảnh công cuộc chuyển đổi số quốc gia đang diễn ra mạnh mẽ trên mọi lĩnh vực, việc ứng dụng công nghệ thông tin vào quản lý, vận hành và cung cấp dịch vụ hành chính công, pháp luật ngày càng trở nên cấp thiết. Đặc biệt đối với lĩnh vực pháp luật, nơi hệ thống văn bản quy phạm pháp luật của Việt Nam rất đồ sộ, phức tạp và thường xuyên được cập nhật, việc tra cứu và tìm hiểu luật của người dân, doanh nghiệp và thậm chí cả các cán bộ chuyên trách đang gặp không ít khó khăn. Người dùng thông thường gặp rào cản lớn về mặt thuật ngữ chuyên ngành cũng như việc phân mảnh của các thông tin. 

Sự bùng nổ của trí tuệ nhân tạo (AI), đặc biệt là các Mô hình ngôn ngữ lớn (Large Language Models - LLMs) đã mở ra hướng đi mới trong việc giải quyết bài toán giao tiếp giữa người và máy. Tuy nhiên, các LLM thông thường dễ gặp phải hiện tượng "ảo giác thông tin" (hallucination) – một điểm chí mạng trong lĩnh vực đòi hỏi tính chính xác tuyệt đối như pháp luật. Để giải quyết triệt để vấn đề này, kiến trúc Retrieval-Augmented Generation (RAG) và hiện đại hơn là mô hình AI Agent (Agentic RAG) ra đời, kết hợp khả năng suy luận ngôn ngữ linh hoạt của LLM với thông tin được trích xuất từ cơ sở dữ liệu luật pháp chuẩn xác, cập nhật theo thời gian thực.

Nhận thấy tiềm năng to lớn đó cùng mong muốn đóng góp một giải pháp thiết thực cho công tác chuyển đổi số, em đã quyết định chọn đề tài: **"Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số"**. 

Mục tiêu chính của đồ án là nghiên cứu và xây dựng một hệ thống Chatbot tư vấn pháp luật (Vietnam Law Chatbot) với các chức năng nổi bật như: Chat hỏi đáp dựa trên cơ sở dữ liệu luật Việt Nam; Tư vấn có hướng dẫn (Guided Consultation) giúp làm rõ các bối cảnh cụ thể của người dùng trước khi trả lời; Cung cấp công cụ quản trị giúp tự động hóa quá trình số hóa và cập nhật văn bản pháp luật bằng các kỹ thuật xử lý PDF đa luồng và mô hình AI.

Nội dung của đồ án được cấu trúc thành 4 chương chính:
- **Chương 1: Tổng quan đề tài và Cơ sở lý thuyết:** Trình bày bối cảnh, thực trạng, các khái niệm về RAG, AI Agent, LLMs và các công nghệ sử dụng trong đồ án.
- **Chương 2: Phương pháp xây dựng hệ thống trợ lý ảo pháp luật:** Trình bày chi tiết giải pháp kỹ thuật, từ kiến trúc tổng thể, đường ống RAG nâng cao (Agentic RAG) đến luồng tư vấn có hướng dẫn.
- **Chương 3: Phân tích và Thiết kế hệ thống:** Đặc tả các yêu cầu chức năng, phi chức năng, biểu đồ Usecase, Sequence Diagram, thiết kế cơ sở dữ liệu và thiết kế API.
- **Chương 4: Triển khai ứng dụng và Thực nghiệm:** Trình bày giao diện ứng dụng, quy trình hoạt động thực tế và các đánh giá về hiệu năng cũng như độ chính xác của hệ thống.

---
