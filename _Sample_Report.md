# PHÂN TÍCH BÁO CÁO MẪU

> File mẫu: *"Hoàng Văn Giang_Xây dựng chatbot phục vụ đào tạo tại Học viện Kỹ thuật mật mã.docx"*
> Mục đích: nắm cấu trúc, văn phong, mức độ chi tiết để áp dụng cho báo cáo của Vương Văn Duy.

---

## 1. THÔNG TIN CHUNG

- **Đề tài mẫu**: "Xây dựng chatbot phục vụ cho đào tạo tại Học viện Kỹ thuật Mật mã" (KBot).
- **Sinh viên**: Hoàng Văn Giang.
- **Hướng dẫn**: TS. Lê Đức Thuận và ThS. Trần Đức Thịnh.
- **Tổng số trang**: ~110 trang (đến phần Tài liệu tham khảo).
- **Tổng số đoạn**: 996 paragraphs, 42 bảng.
- **Định dạng**: Word .docx, sử dụng Heading 1/2/3/4 + style "Tên hình vẽ", "Tên bảng", "Code".

---

## 2. CẤU TRÚC TỔNG THỂ

```
┌─ Phần đầu (i → x):
│   • Lời cảm ơn
│   • Lời cam đoan
│   • Mục lục
│   • Danh mục hình vẽ
│   • Danh mục bảng biểu
│
├─ Lời nói đầu (1 trang)
│
├─ Chương 1: Tổng quan đề tài (3 → 29)               ← Cơ sở lý thuyết
├─ Chương 2: Phương pháp xây dựng hệ thống chatbot   ← Giải pháp kỹ thuật
│             với AI Agent và LLMs (30 → 55)
├─ Chương 3: Phân tích, thiết kế hệ thống (56 → 79)  ← UML, DB, API
├─ Chương 4: Xây dựng hệ thống và thực nghiệm (80 → 98) ← Demo + đánh giá
│
├─ Kết luận (99)
└─ Tài liệu tham khảo (100+)
```

> **Lưu ý quan trọng**: cấu trúc 4 chương + Lời nói đầu + Kết luận là chuẩn HVKTMM. Báo cáo của bạn nên bám sát công thức này.

---

## 3. CHƯƠNG 1 — TỔNG QUAN ĐỀ TÀI (29 trang)

Mục tiêu: trình bày bối cảnh, các khái niệm nền tảng, các công nghệ sẽ dùng. **Không** nói chi tiết về thiết kế hệ thống.

### Mục lục Chương 1

```
1.1. Tổng quan về chatbot
   1.1.1. Khái niệm chatbot
   1.1.2. Khảo sát tiềm năng ứng dụng tại HVKTMM
       1.1.2.1. Lợi ích đối với sinh viên
       1.1.2.2. Lợi ích đối với giảng viên

1.2. Một số phương pháp xây dựng chatbot hiện nay
   1.2.1. Chatbot dựa trên tập luật
   1.2.2. Chatbot dựa trên LLMs
   1.2.3. Chatbot dựa trên AI Agent

1.3. Tìm hiểu về mô hình ngôn ngữ lớn
   1.3.1. Khái niệm
   1.3.2. Khái niệm Chat LLMs

1.4. Tìm hiểu về AI Agent
   1.4.1. Khái niệm AI Agent
   1.4.2. Các thành phần (Perception / Knowledge / Reasoning / Action)
   1.4.3. Tool trong Agent
   1.4.4. Planning trong Agent
   1.4.5. Tự đánh giá và sửa lỗi (Reflection / ReAct)

1.5. Các công nghệ hỗ trợ phát triển hệ thống
   1.5.1. Nền tảng Ollama (~1 trang)
   1.5.2. Ngôn ngữ lập trình Python (~1.5 trang)
   1.5.3. LangGraph Framework (~3 trang) — KHÁ KỸ
       1.5.3.1. Khái niệm
       1.5.3.2. Node và cạnh
       1.5.3.3. Quản lý trạng thái (State)
       1.5.3.4. Các bước xây dựng AI Agent với LangGraph
   1.5.4. FastAPI Framework (~1 trang)
   1.5.5. ReactJS framework (~2 trang)
   1.5.6. Hệ quản trị CSDL PostgreSQL (~1.5 trang)

1.6. Tổng kết chương 1
```

### Đặc điểm văn phong
- Khái niệm trình bày tổng quát, có ưu/nhược điểm rõ ràng (dùng list bullet).
- Mỗi công nghệ ~1–3 trang, có ảnh minh hoạ.
- Trích định nghĩa kinh điển: *"Sách Artificial Intelligence: A Modern Approach (1995) định nghĩa Agent là..."*
- Trộn lẫn Tiếng Việt với thuật ngữ tiếng Anh (Agent, Tool, Planning, ReAct, ...).
- Hình ảnh thường dùng: minh hoạ chatbot rule-based, sơ đồ RAG, mô hình SWE Agent, ReAct flow, sơ đồ Node/Edge LangGraph, ví dụ State.

### Số liệu / cấu trúc cần lưu ý
- Hình ở Chương 1: 9 hình (Hình 1.1 → 1.9).
- Style hình: `[Tên hình vẽ] Hình 1.x. ...`.

---

## 4. CHƯƠNG 2 — PHƯƠNG PHÁP XÂY DỰNG HỆ THỐNG (26 trang)

Mục tiêu: đi sâu vào "thiết kế giải pháp" — kiến trúc Agent cụ thể của đồ án, các node, các tool, prompt sử dụng.

### Mục lục Chương 2

```
2.1. Xây dựng mô hình tổng quát của AI Agent
   2.1.1. Xác định các tính chất của Agent
       2.1.1.1. Tính chất môi trường (Bảng 2.1)
       2.1.1.2. Nguồn dữ liệu (Bảng 2.2)
       2.1.1.3. Tập hành động
   2.1.2. Mô hình tổng quan của AI Agent
       2.1.2.1. Mô hình tổng quan
       2.1.2.2. Luồng xử lý của truy vấn
       2.1.2.3. Đồ thị tổng quan (LangGraph)

2.2. Phương pháp xây dựng chi tiết từng thành phần
   2.2.1. Node Summary_Chat_History (prompt, state)
   2.2.2. Node Initial_Thinking (prompt, state)
   2.2.3. Node Plan_Validator (prompt, state)
   2.2.4. Node Re_Planning (prompt, state)
   2.2.5. Node Do_task (prompt, state)
   2.2.6. Node RAG_Agentic
       2.2.6.1. Khái niệm RAG, Retrieval, Embedding
       2.2.6.2. Agentic RAG (đồ thị, truy vấn kép, prompt)
   2.2.7. Xây dựng các tool
       2.2.7.1. Tool tra điểm sinh viên
       2.2.7.2. Tool tra thông tin sinh viên
       2.2.7.3. Tool tính điểm trung bình

2.3. Lựa chọn mô hình ngôn ngữ lớn (tiêu chí + lý do chọn Gemma3:4b)

2.4. Tổng kết chương 2
```

### Đặc điểm
- **Chi tiết cao**: mỗi node có 1 mục con riêng, kèm prompt full text + bảng State.
- Ảnh: 17 hình (Hình 2.1 → 2.17), gồm sơ đồ Agent, prompt screenshot, code đoạn.
- Bảng: 8 bảng (Bảng 2.1 → 2.10), chủ yếu mô tả State của các node và param của tool.
- Văn phong: bám sát source code thật — *"Node X có prompt như sau:"* + chèn block code prompt → *"State của node X như bảng sau:"* → tham chiếu Bảng x.y.

### Mẫu để bắt chước
- Trình tự cho **mỗi node**: (1) mục đích → (2) prompt → (3) state → (4) hành vi đặc biệt.
- Trình tự cho **mỗi tool**: (1) đầu vào / đầu ra → (2) hàm hiện thực (chèn code) → (3) bảng tham số.

---

## 5. CHƯƠNG 3 — PHÂN TÍCH, THIẾT KẾ HỆ THỐNG (24 trang)

Mục tiêu: chuẩn UML, đặc tả yêu cầu chức năng/phi chức năng, thiết kế CSDL, thiết kế API.

### Mục lục Chương 3

```
3.1. Yêu cầu của hệ thống
   3.1.1. Hình thức sản phẩm
   3.1.2. Yêu cầu chức năng (user + admin)
   3.1.3. Yêu cầu phi chức năng

3.2. Phân tích hệ thống
   3.2.1. Biểu đồ usecase tổng quát (Hình 3.1)
   3.2.2. Đặc tả các usecase (10 usecase với 10 bảng đặc tả: Bảng 3.1 → 3.10)
   3.2.3. Biểu đồ tuần tự (Hình 3.12 → 3.19, 8 sequence diagram)

3.3. Thiết kế hệ thống
   3.3.1. Thiết kế CSDL (6 bảng: Score, Structure, Student, Regulation, Message, Conversation)
   3.3.2. Thiết kế API (9 bảng API: tra điểm, xếp hạng, học bổng, quy định, hội thoại, ...)

3.4. Tổng kết
```

### Đặc điểm
- 19 hình (Hình 3.1 → 3.19): chủ yếu là usecase + sequence.
- 25 bảng (Bảng 3.1 → 3.25): mỗi usecase có 1 bảng đặc tả; mỗi bảng DB có 1 bảng schema; mỗi API có 1 bảng đặc tả request/response.

### Format đặc tả Usecase (mẫu)

| Trường | Nội dung |
|---|---|
| **Tên usecase** | Tra cứu bảng điểm |
| **Tác nhân** | Sinh viên / Người dùng |
| **Mô tả** | Người dùng nhập mã sinh viên → nhận về bảng điểm |
| **Tiền điều kiện** | Mã SV hợp lệ, có dữ liệu trong DB |
| **Luồng cơ bản** | 1) User mở trang... 2) Hệ thống... |
| **Luồng thay thế** | Mã SV không tồn tại → báo lỗi |
| **Hậu điều kiện** | Bảng điểm hiển thị |

### Format thiết kế CSDL (mẫu)

| Cột | Kiểu | Khoá | Ghi chú |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK → users.id | CASCADE |
| ... | ... | ... | ... |

### Format thiết kế API (mẫu)

| Trường | Nội dung |
|---|---|
| **Endpoint** | `POST /api/scores` |
| **Method** | POST |
| **Request body** | `{ "student_code": "..." }` |
| **Response** | `{ "data": [...], "success": true }` |
| **Status code** | 200, 400, 404, 500 |
| **Mô tả** | Tra cứu điểm sinh viên |

---

## 6. CHƯƠNG 4 — XÂY DỰNG HỆ THỐNG VÀ THỰC NGHIỆM (19 trang)

Mục tiêu: khoe sản phẩm cuối + đánh giá định lượng.

### Mục lục Chương 4

```
4.1. Mô hình tổng quan của hệ thống (kiến trúc triển khai, Hình 4.1)

4.2. Các chức năng của hệ thống (mỗi chức năng 1 mục, 1-2 ảnh giao diện)
   4.2.1. Trang chủ (Hình 4.2)
   4.2.2. Tra cứu điểm cá nhân (Hình 4.3, 4.4)
   4.2.3. Tra cứu sinh viên đủ điều kiện học bổng (Hình 4.5, 4.6)
   4.2.4. Chat với chatbot AI (Hình 4.7)
   4.2.5. Một số chức năng của chatbot AI (Hình 4.8 → 4.11)
   4.2.6. Đăng nhập admin (Hình 4.12)
   4.2.7. Cập nhật điểm số (Hình 4.13, 4.14)
   4.2.8. Cập nhật quy định (Hình 4.15, 4.16)

4.3. Đánh giá
   4.3.1. Mô tả bộ dữ liệu thực nghiệm (2 nhóm N1 / N2, mỗi nhóm 100 câu)
   4.3.2. Kịch bản thực nghiệm
       - Accuracy (Hình 4.17 — code)
       - Recall (Hình 4.18 — code)
       - Context Relevance
       - Latency (Hình 4.19 — code)
   4.3.3. Tiến hành thực nghiệm (Hình 4.20 — code)
   4.3.4. Kết quả thực nghiệm (Bảng 4.4, 4.5)

4.4. Tổng kết
```

### Đặc điểm văn phong
- Cách trình bày ảnh giao diện: *"Khi người dùng truy cập... giao diện X được hiển thị (Hình 4.x)"*.
- Phần đánh giá: bám sát công thức + có chèn code thực nghiệm.
- Bộ dữ liệu chia 2 nhóm:
  - **N1**: câu hỏi có đáp án duy nhất (vd: điểm số) → đo Accuracy, Recall.
  - **N2**: câu hỏi có thể trả lời theo nhiều cách (vd: quy định) → thêm Context Relevance.
- Token-based evaluation: dùng `phobert-base` tokenizer của VinAI để so sánh token.

### 4 chỉ số đánh giá AI

| Chỉ số | Định nghĩa | Công thức |
|---|---|---|
| **Accuracy** | Tỷ lệ câu trả lời đúng / tổng câu hỏi | Đo bằng so trùng tokenize hoặc đánh giá thủ công |
| **Recall** | Tỷ lệ token trùng với đáp án mong muốn / tổng token mong muốn | `\| common_tokens \| / \| expected_tokens \|` |
| **Context Relevance** | Mức độ liên kết câu trả lời với context | `\| common(answer, context) \| / \| expected_tokens \|` |
| **Latency** | Thời gian hệ thống xử lý 1 query (giây) | `t_end - t_start` |

### Kết luận thực nghiệm (mẫu)
- N2 có accuracy thấp hơn N1 (do nhiều cách viết).
- Đo thủ công vs đo tự động khác biệt lớn ở N2 (do văn dài).
- Recall của N1 cao do câu trả lời ngắn gọn.
- Context Relevance N2 đạt > 86% → RAG có hiệu quả.
- Latency cao ở các query phức tạp đa bước.

---

## 7. KẾT LUẬN

```
Kết quả đạt được (5 ý)
   • Trình bày khái niệm chatbot, AI chatbot
   • Trình bày AI Agent, RAG, LangGraph
   • Đề xuất mô hình AI Agent + Agentic RAG
   • Áp dụng ReactJs xây ứng dụng web
   • Phân tích thiết kế và xây dựng thành công

Hạn chế (2 ý)
   • Chưa tích hợp lên nhiều nền tảng
   • Một số chức năng còn lỗi nhỏ

Hướng phát triển (2 ý)
   • Hoàn thiện và mở rộng chức năng
   • Cải thiện chatbot, mở rộng tính năng
```

---

## 8. TÀI LIỆU THAM KHẢO (mẫu)

- 9 nguồn, đa số là online docs (LangChain, LangGraph, Hugging Face, ReactJS docs, arxiv papers).
- Format: `[Tên tác giả/Tổ chức], "[Tên tài liệu]", Online: [URL]`.

---

## 9. NHỮNG ĐIỂM CẦN HỌC TỪ BÁO CÁO MẪU

### Văn phong / cấu trúc
1. **Mở mỗi chương = 2-3 dòng giới thiệu**, đóng mỗi chương = 1 đoạn "Tổng kết chương" (chuyển ý sang chương sau).
2. **Lời nói đầu** ngắn (~1 trang), gồm: bối cảnh chuyển đổi số → vấn đề cụ thể → giải pháp đề xuất → cấu trúc 4 chương.
3. **Tránh "tôi"**, dùng "em" (vì là sinh viên báo cáo).
4. **Trộn thuật ngữ EN-VI**: viết tiếng Việt + chèn thuật ngữ tiếng Anh trong ngoặc khi giới thiệu lần đầu.

### Bố cục đặc trưng
5. **Chương 1 = Lý thuyết** — không nói về sản phẩm cụ thể.
6. **Chương 2 = Phương pháp** — đi sâu vào kiến trúc giải pháp + prompts + state + tools.
7. **Chương 3 = UML + Thiết kế** — usecase, sequence diagram, schema CSDL, đặc tả API.
8. **Chương 4 = Sản phẩm + Thực nghiệm** — ảnh giao diện + đánh giá định lượng.
9. **Kết luận** — 3 phần: kết quả đạt được / hạn chế / hướng phát triển.

### Quy ước hình ảnh / bảng biểu
10. **Hình**: đánh số `Hình {chương}.{thứ tự}` + caption tiếng Việt rõ ràng.
11. **Bảng**: đánh số `Bảng {chương}.{thứ tự}` + caption.
12. Khi cần show prompt → dùng style `Code` block, KHÔNG screenshot.
13. Mỗi chức năng / mỗi node / mỗi tool → 1 mục con + 1-2 hình minh hoạ + 1 bảng tham số/state.

### Phần đánh giá
14. **Bộ dữ liệu thực nghiệm**: chia thành 2 nhóm dựa trên đặc tính câu trả lời (đáp án duy nhất vs. mở).
15. **Chỉ số đánh giá AI**: Accuracy, Recall, Context Relevance, Latency — đủ chuẩn học thuật.
16. **Bảng kết quả**: trình bày min/max/avg cho mỗi chỉ số.
17. **Phân tích kết quả**: viết lý do vì sao N2 thấp hơn N1, vì sao Latency cao ở câu phức tạp...

### Cần thay đổi cho phù hợp đồ án Vietnam Law Service

| Phần báo cáo mẫu (KBot) | Áp dụng cho Vietnam Law Service |
|---|---|
| Chatbot phục vụ đào tạo | Trợ lý ảo pháp luật cho chuyển đổi số |
| Domain: điểm sinh viên, quy chế HV | Domain: pháp luật Việt Nam, văn bản QPPL |
| Ollama + Gemma3:4b | Gemini 2.5 Flash + Pro (qua Google API) |
| FAISS + BM25 + RAG đơn giản | ChromaDB + bi-encoder + cross-encoder + Temporal Conflict Resolution |
| RAG_Agentic node trong Agent chính | **Tách rõ**: Agentic RAG (4-node graph) + Simple RAG pipeline 6 bước + Guided Consultation graph |
| ReactJS web only | Next.js Admin (web) + KMP Mobile (Android/iOS) |
| Tools: get_scores, get_info, calc_avg | Tools: retrieve_internal_law, search_web_for_law (Tavily + Google Grounding) |
| 3 Tool đơn giản | 2 Tool phức tạp + Guardrail + Verifier (Gemini Pro) |
| Không có Verifier riêng | Có **Verifier (Gemini Pro)** chống hallucination |
| Không có Web Search | Có **dual-source web search** (Tavily + Google) |
| Không có Temporal Conflict | Có **Temporal Conflict Resolution** — đặc trưng pháp luật |
| Không có Guided | Có **Guided Consultation** với SSE streaming |
| Không có Document Upload Pipeline | Có pipeline upload PDF + OCR + Compensating Transaction |
| 1 DB (PostgreSQL) | **3 DB** (PostgreSQL + MongoDB + ChromaDB) — sức nặng kiến trúc |
| Bộ test 100 + 100 câu | Có thể làm tương tự, thêm chỉ số chống hallucination |

---

## 10. CHECKLIST FORMAT

Trước khi nộp, đảm bảo bám đúng quy chuẩn:
- [ ] Bìa chính + bìa phụ (logo HVKTMM + thông tin SV).
- [ ] Lời cảm ơn (1 trang).
- [ ] Lời cam đoan (0.5 trang).
- [ ] Mục lục đến cấp 3 (Heading 1/2/3).
- [ ] Danh mục hình vẽ.
- [ ] Danh mục bảng biểu.
- [ ] Danh mục từ viết tắt (báo cáo mẫu chưa có, nên bổ sung — luật dùng nhiều viết tắt).
- [ ] Lời nói đầu.
- [ ] 4 chương chính.
- [ ] Kết luận.
- [ ] Tài liệu tham khảo (>= 10 nguồn, ưu tiên papers + docs chính thống).
- [ ] Style: font Times New Roman 13, line-height 1.5, căn lề: trên 2.0 / dưới 2.0 / trái 3.0 / phải 2.0 cm.
- [ ] Đánh số trang: phần đầu Roman (i, ii, iii), từ Lời nói đầu trở đi Arabic (1, 2, 3...).
- [ ] Hình & bảng đánh số theo chương + caption.
- [ ] Code block dùng style monospace.
