from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Bao_Cao" / "02_Chuong_2_ban_hoan_chinh_de_kiem_tra.docx"
OUT = ROOT / "Bao_Cao" / "02_Chuong_2_ban_van_phong_mau.docx"


def main() -> None:
    shutil.copy2(SRC, OUT)
    doc = Document(OUT)
    p = list(doc.paragraphs)

    replacements = {
        1: (
            "Chương này trình bày phương pháp xây dựng hệ thống Vietnam Law Chatbot từ góc nhìn kiến trúc và tổ chức "
            "luồng xử lý. Trọng tâm của chương không phải là mô tả lại từng thành phần cài đặt, mà làm rõ cách hệ thống "
            "được thiết kế để trả lời câu hỏi pháp luật có căn cứ, hỗ trợ người dùng làm rõ tình huống và cho phép quản "
            "trị viên cập nhật tri thức pháp luật mới vào hệ thống."
        ),
        5: (
            "Hệ thống Vietnam Law Chatbot được thiết kế theo kiến trúc Microservices, tức là các nhóm chức năng chính "
            "được tách thành những dịch vụ độc lập và giao tiếp với nhau qua các kênh được kiểm soát. Cách tổ chức này "
            "phù hợp với bài toán chatbot pháp luật vì hệ thống vừa có các nghiệp vụ thông thường như xác thực, hội thoại, "
            "quản trị dữ liệu, vừa có các tác vụ AI có độ trễ và chi phí xử lý cao hơn."
        ),
        6: (
            "Trước hết, việc tách riêng các tác vụ AI giúp hệ thống ổn định hơn trong vận hành. Các bước như tạo embedding, "
            "xếp hạng lại kết quả truy hồi và suy luận bằng LLMs thường mất nhiều thời gian hơn một API nghiệp vụ thông "
            "thường. Nếu đặt toàn bộ vào cùng một khối ứng dụng, các chức năng đơn giản như đăng nhập, xem lịch sử hội "
            "thoại hoặc mở dashboard quản trị cũng có thể bị chậm khi pipeline AI đang xử lý tải lớn."
        ),
        7: (
            "Bên cạnh đó, kiến trúc tách dịch vụ cũng giúp bảo vệ phần lõi AI. RAG Service chứa quy trình truy hồi, suy "
            "luận và kiểm chứng câu trả lời nên được đặt ở lớp nội bộ; người dùng cuối chỉ giao tiếp với Main Service. "
            "Nhờ vậy, hệ thống giảm bề mặt truy cập trực tiếp vào kho tri thức và các thành phần xử lý nhạy cảm."
        ),
        8: (
            "Một lợi ích khác là khả năng phát triển độc lập. Main Service có thể ổn định quanh các nghiệp vụ người dùng "
            "và quản trị, trong khi RAG Service có thể được điều chỉnh thường xuyên hơn về chiến lược truy hồi, cách chọn "
            "nguồn, ngưỡng tin cậy hoặc phương pháp kiểm chứng mà không làm ảnh hưởng đến toàn bộ hệ thống."
        ),
        12: (
            "Nhìn tổng thể, hệ thống được tổ chức thành bốn lớp chính. Cách phân lớp này giúp tách rõ phần giao diện, "
            "phần điều phối nghiệp vụ, phần xử lý tri thức và phần lưu trữ dữ liệu."
        ),
        24: (
            "Từ kiến trúc ở Hình 2.1, có thể thấy người dùng không làm việc trực tiếp với RAG Service hay các cơ sở dữ "
            "liệu phía sau. Mọi yêu cầu đều đi qua lớp giao diện và Main Service trước khi được chuyển đến thành phần phù "
            "hợp. Cách đi này giúp hệ thống kiểm soát xác thực, phân quyền, ghi nhận lịch sử và điều phối xử lý tại một "
            "điểm thống nhất."
        ),
        30: (
            "Ở lớp điều phối, Main Service giữ vai trò cửa ngõ của hệ thống. Thành phần này tiếp nhận yêu cầu từ Mobile "
            "App và Admin Web, sau đó chuyển tiếp đến các nhóm xử lý phù hợp như hội thoại, tra cứu văn bản, tư vấn có "
            "hướng dẫn hoặc cập nhật dữ liệu pháp luật. Cách bố trí trong Hình 2.2 cho thấy Main Service không trực tiếp "
            "thực hiện suy luận AI, mà đóng vai trò kết nối giữa giao diện, cơ sở dữ liệu nghiệp vụ và RAG Service."
        ),
        32: (
            "Việc đặt Main Service ở giữa giúp frontend không cần biết chi tiết các dịch vụ phía sau. Mobile App chỉ cần "
            "gửi câu hỏi, nhận tiến trình xử lý và hiển thị câu trả lời; Admin Web chỉ cần gửi tài liệu, theo dõi trạng "
            "thái và quản lý kho văn bản. Các chi tiết như gọi RAG Service, lưu lịch sử, cập nhật tác vụ hay đồng bộ dữ "
            "liệu đều được Main Service điều phối."
        ),
        36: (
            "RAG Service là phần lõi của hệ thống hỏi đáp pháp luật. Thành phần này nhận yêu cầu đã được Main Service "
            "chuyển sang, phân tích câu hỏi, truy hồi căn cứ, sử dụng LLMs để tổng hợp câu trả lời và kiểm chứng lại nội "
            "dung trước khi trả về. Vì vậy, sơ đồ ở Hình 2.3 nên được hiểu như đường đi của một câu hỏi pháp luật bên trong "
            "hệ thống AI, không phải như sơ đồ thư mục hay danh sách lớp cài đặt."
        ),
        37: (
            "Điểm quan trọng của RAG Service là mọi câu trả lời đều phải gắn với nguồn dữ liệu. LLMs không được sử dụng "
            "để trả lời hoàn toàn dựa trên tri thức sẵn có, mà phải làm việc với các văn bản đã truy hồi được. Thiết kế "
            "này phù hợp với miền pháp luật, nơi câu trả lời cần có căn cứ, có thể kiểm tra lại và hạn chế tối đa suy đoán."
        ),
        43: (
            "Sau khi xác định kiến trúc tổng thể, cần làm rõ tính chất của tác nhân AI trong hệ thống. Với bài toán tư vấn "
            "pháp luật, tác nhân không chỉ tạo sinh câu trả lời mà còn phải biết khi nào cần tra cứu, khi nào cần hỏi thêm "
            "ngữ cảnh, khi nào cần đối chiếu nguồn cập nhật và khi nào phải từ chối một yêu cầu nằm ngoài phạm vi."
        ),
        59: (
            "Từ các yêu cầu trên, luồng RAG có kiểm chứng được thiết kế như một chuỗi xử lý nhiều bước. Thay vì để LLMs "
            "trả lời ngay sau khi nhận câu hỏi, hệ thống tách quá trình trả lời thành các pha nhỏ hơn: kiểm soát đầu vào, "
            "phân tích truy vấn, thu thập bằng chứng, suy luận và kiểm chứng."
        ),
        60: (
            "Cách tách này giúp từng bước có trách nhiệm rõ ràng. Nếu câu hỏi không phù hợp, hệ thống dừng sớm. Nếu câu "
            "hỏi hợp lệ nhưng còn mơ hồ, hệ thống chuẩn hoá lại hướng tìm kiếm. Nếu bằng chứng chưa đủ, hệ thống có thể "
            "tìm thêm nguồn trước khi đưa ra kết luận. Như vậy, chất lượng câu trả lời không chỉ phụ thuộc vào LLMs mà còn "
            "phụ thuộc vào cách tổ chức toàn bộ pipeline."
        ),
        66: (
            "Luồng xử lý ở Hình 2.4 có thể xem là khung kiểm soát chất lượng cho mỗi lượt hỏi đáp. Câu hỏi trước hết đi "
            "qua bước kiểm soát đầu vào để loại bỏ yêu cầu không thuộc phạm vi pháp luật. Sau đó, hệ thống phân tích lại "
            "câu hỏi để tạo hướng truy hồi rõ hơn. Khi đã có định hướng, tác nhân AI bắt đầu thu thập bằng chứng và chỉ "
            "chuyển sang trả lời khi có đủ căn cứ cần thiết."
        ),
        67: (
            "So với cách RAG tuyến tính, điểm khác biệt ở đây là hệ thống không bắt buộc chỉ tìm kiếm một lần. Trong quá "
            "trình suy luận, nếu kết quả thu được chưa đủ chắc chắn, tác nhân có thể tạo truy vấn bổ sung hoặc đối chiếu "
            "nguồn cập nhật trước khi kết luận. Đây là yêu cầu quan trọng với dữ liệu pháp luật vì một câu hỏi ngắn có thể "
            "liên quan đến nhiều văn bản, nhiều thời điểm hiệu lực và nhiều trường hợp áp dụng khác nhau."
        ),
        68: (
            "Có hai lớp kiểm soát được đặt ở hai đầu pipeline. Lớp đầu vào giúp tránh xử lý những yêu cầu ngoài phạm vi; "
            "lớp kiểm chứng đầu ra giúp phát hiện nội dung thiếu căn cứ hoặc suy diễn quá mức. Nhờ vậy, hệ thống vừa tiết "
            "kiệm tài nguyên xử lý, vừa giảm rủi ro trả lời sai trong các tình huống pháp lý nhạy cảm."
        ),
        70: (
            "Bước kiểm soát đầu vào có nhiệm vụ xác định câu hỏi có thuộc phạm vi tư vấn pháp luật hay không. Nếu câu hỏi "
            "lạc đề, hệ thống phản hồi từ chối một cách lịch sự và không chạy các bước truy hồi phía sau. Đây là cách xử "
            "lý cần thiết vì không phải mọi yêu cầu gửi đến chatbot đều phù hợp với mục tiêu của đồ án."
        ),
        74: (
            "Khi câu hỏi đã hợp lệ, hệ thống chuyển sang phân tích truy vấn. Ở bước này, câu hỏi tự nhiên của người dùng "
            "được chuyển thành những thông tin rõ hơn về chủ đề pháp lý, phạm vi tìm kiếm và các thuật ngữ trọng tâm. "
            "Kết quả phân tích giúp bước truy hồi phía sau không bị lệch bởi cách diễn đạt đời thường."
        ),
        75: (
            "Việc tách hướng tìm kiếm thành nguồn nội bộ và nguồn cập nhật bên ngoài cũng được thực hiện tại bước này. "
            "Với kho tri thức nội bộ, truy vấn cần ngắn gọn và gần với thuật ngữ pháp lý. Với nguồn bên ngoài, truy vấn "
            "có thể cần thêm dấu hiệu về văn bản mới, năm ban hành hoặc tình trạng hiệu lực để tăng khả năng đối chiếu đúng."
        ),
        80: (
            "Vòng Re-Act trong Hình 2.5 làm rõ cách tác nhân AI suy luận trong quá trình thu thập bằng chứng. Trước hết, "
            "tác nhân xác định mình cần tìm gì; tiếp theo, nó thực hiện hành động tra cứu phù hợp; cuối cùng, nó quan sát "
            "kết quả trả về để quyết định có đủ thông tin hay cần tiếp tục tìm kiếm."
        ),
        81: (
            "Nhờ cơ chế này, câu trả lời không được sinh ra vội vàng từ lần suy luận đầu tiên. Nếu căn cứ còn thiếu, hệ "
            "thống quay lại bước lập kế hoạch để bổ sung nguồn. Khi căn cứ đã đủ, pipeline mới chuyển sang tổng hợp và "
            "kiểm chứng. Cách làm này giúp câu trả lời bám vào dữ liệu truy hồi thay vì dựa quá nhiều vào khả năng suy đoán của LLMs."
        ),
        82: (
            "Trong miền pháp luật, một câu hỏi thường cần nhiều mảnh thông tin: điều luật gốc, điều kiện áp dụng, mức xử "
            "phạt, thời điểm hiệu lực hoặc văn bản thay thế. Vì vậy, việc tách rõ ba thao tác suy nghĩ, hành động và quan "
            "sát giúp hệ thống kiểm soát tốt hơn quá trình đi từ câu hỏi đến căn cứ trả lời."
        ),
        86: (
            "Ở bước cuối, câu trả lời dự thảo được đối chiếu lại với các nguồn đã truy hồi. Hệ thống cần kiểm tra xem các "
            "kết luận, số điều, mức phạt, thời hạn hoặc nguồn trích dẫn có thực sự xuất hiện trong bằng chứng hay không. "
            "Nếu phần nào chưa đủ căn cứ, nội dung đó phải được loại bỏ hoặc điều chỉnh trước khi trả về người dùng."
        ),
        107: (
            "Pipeline truy xuất ở Hình 2.6 được thiết kế theo hướng lọc rộng trước và chấm sâu sau. Ban đầu, tìm kiếm vector "
            "giúp thu hẹp kho văn bản lớn thành một tập ứng viên có khả năng liên quan. Sau đó, bước xếp hạng lại đánh giá "
            "kỹ hơn mối quan hệ giữa câu hỏi và từng đoạn văn bản để chọn ra các căn cứ phù hợp nhất."
        ),
        15: (
            "• Admin Web (Next.js 16): dashboard quản trị dành cho người quản trị hệ thống. Giao tiếp qua HTTPS/JWT và "
            "theo dõi tiến trình xử lý tài liệu qua WebSocket."
        ),
        105: (
            "Phần dưới đây tập trung vào cách hệ thống chọn căn cứ từ kho dữ liệu lớn trước khi chuyển sang bước suy luận. "
            "Đây là điểm quyết định trực tiếp đến chất lượng câu trả lời, vì LLMs chỉ có thể trả lời tốt khi ngữ cảnh đưa "
            "vào đủ đúng và đủ liên quan."
        ),
        108: (
            "Điểm quan trọng của thiết kế này là không để LLMs tự quyết định toàn bộ việc tìm nguồn. LLMs có khả năng diễn "
            "giải tốt, nhưng không phù hợp để tự tìm kiếm trong kho dữ liệu lớn. Ngược lại, cơ sở dữ liệu vector và bước "
            "xếp hạng lại làm tốt nhiệm vụ chọn căn cứ, còn tác nhân AI chịu trách nhiệm suy luận và trình bày câu trả lời "
            "dựa trên các căn cứ đó."
        ),
        128: (
            "Đối với dữ liệu pháp luật, việc xử lý xung đột theo thời gian là rất quan trọng. Một văn bản cũ có thể diễn "
            "đạt gần với câu hỏi hơn, nhưng văn bản mới hơn lại là căn cứ đang có hiệu lực. Vì vậy, ngoài điểm tương đồng "
            "ngữ nghĩa, hệ thống cần xét thêm thời điểm ban hành, ngày hiệu lực và quan hệ thay thế giữa các văn bản."
        ),
        132: (
            "Điều này cũng cho thấy không thể chỉ sắp xếp kết quả theo điểm liên quan. Trong nhiều trường hợp, văn bản cũ "
            "có điểm cao hơn vì dùng đúng cụm từ người dùng hỏi, còn văn bản mới lại dùng cách diễn đạt khác. Nếu không có "
            "bước xử lý xung đột thời gian, tác nhân AI có thể chọn nhầm căn cứ đã hết hiệu lực."
        ),
        139: (
            "Agentic RAG phù hợp với những câu hỏi đã có đủ ngữ cảnh, nhưng trong thực tế người dùng thường đặt câu hỏi rất "
            "ngắn. Một câu hỏi như \"vượt đèn đỏ phạt bao nhiêu\" chưa cho biết phương tiện, tình huống cụ thể hoặc hành vi "
            "có yếu tố tăng nặng hay không. Vì vậy, hệ thống cần thêm một luồng tư vấn có hướng dẫn để chủ động hỏi lại trước khi trả lời."
        ),
        140: (
            "Ở luồng này, thông tin được bổ sung theo từng bước. Câu hỏi ban đầu được phân tích để tạo các câu hỏi làm rõ; "
            "người dùng chọn phương án phù hợp; sau đó hệ thống mới chạy luồng truy hồi và kiểm chứng trên ngữ cảnh đã đầy "
            "đủ hơn. Cách tổ chức trong Hình 2.8 giúp chức năng tư vấn không chỉ là hỏi đáp tự do, mà trở thành một quy trình "
            "thu thập dữ kiện trước khi đưa ra kết luận pháp lý."
        ),
        147: (
            "Về mặt kỹ thuật, bước làm rõ ngữ cảnh giúp giảm rủi ro suy đoán. Khi các dữ kiện chính đã được người dùng xác "
            "nhận, truy vấn gửi vào pipeline cụ thể hơn, kết quả truy hồi tập trung hơn và bước kiểm chứng cũng có phạm vi "
            "đối chiếu rõ ràng hơn."
        ),
        156: (
            "Ở bước này, hệ thống chỉ tạo câu hỏi làm rõ, chưa đưa ra tư vấn pháp lý cuối cùng. Đây là ranh giới quan trọng "
            "vì câu hỏi làm rõ có thể được sinh nhanh, còn câu trả lời pháp lý cuối cùng bắt buộc phải đi qua truy hồi căn cứ "
            "và kiểm chứng trước khi hiển thị."
        ),
        160: (
            "Cụ thể, hệ thống kết hợp câu hỏi ban đầu với phần ngữ cảnh người dùng đã chọn để tạo thành một yêu cầu đầy đủ "
            "hơn. Trên yêu cầu này, pipeline truy hồi và suy luận được thực hiện như luồng chat thông thường, sau đó câu trả "
            "lời vẫn phải đi qua bước kiểm chứng trước khi trả về."
        ),
        168: (
            "Trong quá trình trả lời, giao diện chỉ hiển thị các trạng thái dễ hiểu như đang chuẩn bị tra cứu, đang tra cứu "
            "nguồn, đang tổng hợp và đang kiểm tra độ chính xác. Cách trình bày này che bớt chi tiết kỹ thuật nội bộ nhưng "
            "vẫn giúp người dùng thấy hệ thống đang xử lý có kiểm soát."
        ),
        173: (
            "Chất lượng tư vấn phụ thuộc trực tiếp vào chất lượng kho dữ liệu pháp luật. Vì vậy, ngoài pipeline hỏi đáp, "
            "hệ thống cần một quy trình riêng để quản trị viên cập nhật văn bản mới, chuẩn hoá nội dung thành các điều luật "
            "có cấu trúc và đồng bộ dữ liệu vào kho truy hồi."
        ),
        174: (
            "Ở phía quản trị, quy trình cập nhật tri thức được tổ chức theo các bước chính: tải văn bản, tiền kiểm, trích "
            "xuất và chuẩn hoá, kiểm tra hợp lệ, lưu dữ liệu gốc, tạo vector và cập nhật trạng thái xử lý. Hình 2.9 cho thấy "
            "luồng này không dừng ở việc lưu file PDF, mà phải đưa văn bản đến trạng thái sẵn sàng phục vụ tra cứu trong chatbot."
        ),
        176: (
            "Quy trình được thiết kế để hạn chế rủi ro đưa dữ liệu sai vào kho tri thức. Bước tiền kiểm giúp phát hiện tài "
            "liệu không phù hợp hoặc trùng lặp trước khi chạy các tác vụ nặng. Sau đó, nội dung PDF được chuyển thành các "
            "đơn vị tri thức như văn bản, điều khoản và metadata để hệ thống có thể tìm kiếm và trích dẫn."
        ),
        177: (
            "Sau khi trích xuất, dữ liệu được đồng bộ theo hai hướng. Phần tri thức gốc phục vụ quản trị, đọc và hiển thị "
            "văn bản; phần vector phục vụ tìm kiếm ngữ nghĩa trong quá trình hỏi đáp. Vì các kho dữ liệu này không nằm trong "
            "cùng một giao dịch duy nhất, hệ thống cần cơ chế hoàn tác để tránh trạng thái dữ liệu bị lệch."
        ),
        179: (
            "Bước tiền kiểm có ý nghĩa thực tế trong vận hành. Nếu quản trị viên tải nhầm một văn bản đã tồn tại, hệ thống "
            "có thể dừng sớm thay vì tiếp tục trích xuất, chuẩn hoá và tạo vector. Điều này giúp tiết kiệm tài nguyên xử lý "
            "và tránh phát sinh dữ liệu trùng trong kho tri thức."
        ),
        200: (
            "Sau khi trích xuất xong, hệ thống phải đồng bộ dữ liệu sang nhiều nơi: kho lưu tri thức gốc, kho vector phục vụ "
            "truy hồi và trạng thái tác vụ để quản trị viên theo dõi. Vấn đề đặt ra là các kho này không tự động nằm trong "
            "một giao dịch duy nhất, nên nếu một bước thất bại, hệ thống phải có cách đưa dữ liệu về trạng thái nhất quán."
        ),
        203: (
            "Nếu một bước đã ghi dữ liệu thành công nhưng bước sau thất bại, hệ thống có thể rơi vào trạng thái lệch: quản "
            "trị viên nhìn thấy văn bản đã tồn tại nhưng tác nhân AI không tìm được qua kho vector, hoặc ngược lại. Vì vậy, "
            "pipeline cần thu hồi phần dữ liệu đã ghi dở trước khi đánh dấu tác vụ thất bại."
        ),
        218: (
            "Ở trải nghiệm chat, yêu cầu quan trọng không chỉ là trả lời đúng mà còn phải cho người dùng biết hệ thống đang "
            "xử lý đến đâu. Luồng ở Hình 2.10 thể hiện quá trình từ khi người dùng gửi câu hỏi, hệ thống ghi nhận hội thoại, "
            "chạy pipeline trả lời theo dòng sự kiện, sau đó lưu và hiển thị câu trả lời cuối cùng kèm nguồn tham chiếu."
        ),
        221: (
            "Luồng chat tuân theo nguyên tắc lưu trước và hiển thị sau đối với dữ liệu quan trọng. Câu hỏi của người dùng "
            "được ghi nhận vào lịch sử hội thoại, sau đó hệ thống mới xử lý bằng pipeline RAG. Khi có câu trả lời cuối cùng, "
            "kết quả tiếp tục được lưu để người dùng có thể mở lại cuộc trò chuyện về sau."
        ),
        232: (
            "Sau khi thiết kế phần lõi backend và pipeline RAG, hệ thống cần một lớp ứng dụng đủ thuận tiện để người dùng "
            "cuối đặt câu hỏi pháp luật, theo dõi quá trình xử lý và kiểm tra nguồn trích dẫn. Đồng thời, quản trị viên cần "
            "một giao diện riêng để cập nhật văn bản pháp luật mới và kiểm soát kho dữ liệu. Vì vậy, lớp frontend được tách "
            "thành hai sản phẩm: Mobile App cho người dùng cuối và Admin Web cho quản trị viên."
        ),
        251: (
            "Một vấn đề phổ biến của chatbot dùng LLMs là thời gian chờ lâu. Với luồng RAG có kiểm chứng, hệ thống còn phải "
            "kiểm tra câu hỏi, phân tích truy vấn, truy hồi nguồn, đối chiếu thông tin và kiểm chứng câu trả lời. Nếu giao "
            "diện chỉ hiển thị trạng thái chờ tĩnh, người dùng khó biết hệ thống còn đang xử lý hay đã gặp lỗi."
        ),
        258: (
            "Bên cạnh ứng dụng người dùng cuối, hệ thống có Admin Web để quản trị viên nạp và quản lý văn bản pháp luật. "
            "Frontend này được xây dựng theo hướng dashboard vận hành, vì đối tượng sử dụng và mục tiêu thao tác khác hẳn "
            "với Mobile App."
        ),
        269: (
            "Khác với chat AI, pipeline tải lên PDF là một tác vụ nền kéo dài và có nhiều bước không sinh văn bản liên tục. "
            "Vì vậy, Admin Web sử dụng WebSocket để backend chủ động đẩy trạng thái xử lý về giao diện trong suốt quá trình cập nhật tài liệu."
        ),
        281: (
            "Cả Mobile App và Admin Web đều không truy cập trực tiếp vào RAG Service. Các yêu cầu được gửi đến Main Service, "
            "sau đó Main Service mới quyết định gọi cơ sở dữ liệu, RAG Service hoặc các dịch vụ phụ trợ khác. Cách thiết kế "
            "này giúp hệ thống giữ được một điểm điều phối thống nhất."
        ),
        287: (
            "Như vậy, lớp ứng dụng không chỉ là phần hiển thị giao diện. Đây còn là nơi thể hiện các quyết định kiến trúc "
            "quan trọng: tách người dùng cuối và quản trị viên, dùng dòng sự kiện cho chat, dùng WebSocket cho tác vụ nền, "
            "chia sẻ logic mobile đa nền tảng và xây dựng dashboard riêng cho vận hành kho dữ liệu pháp luật."
        ),
        290: (
            "Chương 2 đã trình bày phương pháp xây dựng hệ thống Vietnam Law Chatbot từ kiến trúc tổng thể đến các luồng "
            "xử lý trọng tâm. Hệ thống được tổ chức theo kiến trúc microservices, trong đó Main Service đóng vai trò điều "
            "phối nghiệp vụ, RAG Service đảm nhiệm truy hồi và suy luận, còn các kho dữ liệu lưu trữ tri thức pháp luật, "
            "vector tìm kiếm và lịch sử sử dụng."
        ),
        291: (
            "Đối với chức năng hỏi đáp, báo cáo đã trình bày cách kết hợp RAG, tác nhân AI, truy xuất hai giai đoạn và "
            "kiểm chứng đầu ra để tạo câu trả lời có căn cứ. Đối với chức năng tư vấn có hướng dẫn, hệ thống bổ sung bước "
            "làm rõ ngữ cảnh trước khi trả lời nhằm giảm rủi ro suy đoán trong các câu hỏi pháp luật còn thiếu dữ kiện."
        ),
        292: (
            "Đối với chức năng cập nhật văn bản pháp luật, báo cáo đã làm rõ quy trình từ tải file PDF, tiền kiểm, trích "
            "xuất, chuẩn hoá, kiểm tra hợp lệ, lưu trữ, chia nhỏ văn bản đến cập nhật kho vector. Đây là nền tảng để hệ "
            "thống duy trì kho tri thức có cấu trúc và có thể tiếp tục mở rộng."
        ),
        293: (
            "Các nội dung trên là cơ sở để chương 3 chuyển sang phân tích và thiết kế hệ thống ở mức chi tiết hơn, bao gồm "
            "yêu cầu chức năng, mô hình dữ liệu, API, biểu đồ xử lý và các thành phần cài đặt cụ thể."
        ),
        178: (
            "Cách thiết kế này phù hợp với chức năng quản trị vì cập nhật văn bản pháp luật là thao tác có tác động trực "
            "tiếp tới chất lượng tư vấn. Hệ thống không chỉ cần thêm dữ liệu mới, mà còn cần kiểm soát dữ liệu đó có đúng "
            "loại, không trùng lặp và đã được đồng bộ đầy đủ trước khi cho phép sử dụng trong trả lời."
        ),
    }

    for index, text in replacements.items():
        if index < len(p):
            p[index].text = text

    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
