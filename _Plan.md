# PLAN CHI TIẾT VIẾT BÁO CÁO ĐỒ ÁN TỐT NGHIỆP
## Đề tài: "Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số"

> Tài liệu này là **kim chỉ nam** trong quá trình viết báo cáo, bám theo cấu trúc báo cáo mẫu của HVKTMM (xem `_Sample_Report.md`) và áp dụng cho dự án Vietnam Law Service.
>
> **Tài liệu nguồn liên quan**:
> - [`_Project_Overview.md`](./_Project_Overview.md) — kiến trúc backend + Agentic RAG + DB.
> - [`_Frontend_Overview.md`](./_Frontend_Overview.md) — mobile KMP + web admin Next.js (verified từ code).
> - [`_Sample_Report.md`](./_Sample_Report.md) — phân tích báo cáo mẫu HVKTMM.

---

## 0. NGUYÊN TẮC CHUNG

### 0.1. Mục tiêu chiến lược

1. **Bám sát cấu trúc 4 chương + Lời nói đầu + Kết luận** của báo cáo mẫu HVKTMM.
2. **Giữ văn phong học thuật, dùng "em"** thay vì "tôi" / "chúng ta" (vì là báo cáo SV).
3. **Mỗi chương đóng/mở bằng đoạn dẫn dắt + tổng kết chuyển ý sang chương sau**.
4. **Tận dụng tối đa các "điểm sáng" kỹ thuật** của dự án (Verifier, Temporal Conflict, Guided Consultation, ...) để vượt qua mức trung bình của các đồ án chatbot khác.
5. **Số liệu thực tế > nói chung chung**: mỗi tuyên bố nên có con số (ngưỡng, score, latency, số bản ghi DB...).
6. **Ngôn ngữ thuần Việt + thuật ngữ EN** trong ngoặc khi giới thiệu lần đầu.
7. **Tránh lỗi của báo cáo mẫu**: tránh chèn quá nhiều screenshot prompt/code (dùng code block); tránh trộn rule-based + ML chỉ để cho dài.

### 0.2. Quy chuẩn format

- Font Times New Roman 13, line-height 1.5.
- Lề: top 2.0 cm / bottom 2.0 cm / left 3.0 cm / right 2.0 cm.
- Đánh số trang: phần đầu (i, ii, iii); từ Lời nói đầu (1, 2, 3...).
- Heading: H1 / H2 / H3 / H4. Không dùng quá H4.
- Caption hình: `Hình {chương}.{thứ tự}. Mô tả`.
- Caption bảng: `Bảng {chương}.{thứ tự}. Mô tả`.
- Code: monospace, có viền nhẹ, không quá 30 dòng / block.

### 0.3. Mục tiêu độ dài

| Phần | Số trang dự kiến |
|---|---|
| Phần đầu (lời cảm ơn, cam đoan, mục lục) | 6 – 10 |
| Lời nói đầu | 1 – 2 |
| Chương 1 — Tổng quan & cơ sở lý thuyết | 25 – 30 |
| Chương 2 — Phương pháp xây dựng hệ thống | 30 – 35 |
| Chương 3 — Phân tích, thiết kế hệ thống | 25 – 30 |
| Chương 4 — Triển khai & thực nghiệm | 20 – 25 |
| Kết luận | 1 – 2 |
| Tài liệu tham khảo | 2 – 3 |
| **Tổng** | **~110 – 130 trang** |

---

## 1. PHẦN ĐẦU (FRONT MATTER)

### 1.1. Bìa chính + Bìa phụ
- Logo HVKTMM (lấy từ template trường).
- Đề tài: **"NGHIÊN CỨU PHÁT TRIỂN TRỢ LÝ ẢO PHÁP LUẬT CHO CHUYỂN ĐỔI SỐ"**.
- SV: Vương Văn Duy — Lớp CT6D — Chuyên ngành Phát triển phần mềm di động — Mã ngành 7.48.02.01.
- GVHD: ThS. Trần Đức Thịnh.
- Hà Nội, 2026.

### 1.2. Lời cảm ơn
> ✅ ĐÃ CÓ trong `00_Mo_Dau.md` — chỉ cần kiểm tra rà soát chính tả, có thể thêm cảm ơn các bạn cùng khoa nếu muốn.

### 1.3. Lời cam đoan
> ✅ ĐÃ CÓ — kiểm tra lại lớp + chuyên ngành.

### 1.4. Mục lục
- Mục lục tự động sinh từ Heading 1/2/3.

### 1.5. Danh mục hình vẽ
- Sinh tự động từ caption hình.
- Dự kiến **~50–60 hình** trong toàn báo cáo.

### 1.6. Danh mục bảng biểu
- Dự kiến **~40–50 bảng**.

### 1.7. Danh mục từ viết tắt (KHUYẾN NGHỊ THÊM — báo cáo mẫu thiếu)
- LLM, RAG, AI, API, JWT, SSE, JSON, OCR, ORM, DB, KMP, CRUD, REST, ...
- Pháp luật: QPPL (Quy phạm pháp luật), VBQPPL, ...

---

## 2. LỜI NÓI ĐẦU (~1.5 trang)

> ✅ Đã có draft trong `00_Mo_Dau.md`. Cần bổ sung/chỉnh:

**Cấu trúc 5 đoạn**:
1. **Bối cảnh chuyển đổi số** + tầm quan trọng của pháp luật trong CĐS.
2. **Vấn đề thực tế**: hệ thống VBQPPL Việt Nam đồ sộ, phân mảnh; rào cản thuật ngữ; cập nhật liên tục.
3. **Sự xuất hiện của LLM và hạn chế hallucination** → giới thiệu RAG / Agentic RAG là giải pháp.
4. **Lý do chọn đề tài** + giới thiệu hệ thống Vietnam Law Chatbot với các tính năng nổi bật:
   - Agentic RAG (LangGraph 4 node) chống hallucination với Verifier Gemini Pro.
   - Two-stage retrieval với bi-encoder + cross-encoder rerank.
   - Web search dual-source (Tavily + Google Grounding) cập nhật luật mới realtime.
   - **Streaming Response (SSE)** với ThinkingPanel hiển thị tiến trình 5 bước pipeline.
   - **AI-Powered Search** trên thư viện pháp luật (semantic search).
   - **Suggested Questions** — gợi ý câu hỏi tiếp theo dựa trên context.
   - Guided Consultation 2 bước (Clarify + Answer SSE).
   - Temporal Conflict Resolution — đặc trưng pháp luật Việt Nam.
   - Multi-platform: Web admin (Next.js 16, WebSocket realtime task tracking) + Mobile KMP (Android + iOS).
5. **Giới thiệu cấu trúc 4 chương**.

---

## 3. CHƯƠNG 1 — TỔNG QUAN ĐỀ TÀI VÀ CƠ SỞ LÝ THUYẾT (~25-30 trang)

> ✅ Đã có draft trong `01_Chuong_1.md` — nhưng quá ngắn, cần MỞ RỘNG đáng kể.

**Mục tiêu chương**: trang bị nền tảng lý thuyết để người đọc hiểu các thuật ngữ và công nghệ trong các chương sau. Không nói về thiết kế cụ thể của hệ thống.

### 1.1. Tổng quan về chatbot và ứng dụng trong lĩnh vực pháp luật (3-4 trang)

- **1.1.1. Khái niệm chatbot và xu hướng phát triển**:
  - Định nghĩa, phân loại (rule-based / LLM-based / agent-based).
  - Lịch sử phát triển: Eliza → Chatbot rule-based → NLP-based → LLM era.
  - Hình minh hoạ: timeline chatbot.

- **1.1.2. Ứng dụng chatbot trong lĩnh vực pháp luật**:
  - Lợi ích: tăng tiếp cận pháp luật, tiết kiệm chi phí, 24/7.
  - **Yêu cầu đặc thù domain**: độ chính xác **tuyệt đối**, cập nhật liên tục, citation rõ ràng — đặt nền cho lý do dùng RAG + Verifier.
  - Khảo sát các sản phẩm hiện có ở Việt Nam (luatvietnam.vn, thuvienphapluat.vn — chỉ search keyword, không AI).

### 1.2. Vấn đề hallucination và các phương pháp khắc phục (3-4 trang)

- **1.2.1. Hiện tượng hallucination ở LLM**: định nghĩa + ví dụ minh hoạ thực tế (mô hình "bịa" điều luật không tồn tại).
- **1.2.2. Hậu quả trong domain pháp luật**: rủi ro pháp lý, mất uy tín, hậu quả thực tế.
- **1.2.3. Các phương pháp giảm hallucination**:
  - Fine-tuning (chi phí cao, không cập nhật được).
  - **RAG** (Retrieval-Augmented Generation) — focus.
  - Verifier / Self-consistency (LLM tự kiểm tra).
  - Tool calling (gọi nguồn tin cậy bên ngoài).

### 1.3. Mô hình ngôn ngữ lớn (LLM) (3-4 trang)

- **1.3.1. Khái niệm LLM, kiến trúc Transformer, cơ chế Attention**.
- **1.3.2. Các tham số sinh: Temperature, Top-K, Top-P** — giải thích vì sao đồ án này dùng nhiệt độ thấp (chính xác > sáng tạo).
- **1.3.3. So sánh các LLM phổ biến**: GPT-4, Claude, Gemini.
- **1.3.4. Lý do chọn Gemini 2.5 Flash + Pro**:
  - Flash: nhanh, rẻ, tốt cho phân tích/sinh thông thường.
  - Pro: reasoning sâu, dùng cho Verifier.
  - Multi-tier model strategy: tiết kiệm chi phí, tối ưu chất lượng.
  - Hỗ trợ tiếng Việt tốt, function calling native.

### 1.4. Kiến trúc Retrieval-Augmented Generation (RAG) (4-5 trang)

- **1.4.1. Khái niệm RAG**: định nghĩa, kiến trúc 2 bước (Retrieval + Generation).
- **1.4.2. Embedding và Vector Search**:
  - Khái niệm embedding vector.
  - Bi-encoder vs Cross-encoder (vẽ sơ đồ so sánh).
  - Cosine similarity, Euclidean distance.
- **1.4.3. Vector Database**:
  - Khái niệm, so sánh các giải pháp (FAISS, Pinecone, Weaviate, **ChromaDB**).
  - Lý do chọn ChromaDB: open source, dễ self-host, phù hợp scale vừa.
- **1.4.4. Hạn chế của Naive RAG**:
  - Không xử lý được câu hỏi đa bước.
  - Không kiểm chứng được kết quả.
  - Không cập nhật real-time → cần Agentic RAG.

### 1.5. AI Agent và Agentic RAG (3-4 trang)

- **1.5.1. Khái niệm AI Agent**:
  - Định nghĩa từ "Artificial Intelligence: A Modern Approach".
  - 4 thành phần: Perception / Knowledge / Reasoning / Action.
- **1.5.2. Tool calling**: function calling trong LLM, vai trò của tool, tương tác với môi trường.
- **1.5.3. Planning trong Agent**: lên kế hoạch + đánh giá + re-plan.
- **1.5.4. Reflection và ReAct framework**:
  - ReAct (Yao et al., 2022): xen kẽ Thought + Action + Observation.
  - Trích định dạng output mẫu của ReAct.
- **1.5.5. Agentic RAG**: kết hợp Agent + RAG, Agent quyết định khi nào search, đánh giá kết quả, có thể tự tạo truy vấn phụ.

### 1.6. Framework LangGraph (3-4 trang)

- **1.6.1. Giới thiệu LangChain ecosystem**.
- **1.6.2. LangGraph là gì**: stateful multi-actor workflows on top of LangChain.
- **1.6.3. Node và Edge**: Node = action, Edge = transition. Conditional edges.
- **1.6.4. Cycle (vòng lặp)**: ưu điểm so với DAG truyền thống — đặc biệt cho Re-Act.
- **1.6.5. State Management**: TypedDict state, message accumulation pattern.
- **1.6.6. Quy trình xây dựng Agent với LangGraph** (7 bước).

### 1.7. Các công nghệ hỗ trợ phát triển hệ thống (4-5 trang)

> Báo cáo mẫu để mục này dài (~10 trang). Đồ án nên ngắn gọn hơn vì sản phẩm rộng.

- **1.7.1. Python & FastAPI**: framework async, ưu điểm.
- **1.7.2. Hệ quản trị CSDL**:
  - **PostgreSQL** — lưu user, conversation, message (relational).
  - **MongoDB** — lưu articles (document, schema flexible).
  - **ChromaDB** — vector DB (đã nói ở 1.4).
  - Lý do dùng **3 loại DB** (polyglot persistence): mỗi DB tối ưu cho 1 dạng dữ liệu.
- **1.7.3. Next.js** — framework web (admin dashboard).
- **1.7.4. Kotlin Multiplatform & Compose Multiplatform** — chia sẻ code Android/iOS, lý do chọn KMP cho mobile.
- **1.7.5. Docker & Docker Compose** — containerization, dễ triển khai multi-service.
- **1.7.6. Tavily Search API & Google Grounding** — hai nguồn tìm kiếm web bổ trợ nhau.

### 1.8. Tổng kết chương 1

- 3-4 dòng tổng kết, dẫn dắt chương 2.

---

## 4. CHƯƠNG 2 — PHƯƠNG PHÁP XÂY DỰNG HỆ THỐNG TƯ VẤN PHÁP LUẬT VỚI AGENTIC RAG (~30-35 trang)

> ✅ Đã có draft trong `02_Chuong_2.md` — quá ngắn (~50 dòng). Cần MỞ RỘNG **rất nhiều**.

**Mục tiêu**: đi sâu vào kiến trúc giải pháp cụ thể của đồ án — tương đương "Chương 2 báo cáo mẫu" nhưng quy mô lớn hơn vì hệ thống phức tạp hơn.

### 2.1. Kiến trúc tổng quan hệ thống Vietnam Law Chatbot (3-4 trang)

- **2.1.1. Tổng quan kiến trúc microservices**:
  - Sơ đồ mermaid (Hình 2.1) — 4 sub-project + 3 DB + LLM + Web search.
  - Lý do chọn microservices: tách riêng AI workload (CPU/GPU intensive) khỏi API thông thường, dễ scale từng service.
- **2.1.2. Main Service (Port 8000)**:
  - Vai trò: API Gateway, auth, chat, document upload, browse luật.
  - Stack công nghệ.
  - Sơ đồ thành phần (Hình 2.2).
- **2.1.3. RAG Service (Port 8001)**:
  - Vai trò: AI core, internal-only.
  - Stack.
  - Sơ đồ thành phần (Hình 2.3).
- **2.1.4. Giao tiếp giữa các service**:
  - Main → RAG: HTTP nội bộ với `X-API-Key`.
  - Frontend → Main: JWT.
  - Bảng đặc tả các kênh giao tiếp.

### 2.2. Xác định tính chất AI Agent (2-3 trang)

> Học theo bố cục báo cáo mẫu (Bảng 2.1, 2.2)

- **2.2.1. Tính chất môi trường của Agent** (Bảng 2.1):
  - Đối tượng sử dụng: người dân, doanh nghiệp, cán bộ pháp chế.
  - Bối cảnh: tra cứu, tư vấn pháp luật.
  - Vai trò chatbot: trợ lý pháp luật.
  - Phạm vi phục vụ: chỉ pháp luật Việt Nam, từ chối domain khác.
  - Phạm vi đạo đức: không bịa, không tư vấn vi phạm pháp luật.
- **2.2.2. Nguồn dữ liệu của Agent** (Bảng 2.2):
  - VBQPPL từ luatvietnam.vn / thuvienphapluat.vn (PDF, HTML).
  - Web realtime (Tavily, Google Grounding).
  - Lịch sử hội thoại của user.
- **2.2.3. Tập hành động (Action set)**:
  - Tra cứu CSDL nội bộ (`retrieve_internal_law`).
  - Tìm kiếm web (`search_web_for_law`).
  - Sinh câu trả lời có citation.
  - Đặt câu hỏi làm rõ (Guided Consultation).
  - Từ chối (Guardrail).

### 2.3. Luồng Agentic RAG (LangGraph 4-node) (8-10 trang) **— TRỌNG TÂM**

- **2.3.1. Đồ thị tổng quan của Agent** (Hình 2.4 — sơ đồ 4 node):
  ```
  START → guardrail → query_analysis → agent ⇄ tools → verifier → END
  ```
- **2.3.2. Định nghĩa State** (Bảng 2.3 — `AgentState`):
  - `messages`, `query_analysis`, `retrieved_docs`, `iteration_count`, `is_valid_query`, `rejection_reason`...

- **2.3.3. Node Guardrail**:
  - Mục đích.
  - Prompt đầy đủ (block code).
  - Cơ chế quyết định: REJECT / ACCEPT.
  - Bảng State input/output.
  - Hình: ví dụ Guardrail từ chối câu hỏi off-topic.

- **2.3.4. Node Query Analysis**:
  - Vì sao cần phân tích lại query?
  - Prompt đầy đủ.
  - Cấu trúc JSON output: `topic`, `internal_search_query`, `web_search_query`, `requires_web_search`, `key_entities`.
  - Bảng State.
  - Ví dụ minh hoạ: "Vượt đèn đỏ phạt bao nhiêu?" → JSON.

- **2.3.5. Node Agent (Re-Act loop với Tools)**:
  - Mô hình LLM: Gemini 2.5 Flash.
  - Cơ chế Function Calling (giải thích).
  - Vòng lặp Re-Act: Thought → Action (tool call) → Observation → Repeat.
  - Max iterations = 6.
  - Prompt system của Agent (block code).
  - Bảng State.
  - Hình: minh hoạ 1 vòng Re-Act với câu hỏi cụ thể.

- **2.3.6. Node Verifier (chống hallucination)**:
  - Mô hình LLM: **Gemini 2.5 Pro** (tại sao Pro?).
  - Cơ chế kiểm chứng: đối chiếu chéo từng claim với context.
  - Hành vi khi phát hiện lỗi: sửa lại / giữ nguyên phần có căn cứ.
  - Prompt verifier (block code).
  - Bảng State.
  - Hình: ví dụ Verifier sửa hallucination.

### 2.4. Hai công cụ (Tools) của Agent (5-6 trang)

- **2.4.1. Tool retrieve_internal_law**:
  - Signature, mô tả.
  - Sơ đồ pipeline retrieve (Hình 2.x):
    1. Encode query (bi-encoder).
    2. ChromaDB cosine similarity (top-60).
    3. Cross-encoder rerank (`ms-marco-MiniLM-L-6-v2`).
    4. Year boost.
    5. Temporal Conflict Resolution.
  - Công thức blended score: `Score = 0.3 × BiScore + 0.7 × CrossScore`.
  - Năm boost: bảng cộng/trừ điểm theo độ mới.
  - Bảng tham số tool (Bảng 2.x).
  - Hình: code đoạn `retrieve_internal_law()`.

- **2.4.2. Tool search_web_for_law**:
  - Signature, mô tả.
  - Hai nguồn:
    - **Tavily**: ưu tiên domains `*.gov.vn`, `thuvienphapluat.vn`, `luatvietnam.vn`, `chinhphu.vn`.
    - **Google Grounding**: bổ sung realtime.
  - Cơ chế gọi song song (asyncio gather).
  - Bảng tham số.
  - Hình: code đoạn.

### 2.5. Tối ưu RAG Pipeline với Two-Stage Retrieval (3-4 trang)

- **2.5.1. Vấn đề khi chỉ dùng bi-encoder**: bi-encoder mã hoá độc lập query và document → bỏ sót ngữ nghĩa tinh tế.
- **2.5.2. Cross-encoder reranking**: chấm điểm dựa trên cặp (query, document) → chính xác hơn nhưng chậm.
- **2.5.3. Two-stage strategy**: bi-encoder lọc nhanh (top 60) → cross-encoder rerank kỹ (top 20).
- **2.5.4. Blended score formula**.
- **2.5.5. Year boost** — bảng + giải thích.
- **2.5.6. Temporal Conflict Resolution** — **ĐIỂM SÁNG ĐỘC ĐÁO**:
  - Vấn đề: cùng 1 nội dung pháp luật nhưng có 2 văn bản ở 2 năm khác nhau (vd: Nghị định 100/2019 vs 168/2024 về xử phạt giao thông).
  - Thuật toán: nhóm các kết quả theo "topic + entity"; nếu nhóm có >= 2 kết quả khác năm → đánh dấu ⛔ (cũ) / ✅ (mới).
  - Hình: ví dụ minh hoạ.

### 2.6. Luồng Tư vấn có hướng dẫn (Guided Consultation) (4-5 trang)

- **2.6.1. Vấn đề**: câu hỏi pháp luật thường thiếu ngữ cảnh (vd: "Vượt đèn đỏ phạt bao nhiêu?" cần biết loại xe).
- **2.6.2. Kiến trúc 2 bước**:
  - **Step 1 — Clarify**: phân tích query → sinh câu hỏi trắc nghiệm.
  - **Step 2 — Answer**: kết hợp `original_query + clarify_context + detected_topic` → chạy guided graph → SSE stream về client.
- **2.6.3. Đồ thị Guided Graph** (Hình 2.x): START → planning → agent → verifier → END.
- **2.6.4. Planning Node (deterministic, không dùng LLM)**:
  - Lý do chọn deterministic: tiết kiệm token, giảm latency, không cần LLM khi đã có structured input.
  - Thuật toán ghép queries.
- **2.6.5. SSE streaming**:
  - Vì sao chọn SSE thay vì WebSocket: nhẹ hơn, browser/mobile hỗ trợ tốt, đơn hướng (server → client) đủ cho use case.
  - Format event: `thinking`, `answer`, `done`.
  - Hình: minh hoạ thinking panel trên mobile.

### 2.7. Pipeline Document Ingestion (3-4 trang)

- **2.7.1. Tổng quan luồng**:
  - User/Admin upload PDF → MainService tạo `DocumentTask` → background processing.
  - Hình: Sequence diagram của ingestion pipeline.
- **2.7.2. Parse PDF với Gemini Vision**:
  - Vì sao dùng Gemini Vision thay vì OCR thuần?
  - Khả năng hiểu cấu trúc văn bản (Điều, Khoản, Mục).
  - Fallback PaddleOCR / Tesseract khi cần.
- **2.7.3. Concurrent processing**: Cloudinary upload và Gemini parse chạy song song để tối ưu thời gian.
- **2.7.4. Compensating Transaction**:
  - Vì sao cần: 2 DB (MongoDB + ChromaDB) không có distributed transaction tự nhiên.
  - Cơ chế: nếu MongoDB OK nhưng ChromaDB fail → rollback MongoDB; ngược lại tương tự.
- **2.7.5. Chunking strategy**: max 1000 từ / chunk, overlap 150 từ.

### 2.8. Lựa chọn LLM và chiến lược Multi-API-Key (2 trang)

- **2.8.1. Tiêu chí chọn**: chất lượng tiếng Việt, hỗ trợ function calling, chi phí, tốc độ.
- **2.8.2. Multi-tier model**:
  - Flash cho RAG/Agent (tốc độ + chi phí).
  - Pro cho Verifier (chính xác cao nhất).
- **2.8.3. Multi-API-Key rotation**:
  - Vấn đề: rate limit khi demo nhiều, đặc biệt lúc bảo vệ.
  - Cơ chế xoay vòng: detect 429/403 → chuyển sang key tiếp theo.
  - Hình: code đoạn `LLMService` rotation logic.

### 2.9. Tổng kết chương 2

---

## 5. CHƯƠNG 3 — PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG (~25-30 trang)

> Chưa có draft. Cần làm UML đầy đủ.

### 3.1. Đặc tả yêu cầu hệ thống (3 trang)

- **3.1.1. Yêu cầu về hình thức sản phẩm**:
  - Hệ thống gồm: Mobile app (Android/iOS), Web admin, Backend (Main + RAG), CSDL.
- **3.1.2. Yêu cầu chức năng cho người dùng cuối** (mobile):
  - Đăng ký, đăng nhập (email + password).
  - Quản lý hội thoại với Chatbot AI (CRUD, pin, archive).
  - Gửi tin nhắn, nhận trả lời từ Agentic RAG.
  - Tư vấn có hướng dẫn (Guided Consultation).
  - Tra cứu thư viện pháp luật (browse, filter, search).
  - Xem chi tiết điều luật.
  - Quản lý tài khoản (đổi mật khẩu, profile).
  - *(nếu có)* Bookmark điều luật, Share điều luật, Suggested questions.
- **3.1.3. Yêu cầu chức năng cho admin** (web):
  - Đăng nhập admin.
  - Upload PDF văn bản pháp luật → tự động parse + ingest.
  - Theo dõi tiến trình xử lý PDF (DocumentTask).
  - Quản lý danh sách văn bản (xem, xoá).
  - Dashboard thống kê (số user, hội thoại, văn bản).
  - Quản lý người dùng (xem, vô hiệu hoá).
- **3.1.4. Yêu cầu phi chức năng**:
  - Hiệu năng: latency Agentic RAG < 15 giây.
  - Bảo mật: JWT, password hash bcrypt, internal API key.
  - Mở rộng: microservices, dễ scale từng service.
  - Đa nền tảng: Android + iOS từ 1 codebase (KMP).
  - Khả dụng: 24/7, fault tolerance qua compensating transaction.
  - UX: giao diện thân thiện, hỗ trợ streaming response.

### 3.2. Phân tích hệ thống — Biểu đồ Use Case (8-10 trang)

- **3.2.1. Biểu đồ Use Case tổng quát** (Hình 3.1):
  - Tác nhân: User (sinh viên/người dân/CB) + Admin.
  - Use cases chính:
    - User: Đăng ký, Đăng nhập, Chat AI, Guided Consultation, Browse law, View article, Bookmark, Manage profile.
    - Admin: Login, Upload PDF, Track task, Manage documents, Manage users, View dashboard.
- **3.2.2. Đặc tả các use case** (mỗi use case 1 mục con + 1 hình + 1 bảng đặc tả).

> Mỗi bảng theo template:
> | Trường | Nội dung |
> | Tên usecase | ... |
> | Tác nhân | ... |
> | Mô tả | ... |
> | Tiền điều kiện | ... |
> | Luồng cơ bản | bước 1, 2, 3... |
> | Luồng thay thế | ... |
> | Hậu điều kiện | ... |

> Khoảng **10–12 use case** chính cần đặc tả. Bảng đặc tả tổng cộng ~10–12 bảng. Hình use case ~10–12 hình.

**Danh sách use case chi tiết** (đối chiếu với code thực tế đã verified):
1. UC-01: Đăng ký tài khoản (mobile only).
2. UC-02: Đăng nhập / Đăng xuất (mobile + admin web).
3. UC-03: Đổi mật khẩu (mobile).
4. UC-04: Quản lý cuộc hội thoại — CRUD + pin + archive (mobile).
5. UC-05: Gửi tin nhắn cho Chatbot AI — **Streaming SSE** với ThinkingPanel (mobile).
6. UC-06: Xem gợi ý câu hỏi tiếp theo (Suggested Questions) (mobile).
7. UC-07: Tư vấn có hướng dẫn (Guided Consultation) — Clarify + Answer SSE (mobile).
8. UC-08: Duyệt thư viện pháp luật (mobile + web).
9. UC-09: Tìm kiếm điều luật theo keyword/topic/year (mobile + web).
10. UC-10: **Tìm kiếm AI ngữ nghĩa** (AI-Powered Search) (mobile).
11. UC-11: Xem chi tiết văn bản và điều luật (mobile + web).
12. UC-12: Đăng nhập admin (web).
13. UC-13: Upload PDF văn bản pháp luật (web — drag&drop, AbortController, resume).
14. UC-14: Theo dõi tiến trình xử lý PDF qua **WebSocket realtime** (web).
15. UC-15: Quản lý danh sách văn bản — paginate, search, view detail (web).
16. UC-16: Xem dashboard thống kê (web — recharts BarChart, auto-refetch).

### 3.3. Phân tích hệ thống — Biểu đồ tuần tự (Sequence Diagrams) (6-8 trang)

> Mỗi sequence diagram 1 hình + 0.5 trang giải thích. Ưu tiên các luồng phức tạp/đặc trưng:

1. **SD-01**: Luồng đăng ký + đăng nhập + JWT token rotation tự động (Ktor `Auth { bearer { refreshTokens } }`).
2. **SD-02**: Luồng gửi tin nhắn **Agentic RAG đầy đủ với SSE streaming** — User → Mobile (`sendMessageStream`) → Main → RAG (graph 4 node) → Tools → SSE events (`ready` → `progress`* → `done`) → ThinkingPanel update → ChatBubble cập nhật. **Hình quan trọng nhất** — phải vẽ kỹ.
3. **SD-03**: Luồng Guided Consultation 2 bước:
   - 3a) Clarify: `POST /guided/clarify` → trả câu hỏi trắc nghiệm.
   - 3b) Answer SSE: `POST /guided/answer/stream` → stream tiến trình + answer.
4. **SD-04**: Luồng AI-Powered Search trên Library — `POST /laws/ai-search` → bi-encoder → ChromaDB → cross-encoder → ranked results với score → render lên UI.
5. **SD-05**: Luồng upload PDF + ingest (concurrent: Cloudinary // Gemini Vision parse, compensating transaction MongoDB ↔ ChromaDB).
6. **SD-06**: Luồng tracking DocumentTask qua **WebSocket** — Mobile/Web subscribe → backend broadcast `UPLOAD_PROGRESS` + `UPLOAD_STATUS` → UI cập nhật realtime → toast khi hoàn tất.
7. **SD-07**: Luồng Suggested Questions — sau khi nhận message AI → mobile request `GET /messages/{id}/suggested-questions` → hiển thị chips clickable.
8. **SD-08**: Luồng browse + view article (MongoDB aggregation `get_law_detail()`).

### 3.4. Thiết kế cơ sở dữ liệu (5-6 trang)

- **3.4.1. Lý do chọn polyglot persistence (3 DB)**:
  - PostgreSQL: relational data (user, conversation, message).
  - MongoDB: flexible schema cho article (mỗi luật có metadata khác nhau).
  - ChromaDB: vector embeddings → semantic search.

- **3.4.2. Thiết kế PostgreSQL** (5 bảng — 5 bảng schema):
  - Bảng `users`.
  - Bảng `conversations`.
  - Bảng `messages` (chú ý: `question_id` self-reference cho Q&A pair, `sources` JSONB, `metadata` JSONB).
  - Bảng `document_tasks` (status enum, progress, current_step).
  - Bảng `refresh_tokens`.
  - **Hình**: ER Diagram của PostgreSQL.

- **3.4.3. Thiết kế MongoDB**:
  - Collection `articles` (1 bảng schema).
  - Document JSON example.
  - Indexes (text-index, B-tree).
  - Aggregation pipelines chính: `get_laws()`, `get_law_detail()`, `get_all_topics()`, `search()`.

- **3.4.4. Thiết kế ChromaDB**:
  - Collection `vietnamese_law` (1 bảng schema).
  - Cấu trúc id, document, embedding, metadata.
  - Lưu ý: topics/keywords lưu dạng JSON-string.

- **3.4.5. Mối quan hệ giữa 3 DB**:
  - 1 luật (`law_id`) → N articles trong MongoDB → 1..N chunks trong ChromaDB.
  - `messages.sources` chứa chunk-id để truy hồi citation.
  - `document_tasks.law_id` liên kết task upload với MongoDB + ChromaDB.
  - **Hình**: sơ đồ liên kết 3 DB.

### 3.5. Thiết kế API (4-5 trang)

> Tương tự báo cáo mẫu: mỗi API 1 bảng đặc tả. Tập trung **các API quan trọng** (~15-20 API, không cần list hết).

**Template bảng API**:
| Trường | Nội dung |
| Endpoint | `POST /api/v1/auth/register` |
| Method | POST |
| Authentication | None / JWT |
| Request Body | `{ "email": "...", "password": "...", "full_name": "..." }` |
| Response | `{ "access_token": "...", "refresh_token": "...", "user": {...} }` |
| Status Codes | 201 Created, 400, 409, 500 |
| Mô tả | Đăng ký tài khoản mới |

**Danh sách API ưu tiên đặc tả**:
1. `POST /auth/register`
2. `POST /auth/login`
3. `POST /auth/refresh`
4. `POST /chat/conversations`
5. `GET /chat/conversations`
6. `POST /chat/conversations/{id}/messages` (Agentic RAG)
7. `POST /guided/clarify`
8. `POST /guided/answer` (SSE streaming) — **đặc biệt note SSE**.
9. `GET /laws`
10. `GET /laws/{id}/articles`
11. `POST /documents/upload`
12. `GET /documents/tasks/{task_id}`
13. (RAG service internal) `POST /rag/agent-search`
14. (RAG service internal) `POST /ingest/articles`

### 3.6. Thiết kế giao diện (UI/UX) — *Tuỳ chọn* (2-3 trang)

> Có thể đẩy phần này lên Chương 4. Gợi ý:
- Wireframe các màn hình chính (Mobile + Web).
- Design system: màu sắc, typography, component library (shadcn/ui + Compose Material).

### 3.7. Tổng kết chương 3

---

## 6. CHƯƠNG 4 — TRIỂN KHAI ỨNG DỤNG VÀ THỰC NGHIỆM (~20-25 trang)

> Chưa có draft. Quan trọng: có ảnh giao diện thật + đo lường thật.

### 4.1. Mô hình triển khai (2 trang)

- **4.1.1. Sơ đồ kiến trúc triển khai** (Hình 4.1): các container Docker, port mapping, volume, network.
- **4.1.2. Cấu hình môi trường**: file `.env`, các biến quan trọng.
- **4.1.3. Lệnh khởi động**: `docker-compose up -d`.
- **4.1.4. Yêu cầu phần cứng**: RAM tối thiểu (model embedding ~500MB, ChromaDB index, etc.), CPU.

### 4.2. Giao diện và chức năng — Mobile App (KMP) (4-5 trang)

> Mỗi chức năng 1 mục con + 1-2 ảnh giao diện thật.

- **4.2.1. Màn hình đăng ký / đăng nhập** (Hình 4.2, 4.3).
- **4.2.2. Màn hình chính (3 tab: Library / Chat / Settings)** (Hình 4.4).
- **4.2.3. Tra cứu thư viện pháp luật**:
  - Danh sách văn bản (Hình 4.5).
  - Lọc theo chủ đề / năm (Hình 4.6).
  - Chi tiết văn bản + danh sách điều luật (Hình 4.7).
  - Chi tiết điều luật (Hình 4.8).
- **4.2.4. Chat với AI**:
  - Danh sách hội thoại + actions (pin/archive/rename/delete) (Hình 4.9).
  - Cuộc hội thoại đang mở — bubble user/assistant (Hình 4.10).
  - **Câu trả lời AI markdown render với citation** (Hình 4.11).
  - **ThinkingPanel với 5 step pipeline đang chạy realtime** — Hình 4.12 (animated, BẮT BUỘC quay video gif demo).
  - **Suggested Questions chips** dưới mỗi câu trả lời (Hình 4.13).
  - **TypingBubble streaming text với cursor blink** (Hình 4.14).
- **4.2.5. AI-Powered Search trong Library** (Hình 4.15, 4.16):
  - Toggle "Tìm thường ↔ Tìm AI 🤖" trên thanh search.
  - Kết quả với relevance score bar.
  - **So sánh A/B**: cùng query "vượt đèn đỏ" — keyword search vs AI search.
- **4.2.6. Tư vấn có hướng dẫn (Guided Consultation)**:
  - Suggested topics (entry point) (Hình 4.17).
  - Bước Clarify — câu hỏi trắc nghiệm với option chips (Hình 4.18).
  - Bước Answer — ThinkingPanel + streaming response (Hình 4.19, 4.20).
- **4.2.7. Cài đặt, Profile, Archived, Đổi mật khẩu** (Hình 4.21, 4.22, 4.23).

### 4.3. Giao diện và chức năng — Admin Web (Next.js) (3-4 trang)

- **4.3.1. Đăng nhập admin** với verify role (Hình 4.24).
- **4.3.2. Dashboard tổng quan** (Hình 4.25):
  - 5 stat cards (Total laws, articles, success, failed, processing).
  - **BarChart top topics** (recharts) (Hình 4.26).
  - **Latest tasks với realtime status** từ WebSocket (Hình 4.27).
- **4.3.3. Quản lý văn bản pháp luật**:
  - Danh sách văn bản (paginate, search) (Hình 4.28).
  - Modal chi tiết văn bản với expand article (Hình 4.29).
- **4.3.4. Upload PDF**:
  - Drag-drop zone (Hình 4.30).
  - **Phase machine**: idle → uploading → processing → done (Hình 4.31).
  - **Resume sau reload** với progress restore từ task_id localStorage (Hình 4.32).
  - Kết quả: list articles parsed với expand/collapse (Hình 4.33).
- **4.3.5. Tracker page** — bảng tất cả document tasks với realtime updates (Hình 4.34).
- **4.3.6. WebSocket realtime task tracking architecture** — sơ đồ flow Hình 4.35 (CHỌN ĐƯA VÀO BÁO CÁO).

### 4.4. Đánh giá hệ thống (8-10 trang) **— TRỌNG TÂM ĐÁNH GIÁ**

> Học theo báo cáo mẫu: chia bộ dữ liệu, đo nhiều chỉ số.

- **4.4.1. Mô tả bộ dữ liệu thực nghiệm**:
  - Cấu trúc bộ dữ liệu (Bảng 4.1 — các trường: `question_id`, `category`, `question`, `expected_answer`, `expected_keywords`).
  - **2 nhóm câu hỏi**:
    - **Nhóm N1 — Câu hỏi có đáp án xác định**: ví dụ "Mức phạt vượt đèn đỏ với xe máy theo NĐ 168/2024" → đáp án có thể đối chiếu chính xác.
    - **Nhóm N2 — Câu hỏi mở**: ví dụ "Quy trình thành lập doanh nghiệp tư nhân" → có thể trả lời nhiều cách.
  - **Số câu hỏi**: 100 N1 + 100 N2 (theo mẫu).
  - Bảng ví dụ N1 (Bảng 4.2), N2 (Bảng 4.3).

- **4.4.2. Kịch bản thực nghiệm — Các chỉ số đánh giá**:

  - **Accuracy** (Bảng formula):
    - Tokenize câu trả lời + đáp án bằng `phobert-base` (VinAI).
    - So trùng token → binary score (chấp nhận / không).
    - Đo song song bằng tay (manual review).
    - Code đo (Hình 4.x — block code).
  - **Recall**:
    - `Recall = |common_tokens| / |expected_tokens|`.
    - Code đo (Hình 4.x).
  - **Context Relevance**:
    - Tỉ lệ token trùng giữa câu trả lời và context (sources retrieved).
    - Phép đo gián tiếp đo độ "neo" của câu trả lời vào ngữ cảnh.
  - **Latency**:
    - Đo `t_end - t_start` từ lúc gọi API đến khi nhận đủ response.
    - Phân chia theo: Agentic RAG vs Simple RAG vs Guided Consultation.
    - Code đo (Hình 4.x).

  - **🆕 Bonus chỉ số riêng cho domain pháp luật**:
    - **Citation Accuracy**: tỉ lệ điều luật được trích dẫn có thật trong CSDL (đo trực tiếp khả năng chống hallucination).
    - **Temporal Conflict Detection Rate**: với bộ N3 (câu hỏi có 2 luật cũ/mới song song), tỉ lệ hệ thống phát hiện và trả luật mới đúng.

- **4.4.3. Tiến hành thực nghiệm**:
  - Quy trình: import CSV → loop từng câu → gọi API → ghi kết quả → tổng hợp.
  - Code đo (Hình 4.x).
  - Hình: chương trình đang chạy (Hình 4.x).

- **4.4.4. Kết quả thực nghiệm**:
  - **Bảng 4.4**: Kết quả N1 (Accuracy auto, Accuracy manual, Recall min/max/avg, Context Relevance, Latency).
  - **Bảng 4.5**: Kết quả N2.
  - **Bảng 4.6 (mới)**: Citation Accuracy.
  - **Bảng 4.7 (mới)**: Temporal Conflict Detection Rate.

- **4.4.5. Phân tích kết quả**:
  - Accuracy N2 thấp hơn N1 (đặc tính câu trả lời mở).
  - Khác biệt giữa auto vs manual đánh giá ở N2.
  - Recall N1 cao do câu trả lời ngắn.
  - Context Relevance đạt > 80% → RAG hiệu quả.
  - **Citation Accuracy cao (>= 95%)** → Verifier hoạt động tốt — **điểm mạnh trình bày**.
  - Latency Agentic RAG: 5–15s (có web search), Simple RAG: 2–3s.
  - Hạn chế: Latency cao ở câu phức tạp đa bước; verify thêm ~3s cho mỗi câu.

- **4.4.6. So sánh A/B với Naive RAG (đề xuất bonus)**:
  - Bảng so sánh: Naive RAG (chỉ vector search + LLM) vs Agentic RAG (với Verifier + Web search).
  - Cho thấy Citation Accuracy của Naive thấp hơn → bằng chứng cho lựa chọn kiến trúc.

### 4.5. Tổng kết chương 4

---

## 7. KẾT LUẬN (~1.5 trang)

### 7.1. Kết quả đạt được (5–7 ý)

- Trình bày đầy đủ cơ sở lý thuyết: chatbot, LLM, RAG, AI Agent, LangGraph, two-stage retrieval.
- Đề xuất kiến trúc Agentic RAG với 4 node + Verifier (Gemini Pro) chống hallucination.
- Triển khai thuật toán Temporal Conflict Resolution đặc thù cho domain pháp luật Việt Nam.
- Xây dựng luồng Tư vấn có hướng dẫn (Guided Consultation) với SSE streaming.
- Phát triển hệ thống microservices (2 service backend) + 3 cơ sở dữ liệu (PostgreSQL + MongoDB + ChromaDB) — kiến trúc đa-DB phù hợp với đặc tính dữ liệu pháp luật.
- Xây dựng ứng dụng cross-platform với Kotlin Multiplatform + Compose Multiplatform (Android/iOS) — phù hợp chuyên ngành Phát triển phần mềm di động.
- Xây dựng pipeline ingestion document tự động: parse PDF (Gemini Vision + OCR) + chunking + embedding + compensating transaction.
- Đánh giá định lượng hệ thống trên 200+ câu hỏi pháp luật, đạt: Accuracy N1 = X%, Citation Accuracy = Y%, Latency trung bình = Z giây.

### 7.2. Hạn chế

- Latency Agentic RAG còn cao (5–15s) so với chatbot truyền thống do chi phí Verifier + Web search.
- CSDL nội bộ hiện tại còn giới hạn (chỉ X văn bản); cần mở rộng thêm.
- Tính năng Guided Consultation hiện chỉ xử lý được X domain (giao thông, lao động); cần huấn luyện thêm topic.
- Chưa hỗ trợ multi-modal (hình ảnh, voice).
- Chưa tích hợp lên các nền tảng nhắn tin phổ biến (Zalo, Messenger).

### 7.3. Hướng phát triển

- **Streaming response cho luồng Chat thông thường** (hiện chỉ có ở Guided): nâng cao UX.
- **Feedback loop / RLHF**: thu thập đánh giá từ user → cải thiện model retrieval.
- **AI-Powered Search trên giao diện thư viện** (semantic search trực quan).
- **Bookmark + Share điều luật** trên mobile.
- **Multi-modal**: hỗ trợ upload ảnh giấy tờ → AI phân tích pháp lý.
- **Tích hợp Zalo / Messenger / Web Widget**.
- **Mở rộng CSDL**: tự động crawl từ chinhphu.vn và luatvietnam.vn theo lịch.
- **Triển khai cloud**: AWS / GCP với Kubernetes để scale theo nhu cầu.

---

## 8. TÀI LIỆU THAM KHẢO (~15-20 nguồn — nhiều hơn báo cáo mẫu)

> Format: `[Tên tác giả/tổ chức], "[Tên tài liệu]", Online: [URL]`

**Bắt buộc nên có**:

### Papers / Khoa học
1. Lewis, P., et al. (2020). *"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"*, NeurIPS. arxiv.org/abs/2005.11401.
2. Yao, S., et al. (2022). *"ReAct: Synergizing Reasoning and Acting in Language Models"*, ICLR. arxiv.org/abs/2210.03629.
3. Gao, Y., et al. (2023). *"Retrieval-Augmented Generation for Large Language Models: A Survey"*. arxiv.org/abs/2312.10997.
4. Vaswani, A., et al. (2017). *"Attention is All You Need"*, NeurIPS. arxiv.org/abs/1706.03762.

### Documentation chính thống
5. LangGraph Documentation. *"Building Stateful Multi-Actor Apps"*. langchain-ai.github.io/langgraph/.
6. LangChain Documentation. *"Build a RAG App"*. python.langchain.com/docs/tutorials/rag/.
7. Google Gemini API Documentation. ai.google.dev.
8. ChromaDB Documentation. docs.trychroma.com.
9. FastAPI Documentation. fastapi.tiangolo.com.
10. Tavily Search API Docs. docs.tavily.com.
11. Kotlin Multiplatform Docs. kotlinlang.org/docs/multiplatform.html.
12. Compose Multiplatform Docs. jb.gg/cmp.
13. Sentence Transformers Docs. sbert.net.
14. PostgreSQL Documentation. postgresql.org/docs.
15. MongoDB Documentation. docs.mongodb.com.

### Mô hình tiếng Việt
16. BKAI Foundation Models. *"Vietnamese Bi-Encoder"*. huggingface.co/bkai-foundation-models/vietnamese-bi-encoder.
17. VinAI Research. *"PhoBERT-base"*. github.com/VinAIResearch/PhoBERT.

### Sách
18. Russell, S., & Norvig, P. (2010). *"Artificial Intelligence: A Modern Approach"* (3rd ed.). Pearson.
19. Huyen, C. (2025). *"AI Agents"* (blog post). huyenchip.com/2025/01/07/agents.html.

### Pháp luật Việt Nam
20. Cơ sở dữ liệu pháp luật quốc gia. vbpl.vn.
21. Thư viện pháp luật. thuvienphapluat.vn.

---

## 9. PLAN THỰC THI (TIMELINE)

> Đề xuất chia 4 tuần, mỗi tuần 1 chương + buffer.

| Tuần | Công việc | Output |
|---|---|---|
| **Tuần 1** | Hoàn thiện **Chương 1** (Cơ sở lý thuyết) — mở rộng draft hiện tại lên 25-30 trang | `01_Chuong_1.md` (final) |
| **Tuần 2** | Hoàn thiện **Chương 2** (Phương pháp xây dựng) — focus Agentic RAG, Tools, Guided | `02_Chuong_2.md` (final) |
| **Tuần 3** | Viết **Chương 3** (Phân tích & Thiết kế) — UML, DB, API | `03_Chuong_3.md` |
| **Tuần 3.5** | Vẽ tất cả **diagrams** (use case, sequence, ERD, class diagram) bằng draw.io / mermaid / PlantUML | `diagrams/` |
| **Tuần 4** | Viết **Chương 4** (Triển khai & Thực nghiệm) — chuẩn bị bộ test, chạy đo lường, capture screenshots | `04_Chuong_4.md` |
| **Tuần 4.5** | Viết **Kết luận**, hoàn thiện **Tài liệu tham khảo**, **Mục lục**, danh mục hình/bảng | `05_Ket_Luan.md` |
| **Tuần 5** | Convert MD → DOCX (Pandoc / Word), format chuẩn HVKTMM, soát lỗi chính tả | File DOCX cuối cùng |
| **Tuần 5.5** | Gửi GVHD review, sửa theo phản hồi | Bản chỉnh sửa |

### Công việc đo lường thực nghiệm (cần làm sớm — chiếm thời gian)
- **Tuần 1-2**: chuẩn bị bộ test 200+ câu hỏi (100 N1 + 100 N2) — có thể tự viết hoặc xin từ luatvietnam.vn FAQ.
- **Tuần 3**: viết script đo Accuracy/Recall/Latency.
- **Tuần 4**: chạy đo + tổng hợp kết quả.

### Công việc chuẩn bị diagrams
- **Use Case Diagrams** (12-14 cái): vẽ bằng draw.io theo style UML chuẩn.
- **Sequence Diagrams** (6 cái): nên dùng mermaid trong VS Code → export PNG.
- **ER Diagram** (PostgreSQL): dùng dbdiagram.io hoặc draw.io.
- **Architecture Diagram**: mermaid hoặc draw.io.
- **Screenshots ứng dụng**: chụp từ mobile (Android Studio emulator + iOS simulator) và web (Chrome DevTools).

---

## 10. CHECKLIST CUỐI CÙNG (TRƯỚC KHI NỘP)

- [ ] Đủ 4 chương + Lời nói đầu + Kết luận + TLTK.
- [ ] Bìa chính + Bìa phụ đúng template HVKTMM.
- [ ] Lời cảm ơn + Lời cam đoan đã ký tên.
- [ ] Mục lục đến cấp 3.
- [ ] Danh mục hình + bảng đầy đủ, đánh số đúng.
- [ ] Danh mục từ viết tắt.
- [ ] Tất cả hình caption đầy đủ + đánh số `Hình {chương}.{thứ tự}`.
- [ ] Tất cả bảng caption đầy đủ + đánh số `Bảng {chương}.{thứ tự}`.
- [ ] Code blocks định dạng monospace, không quá dài.
- [ ] Font Times New Roman 13, line-height 1.5, đúng lề.
- [ ] Đánh số trang Roman (front matter) → Arabic (từ Lời nói đầu).
- [ ] Tài liệu tham khảo >= 15 nguồn, format chuẩn.
- [ ] Soát chính tả tiếng Việt (đặc biệt dấu thanh).
- [ ] Bản DOCX chạy được trên Word + LibreOffice không lỗi font.
- [ ] **In thử 1 bản giấy** để kiểm tra layout cuối.
