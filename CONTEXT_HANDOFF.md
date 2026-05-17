# CONTEXT HANDOFF — BÁO CÁO ĐỒ ÁN TỐT NGHIỆP
## "Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số"

> **Mục đích file này**: Cung cấp đủ context để AI/người khác tiếp tục viết báo cáo từ đúng chỗ hiện tại, không cần đọc lại toàn bộ source code.
> **Ngày cập nhật**: 2026-05-13

---

## 1. THÔNG TIN ĐỀ TÀI

| Trường | Nội dung |
|---|---|
| Sinh viên | Vương Văn Duy |
| Lớp | CT6D |
| Chuyên ngành | Phát triển phần mềm di động — Mã ngành 7.48.02.01 |
| GVHD | ThS. Trần Đức Thịnh |
| Đơn vị | Học viện Kỹ thuật Mật mã — Khoa Công nghệ Thông tin |
| Năm | 2026 |
| Đề tài | "Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số" |
| Sản phẩm | Vietnam Law Chatbot (Agentic RAG) |

---

## 2. TRẠNG THÁI HIỆN TẠI

### 2.1. Tiến độ các phần

| Phần | Trạng thái | File |
|---|---|---|
| Phần đầu (bìa, cảm ơn, cam đoan, lời nói đầu) | ✅ Có draft trong `00_Mo_Dau.md` — cần chỉnh nhẹ | `00_Mo_Dau.md` |
| **Chương 1 — Tổng quan & Cơ sở lý thuyết** | ✅ **HOÀN THIỆN** — đã update vào file DOCX chính | `01_Chuong_1.md` + trong `Vương Văn Duy_Báo cáo.docx` |
| **Chương 2 — Phương pháp xây dựng hệ thống** | 🔄 **CẦN VIẾT TIẾP** — đã có draft sơ bộ | `02_Chuong_2.md` (có nội dung, cần bổ sung) |
| Chương 3 — Phân tích & Thiết kế | 🔄 Có draft | `03_Chuong_3.md` |
| Chương 4 — Triển khai & Thực nghiệm | ❌ Chưa viết | — |
| Kết luận | ❌ Chưa viết | — |
| Tài liệu tham khảo | 🔄 Có danh sách trong `_Plan.md` | — |

### 2.2. File DOCX chính

- **`Vương Văn Duy_Báo cáo.docx`** — file báo cáo tổng hợp chính
- **`01_Chuong_1.docx`** — file chương 1 riêng (đã rebuild từ MD mới nhất)
- **Script**: `make_chapter1_docx.py` — convert MD → DOCX chuẩn format HVKTMM

### 2.3. NHIỆM VỤ NGAY BÂY: Viết Chương 2

**Chương 2 là ưu tiên số 1.** Đã có draft trong `02_Chuong_2.md` nhưng cần mở rộng và hoàn thiện theo cấu trúc bên dưới.

---

## 3. QUY CHUẨN VIẾT BÁO CÁO

### 3.1. Văn phong & nguyên tắc

- Dùng **"em"** thay cho "tôi" (báo cáo sinh viên gửi GVHD).
- Văn phong học thuật, câu đầy đủ chủ vị, không viết tắt tùy tiện.
- Thuật ngữ kỹ thuật EN: giới thiệu lần đầu thì viết *Tên tiếng Việt (English term — viết tắt)*, ví dụ: *Mô hình ngôn ngữ lớn (Large Language Models — LLM)*.
- Sau lần đầu giới thiệu → dùng viết tắt.
- Mỗi chương mở bằng đoạn dẫn dắt, kết bằng đoạn tổng kết + chuyển ý sang chương tiếp.
- **Ưu tiên số liệu thực tế** hơn nói chung chung.

### 3.2. Format HVKTMM

- Font: **Times New Roman 14pt**, line-height **1.3×**
- Lề: Trái 3.0cm / Phải 1.5cm / Trên 2.0cm / Dưới 2.0cm
- Heading: H1 (16pt Bold Centered) / H2 (14pt Bold) / H3 (14pt Bold Italic) / H4 (14pt Italic, NOT bold)
- Caption hình: `*Hình X.Y. Mô tả*` — căn giữa, italic, trước 6pt sau 12pt
- Caption bảng: `*Bảng X.Y. Mô tả*` — căn giữa, bold, trước 6pt sau 4pt
- Code: Courier New 11pt, thụt lề 1cm

### 3.3. Quy ước trong file MD để convert sang DOCX

```
# Heading 1 (chương)
## Heading 2 (mục)
### Heading 3 (tiểu mục)
#### Heading 4
- bullet list
1. numbered list
[IMG:tenfile.png]          ← nhúng ảnh (tìm trong thư mục sample_images/)
*Hình 1.1. Tên hình*       ← caption hình
*Bảng 1.1. Tên bảng*      ← caption bảng
| col | col |              ← bảng markdown
```

Script `make_chapter1_docx.py` xử lý convert. Cần chạy lại sau khi sửa MD.

### 3.4. Mục tiêu độ dài

| Chương | Trang dự kiến |
|---|---|
| Chương 1 | 25–30 ✅ |
| Chương 2 | 30–35 |
| Chương 3 | 25–30 |
| Chương 4 | 20–25 |
| Kết luận | 1–2 |
| **Tổng** | ~110–130 |

---

## 4. KIẾN TRÚC HỆ THỐNG (TÓM TẮT CHO AI VIẾT BÁO CÁO)

### 4.1. Tổng quan — Microservices

```
Mobile App (KMP)  +  Web Admin (Next.js)
        │ JWT
        ▼
  Main Service :8000       ← API public, auth, chat, laws, upload
        │ X-API-Key (nội bộ)
        ▼
  RAG Service :8001        ← AI core: Agentic RAG, ingestion, embedding
        │
  ┌─────┴──────┐
ChromaDB :8002  Gemini API
                Tavily + Google Grounding (web search)

Databases:
• PostgreSQL  — users, conversations, messages, document_tasks, refresh_tokens
• MongoDB     — VietnamLawDB.articles (528,620 documents)
• ChromaDB    — collection "vietnamese_law" (690,360 vectors, 768-dim)
```

### 4.2. Agentic RAG — LangGraph 4 node

```
START → guardrail → query_analysis → agent ⇄ tools → verifier → END
```

| Node | LLM | Vai trò |
|---|---|---|
| `guardrail_node` | gemini-2.5-flash | Lọc off-topic, prompt injection. Output: `is_valid_query` |
| `query_analysis_node` | gemini-2.5-flash | Phân tích câu hỏi → JSON: topic, internal_query, web_query, requires_web_search, key_entities |
| `agent_node` | gemini-2.5-flash + tools | Re-Act loop: Thought→Action(tool call)→Observation. Max 6 iterations |
| `verifier_node` | **gemini-2.5-pro** | Kiểm chứng chéo từng claim với context, loại bỏ hallucination |

### 4.3. Hai Tool của Agent

**Tool 1: `retrieve_internal_law(query)`**
- Bi-encoder: `bkai-foundation-models/vietnamese-bi-encoder` (768-dim) → ChromaDB top-60
- Cross-encoder rerank: `cross-encoder/ms-marco-MiniLM-L-6-v2` → top-20
- Blended score: `FinalScore = 0.3 × BiScore + 0.7 × CrossScore`
- Year boost: cộng/trừ điểm theo độ mới của văn bản
- **Temporal Conflict Resolution**: phát hiện 2 văn bản cùng quy định khác năm → đánh dấu ⛔(cũ)/✅(mới)
- Ngưỡng: `SCORE_THRESHOLD_DISPLAY=0.60`, `SCORE_THRESHOLD_GENERATION=0.75`

**Tool 2: `search_web_for_law(query)`**
- Tavily API (search depth=advanced, ưu tiên `*.gov.vn`, `thuvienphapluat.vn`, `luatvietnam.vn`, `chinhphu.vn`)
- Google Grounding API
- Gọi song song (asyncio gather) → merge kết quả

### 4.4. AgentState (TypedDict)

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query_analysis: str
    is_valid_query: bool
    rejection_reason: str
    iteration_count: int
```

### 4.5. Guided Consultation (Tư vấn có hướng dẫn)

Luồng 2 bước stateless:

**Bước 1 — Clarify** (`POST /api/v1/guided/clarify`):
- Input: `{ "query": "..." }`
- Gemini Flash phân tích → sinh câu hỏi trắc nghiệm multiple-choice
- Output: `{ "detected_topic": "...", "clarify_questions": [...] }`

**Bước 2 — Answer** (`POST /api/v1/guided/answer` — SSE streaming):
- Input: `original_query + detected_topic + clarify_context`
- Guided Graph riêng: `START → planning → agent → verifier → END`
- Planning Node: **deterministic** (không dùng LLM) → ghép queries theo template
- Output: SSE events `thinking` + `answer` (markdown) + `done`

### 4.6. Document Ingestion Pipeline

```
Upload PDF → DocumentTask (pending)
  │ (parallel)
  ├── Cloudinary upload → cloud_url
  └── Gemini Vision parse → law_id, articles[]
         │
  Save MongoDB (articles)
         │
  RAG Service /ingest/articles
      ├── Chunking (≤1000 từ, overlap 150)
      ├── Bi-encoder batch encode
      └── Save ChromaDB
  Compensating Transaction: nếu 1 DB fail → rollback DB kia
```

### 4.7. Cơ sở dữ liệu chi tiết

**PostgreSQL — 5 bảng:**
- `users`: id(UUID), email, hashed_password, full_name, role, is_active
- `conversations`: id, user_id(FK), title, is_pinned, is_archived, message_count
- `messages`: id, conversation_id, question_id(self-FK), role, content, sources(JSONB), metadata(JSONB)
- `document_tasks`: id, filename, status(enum), progress(%), current_step, law_id, article_count
- `refresh_tokens`: id, user_id, token, expires_at, is_revoked

**MongoDB — `VietnamLawDB.articles`:**
```json
{
  "_id": "{law_id}_{article_id}",
  "law_id": "01/2025/QH16",
  "article_id": "1",
  "title": "Điều 1. Phạm vi điều chỉnh",
  "text": "Luật này quy định về...",
  "metadata": { "topics": [...], "keywords": [...], "year": "2025" }
}
```
Index: text-index trên `full_content_search`, B-tree trên `law_id`, `metadata.year`, `metadata.topics`.

**ChromaDB — collection `vietnamese_law`:**
```
id:        "{law_id}_{article_id}_chunk{index}"
document:  "{title}\n\n{chunk_text}"
embedding: float[768]
metadata:  law_id, article_id, year, topics(JSON-string), keywords(JSON-string)
```
HNSW: `ef_construction=100, ef_search=100, max_neighbors=16`, cosine distance, top-60 query < 200ms.

### 4.8. Frontend

**Web Admin (vietnam-law-admin-fe)**
- Next.js 16.1.6, React 19.2.3, TypeScript 5.x, TailwindCSS 4, shadcn/ui 3.8
- Trang: Login → Dashboard (BarChart recharts) → Documents (list/detail) → Upload (drag-drop, state machine, resume) → Tracker
- WebSocket (`/documents/ws`): broadcast `UPLOAD_PROGRESS` + `UPLOAD_STATUS`, auto-reconnect 3 lần
- Resume sau reload: localStorage `task_id` + `GET /documents/tasks/{id}`

**Mobile App (vietnam-law-chatbot — KMP)**
- Kotlin 2.3.0 + Compose Multiplatform 1.10.0
- Targets: Android (SDK 24–36) + iOS (arm64 + simulator) + JVM desktop
- Architecture: MVI (`BaseViewModel<State, Intent, Effect>`)
- ~16 màn hình, 15 ViewModel
- Ktor 3.4 với `Auth { bearer { refreshTokens } }` — JWT auto-refresh
- Custom SSE client (`SseClient.kt`) với `callbackFlow`
- **ThinkingPanel**: 5 bước pipeline animated realtime (Guardrail→QueryAnalysis→Agent→Tools→Verifier)
- **TypingBubble**: cursor blink hiệu ứng streaming
- Markdown render: `multiplatform-markdown-renderer-m3 0.27`
- Storage: DataStore (tokens) + KSafe 1.4 (encrypted, Keystore/Keychain)
- Navigation 3 (alpha), Koin 4.1 (DI)

---

## 5. CẤU TRÚC CHƯƠNG 2 CẦN VIẾT (ƯU TIÊN)

> File `02_Chuong_2.md` đã có nội dung tốt. **Nhiệm vụ: đọc file đó và tiếp tục mở rộng / hoàn thiện** theo outline dưới đây. Không viết lại từ đầu nếu phần đã có nội dung tốt.

**Tổng quan Chương 2**: Trình bày phương pháp và kiến trúc kỹ thuật cụ thể của hệ thống. Khác với Chương 1 (lý thuyết), Chương 2 đi sâu vào quyết định thiết kế và cách chúng được tích hợp.

### Mục lớn cần có:

**2.1. Kiến trúc tổng quan hệ thống** (~3-4 trang)
- Sơ đồ kiến trúc microservices (4 sub-project + 3 DB + LLM + Web search)
- Lý do chọn microservices: tách AI workload, bảo mật RAG Service internal-only
- Main Service (port 8000): vai trò, stack, thành phần
- RAG Service (port 8001): vai trò, stack, thành phần
- Giao tiếp giữa các service: JWT (client→main), X-API-Key (main→RAG)

**2.2. Xác định tính chất AI Agent** (~2-3 trang)
- Bảng tính chất môi trường (đối tượng, bối cảnh, vai trò, phạm vi, giới hạn đạo đức)
- Bảng nguồn dữ liệu (CSDL nội bộ, web realtime, lịch sử hội thoại)
- Tập hành động: retrieve_internal_law, search_web_for_law, sinh câu trả lời, hỏi làm rõ, từ chối

**2.3. Đồ thị Agentic RAG (LangGraph 4 node)** (~8-10 trang) ← TRỌNG TÂM
- Sơ đồ tổng quan đồ thị
- AgentState (TypedDict với các trường + giải thích reducer `add_messages`)
- Node Guardrail: mục đích, cơ chế, State input/output
- Node Query Analysis: mục đích, JSON output format, ví dụ cụ thể
- Node Agent (Re-Act loop): vòng lặp Thought→Act→Observation, max 6 iterations, function calling
- Node Verifier: Gemini Pro, kiểm chứng chéo từng claim, hành vi khi phát hiện lỗi

**2.4. Hai Tool của Agent** (~5-6 trang)
- Tool retrieve_internal_law: pipeline Two-stage Retrieval chi tiết
- Blended score formula: `0.3×Bi + 0.7×Cross`
- Year boost (bảng cộng trừ điểm)
- Temporal Conflict Resolution: vấn đề đặc thù pháp luật VN, thuật toán, ví dụ NĐ 100/2019 vs 168/2024
- Tool search_web_for_law: Tavily + Google Grounding song song, domain ưu tiên

**2.5. Two-Stage Retrieval chi tiết** (~3-4 trang)
- Vấn đề của bi-encoder thuần
- Cross-encoder: cơ chế, ưu/nhược
- Two-stage strategy: tại sao top-60 → top-20
- Blended score + Year boost + ngưỡng

**2.6. Guided Consultation** (~4-5 trang)
- Vấn đề: câu hỏi thiếu ngữ cảnh
- Kiến trúc 2 bước (Clarify + Answer)
- Guided Graph: START→planning→agent→verifier→END
- Planning Node deterministic: lý do, thuật toán ghép query
- SSE streaming: format event, lý do chọn SSE thay WebSocket

**2.7. Document Ingestion Pipeline** (~3-4 trang)
- Tổng quan luồng (sơ đồ sequence)
- Parse PDF: Gemini Vision + fallback PaddleOCR/Tesseract
- Concurrent upload Cloudinary // parse PDF
- Compensating Transaction: cơ chế rollback 2 DB
- Chunking: max 1000 từ, overlap 150

**2.8. Chiến lược Multi-LLM và Multi-API-Key** (~2 trang)
- Flash cho Agent/RAG vs Pro cho Verifier
- Rotation key: detect 429/503 → chuyển key tiếp theo

**2.9. Tổng kết chương 2**

---

## 6. CẤU TRÚC CHƯƠNG 3 (THAM KHẢO — file `03_Chuong_3.md` đã có nội dung tốt)

**3.1. Đặc tả yêu cầu hệ thống**
- 4 thành phần: Mobile App, Web Admin, Main Service, RAG Service
- Yêu cầu chức năng người dùng (11 tính năng — F-01 đến F-11)
- Yêu cầu chức năng admin (7 tính năng)
- Yêu cầu phi chức năng

**3.2. Biểu đồ Use Case** (16 UC — xem danh sách đầy đủ trong `_Plan.md`)

**3.3. Biểu đồ Sequence** (8 SD quan trọng)
- SD-02: Luồng Agentic RAG với SSE ← QUAN TRỌNG NHẤT
- SD-03: Guided Consultation 2 bước
- SD-05: Upload PDF + Ingestion

**3.4. Thiết kế CSDL** (PostgreSQL ER diagram + MongoDB schema + ChromaDB schema + quan hệ 3 DB)

**3.5. Thiết kế API** (~15-20 API quan trọng theo template bảng)

---

## 7. CẤU TRÚC CHƯƠNG 4 (CHƯA VIẾT)

**4.1.** Mô hình triển khai (Docker Compose, port mapping, volumes)

**4.2.** Giao diện Mobile App:
- Đăng ký/đăng nhập, Library, Chat với ThinkingPanel, AI-Powered Search, Guided Consultation, Settings

**4.3.** Giao diện Admin Web:
- Login, Dashboard (BarChart + WebSocket realtime), Documents, Upload (state machine + resume), Tracker

**4.4.** Đánh giá hệ thống ← TRỌNG TÂM
- Bộ dữ liệu: N1 (100 câu có đáp án xác định) + N2 (100 câu mở)
- Chỉ số: Accuracy, Recall, Context Relevance, Latency
- Bonus: Citation Accuracy (chống hallucination), Temporal Conflict Detection Rate
- Kết quả + phân tích
- So sánh A/B: Naive RAG vs Agentic RAG

---

## 8. CÁC ĐIỂM SÁNG KỸ THUẬT CẦN ĐẨY MẠNH

Khi viết, luôn nhấn mạnh các điểm này vì chúng phân biệt đề tài với các đồ án chatbot thông thường:

1. **Verifier Gemini Pro** — 2 tầng LLM (Flash sinh + Pro kiểm chứng) → chống hallucination
2. **Temporal Conflict Resolution** — đặc thù pháp luật VN (NĐ 100/2019 vs 168/2024), hiếm đồ án xử lý
3. **Two-stage retrieval** (bi-encoder tiếng Việt `vietnamese-bi-encoder` + cross-encoder MS-MARCO)
4. **Guided Consultation** với Planning deterministic: tiết kiệm token, giảm latency
5. **Microservices + Docker + Polyglot Persistence** (PostgreSQL + MongoDB + ChromaDB)
6. **Kotlin Multiplatform** — 1 codebase → Android + iOS (phù hợp chuyên ngành)
7. **Document ingestion** với Compensating Transaction (MongoDB ↔ ChromaDB)
8. **Multi-API-key rotation** — thực tế cao
9. **Web search dual-source** (Tavily + Google Grounding song song)
10. **ThinkingPanel** — hiển thị 5 bước pipeline realtime trên mobile

---

## 9. SỐ LIỆU THỰC TẾ (dùng trong báo cáo)

| Chỉ số | Giá trị |
|---|---|
| Số văn bản pháp luật trong CSDL | 46,047 văn bản |
| Số điều luật (MongoDB articles) | 528,620 |
| Số vector (ChromaDB chunks) | 690,360 |
| Chiều vector | 768 |
| Thời gian truy vấn top-60 ChromaDB | < 200ms |
| Bi-encoder model | `bkai-foundation-models/vietnamese-bi-encoder` |
| Cross-encoder model | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Blended score weights | 0.3×Bi + 0.7×Cross |
| Top-K bi-encoder | 60 |
| Top-M cross-encoder | 20 |
| Max Agent iterations | 6 |
| Score threshold display | 0.60 |
| Score threshold generation | 0.75 |
| Chunking: max tokens | 1000 từ |
| Chunking: overlap | 150 từ |
| Latency Agentic RAG | 5–15 giây |
| Latency Simple RAG | 2–3 giây |
| Android min SDK | 24 |
| Android target SDK | 36 |
| Kotlin version | 2.3.0 |
| Compose Multiplatform version | 1.10.0 |
| Next.js version | 16.1.6 |
| React version | 19.2.3 |
| Ktor version | 3.4 |
| Koin version | 4.1.1 |
| Thời gian lịch sử CSDL luật | 1945–2026 (82 năm) |
| Chủ đề pháp lý | > 62,000 |

---

## 10. TÀI LIỆU THAM KHẢO (DANH SÁCH ĐÃ CÓ)

1. Lewis, P., et al. (2020). *"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"*, NeurIPS. arxiv.org/abs/2005.11401
2. Yao, S., et al. (2022). *"ReAct: Synergizing Reasoning and Acting in Language Models"*, ICLR. arxiv.org/abs/2210.03629
3. Gao, Y., et al. (2023). *"Retrieval-Augmented Generation for Large Language Models: A Survey"*. arxiv.org/abs/2312.10997
4. Vaswani, A., et al. (2017). *"Attention is All You Need"*, NeurIPS. arxiv.org/abs/1706.03762
5. LangGraph Documentation. langchain-ai.github.io/langgraph/
6. LangChain Documentation. python.langchain.com/docs/tutorials/rag/
7. Google Gemini API Documentation. ai.google.dev
8. ChromaDB Documentation. docs.trychroma.com
9. FastAPI Documentation. fastapi.tiangolo.com
10. Tavily Search API Docs. docs.tavily.com
11. Kotlin Multiplatform Docs. kotlinlang.org/docs/multiplatform.html
12. Compose Multiplatform Docs. jb.gg/cmp
13. Sentence Transformers Docs. sbert.net
14. PostgreSQL Documentation. postgresql.org/docs
15. MongoDB Documentation. docs.mongodb.com
16. BKAI Foundation Models. *"Vietnamese Bi-Encoder"*. huggingface.co/bkai-foundation-models/vietnamese-bi-encoder
17. VinAI Research. *"PhoBERT-base"*. github.com/VinAIResearch/PhoBERT
18. Russell, S., & Norvig, P. (2010). *"Artificial Intelligence: A Modern Approach"* (3rd ed.). Pearson
19. Huyen, C. (2025). *"AI Agents"*. huyenchip.com/2025/01/07/agents.html
20. Cơ sở dữ liệu pháp luật quốc gia. vbpl.vn
21. Thư viện pháp luật. thuvienphapluat.vn

---

## 11. CẤU TRÚC FILE BÁO CÁO HIỆN TẠI

```
/Users/duy/Downloads/sourcecode/
├── Vương Văn Duy_Báo cáo.docx        ← FILE DOCX CHÍNH (chứa tất cả chương)
├── Vương Văn Duy_Báo cáo_backup.docx ← Backup trước lần merge cuối
└── Bao_Cao/
    ├── 00_Mo_Dau.md                   ← Lời cảm ơn, cam đoan, lời nói đầu
    ├── 01_Chuong_1.md                 ← Chương 1 (HOÀN THIỆN)
    ├── 01_Chuong_1.docx               ← DOCX chương 1 riêng
    ├── 02_Chuong_2.md                 ← Chương 2 (CẦN BỔ SUNG)
    ├── 03_Chuong_3.md                 ← Chương 3 (CÓ DRAFT)
    ├── make_chapter1_docx.py          ← Script convert MD → DOCX
    ├── _Plan.md                       ← Kế hoạch chi tiết toàn bộ báo cáo
    ├── _Project_Overview.md           ← Mô tả kỹ thuật dự án đầy đủ
    ├── _Frontend_Overview.md          ← Chi tiết frontend (KMP + Next.js)
    ├── _Sample_Report.md              ← Phân tích báo cáo mẫu HVKTMM
    ├── _DB_Stats.md                   ← Thống kê CSDL
    ├── _Diagrams.md                   ← Sơ đồ hệ thống
    ├── CONTEXT_HANDOFF.md             ← File này
    └── sample_images/                 ← Thư mục ảnh (70 ảnh từ báo cáo mẫu)
        ├── image2.png  → Hình 1.1 (Chatbot tập luật)
        ├── image3.jpeg → Hình 1.2 (Mô hình RAG)
        ├── image4.jpeg → Hình 1.3 (AI Agent)
        ├── image5.png  → Hình 1.4 (SWE Agent)
        ├── image6.png  → Hình 1.5 (Thành phần Agent)
        ├── image7.png  → Hình 1.6 (Planning/Re-planning)
        ├── image8.png  → Hình 1.7 (ReAct ví dụ)
        ├── image9.png  → Hình 1.8 (LangGraph nodes/edges)
        └── image10.png → Hình 1.9 (LangGraph State)
```

---

## 12. CHECKLIST CUỐI KỲ

- [ ] Chương 2 hoàn thiện → update vào `Vương Văn Duy_Báo cáo.docx`
- [ ] Chương 3 hoàn thiện → update vào DOCX
- [ ] Chương 4 viết + ảnh chụp giao diện thật → update vào DOCX
- [ ] Kết luận (~1.5 trang)
- [ ] Tài liệu tham khảo (≥15 nguồn, format chuẩn)
- [ ] Phần đầu: bìa, lời cảm ơn, cam đoan, mục lục, danh mục hình/bảng/viết tắt
- [ ] Format chuẩn HVKTMM toàn bộ DOCX
- [ ] Số trang: Roman (front matter) → Arabic (từ Lời nói đầu)
- [ ] Soát lỗi chính tả tiếng Việt
- [ ] In thử kiểm tra layout

---

## 13. HƯỚNG DẪN CHO AI TIẾP TỤC

**Bước 1**: Đọc file `02_Chuong_2.md` để nắm nội dung đã có.

**Bước 2**: Đọc file `_Project_Overview.md` để biết chi tiết kỹ thuật chính xác.

**Bước 3**: Viết/bổ sung Chương 2 theo outline ở mục 5 của file này, đảm bảo:
- Không mâu thuẫn với nội dung Chương 1 đã có
- Dùng số liệu từ mục 9 của file này
- Văn phong "em", học thuật, tiếng Việt chuẩn
- Đủ các bảng và hình theo yêu cầu

**Bước 4**: Sau khi có MD hoàn chỉnh, dùng script `make_chapter1_docx.py` (chỉnh tên file) để convert MD → DOCX, rồi merge vào `Vương Văn Duy_Báo cáo.docx` bằng script Python tương tự `merge_chapter1_v2.py`.

**Lưu ý quan trọng**:
- Chương 2 trong `Vương Văn Duy_Báo cáo.docx` hiện là **nội dung cũ** — cần merge nội dung mới từ MD sau khi hoàn thiện
- Script merge nằm ở `/tmp/merge_chapter1_v2.py` — có thể tái sử dụng cho Chương 2, 3, 4 bằng cách thay tên heading tìm kiếm
