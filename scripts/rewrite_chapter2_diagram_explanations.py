from __future__ import annotations

from pathlib import Path

from docx import Document


DOCX = Path("Bao_Cao/02_Chuong_2.docx")


def delete_paragraph(paragraph) -> None:
    element = paragraph._element
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)


def main() -> None:
    doc = Document(DOCX)
    paragraphs = list(doc.paragraphs)

    replacements = {
        24: (
            'Hình 2.1 được sử dụng để giải thích hệ thống ở mức kiến trúc lớp. '
            'Từ trên xuống dưới, người đọc có thể thấy bốn lớp chính: lớp giao diện, '
            'lớp điều phối nghiệp vụ, lớp tri thức và suy luận, cuối cùng là lớp dữ liệu nền. '
            'Cách trình bày này giúp làm rõ rằng người dùng không tương tác trực tiếp với phần AI '
            'hay kho dữ liệu, mà mọi thao tác đều đi qua lớp điều phối.'
        ),
        25: (
            'Trong sơ đồ, lớp điều phối nghiệp vụ là điểm trung gian quan trọng. '
            'Lớp này tiếp nhận yêu cầu từ Mobile App và Admin Web, kiểm tra người dùng, '
            'ghi nhận trạng thái cần thiết rồi chuyển những tác vụ cần tri thức pháp luật '
            'xuống lớp suy luận. Nhờ vậy, giao diện phía client chỉ cần làm việc với một luồng ổn định, '
            'không phải biết hệ thống bên dưới đang dùng bao nhiêu kho dữ liệu hay bao nhiêu bước xử lý.'
        ),
        26: (
            'Lớp dữ liệu nền thể hiện các loại dữ liệu lâu dài của hệ thống, bao gồm thông tin người dùng, '
            'lịch sử hội thoại, văn bản pháp luật và vector tri thức. Khối nguồn hỗ trợ bên ngoài được đặt riêng '
            'để nhấn mạnh rằng LLMs, tìm kiếm pháp luật và lưu trữ file chỉ đóng vai trò hỗ trợ cho pipeline, '
            'không phải nơi quyết định trực tiếp cấu trúc nghiệp vụ của hệ thống.'
        ),
        30: (
            'Hình 2.2 mô tả Main Service như trung tâm điều phối của toàn bộ hệ thống. '
            'Thay vì liệt kê từng file hay từng lớp mã nguồn, sơ đồ tập trung vào các năng lực nghiệp vụ chính: '
            'xác thực, hội thoại, tư vấn có hướng dẫn, quản trị văn bản, làm việc với dữ liệu giao dịch '
            'và chuyển các tác vụ tri thức sang RAG Service.'
        ),
        40: (
            'Khối trung tâm trong hình thể hiện vai trò của Main Service: chuẩn hóa yêu cầu từ nhiều giao diện '
            'thành các luồng xử lý thống nhất. Với người dùng cuối, Main Service đảm bảo chat và tư vấn có hướng dẫn '
            'được lưu trạng thái rõ ràng. Với quản trị viên, Main Service tiếp nhận văn bản mới, theo dõi tiến trình '
            'xử lý và chỉ công bố tri thức khi dữ liệu đã được cập nhật đồng bộ.'
        ),
        41: (
            'Cách thiết kế này giúp giảm độ phức tạp cho frontend. Mobile App và Admin Web không cần gọi trực tiếp '
            'nhiều thành phần backend khác nhau; mọi yêu cầu đều đi qua Main Service. Nhờ đó, các quy tắc xác thực, '
            'phân quyền, ghi log, lưu hội thoại và điều phối tác vụ nặng được đặt tại một điểm kiểm soát thống nhất.'
        ),
        45: (
            'Hình 2.3 trình bày RAG Service như một bộ máy trả lời có kiểm chứng. '
            'Sơ đồ không nhằm mô tả cấu trúc file cài đặt, mà mô tả đường đi của một câu hỏi pháp luật: '
            'hệ thống trước hết hiểu ý định và phạm vi câu hỏi, sau đó truy hồi tri thức, suy luận trên bằng chứng, '
            'kiểm chứng lại nội dung và cuối cùng mới tạo câu trả lời kèm nguồn tham chiếu.'
        ),
        54: (
            'Điểm quan trọng của sơ đồ là câu trả lời không được sinh trực tiếp từ LLMs một cách độc lập. '
            'Khối kho tri thức cung cấp dữ liệu nền; khối truy hồi chọn ra nguồn liên quan; khối suy luận tổng hợp '
            'thành câu trả lời; còn khối kiểm chứng đóng vai trò rà soát cuối cùng để hạn chế nội dung thiếu căn cứ. '
            'Cách chia vai trò này phù hợp với bài toán pháp luật, nơi câu trả lời cần dựa trên nguồn rõ ràng.'
        ),
        55: (
            'Nhìn từ góc độ phương pháp xây dựng hệ thống, RAG Service là nơi kết hợp ba nhóm kỹ thuật: '
            'truy hồi thông tin để tìm bằng chứng, suy luận ngôn ngữ để giải thích nội dung pháp luật, '
            'và kiểm chứng để giảm rủi ro sai lệch. Sơ đồ vì vậy được đọc như một pipeline đảm bảo chất lượng, '
            'không phải như danh sách module lập trình.'
        ),
        108: (
            'Hình 2.4 mô tả phương pháp Agentic RAG theo bốn bước lớn. Đầu tiên, hệ thống kiểm soát đầu vào '
            'để loại bỏ các câu hỏi ngoài phạm vi pháp luật. Tiếp theo, câu hỏi hợp lệ được phân tích thành nhu cầu '
            'tìm kiếm rõ hơn. Sau đó, Agent chủ động thu thập bằng chứng bằng các công cụ truy hồi. Cuối cùng, '
            'câu trả lời được kiểm chứng trước khi trả về người dùng.'
        ),
        109: (
            'Điểm khác biệt so với RAG tuyến tính là hệ thống không chỉ tìm kiếm một lần rồi trả lời ngay. '
            'Ở bước Agent hành động, hệ thống có thể tiếp tục thu thập thêm bằng chứng nếu thông tin hiện tại chưa đủ. '
            'Điều này phù hợp với câu hỏi pháp luật vì nhiều tình huống cần vừa tra cứu văn bản nội bộ, vừa đối chiếu '
            'nguồn cập nhật trước khi kết luận.'
        ),
        110: (
            'Sơ đồ cũng làm rõ hai lớp kiểm soát chất lượng: kiểm soát đầu vào ở bước Guardrail và kiểm soát đầu ra '
            'ở bước Kiểm chứng. Nhờ vậy, hệ thống vừa hạn chế xử lý những yêu cầu không phù hợp, vừa giảm khả năng '
            'trả lời thiếu căn cứ trong các tình huống pháp lý nhạy cảm.'
        ),
        190: (
            'Hình 2.5 giải thích vòng lặp Re-Act theo cách trực quan. Hệ thống bắt đầu từ nhiệm vụ trả lời câu hỏi, '
            'sau đó lần lượt đi qua các trạng thái Think, Act và Observe. Think là bước lập kế hoạch tìm kiếm; '
            'Act là bước gọi công cụ truy hồi; Observe là bước nhận lại bằng chứng để đánh giá.'
        ),
        198: (
            'Ý nghĩa của vòng lặp này là câu trả lời không được tạo ra ngay từ lần suy luận đầu tiên. '
            'Nếu bằng chứng thu được chưa đủ, hệ thống quay lại bước lập kế hoạch để tìm thêm nguồn. '
            'Khi bằng chứng đã đủ, pipeline mới chuyển sang bước trả lời và dẫn nguồn. Cách làm này giúp câu trả lời '
            'bám sát dữ liệu hơn so với việc để LLMs tự suy luận từ tri thức sẵn có.'
        ),
        199: (
            'Trong bối cảnh pháp luật, Re-Act đặc biệt hữu ích vì cùng một câu hỏi có thể cần nhiều mảnh bằng chứng: '
            'điều luật gốc, trạng thái hiệu lực, quy định mới thay thế hoặc nguồn tham chiếu bổ sung. '
            'Việc tách rõ lập kế hoạch, hành động và quan sát giúp hệ thống kiểm soát được quá trình thu thập căn cứ.'
        ),
        205: (
            'Để tránh vòng lặp kéo dài không cần thiết, hệ thống đặt giới hạn cho số lần lặp và luôn chuyển sang bước '
            'kiểm chứng trước khi trả lời. Nhờ đó, pipeline vừa có khả năng chủ động tìm thêm bằng chứng, vừa giữ được '
            'độ trễ trong phạm vi chấp nhận được cho trải nghiệm chat.'
        ),
        246: (
            'Ở mức phương pháp, truy vấn đưa vào công cụ truy hồi không còn là nguyên văn câu hỏi ban đầu, '
            'mà là phiên bản đã được rút gọn theo ý định pháp lý chính. Cách này giúp hệ thống tìm đúng nhóm văn bản '
            'liên quan thay vì bị nhiễu bởi các phần hội thoại không cần thiết.'
        ),
        250: (
            'Hình 2.6 mô tả pipeline truy xuất theo tầng lọc. Bước đầu tiên tìm kiếm rộng trong kho vector để lấy '
            'một tập ứng viên đủ lớn. Sau đó, hệ thống xếp hạng lại các ứng viên theo mức phù hợp với câu hỏi, '
            'rồi kiểm tra thêm yếu tố thời điểm để ưu tiên văn bản hiện hành.'
        ),
        251: (
            'Kết quả cuối cùng của pipeline là ngữ cảnh chọn lọc cho Agent. Nếu nguồn nội bộ chưa đủ chắc chắn, '
            'pipeline tạo tín hiệu để hệ thống bổ sung tìm kiếm từ nguồn pháp luật cập nhật. Nhờ vậy, phần truy hồi '
            'không chỉ tối ưu theo độ giống ngữ nghĩa, mà còn xét đến độ tin cậy của nguồn dùng cho trả lời.'
        ),
        267: (
            'Công cụ tìm kiếm web được dùng như một nguồn bổ sung khi hệ thống cần kiểm tra tính cập nhật của quy định. '
            'Trong báo cáo này, phần quan trọng không nằm ở tên thư viện hay endpoint cụ thể, mà ở vai trò phương pháp: '
            'nguồn web giúp đối chiếu xem văn bản đang được dùng có còn phù hợp với quy định hiện hành hay không.'
        ),
        276: (
            'Khi kết hợp nguồn nội bộ và nguồn cập nhật, hệ thống ưu tiên nguyên tắc an toàn: câu trả lời chỉ nên khẳng định '
            'nội dung pháp lý khi có căn cứ rõ ràng. Nếu nguồn nội bộ và nguồn cập nhật có dấu hiệu khác nhau, thông tin mới '
            'được ưu tiên để tránh áp dụng quy định đã cũ.'
        ),
        290: (
            'Như vậy, web search không thay thế kho dữ liệu nội bộ, mà đóng vai trò kiểm tra và bổ sung. '
            'Kho nội bộ cung cấp cấu trúc văn bản đã được chuẩn hóa, còn nguồn cập nhật giúp giảm rủi ro sử dụng văn bản '
            'không còn hiệu lực.'
        ),
        317: (
            'Hình 2.7 giải thích cách hệ thống xử lý xung đột thời gian giữa văn bản cũ và văn bản mới. '
            'Trong lĩnh vực pháp luật, hai văn bản có thể cùng nói về một vấn đề nhưng khác thời điểm ban hành hoặc hiệu lực. '
            'Nếu chỉ dựa vào độ liên quan ngữ nghĩa, hệ thống có thể chọn nhầm văn bản cũ vì nội dung của nó giống câu hỏi hơn.'
        ),
        319: (
            'Sơ đồ thể hiện ba thao tác chính: nhận diện các nguồn có khả năng cùng chủ đề, đối chiếu hiệu lực và quan hệ sửa đổi, '
            'sau đó gắn trạng thái cho nguồn hiện hành và nguồn cũ. Nguồn hiện hành được dùng làm căn cứ chính, trong khi nguồn cũ '
            'chỉ nên dùng để giải thích sự thay đổi hoặc so sánh khi cần.'
        ),
        325: (
            'Thiết kế này giúp câu trả lời phù hợp hơn với bản chất của bài toán pháp luật: người dùng không chỉ cần câu trả lời '
            'có vẻ liên quan, mà cần câu trả lời dựa trên quy định đang có giá trị áp dụng. Vì vậy, yếu tố thời gian và hiệu lực '
            'được đưa vào pipeline như một tiêu chí riêng, bên cạnh điểm liên quan ngữ nghĩa.'
        ),
        334: (
            'Hình 2.8 mô tả luồng tư vấn có hướng dẫn theo dạng pipeline nghiệp vụ. Sơ đồ nhấn mạnh sự biến đổi của thông tin: '
            'từ câu hỏi ban đầu còn thiếu dữ kiện, hệ thống tạo câu hỏi làm rõ; người dùng chọn các phương án phù hợp; '
            'sau đó hệ thống mới trả lời dựa trên dữ kiện đã được bổ sung. Cách trình bày này giúp người đọc hiểu mục tiêu '
            'của chức năng mà không cần đi vào từng request kỹ thuật.'
        ),
        351: (
            'Ở bước hỏi làm rõ, hệ thống phân tích câu hỏi ban đầu để xác định những thông tin còn thiếu. '
            'Kết quả không phải là câu trả lời pháp lý ngay, mà là một tập câu hỏi ngắn giúp người dùng bổ sung bối cảnh. '
            'Bước này đặc biệt hữu ích với các câu hỏi mơ hồ như không nêu rõ đối tượng, thời điểm, loại thủ tục hoặc tình huống áp dụng.'
        ),
        390: 'Hình 2.9. Luồng cập nhật tri thức pháp luật từ phía quản trị',
        392: (
            'Hình 2.9 trình bày luồng cập nhật tri thức pháp luật từ phía quản trị theo mức khái niệm. '
            'Sơ đồ bắt đầu từ việc admin tải văn bản mới, đi qua bước tiền kiểm, trích xuất cấu trúc, lưu tri thức gốc '
            'và tạo vector truy hồi. Điểm cuối của luồng là trạng thái "sẵn sàng phục vụ hỏi đáp", nghĩa là văn bản mới '
            'đã có thể được dùng trong pipeline trả lời.'
        ),
        394: (
            'Quy trình được thiết kế để giảm rủi ro đưa dữ liệu sai vào kho tri thức. Bước tiền kiểm giúp phát hiện tài liệu '
            'không phù hợp hoặc trùng lặp trước khi chạy các tác vụ nặng. Bước trích xuất cấu trúc chuyển nội dung PDF thành '
            'các đơn vị tri thức có thể tra cứu, gồm điều khoản, metadata và nguồn gốc văn bản.'
        ),
        395: (
            'Sau khi trích xuất, dữ liệu được đồng bộ theo hai hướng: tri thức gốc phục vụ đọc và hiển thị văn bản, '
            'còn vector truy hồi phục vụ tìm kiếm ngữ nghĩa trong quá trình hỏi đáp. Cơ chế hoàn tác trong sơ đồ nhấn mạnh '
            'nguyên tắc nhất quán dữ liệu: nếu một bước đồng bộ thất bại, hệ thống cần đưa các kho liên quan về trạng thái an toàn.'
        ),
        401: (
            'Cách thiết kế này phù hợp với chức năng admin vì cập nhật văn bản pháp luật là thao tác có tác động trực tiếp '
            'tới chất lượng tư vấn. Hệ thống không chỉ cần thêm dữ liệu mới, mà còn cần kiểm soát dữ liệu đó có đúng loại, '
            'không trùng lặp và đã được đồng bộ đầy đủ trước khi cho phép sử dụng trong trả lời.'
        ),
        475: 'Hình 2.10. Luồng trải nghiệm hỏi đáp theo thời gian thực',
        476: (
            'Hình 2.10 mô tả luồng trải nghiệm hỏi đáp theo thời gian thực. Sơ đồ được đọc từ trái sang phải: người dùng đặt câu hỏi, '
            'hệ thống ghi nhận hội thoại, chuyển sang bước streaming xử lý, sau đó trả về câu trả lời cuối cùng kèm nguồn tham chiếu. '
            'Các khối bên dưới thể hiện dữ liệu hội thoại được lưu lại và câu hỏi gợi ý được sinh sau khi câu trả lời chính hoàn tất.'
        ),
        477: (
            'Điểm quan trọng của thiết kế này là tách câu trả lời cuối cùng khỏi tiến trình xử lý trung gian. '
            'Trong lúc Agentic RAG đang truy hồi và kiểm chứng, giao diện có thể hiển thị tiến trình để người dùng biết hệ thống đang làm việc. '
            'Tuy nhiên, nội dung pháp lý cuối cùng chỉ nên xuất hiện sau khi pipeline đã hoàn tất và câu trả lời đã có nguồn tham chiếu.'
        ),
        479: (
            'Luồng chat được thiết kế theo nguyên tắc lưu trước, hiển thị sau đối với dữ liệu quan trọng. '
            'Câu hỏi của người dùng được ghi nhận vào lịch sử hội thoại, sau đó hệ thống mới xử lý bằng pipeline RAG. '
            'Khi có câu trả lời cuối cùng, kết quả tiếp tục được lưu vào lịch sử để người dùng có thể mở lại cuộc trò chuyện về sau.'
        ),
        486: (
            'Nguyên tắc này giúp tránh tình trạng người dùng đã thấy câu trả lời nhưng backend chưa kịp ghi nhận dữ liệu. '
            'Với hệ thống tư vấn pháp luật, lịch sử hội thoại không chỉ phục vụ trải nghiệm mà còn giúp người dùng theo dõi lại '
            'bối cảnh tư vấn và các nguồn đã được sử dụng.'
        ),
        491: (
            'Các cập nhật trong quá trình streaming chỉ đóng vai trò trạng thái xử lý, không phải dữ liệu pháp lý cuối cùng. '
            'Chúng giúp giao diện tránh trạng thái chờ thụ động, đồng thời vẫn bảo đảm câu trả lời chính chỉ được hiển thị '
            'khi đã đi qua bước truy hồi và kiểm chứng.'
        ),
        493: (
            'Lịch sử hội thoại được dùng để hiểu ngữ cảnh các câu hỏi nối tiếp, ví dụ khi người dùng hỏi tiếp một ý sau câu trả lời trước đó. '
            'Tuy nhiên, lịch sử không được xem là căn cứ pháp lý. Mỗi câu trả lời vẫn cần dựa trên nguồn được truy hồi trong lượt xử lý hiện tại.'
        ),
        498: (
            'Câu hỏi gợi ý được xử lý như một tác vụ hỗ trợ trải nghiệm. Nó được sinh sau câu trả lời chính và không làm chậm luồng trả lời. '
            'Nhờ vậy, hệ thống vừa giữ được tốc độ phản hồi, vừa giúp người dùng tiếp tục mạch tư vấn bằng các câu hỏi liên quan.'
        ),
        508: (
            'Tầng chia sẻ logic nghiệp vụ gồm các mô hình dữ liệu, lớp truy cập API, phần ánh xạ dữ liệu, xử lý stream và quản lý trạng thái. '
            'Các thành phần này được dùng chung giữa các nền tảng để bảo đảm luồng chat và tư vấn có hướng dẫn hoạt động nhất quán.'
        ),
        523: (
            'Với MVI, các luồng phức tạp như streaming không bị trộn trực tiếp vào giao diện. '
            'Sự kiện từ server được chuyển thành thay đổi trạng thái rõ ràng; màn hình chỉ cần hiển thị theo state hiện tại. '
            'Cách tổ chức này giúp giao diện chat ổn định hơn khi cùng lúc có tin nhắn người dùng, tiến trình xử lý, câu trả lời cuối và câu hỏi gợi ý.'
        ),
    }

    delete_indices = {
        31, 32, 33, 34, 35, 36, 37, 38, 39,
        46, 47, 48, 49, 50, 51, 52, 53,
        104, 105, 106, 107, 111, 112, 113, 114,
        191, 192, 193, 194, 195, 196, 197, 200, 201, 202, 203, 204,
        247, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 262, 263, 264, 265,
        268, 269, 270, 271, 272, 273, 274, 275, 277, 278, 279, 280, 281, 282, 283,
        284, 285, 286, 287, 288, 289,
        320, 321, 322, 323, 324,
        396, 397, 398, 399, 400, 402, 403, 404, 405,
        480, 481, 482, 483, 484, 485, 487, 490, 494, 495, 496, 499, 500,
        507, 509, 510, 511,
    }

    for idx, text in replacements.items():
        paragraphs[idx].text = text

    for idx in sorted(delete_indices, reverse=True):
        delete_paragraph(paragraphs[idx])

    doc.save(DOCX)


if __name__ == "__main__":
    main()
