# MÔ TẢ CHI TIẾT DỰ ÁN: VIETNAM LAW SERVICE

> Tài liệu nội bộ phục vụ viết báo cáo đồ án tốt nghiệp.
> Tổng hợp từ source code thực tế tại `d:\doan\sourcecode\` và các file docs.

---

## 1. THÔNG TIN ĐỀ TÀI

- **Tên đề tài**: Nghiên cứu phát triển trợ lý ảo pháp luật cho chuyển đổi số.
- **Sinh viên thực hiện**: Vương Văn Duy.
- **Lớp**: CT6D — Chuyên ngành: Phát triển phần mềm di động — Mã ngành: 7.48.02.01.
- **Giáo viên hướng dẫn**: ThS. Trần Đức Thịnh.
- **Đơn vị**: Học viện Kỹ thuật Mật mã — Khoa Công nghệ Thông tin.
- **Thời gian**: Năm học 2025 – 2026.

---

## 2. KIẾN TRÚC TỔNG THỂ

### 2.1. Sơ đồ hệ thống cấp cao

Hệ thống được tổ chức theo mô hình **Microservices**, gồm 4 thành phần độc lập, giao tiếp qua REST API/HTTP và chia sẻ qua hệ thống cơ sở dữ liệu được quản lý qua Docker Compose:

```
┌──────────────────────────────────────────────────────────────┐
│  Mobile App (Kotlin Multiplatform)  |  Admin Web (Next.js)  │
└───────────────────────┬──────────────────────────────────────┘
                        │ JWT Auth (HTTPS)
                        ▼
                ┌───────────────────────┐
                │ Main Service :8000    │
                │ - Auth, Chat, Laws    │
                │ - Document Upload     │
                │ - Guided Consultation │
                └────────┬──────────────┘
                         │ X-API-Key (HTTP nội bộ)
                         ▼
                ┌───────────────────────┐
                │ RAG Service :8001     │
                │ - Agentic RAG (LangGraph)
                │ - Simple RAG Pipeline │
                │ - Document Ingestion  │
                └────┬───────────┬──────┘
                     │           │
                     ▼           ▼
              ChromaDB :8002   Gemini API (LLM)
                     ▲           ▲
                     │           │
                     │     Tavily / Google Grounding
                     │
       ┌─────────────┴───────────┐
       │  Embedding models       │
       │  bi-encoder + cross-enc.│
       └─────────────────────────┘

  Persisted Data:
   • PostgreSQL: users, conversations, messages, document_tasks, refresh_tokens
   • MongoDB: VietnamLawDB.articles
   • ChromaDB: vietnamese_law (vector chunks)
```

### 2.2. Bốn sub-project

| Sub-project | Vai trò | Công nghệ |
|---|---|---|
| `vietnam-law-service/main-service` | API Gateway: auth, chat, browse luật, upload tài liệu, guided consultation | FastAPI (Python), SQLAlchemy async, Motor (MongoDB), httpx |
| `vietnam-law-service/rag-service` | Lõi AI: Agentic RAG, simple RAG, ingestion, embedding | FastAPI, LangGraph, sentence-transformers, ChromaDB, google-genai (Gemini) |
| `vietnam-law-admin-fe` | Web admin: upload PDF, theo dõi pipeline qua WebSocket, dashboard thống kê | Next.js 16, React 19, TypeScript, TailwindCSS 4, shadcn/ui 3.8, axios, recharts, sonner |
| `vietnam-law-chatbot` (Vietnam Law Chatbot) | Mobile app cho người dùng cuối — chat AI, guided consultation, library, AI-powered search | Kotlin 2.3 + Compose Multiplatform 1.10 (Android + iOS + JVM desktop), Ktor 3.4, Koin 4.1, Navigation 3, KSafe |
| `vietnamese-law-rag` | Module thử nghiệm RAG, OCR, embedding offline (chỉ dev) | Python notebooks/scripts |

---

## 3. VIETNAM-LAW-SERVICE — BACKEND

### 3.1. Main Service (port 8000)

**Vai trò**: API public cho mobile app + admin dashboard. Là cửa ngõ duy nhất tiếp xúc với client; mọi gọi xuống RAG Service đều đi qua tầng này.

**Cấu trúc thư mục `app/`**:
- `api/v1/` — REST routes:
  - `auth.py`: register/login/refresh/me/change-password
  - `chat.py`: CRUD conversation, gửi tin nhắn (gọi RAG Agentic)
  - `documents.py`: upload PDF, theo dõi document task
  - `laws.py`: liệt kê luật, lấy chi tiết điều, search by topic/year/keyword
  - `guided.py`: 2 endpoint cho Guided Consultation
  - `dashboard.py`: thống kê admin
- `services/` — business logic: `auth_service`, `chat_service`, `document_processor`, `document_parser`, `llm_parser`, `cloud_storage`, `law_service`, `rag_client`, `metadata_enricher`, `validators`, `websocket_manager`.
- `repositories/` — data access: `user_repo`, `conversation_repo`, `message_repo`, `law_repo`, `document_task_repo`, `refresh_token_repo`.
- `models/` — SQLAlchemy ORM (User, Conversation, Message, DocumentTask, RefreshToken).
- `schemas/` — Pydantic request/response.
- `core/` — config (`pydantic-settings`), security (JWT helpers), exceptions.
- `db/base.py` — async engine + session factory.

**Chức năng nổi bật**:
1. **JWT Authentication**: access token + refresh token (rotation, revoke). Hash mật khẩu bằng bcrypt.
2. **Quản lý hội thoại**: pin/archive conversation, đếm message, auto-title từ topic của RAG.
3. **Document Upload Pipeline**:
   - Tạo `DocumentTask` ngay khi nhận file → trả `task_id` để mobile/admin theo dõi.
   - Concurrent: Upload Cloudinary // Gemini Vision parse PDF.
   - Save MongoDB toàn văn → gửi sang RAG để chunk + embed.
   - Compensating Transaction: rollback MongoDB nếu ChromaDB lỗi và ngược lại.
4. **WebSocket / progress callback** để stream tiến trình xử lý PDF.
5. **Law browsing**: aggregation pipelines trên MongoDB (group by `law_id`, lấy summary, distinct year/topic).

### 3.2. RAG Service (port 8001)

**Vai trò**: nội bộ (internal-only). Xác thực bằng `X-API-Key`. Đây là "trái tim AI" — toàn bộ logic agentic, embedding, tool calling đều ở đây.

**Cấu trúc thư mục `app/`**:
- `api/v1/`:
  - `rag.py` — endpoint `/rag/search` (Simple RAG) và `/rag/agent-search` (Agentic RAG).
  - `ingest.py` — endpoint `/ingest/articles`, `/ingest/delete-by-law-id`.
  - (guided endpoints tích hợp trong cùng hoặc module riêng).
- `agent/`:
  - `graph.py` — định nghĩa `StateGraph` cho luồng chat.
  - `nodes.py` — 4 node: `guardrail_node`, `query_analysis_node`, `agent_node`, `verifier_node`.
  - `state.py` — `AgentState` (TypedDict): messages, query_analysis, retrieved_docs, iteration_count, ...
  - `guided_graph.py` + `guided_nodes.py` + `guided_state.py` — graph riêng cho Guided Consultation.
- `tools/`:
  - `guardrail.py` — kiểm soát đầu vào (off-topic, prompt injection).
  - `internal_law_tool.py` — `@tool retrieve_internal_law(query)`.
  - `web_search.py` — `@tool search_web_for_law(query)` (Tavily + Google Grounding).
- `services/`:
  - `rag_service.py` — pipeline 6 bước (Simple RAG): metadata filter → vector search → cross-encoder rerank → LLM ranking → temporal conflict → generate.
  - `llm_service.py` — wrapper Gemini với multi-key rotation, retry trên 429/503, 3 chức năng (analyze_query, rank_documents, generate_answer).
- `repositories/`:
  - `chroma_repo.py` (Singleton) — HTTP/Persistent client cho ChromaDB, collection `vietnamese_law`.
  - `embedding_repo.py` (Singleton) — load `vietnamese-bi-encoder` + `ms-marco-MiniLM-L-6-v2` qua `sentence-transformers`.
- `core/internal_auth.py` — middleware kiểm tra `X-API-Key`.

**Models LLM**:
| Vai trò | Model | Mục đích |
|---|---|---|
| RAG pipeline (analyze, generate) | `gemini-2.5-flash` | Nhanh, rẻ |
| Agent (reasoning + tool calling) | `gemini-2.5-flash` | Cân bằng |
| Verifier (anti-hallucination) | `gemini-2.5-pro` | Chính xác cao nhất |

**Embeddings**:
- Bi-encoder: `bkai-foundation-models/vietnamese-bi-encoder` (768-d, tối ưu tiếng Việt).
- Cross-encoder: `cross-encoder/ms-marco-MiniLM-L-6-v2` (rerank).

### 3.3. Cấu hình & môi trường

`.env` chính (rag-service):
- `GEMINI_API_KEYS_STR` — nhiều API key, phân tách bằng `,` (rotation).
- `AGENT_MODEL=gemini-2.5-flash`, `VERIFIER_MODEL=gemini-2.5-pro`.
- `CHROMA_HOST`, `CHROMA_PORT`, `EMBEDDING_MODEL`, `CROSS_ENCODER_MODEL`.
- `METADATA_FILTER_LIMIT=200`, `VECTOR_SEARCH_TOP_K=60`, `ROUND2_CANDIDATES=20`.
- `SCORE_THRESHOLD_DISPLAY=0.60`, `SCORE_THRESHOLD_GENERATION=0.75`.
- `TAVILY_API_KEY`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`.

`.env` chính (main-service):
- `DATABASE_URL=postgresql+asyncpg://...`
- `MONGO_URI=mongodb://...`, `MONGO_DB=VietnamLawDB`, `MONGO_COLLECTION=articles`.
- `RAG_SERVICE_URL=http://localhost:8001`, `RAG_SERVICE_API_KEY=...`.
- `JWT_SECRET`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`.
- `GEMINI_API_KEY` (cho DocumentParser).
- `CLOUDINARY_*` (cloud storage).

---

## 4. CƠ SỞ DỮ LIỆU

### 4.1. PostgreSQL (5 bảng) — main-service

| Bảng | Mục đích |
|---|---|
| `users` | id (UUID), email (unique), hashed_password, full_name, phone, role, is_active, last_login_at, password_changed_at, created/updated_at |
| `conversations` | id, user_id (FK), title, is_pinned, is_archived, message_count, last_message_at |
| `messages` | id, conversation_id, **question_id (self-FK Q&A)**, role (`user`/`assistant`), content, **sources (JSONB)**, **metadata (JSONB)** |
| `document_tasks` | id, filename, file_size_bytes, status (enum), progress (%), current_step, law_id, article_count, error_message |
| `refresh_tokens` | id, user_id, token (unique), expires_at, is_revoked |

**Đặc điểm**: bảng được tạo tự động qua `Base.metadata.create_all` (không dùng Alembic). Migrations thủ công đặt ở `main-service/migrations/`.

### 4.2. MongoDB — `VietnamLawDB.articles`

```json
{
  "_id": "{law_id}_{article_id}",
  "law_id": "01/2025/QH16",
  "article_id": "1",
  "title": "Điều 1. Phạm vi điều chỉnh",
  "text": "Luật này quy định về...",
  "source_url": "https://cloudinary.com/...",
  "full_content_search": "{title}\n{text}",
  "metadata": {
    "topics": ["Dân sự", "Hợp đồng"],
    "keywords": ["hợp đồng", "giao dịch"],
    "summary": "...",
    "year": "2025"
  }
}
```

Index: text-index trên `full_content_search`; B-tree index trên `law_id`, `article_id`, `metadata.year`, `metadata.topics`.

Aggregation queries chính: `get_laws()`, `get_law_detail()`, `get_all_topics()`, `get_all_years()`, `search()`.

### 4.3. ChromaDB — collection `vietnamese_law`

```
id:        "{law_id}_{article_id}_chunk{index}"
document:  "{title}\n\n{chunk_text}"
embedding: float[768]   ← bi-encoder
metadata:
  law_id, article_id, title, chunk_index, total_chunks,
  year, topics (JSON-string), keywords (JSON-string), summary
```

> Chú ý: `topics`/`keywords` lưu dạng **JSON string** (ChromaDB metadata chỉ hỗ trợ scalar), khác với MongoDB.

### 4.4. Quan hệ giữa 3 DB

- 1 luật (`law_id`) → N articles trong MongoDB.
- 1 article → 1..N chunks trong ChromaDB (chia nếu text dài, max 1000 từ, overlap 150).
- `messages.sources` (JSONB) chứa chunk-id để truy hồi nguồn khi hiển thị citation.
- `document_tasks.law_id` liên kết task upload với MongoDB + ChromaDB.

---

## 5. AGENTIC RAG PIPELINE (luồng chính)

### 5.1. Vì sao Agentic RAG?

RAG truyền thống (Naive RAG) gặp khó với:
- Câu hỏi mơ hồ, nhiều bước suy luận.
- Câu hỏi cần tổng hợp dữ liệu nội bộ + nguồn web (đặc biệt với luật mới ban hành chưa có trong CSDL).
- Đòi hỏi kiểm chứng chống hallucination — yếu tố sống còn trong domain pháp luật.

Agentic RAG giải bài toán này bằng cách giao quyền điều phối cho một AI Agent có khả năng lập kế hoạch, gọi nhiều tool, tự đánh giá và lặp lại cho đến khi đủ thông tin (Re-Act).

### 5.2. Graph 4 node (LangGraph)

```
START → guardrail → query_analysis → agent ⇄ tools
                                       ↓ (final answer)
                                    verifier → END
```

| Node | LLM | Vai trò |
|---|---|---|
| `guardrail_node` | Flash | Lọc câu hỏi off-topic, prompt injection, vi phạm. Trả `is_valid_query` + lý do. |
| `query_analysis_node` | Flash | Kết hợp lịch sử chat + câu hỏi → JSON: `topic`, `internal_search_query`, `web_search_query`, `requires_web_search`, `key_entities`. |
| `agent_node` | Flash + tool calling | Vòng lặp Re-Act: gọi tool → đánh giá → có thể gọi tool tiếp. Max iterations = 6. |
| `verifier_node` | **Pro** | Đối chiếu chéo từng câu khẳng định với context, sửa hoặc loại bỏ phần hallucinate. |

### 5.3. Hai tool

#### Tool 1 — `retrieve_internal_law(query)`

Gọi `RAGService.retrieve_documents_for_agent()`. Phía sau là pipeline 2 giai đoạn:

1. **Bi-encoder**: encode query, ChromaDB cosine similarity, lấy top-60 (`VECTOR_SEARCH_TOP_K`).
2. **Cross-encoder rerank**: chấm điểm lại các cặp (query, document). Score tổng hợp:

   ```
   FinalScore = 0.3 × BiEncoderScore + 0.7 × CrossEncoderScore
   ```

3. **Year boost** (cộng/trừ theo độ mới của văn bản — ưu tiên luật mới).
4. **Temporal Conflict Resolution**: phát hiện 2 văn bản cùng quy định nhưng khác năm → đánh dấu ⛔ (cũ) / ✅ (mới) trước khi đẩy cho LLM.
5. Trả về top-N kết quả (mặc định 10 cho agent) đã format sẵn dạng text có citation.

#### Tool 2 — `search_web_for_law(query)`

- **Tavily**: search depth = `advanced`, ưu tiên domains pháp luật Việt Nam (`*.gov.vn`, `thuvienphapluat.vn`, `luatvietnam.vn`, `chinhphu.vn`, ...).
- **Google Grounding API**: bổ sung kết quả realtime, giảm rủi ro Tavily index trễ.
- Hai nguồn gọi **song song** (asyncio gather) → merge → trả về cho agent.

### 5.4. Cấu hình ngưỡng tin cậy

| Biến | Giá trị | Ý nghĩa |
|---|---|---|
| `SCORE_THRESHOLD_DISPLAY=0.60` | Ngưỡng tối thiểu để hiển thị làm "source" cho user. |
| `SCORE_THRESHOLD_GENERATION=0.75` | Ngưỡng để LLM được phép sinh câu trả lời chuyên sâu (nếu không đạt → lùi về câu trả lời "không đủ căn cứ"). |
| `ROUND2_CANDIDATES=20` | Số document đẩy vào cross-encoder. |
| `METADATA_FILTER_LIMIT=200` | Số candidate sau bước metadata filter (Simple RAG). |

### 5.5. Re-Act loop

Trong mỗi vòng, agent có thể:
- Quan sát kết quả tool.
- Quyết định **đủ thông tin** → final answer.
- Hoặc **chưa đủ** → tự sinh truy vấn phụ → gọi tool lại.

Giới hạn `MAX_ITERATIONS = 6` để tránh infinite loop. Khi vượt giới hạn, agent buộc phải tổng hợp với những gì đang có và kèm cảnh báo.

---

## 6. SIMPLE RAG (LEGACY) — 6 BƯỚC

Ngoài Agentic RAG, hệ thống vẫn giữ Simple RAG cho query đơn giản, low-latency:

1. **Gemini phân tích query** → topics, keywords.
2. **Metadata filter** (MongoDB-side) → max 200 candidates.
3. **Vector search** (bi-encoder, 70% vector + 30% metadata score) → top 60.
4. **Cross-encoder rerank** (40% prev + 60% cross-encoder) → top 20.
5. **LLM ranking** (60% cross-encoder + 40% LLM) — tinh chỉnh thứ tự cuối.
6. **Generate answer** (Gemini Flash) — dựa trên các doc đạt ngưỡng.

Pipeline này được expose qua `/rag/search`. Agentic RAG đi qua `/rag/agent-search`.

---

## 7. GUIDED CONSULTATION (Tư vấn có hướng dẫn)

### 7.1. Vì sao tách luồng?

Người dùng cuối thường hỏi câu thiếu ngữ cảnh: *"Vượt đèn đỏ phạt bao nhiêu?"* — cần biết loại phương tiện, lỗi phụ kèm, ... Nếu để Agentic RAG xử lý, agent sẽ bịa hoặc hỏi lại nhiều lần, mất UX.

Guided Consultation giải quyết bằng quy trình **2 bước có cấu trúc**, **stateless** (không lưu lịch sử):

### 7.2. Step 1 — Clarify

`POST /api/v1/guided/clarify`

```
Input: { "query": "Vượt đèn đỏ bị phạt bao nhiêu?" }
Output:
{
  "detected_topic": "Giao thông",
  "clarify_questions": [
    {
      "question": "Bạn điều khiển phương tiện gì?",
      "options": ["Ô tô", "Xe máy", "Xe đạp", "Khác"]
    },
    ...
  ]
}
```

Backend phân tích nhanh bằng Gemini Flash → sinh câu hỏi trắc nghiệm (multiple-choice) hiển thị trên mobile.

### 7.3. Step 2 — Answer

`POST /api/v1/guided/answer` (SSE streaming)

Input gồm: `original_query`, `detected_topic`, `clarify_context` (string đã ghép từ lựa chọn user).

Phía RAG Service dùng **Guided Graph** riêng:

```
START → planning → agent → verifier → END
```

- **Planning Node** — *deterministic* (không dùng LLM). Ghép queries tối ưu theo template tiền định, giúp tiết kiệm token và rút ngắn thời gian phản hồi.
- **Agent Node** — system prompt khác (đã biết context giàu), gọi `retrieve_internal_law` + (tuỳ chọn) `search_web_for_law`.
- **Verifier Node** — kiểm tra câu trả lời có đúng bối cảnh user vừa cung cấp.

Output: **SSE stream** các event `thinking` (hiển thị "đường ray" trên mobile) và `answer` (text dạng markdown), kết thúc `done`.

---

## 8. DOCUMENT INGESTION PIPELINE

`POST /api/v1/documents/upload` (multipart) → tạo `DocumentTask` (status = `pending`) → trả `task_id`.

Background task chạy `DocumentProcessor.process_document(file_path, on_progress)`:

```
DOWNLOADING (nếu URL)
   │
PROCESSING
   ├─ Cloudinary upload (parallel)         →  cloud_url
   ├─ Gemini Vision parse PDF (parallel)   →  parsed_articles[law_id, articles[]]
   ├─ Save MongoDB (full articles)
   └─ Gọi rag-service /ingest/articles
        ├─ Chunking (≤1000 từ, overlap 150)
        ├─ Bi-encoder batch encoding
        └─ Save ChromaDB (chunks + vectors)
COMPLETED
```

**Compensating Transaction**:
- Nếu MongoDB OK nhưng ChromaDB fail → xoá MongoDB.
- Nếu ChromaDB OK nhưng MongoDB fail → xoá ChromaDB.

Tracking progress qua polling `GET /documents/tasks/{task_id}` hoặc WebSocket (nếu enabled).

Công cụ liên quan: `PyMuPDF`, `pdf2image`, `paddleocr`, `pytesseract`, `cloudinary`, `google-genai` (Gemini Vision).

---

## 9. FRONTEND

> Đã verify chi tiết — xem `_Frontend_Overview.md` để có đầy đủ.

### 9.1. vietnam-law-admin-fe (Next.js 16 + React 19)

**Mục đích**: web admin cho quản trị viên hệ thống.

**3 trang chính** (verified):
1. `/` — Login (với mapping 17 mã lỗi backend → tiếng Việt; verify `role === "admin"` sau login).
2. `/dashboard` — Tổng quan thống kê (BarChart top topics, latest tasks, auto-refetch khi task xong).
3. `/dashboard/documents` — Danh sách văn bản (search, paginate 15/page, dialog detail + lazy load article).
4. `/dashboard/documents/upload` — **Upload PDF với drag-drop, AbortController, resume task sau reload** (state machine: idle → uploading → processing → done).
5. `/dashboard/tracker` — Theo dõi tất cả document tasks với status realtime.

**Điểm sáng kỹ thuật**:
- **`WebSocketProvider`** — kết nối `ws://.../documents/ws?token=...` để nhận `UPLOAD_PROGRESS` + `UPLOAD_STATUS`. Auto-connect khi có task processing, auto-disconnect khi xong, auto-reconnect retry max 3 lần.
- **Resume upload state** — sau reload tab, lấy `task_id` từ localStorage + `GET /documents/tasks/{id}` để build lại UI.
- **axios interceptor** — gắn JWT từ cookie tự động; 401/403 → xoá cookie + redirect login.
- **Type-safe**: TypeScript interface cho mọi DTO.

**Stack chi tiết**:
- Next.js 16.1.6 (App Router), React 19.2.3, TypeScript 5.x.
- TailwindCSS 4 + `tw-animate-css`.
- shadcn/ui 3.8.5 (built on Radix UI 1.4.3) — 14 components.
- axios 1.13, react-hook-form 7.71 + zod 4.3, recharts 3.7, sonner 2.0, date-fns 4.1, js-cookie 3.0.

### 9.2. vietnam-law-chatbot (Kotlin Multiplatform)

**Mục đích**: app cho người dùng cuối, hỗ trợ Android + iOS từ 1 codebase.

**Multi-target**:
- `androidTarget` (min SDK 24, target SDK 36).
- `iosArm64` + `iosSimulatorArm64`.
- `jvm` (desktop — phụ).

**Architecture: MVI**:
```kotlin
abstract class BaseViewModel<S : UiState, I : MVIIntent, F : MVIEffect> : ViewModel()
// State: MutableStateFlow + StateFlow (immutable)
// Intent: sendIntent(intent: I) — UI -> VM
// Effect: Channel<F> — VM -> UI (one-shot navigate, toast)
```

**~16 màn hình + 15 ViewModel** (verified từ `appModule.kt`):
- **Auth flow**: Splash → Login → SignUp.
- **Home (3 bottom-bar tabs)**: Chat (list) | Library | Setting.
- **Sub-screens**:
  - ChatDetail (cuộc hội thoại đang mở, có ThinkingPanel + TypingBubble).
  - LawDetail, ArticleDetail.
  - GuidedConsultation (Clarify + Answer SSE).
  - ArchivedConversations, Profile, ChangePassword.

**Network layer (verified)**:
- **Ktor 3.4** với `Auth { bearer { refreshTokens } }` plugin → JWT auto-refresh 100% tự động khi 401.
- **Custom SSE client** (`SseClient.kt`) dùng `callbackFlow` để parse SSE frames (`event:` / `data:` / `:heartbeat`) — workaround cho "Flow invariant violated" của Ktor `UndispatchedCoroutine`.
- **3 SSE endpoints**: `chat/messages/stream`, `guided/answer/stream`, và planned future.
- **Domain events**: `sealed interface ChatStreamEvent { Ready / Progress / Done / Error }` → repository map từ raw SSE → typed Flow.

**UI components độc đáo**:
- **`ThinkingPanel`** — vertical timeline animated, hiển thị 5 step pipeline (Guardrail → Query Analysis → Agent → Tools → Verifier) đang chạy realtime, auto-collapse khi xong.
- **`TypingBubble`** — bubble với cursor blink hiệu ứng typing.
- **Markdown renderer** (`multiplatform-markdown-renderer-m3`) cho câu trả lời AI.

**Local storage**:
- `DataStoreManager` (androidx.datastore) cho JWT tokens + preferences.
- `KSafe` 1.4 cho encrypted storage (Android KeyStore / iOS Keychain qua expect/actual).

**Navigation**:
- `Navigation 3` (alpha) — thế hệ navigation mới của Compose, dựa trên `NavBackStack` + `NavEntry` + `SavedStateConfiguration`.
- 11 main routes (`MainRoute` sealed) + 3 home tabs (`HomeRoute`).

**Stack chi tiết**:
- Kotlin 2.3.0, Compose Multiplatform 1.10.0, Material3 1.10-alpha05.
- Ktor 3.4 (`okhttp` Android, `darwin` iOS, `cio` desktop).
- Koin 4.1.1 (DI), kotlinx-serialization 1.10, kotlinx-datetime 0.7.1.
- androidx.datastore 1.2 + ksafe 1.4 (storage).
- Mike Penz multiplatform-markdown-renderer-m3 0.27 (markdown UI).

---

## 10. TÍNH NĂNG NỔI BẬT (đối chiếu báo cáo)

| Tính năng | Trạng thái | Đặc tính kỹ thuật cần highlight trong báo cáo |
|---|---|---|
| Agentic RAG (LangGraph) | ✅ | 4 node, Re-Act, Max iter 6, multi-LLM (Flash/Pro) |
| Two-stage retrieval | ✅ | Bi-encoder + cross-encoder rerank, blended score 0.3/0.7 |
| Web search dual-source | ✅ | Tavily + Google Grounding song song |
| Temporal Conflict Resolution | ✅ | Phát hiện xung đột năm ban hành, đánh dấu ⛔/✅ |
| Verifier (anti-hallucination) | ✅ | Gemini Pro, kiểm chứng chéo từng claim |
| Guided Consultation | ✅ | 2 bước (Clarify + Answer), Planning deterministic, SSE streaming |
| Document upload + OCR | ✅ | Gemini Vision + PaddleOCR/Tesseract, concurrent với Cloudinary |
| JWT + refresh rotation | ✅ | Bcrypt, revoke list |
| Compensating transaction | ✅ | MongoDB ↔ ChromaDB rollback |
| Multi-API-key rotation | ✅ | LLMService xoay vòng khi 429/403 |
| Gợi ý câu hỏi (suggested) | ✅ BE + Mobile DONE | `GET /messages/{id}/suggested-questions`, `getSuggestedQuestions()` trong ChatService |
| **Streaming chat response (regular chat)** | ✅ DONE | `chat/messages/stream`, `sendMessageStream()` SSE, ThinkingPanel composable |
| **Streaming guided consultation** | ✅ DONE | `guided/answer/stream`, `answerStream()` SSE |
| **AI-Powered Search trong Library** | ✅ DONE | `POST /laws/ai-search`, `LawService.aiSearch()`, model `AISearchResult` |
| **WebSocket task tracking (admin)** | ✅ DONE | `/documents/ws`, `WebSocketProvider`, auto-reconnect |
| **Resume upload sau reload (admin)** | ✅ DONE | localStorage + `GET /tasks/{id}` |
| Feedback / rating AI | ❌ | Trong `feature_suggestions.md` — chưa làm |
| Bookmark điều luật | ❌ | Trong `feature_suggestions.md` — chưa làm |
| Lịch sử tra cứu | ❌ | Trong `feature_suggestions.md` — chưa làm |
| Share điều luật | ❌ | Trong `feature_suggestions.md` — chưa làm |
| Quản lý người dùng (admin) | ⚠ | Backend có `/dashboard/users`, web admin chưa làm UI |

> **CẬP NHẬT QUAN TRỌNG (sau khi đọc code thực tế)**: Streaming Response, Suggested Questions, AI-Powered Search **đã hoàn thành** — KHÁC với memory cũ ghi "chưa làm". Đây là 3 tính năng "wow" lớn nhất, **bắt buộc đẩy mạnh trong báo cáo**.

---

## 11. TRIỂN KHAI DOCKER

`docker-compose.yml` ở root khởi động đồng thời:
- `postgres:16-alpine` (port 5432).
- `mongo:7` (port 27017).
- `chromadb` (port 8002).
- `main-service` (port 8000).
- `rag-service` (port 8001).
- `admin-frontend` (port 3000) — nếu được build kèm.

Volumes: `postgres_data`, `mongo_data`, `chroma_data`, `upload_data`, `model_cache`.

Lệnh chạy:
```bash
docker-compose up -d
```

---

## 12. CÔNG CỤ THEO DÕI / DEBUG

- **LangSmith**: bật qua `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY` để trace toàn bộ Agentic RAG run.
- **Logging**: structured logging trên cả 2 service.
- **Test scripts**:
  - `rag-service/scripts/run_test_cases.py`
  - `rag-service/scripts/run_graph_test.py`
  - `rag-service/scripts/run_tool_test.py`

---

## 13. NHỮNG ĐIỂM CÓ THỂ LÀM "ĐIỂM SÁNG" KHI PHẢN BIỆN

1. **Agentic RAG + Verifier 2 tầng LLM** (Flash sinh, Pro kiểm chứng) — vượt mức RAG cơ bản, giải quyết bài toán hallucination trong domain pháp luật.
2. **Temporal Conflict Resolution** — vấn đề đặc thù của luật Việt Nam (cùng nội dung, năm ban hành khác nhau). Hiếm đồ án nào xử lý.
3. **Two-stage retrieval với bi-encoder tiếng Việt + cross-encoder MS-MARCO**: kết hợp tốc độ và độ chính xác.
4. **Guided Consultation với Planning deterministic**: tối ưu chi phí token, giảm latency, UX trực quan.
5. **Microservices + Docker Compose + Multi-DB (PostgreSQL, MongoDB, ChromaDB)**: thể hiện kỹ năng kiến trúc hệ thống thực tế.
6. **Multi-platform UI**: Web admin (Next.js) + Mobile cross-platform (Compose Multiplatform).
7. **Document ingestion pipeline với OCR + Compensating Transaction**: khía cạnh "kỹ thuật phần mềm" rõ ràng.
8. **Multi-API-key rotation cho LLM**: chi tiết nhỏ nhưng rất thực tế (chống rate limit khi demo).
9. **Web search dual-source (Tavily + Google Grounding)**: đảm bảo cập nhật luật mới ban hành.
10. **Mobile KMP**: chia sẻ codebase Android/iOS — sức nặng cho chuyên ngành "Phát triển phần mềm di động".
