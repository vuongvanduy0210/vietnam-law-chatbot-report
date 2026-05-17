# CHƯƠNG 2: PHƯƠNG PHÁP XÂY DỰNG HỆ THỐNG TƯ VẤN PHÁP LUẬT VỚI AGENTIC RAG

Trong chương này, em trình bày chi tiết các phương pháp và kiến trúc kỹ thuật được áp dụng để xây dựng hệ thống Vietnam Law Chatbot. Khác với chương 1 tập trung vào nền tảng lý thuyết, chương này đi sâu vào các quyết định thiết kế cụ thể, giải thích lý do lựa chọn từng kỹ thuật và mô tả chi tiết cách chúng được tích hợp thành một hệ thống thống nhất, đáp ứng yêu cầu đặc thù của domain pháp luật Việt Nam.

---

## 2.1. Kiến trúc tổng quan hệ thống Vietnam Law Chatbot

### 2.1.1. Lý do chọn kiến trúc Microservices

Hệ thống Vietnam Law Chatbot được thiết kế theo kiến trúc **Microservices** — mô hình tổ chức phần mềm trong đó ứng dụng được chia thành các dịch vụ nhỏ, độc lập, có thể triển khai và mở rộng riêng lẻ. Quyết định này xuất phát từ ba yêu cầu kỹ thuật cụ thể:

**Thứ nhất, tách biệt workload tính toán nặng.** Các pipeline AI trong hệ thống (embedding, cross-encoder reranking, LLM inference) đòi hỏi lượng CPU/RAM lớn và có độ trễ cao (thường từ 3–15 giây). Nếu tích hợp chung với API thông thường (đăng ký, đăng nhập, tra cứu), một yêu cầu AI nặng sẽ chiếm tài nguyên và làm ảnh hưởng đến toàn bộ hệ thống. Kiến trúc microservices giải quyết bằng cách tách lõi AI thành **RAG Service** (port 8001) hoàn toàn độc lập, có thể cấp phát tài nguyên riêng và scale theo chiều ngang nếu cần.

**Thứ hai, tối ưu hoá bảo mật.** RAG Service chứa các mô hình embedding và logic AI nhạy cảm — đây là "tài sản" kỹ thuật quan trọng. Bằng cách thiết kế RAG Service là **internal-only** (chỉ nhận kết nối từ Main Service thông qua API key nội bộ, không expose ra internet), hệ thống hạn chế bề mặt tấn công. Người dùng cuối không bao giờ giao tiếp trực tiếp với RAG Service.

**Thứ ba, khả năng phát triển độc lập.** Main Service (API thông thường) và RAG Service (AI pipeline) có nhịp độ thay đổi hoàn toàn khác nhau. Việc tách biệt cho phép nâng cấp mô hình AI, thay đổi prompt, điều chỉnh tham số retrieval mà không ảnh hưởng đến logic nghiệp vụ thông thường.

### 2.1.2. Tổng quan kiến trúc bốn lớp

[IMG:hinh_2_1.png]
*Hình 2.1. Kiến trúc tổng quan hệ thống Vietnam Law Chatbot*

Hệ thống tổ chức theo 4 lớp từ trên xuống dưới:

**Lớp giao diện người dùng (Frontend)**:
- **Mobile App** (Kotlin Multiplatform): ứng dụng dành cho người dùng cuối, chạy native trên cả Android và iOS từ một codebase chung. Giao tiếp với backend qua HTTPS/JWT và nhận streaming response qua SSE (Server-Sent Events).
- **Admin Web** (Next.js 16): dashboard quản trị cho admin hệ thống. Giao tiếp qua HTTPS/JWT và theo dõi tiến trình xử lý tài liệu qua WebSocket.

**Lớp dịch vụ backend**:
- **Main Service (port 8000)**: cửa ngõ duy nhất tiếp xúc với frontend. Đảm nhận xác thực, quản lý hội thoại, tra cứu luật, upload tài liệu và điều phối gọi sang RAG Service.
- **RAG Service (port 8001)**: nội bộ. Toàn bộ logic AI, embedding pipeline, Agentic RAG graph và document ingestion.

**Lớp dữ liệu** (3 cơ sở dữ liệu, phân tích chi tiết ở chương 3):
- PostgreSQL: dữ liệu quan hệ (người dùng, hội thoại, tin nhắn).
- MongoDB: kho văn bản pháp luật (528,620 điều luật).
- ChromaDB: kho vector embedding (690,360 chunks).

**Lớp dịch vụ bên ngoài**: LLM provider (suy luận ngôn ngữ và function calling), Tavily Search API (web search), Google Grounding API (real-time), Cloudinary (lưu trữ PDF).

Hình 2.1 thể hiện cách hệ thống phân tách trách nhiệm theo hướng "frontend không biết RAG Service". Mobile App và Admin Web chỉ giao tiếp với Main Service, còn Main Service đóng vai trò API gateway nghiệp vụ: xác thực người dùng, kiểm tra quyền, lưu lịch sử và chuyển tiếp các tác vụ AI sang RAG Service. Cách thiết kế này giúp frontend không phụ thuộc trực tiếp vào cấu trúc AI bên trong; nếu sau này thay đổi graph, thay đổi embedding model hoặc tách thêm worker xử lý tài liệu, contract phía client vẫn có thể giữ ổn định.

Một điểm quan trọng trong sơ đồ là lớp dữ liệu không được gom vào một database duy nhất. PostgreSQL phù hợp với dữ liệu quan hệ và transaction như người dùng, hội thoại, tin nhắn; MongoDB phù hợp với văn bản pháp luật dạng document dài, metadata linh hoạt; còn ChromaDB phục vụ riêng cho vector search. Việc chọn ba loại lưu trữ khác nhau làm hệ thống phức tạp hơn, nhưng đổi lại mỗi loại dữ liệu được đặt vào đúng công cụ của nó. Đây là một quyết định thiết kế có chủ ý, vì bài toán pháp luật vừa cần tính toàn vẹn dữ liệu người dùng, vừa cần lưu văn bản dài, vừa cần truy xuất ngữ nghĩa tốc độ cao.

Lớp dịch vụ bên ngoài được đặt ngoài biên hệ thống để nhấn mạnh rằng đây là các dependency có thể thay đổi. Hệ thống không gắn chặt logic nghiệp vụ vào một model LLM cụ thể; thay vào đó, phần gọi LLM được bọc trong `LLMService`. Tương tự, web search và cloud storage cũng là các dịch vụ được gọi qua adapter/service riêng. Cách làm này giúp đồ án có khả năng mở rộng: khi cần thay provider, chỉ cần thay lớp tích hợp thay vì viết lại toàn bộ Agent hoặc frontend.

### 2.1.3. Thành phần Main Service

[IMG:hinh_2_2.png]
*Hình 2.2. Sơ đồ thành phần Main Service*

Main Service được tổ chức theo kiến trúc 3 lớp chuẩn (Routes → Services → Repositories), sử dụng FastAPI với async/await và SQLAlchemy async:

**API Routes** (`/api/v1/`):
- `auth.py`: đăng ký, đăng nhập, refresh token, xem thông tin bản thân, đổi mật khẩu.
- `chat.py`: CRUD hội thoại (tạo, đổi tên, xoá, pin, archive), gửi tin nhắn (stream SSE), lấy gợi ý câu hỏi tiếp theo.
- `documents.py`: upload PDF, theo dõi task, WebSocket.
- `laws.py`: duyệt thư viện pháp luật, tìm kiếm theo topic/year/keyword, tìm kiếm AI ngữ nghĩa.
- `guided.py`: hai endpoint Guided Consultation (Clarify và Answer SSE).
- `dashboard.py`: thống kê tổng quan cho admin.

**Services**: `auth_service` (JWT + bcrypt), `chat_service` (proxy RAG + SSE bridge), `document_processor` (xử lý tài liệu với compensating transaction), `law_service` (MongoDB aggregation), `websocket_manager` (broadcast tiến trình), `rag_client` (gọi RAG Service qua httpx async).

**Repositories**: pattern Repository tách rời data access, giúp dễ test và thay thế nguồn dữ liệu. `user_repo`, `conversation_repo`, `message_repo`, `document_task_repo` tương tác với PostgreSQL qua SQLAlchemy async. `law_repo` tương tác với MongoDB qua Motor async.

Hình 2.2 có thể đọc từ trên xuống dưới theo các tầng trách nhiệm chính. Nhóm **API Routes** là lớp tiếp nhận request HTTP/WebSocket, chỉ nên làm nhiệm vụ parse input, gọi service phù hợp và chuẩn hóa response. Nhóm **Business Services** chứa logic nghiệp vụ thật sự: `chat_service` quyết định khi nào tạo conversation, khi nào lưu message, khi nào gọi RAG; `document_processor` điều phối OCR, lưu file, parse nội dung và cập nhật tiến trình; `rag_client` là cầu nối nội bộ sang RAG Service. Nhóm **Data Access** giúp phần service không phải biết chi tiết SQL/Mongo query, nhờ đó mỗi lớp có trách nhiệm rõ ràng.

Trong thiết kế này, Main Service đóng vai trò "điểm hội tụ" của các luồng nghiệp vụ. Luồng chat cần PostgreSQL để lưu hội thoại và RAG Service để trả lời; luồng thư viện pháp luật cần MongoDB để duyệt văn bản; luồng upload cần cả PostgreSQL để lưu task, MongoDB để lưu điều luật và RAG Service để ingest vector. Nếu để frontend gọi nhiều service riêng lẻ, client sẽ phải hiểu quá nhiều chi tiết nội bộ. Vì vậy Main Service gom các chi tiết này lại thành API ổn định hơn cho Mobile App và Admin Web.

### 2.1.4. Thành phần RAG Service

[IMG:hinh_2_3.png]
*Hình 2.3. Sơ đồ thành phần RAG Service*

RAG Service là "trái tim AI" của hệ thống, bảo vệ bởi middleware `X-API-Key`. Cấu trúc chính:

**API Routes**:
- `/rag/agent-search`: endpoint chạy Agentic RAG đầy đủ (4-node LangGraph).
- `/rag/search`: pipeline RAG truyền thống cho truy vấn đơn giản, low-latency.
- `/rag/guided-clarify` và `/rag/guided-answer/stream`: hai endpoint Guided Consultation ở tầng RAG Service.
- `/ingest/articles`: nhận articles từ Main Service để chunk, embed và lưu ChromaDB.

**Agent module**: `graph.py` định nghĩa `StateGraph` với 4 node. `nodes.py` chứa logic từng node. `state.py` định nghĩa `AgentState` (TypedDict). Module `guided_graph.py` + `guided_nodes.py` + `guided_state.py` định nghĩa graph riêng cho Guided Consultation.

**Tools**: `guardrail.py` kiểm soát đầu vào. `internal_law_tool.py` định nghĩa `@tool retrieve_internal_law()`. `web_search.py` định nghĩa `@tool search_web_for_law()`.

**Repositories (Singleton)**: `chroma_repo.py` quản lý kết nối ChromaDB dạng Singleton (khởi tạo một lần khi startup, tái sử dụng). `embedding_repo.py` tải và giữ hai mô hình `vietnamese-bi-encoder` và `ms-marco-MiniLM-L-6-v2` trong bộ nhớ — tải mô hình lần đầu mất ~30 giây, các request tiếp theo chỉ mất vài ms.

Hình 2.3 cho thấy RAG Service không chỉ là một endpoint sinh câu trả lời. Nó gồm ba khối chính: API nội bộ, Agent Graph và lớp tool/repository. API nội bộ nhận request đã được Main Service xác thực bằng `X-API-Key`; Agent Graph quyết định thứ tự kiểm tra, phân tích, gọi tool và kiểm chứng; còn tool/repository chịu trách nhiệm truy xuất dữ liệu thật. Cách tách này đặc biệt quan trọng trong hệ thống pháp luật vì LLM không được phép tự bịa dữ liệu: mọi câu trả lời phải đi qua tool để có căn cứ.

Việc dùng Singleton cho ChromaDB và embedding repository là tối ưu quan trọng về hiệu năng. Nếu mỗi request đều khởi tạo lại model embedding hoặc kết nối vector database, độ trễ sẽ tăng rất mạnh và có thể làm nghẽn tài nguyên. Thay vào đó, mô hình được tải một lần khi service khởi động, sau đó các request chỉ dùng lại object đã sẵn sàng trong bộ nhớ. Đây là lý do RAG Service được tách thành service riêng: nó có vòng đời và nhu cầu tài nguyên khác với API nghiệp vụ thông thường.

### 2.1.5. Kênh giao tiếp giữa các thành phần

**Bảng 2.1. Đặc tả các kênh giao tiếp trong hệ thống**

| Kênh | Từ | Đến | Giao thức | Xác thực | Ghi chú |
|---|---|---|---|---|---|
| Mobile → Main | Mobile App | Main Service | HTTPS REST + SSE | JWT Bearer | Access token 30 phút, tự refresh |
| Web → Main | Admin Web | Main Service | HTTPS REST + WebSocket | JWT Bearer | Cookie `admin_token` |
| Main → RAG | Main Service | RAG Service | HTTP nội bộ | `X-API-Key` header | Không expose ra internet |
| RAG → ChromaDB | RAG Service | ChromaDB | HTTP/Persistent client | Docker network | Vector search và lưu embeddings |
| Main → MongoDB | Main Service | MongoDB | Motor async | Không (Docker network) | Law browsing, articles |
| Main → PostgreSQL | Main Service | PostgreSQL | asyncpg | Không (Docker network) | Users, conversations, messages |
| RAG → LLM Provider | RAG Service | LLM API | HTTPS | API Key | Gọi thông qua lớp `LLMService`, có thể thay đổi provider/model bằng cấu hình |
| RAG → Tavily | RAG Service | Tavily API | HTTPS | API Key | Web search |

---

## 2.2. Xác định tính chất AI Agent

Từ kiến trúc tổng thể trên, thành phần cần phân tích sâu nhất là RAG Service, vì đây là nơi quyết định chất lượng tư vấn pháp luật. Trước khi thiết kế graph và prompt, em xác định rõ Agent sẽ hoạt động trong môi trường nào, có quyền làm gì, bị giới hạn bởi những nguồn dữ liệu nào và phải tuân thủ các nguyên tắc pháp lý nào. Đây là bước quan trọng theo phương pháp luận phát triển hệ thống AI Agent (theo Russell & Norvig, 2021).

### 2.2.1. Tính chất môi trường của Agent

**Bảng 2.2. Tính chất môi trường của Vietnam Law AI Agent**

| Tính chất | Phân loại | Giải thích |
|---|---|---|
| Khả năng quan sát | **Quan sát được một phần** (partially observable) | Agent không biết toàn bộ CSDL pháp luật — chỉ thấy kết quả từ tool trong mỗi vòng Re-Act |
| Tính xác định | **Ngẫu nhiên** (stochastic) | Cùng câu hỏi có thể cho kết quả khác nhau do LLM có tính ngẫu nhiên |
| Tính tuần tự | **Tuần tự** (sequential) | Câu trả lời hiện tại phụ thuộc vào lịch sử hội thoại trước đó |
| Thời gian | **Bán tĩnh** (semi-dynamic) | Dữ liệu pháp luật thay đổi chậm; Agent không thay đổi trong lúc người dùng suy nghĩ |
| Không gian hành động | **Rời rạc** (discrete) | Các action (tool calls) là rời rạc, có thể đếm được |
| Số tác nhân | **Một Agent** (single agent) | Một Agent duy nhất xử lý từng request độc lập |
| Môi trường | Người dùng (mobile/web) + CSDL pháp luật + Web search + LLM | Môi trường rộng, đa nguồn |

### 2.2.2. Đặc tả vai trò và phạm vi Agent

**Bảng 2.3. Định nghĩa vai trò và giới hạn hoạt động của Agent**

| Mục | Nội dung |
|---|---|
| **Vai trò** | Luật sư tư vấn pháp luật Việt Nam — tư vấn dựa trên văn bản quy phạm pháp luật, không đưa ra ý kiến pháp lý cá nhân |
| **Đối tượng phục vụ** | Người dân, doanh nghiệp, cán bộ pháp chế, sinh viên luật |
| **Phạm vi thẩm quyền** | Chỉ pháp luật Việt Nam (luật, nghị định, thông tư, quyết định) — từ chối domain khác (y tế, tài chính, kỹ thuật thuần túy) |
| **Giới hạn đạo đức** | Không tư vấn cách lách luật, trốn thuế, thực hiện hành vi bất hợp pháp |
| **Giới hạn kỹ thuật** | Dữ liệu nội bộ cập nhật đến năm 2026; với luật rất mới → dựa vào web search |
| **Tuyên bố miễn trừ** | Kết quả mang tính tham khảo; vụ việc phức tạp nên tham khảo luật sư chuyên môn |

### 2.2.3. Nguồn dữ liệu hỗ trợ Agent và hệ thống

**Bảng 2.4. Nguồn dữ liệu phục vụ Agent và các chức năng tra cứu**

| Nguồn | Loại | Cơ chế truy cập | Thế mạnh | Hạn chế |
|---|---|---|---|---|
| ChromaDB (CSDL nội bộ) | Vector DB | Tool `retrieve_internal_law` | Nguyên văn điều khoản đầy đủ, có cấu trúc | Không cập nhật real-time, cần re-ingest |
| MongoDB (articles) | Document DB | Đọc qua `law_service` ở Main Service | Full-text search, aggregation linh hoạt; phục vụ thư viện và chi tiết nguồn | Agent không truy cập trực tiếp trong graph |
| Tavily Search | Web search | Tool `search_web_for_law` | Real-time, ưu tiên domain gov.vn | Chỉ trả snippet, không toàn văn |
| Google Grounding | Web search | Tool `search_web_for_law` | Google index đầy đủ, real-time | Phụ thuộc kết quả Google |
| Lịch sử hội thoại | Context | Truyền trực tiếp qua messages | Hiểu context đa lượt | Bị giới hạn bởi context window LLM |

### 2.2.4. Tập hành động của Agent

Agent có 5 hành động chính, ánh xạ sang các tool call và quyết định nội tại:

1. **Tra cứu nội bộ** (`retrieve_internal_law`): tìm điều luật trong CSDL 528,620 articles.
2. **Tìm kiếm web** (`search_web_for_law`): lấy thông tin pháp luật real-time từ Tavily + Google.
3. **Sinh câu trả lời**: tổng hợp thông tin từ các tool, format câu trả lời có citation đầy đủ.
4. **Từ chối (Guardrail)**: nhận dạng câu hỏi off-topic hoặc vi phạm → trả về thông báo lịch sự.
5. **Lặp lại tra cứu** (Re-Act loop): nếu kết quả chưa đủ → tự sinh truy vấn phụ → gọi tool tiếp.

---

## 2.3. Luồng Agentic RAG — Đồ thị 4 Node LangGraph

Sau khi xác định vai trò, nguồn dữ liệu và tập hành động, bước tiếp theo là chuyển các yêu cầu đó thành một quy trình xử lý có thể triển khai được. Thay vì để LLM trả lời trực tiếp, hệ thống tổ chức quá trình suy luận thành một đồ thị có trạng thái, trong đó mỗi node đảm nhiệm một trách nhiệm riêng và kết quả của node trước trở thành đầu vào cho node sau.

Đây là trọng tâm kỹ thuật của đồ án. Toàn bộ pipeline chat AI được định nghĩa thành một **đồ thị có trạng thái** (stateful graph) bằng LangGraph với 4 node tuần tự và một vòng lặp.

### 2.3.1. Định nghĩa trạng thái Agent (AgentState)

Trạng thái (State) trong LangGraph là một TypedDict được chia sẻ giữa tất cả các node. Mỗi node đọc và cập nhật một phần của state. Dưới đây là `AgentState` của hệ thống:

```python
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Danh sách tin nhắn (user + assistant + tool results)
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Kết quả phân tích câu hỏi từ Node 2 (JSON string)
    query_analysis: str
    
    # Danh sách tài liệu đã retrieve (cho citation)
    retrieved_docs: list[dict]
    
    # Số vòng lặp Re-Act hiện tại (giới hạn max 6)
    iteration_count: int
    
    # Kết quả Guardrail
    is_valid_query: bool
    rejection_reason: str
```

**Bảng 2.5. Ý nghĩa từng trường trong AgentState**

| Trường | Kiểu | Cập nhật bởi | Mục đích |
|---|---|---|---|
| `messages` | `list[BaseMessage]` | Tất cả các node | Lưu toàn bộ lịch sử hội thoại + kết quả tool |
| `query_analysis` | `str` (JSON) | `query_analysis_node` | Truyền metadata phân tích sang `agent_node` |
| `retrieved_docs` | `list[dict]` | `agent_node` (qua tool) | Lưu tài liệu đã retrieve để Verifier đối chiếu |
| `iteration_count` | `int` | `agent_node` | Đếm số vòng Re-Act, dừng khi đạt giới hạn |
| `is_valid_query` | `bool` | `guardrail_node` | Flag để conditional edge bỏ qua các node tiếp theo |
| `rejection_reason` | `str` | `guardrail_node` | Lý do từ chối (ghi log + phản hồi người dùng) |

### 2.3.2. Cấu trúc đồ thị tổng quan

[IMG:hinh_2_4.png]
*Hình 2.4. Đồ thị Agentic RAG gồm 4 nút LangGraph*

```
START → guardrail_node → [REJECT → END]
                       → query_analysis_node → agent_node ⇄ tools
                                                     ↓ (final answer)
                                              verification_node → END
```

Đây là đồ thị **có chu kỳ** (cyclic graph) — điểm mà DAG (Directed Acyclic Graph) truyền thống không thể biểu diễn. Vòng lặp `agent_node ⇄ tools` chính là hiện thân của pattern Re-Act: Agent gọi tool → nhận Observation → quyết định gọi tiếp hay không.

Hình 2.4 được vẽ ở mức logic xử lý thay vì mức sequence request/response. Mục tiêu của hình là làm rõ thứ tự ra quyết định bên trong Agent: câu hỏi đi qua guardrail trước, sau đó được phân tích để tạo truy vấn tối ưu, rồi mới vào vòng Agent - Tools. Sau khi Agent cho rằng đã đủ bằng chứng để trả lời, câu trả lời không được trả ngay cho người dùng mà phải đi qua Verifier. Nhờ vậy, graph có hai lớp kiểm soát: kiểm soát đầu vào ở guardrail và kiểm soát đầu ra ở verifier.

Thiết kế này phù hợp với domain pháp luật hơn so với pipeline RAG tuyến tính thông thường. Với RAG tuyến tính, hệ thống thường chỉ retrieve một lần rồi sinh câu trả lời. Trong bài toán pháp luật, một lần retrieve có thể chưa đủ vì câu hỏi có thể cần cả nguyên văn điều luật nội bộ và thông tin cập nhật từ web. Vòng lặp Re-Act cho phép Agent chủ động gọi công cụ nhiều lần, nhưng vẫn bị giới hạn bởi `iteration_count` để tránh chạy vô hạn.

**Quy tắc chuyển trạng thái (Conditional Edges)**:
- Sau `guardrail_node`: nếu `is_valid_query = False` → kết thúc ngay (không lãng phí token). Nếu `True` → chuyển sang `query_analysis_node`.
- Trong `agent_node`: nếu LLM trả về `tool_calls` → LangGraph tự động gọi tool (qua `ToolNode`) và thêm kết quả vào `messages`. Nếu LLM trả về `AIMessage` thuần (không có `tool_calls`) → chuyển sang `verification_node`.
- Giới hạn vòng lặp: nếu `iteration_count ≥ 6` → bắt buộc chuyển sang `verification_node`.

### 2.3.3. Node 1 — Guardrail (Kiểm soát đầu vào)

**Mục đích**: bảo vệ hệ thống khỏi câu hỏi lạc đề (off-topic), prompt injection và nội dung vi phạm. Được đặt ở đầu pipeline để tiết kiệm chi phí token — chỉ mất ~100ms để từ chối thay vì chạy cả pipeline 4-15 giây.

**Prompt Guardrail** (trích từ source code `guardrail.py`):

```
Bạn là một bộ lọc kiểm duyệt cực kỳ nghiêm ngặt cho Hệ thống AI Tư vấn
Luật pháp Việt Nam. Nhiệm vụ của bạn là đánh giá câu hỏi đầu vào và quyết
định xem nó có hợp lệ để xử lý tiếp hay không.

Các nguyên tắc từ chối (REJECT):
1. Xúi giục vi phạm: Trốn thuế, lách luật mờ ám, tội phạm mạng, bạo lực,
   giết người, lừa đảo.
2. Chống phá: Xúc phạm chính quyền, nhà nước hoặc liên quan chính trị
   nhạy cảm.
3. Lạc đề (Out-of-domain): Câu hỏi không CÓ BẤT KỲ liên hệ nào tới luật
   pháp, quy định pháp lý, hành chính (VD: xin code python, giải toán,
   dịch tiếng Anh, tán gẫu đời sống).

Hãy chỉ trả về ĐÚNG MỘT TỪ:
- "PASS" nếu câu hỏi hợp lệ và thuộc phạm trù luật pháp, đời sống dân sự
  hành chính.
- "REJECT" nếu câu hỏi vi phạm các nguyên tắc trên hoặc hoàn toàn lạc đề.

Câu hỏi: {query}
```

**Cơ chế hoạt động**: Node gọi `check_guardrail(query)` → trả về `{"status": "PASS/REJECT", "reason": "..."}`. Nếu `REJECT`, node tự sinh `AIMessage` từ chối lịch sự và đặt `is_valid_query = False`. LangGraph conditional edge sẽ nhận thấy flag này và kết thúc graph ngay, không gọi các node tiếp theo.

**Bảng 2.6. State input/output của Guardrail Node**

| | Trường | Giá trị ví dụ |
|---|---|---|
| **Input** | `messages[-1].content` | "Vượt đèn đỏ phạt bao nhiêu?" |
| **Output (PASS)** | `is_valid_query = True` | — |
| **Output (REJECT)** | `is_valid_query = False` | — |
| | `rejection_reason` | "Câu hỏi nằm ngoài phạm vi tư vấn pháp luật" |
| | `messages` | `AIMessage("Là một trợ lý AI Tư vấn Pháp luật Việt Nam, tôi phải từ chối trả lời: ...")` |

**Ví dụ minh hoạ**: Câu hỏi *"Viết cho tôi một đoạn code Python sắp xếp mảng"* → Guardrail trả về `REJECT` ngay, hệ thống phản hồi trong ~100ms mà không tiêu tốn token cho pipeline AI.

### 2.3.4. Node 2 — Query Analysis (Phân tích và tái cấu trúc truy vấn)

**Mục đích**: Câu hỏi tự nhiên của người dùng thường chứa ngôn ngữ thông thường, thiếu thuật ngữ pháp lý chuẩn xác, hoặc đặt trong ngữ cảnh hội thoại nhiều lượt. Node này "dịch" câu hỏi sang ngôn ngữ phù hợp với từng hệ thống tìm kiếm.

**Prompt Query Analysis** (trích từ `llm_service.py`):

```
Bạn là chuyên gia phân tích pháp luật Việt Nam. Nhiệm vụ: Phân tích câu hỏi
pháp lý và tạo ra các truy vấn tìm kiếm TỐI ƯU cho 2 hệ thống khác nhau.

OUTPUT JSON BẮT BUỘC:
{
  "legal_topic": "Chủ đề pháp lý CỤ THỂ nhất",
  "legal_domain": "Lĩnh vực luật (Hình sự, Dân sự, Đất đai, ...)",
  "relevant_laws": ["Tên chính thức các luật có thể liên quan"],
  "internal_search_query": "Câu truy vấn TỐI ƯU cho vector search (≤15 từ,
    CHỈ thuật ngữ pháp lý cốt lõi, KHÔNG đưa số hiệu văn bản cụ thể)",
  "web_search_query": "Câu truy vấn tìm NỘI DUNG MỚI NHẤT trên web
    (kèm tên văn bản mới nhất nếu biết + số điều + 'mới nhất/năm hiện tại')",
  "key_legal_terms": ["Thuật ngữ pháp lý chuyên ngành quan trọng"],
  "analysis_summary": "Tóm tắt: người dùng cần biết gì, tra cứu phần nào"
}

QUY TẮC: internal_search_query dùng thuật ngữ mô tả NỘI DUNG cho vector
search. web_search_query PHẢI kèm tên văn bản MỚI NHẤT và năm để search
engine ưu tiên kết quả gần đây.
```

**Tại sao cần tách hai loại query?** Vector search (bi-encoder) hoạt động tốt nhất với **thuật ngữ pháp lý cốt lõi ngắn gọn** — vì mô hình được train để hiểu ngữ nghĩa pháp lý. Ngược lại, web search hoạt động tốt với **tên văn bản cụ thể + số điều + năm** để search engine xếp hạng ưu tiên. Dùng chung một câu hỏi tự nhiên cho cả hai sẽ cho kết quả kém hơn đáng kể.

**Ví dụ minh hoạ**:

Input: *"Tôi đi xe máy uống bia bị cảnh sát bắt thì bị phạt bao nhiêu tiền?"*

Output JSON:
```json
{
  "legal_topic": "Xử phạt vi phạm nồng độ cồn đối với xe mô tô, xe gắn máy",
  "legal_domain": "Hành chính - Giao thông đường bộ",
  "relevant_laws": ["Nghị định 168/2024/NĐ-CP", "Nghị định 100/2019/NĐ-CP"],
  "internal_search_query": "xử phạt nồng độ cồn xe mô tô xe gắn máy trừ điểm giấy phép lái xe",
  "web_search_query": "Nghị định 168/2024 Điều 7 mức phạt nồng độ cồn xe máy quy định mới nhất",
  "key_legal_terms": ["nồng độ cồn", "xe mô tô", "mức phạt tiền", "tước giấy phép lái xe", "trừ điểm"],
  "analysis_summary": "Cần tra cứu Điều 7 Nghị định 168/2024/NĐ-CP về xử phạt người điều khiển xe mô tô vi phạm nồng độ cồn"
}
```

Node sau đó đóng gói JSON này thành `SystemMessage` và thêm vào `messages`, kèm hướng dẫn cho Agent sử dụng chính xác các query đã tối ưu:

```
KẾT QUẢ PHÂN TÍCH CÂU HỎI PHÁP LÝ:
{analysis_json}

HƯỚNG DẪN SỬ DỤNG:
- Khi gọi retrieve_internal_law: SỬ DỤNG CHÍNH XÁC giá trị
  "internal_search_query" làm tham số query.
- Khi gọi search_web_for_law: SỬ DỤNG CHÍNH XÁC giá trị
  "web_search_query" làm tham số query.
- KHÔNG tự sáng tạo query khác. Các query trên đã được tối ưu
  cho từng hệ thống tìm kiếm.
```

**Bảng 2.7. State input/output của Query Analysis Node**

| | Trường | Giá trị ví dụ |
|---|---|---|
| **Input** | `messages[-1].content` | "Đi xe máy uống bia bị phạt bao nhiêu?" |
| **Input** | Chat history (optional) | 5-10 messages trước |
| **Output** | `query_analysis` | JSON string với 6 trường |
| **Output** | `messages` | Thêm `SystemMessage` chứa analysis |

### 2.3.5. Node 3 — Agent (Trung tâm suy luận — Re-Act loop)

[IMG:hinh_2_5.png]
*Hình 2.5. Vòng lặp Re-Act trong Node Agent*

Đây là node trung tâm, sử dụng **mô hình LLM được cấu hình cho Agent** với cơ chế **Function Calling** (gọi hàm). Agent được cung cấp hai công cụ và một system prompt chi tiết định nghĩa vai trò, quy tắc sử dụng tool, cách trình bày câu trả lời và các điều cấm tuyệt đối. Việc gọi model được đóng gói sau lớp `LLMService`, nhờ đó báo cáo tập trung vào phương pháp thiết kế Agent thay vì phụ thuộc vào tên một provider cụ thể.

**System Prompt của Agent** bao gồm 4 phần chính:

- **Phần A — Quy tắc sử dụng công cụ**: bắt buộc gọi `retrieve_internal_law` trước (tra cứu nguyên văn), sau đó **bắt buộc** gọi `search_web_for_law` để xác minh hiệu lực hiện hành. Thứ tự ưu tiên: kết quả web > dữ liệu nội bộ.

- **Phần B — Quy tắc trả lời theo hai trường hợp**:
  - TH1: Khi web xác nhận luật đã bị sửa đổi/thay thế → câu trả lời phải dựa vào quy định mới, kèm section so sánh quy định cũ với nhãn "(quy định cũ, đã hết hiệu lực)".
  - TH2: Khi web xác nhận luật vẫn còn hiệu lực → dựa vào nguyên văn nội bộ, xác nhận hiệu lực.

- **Phần C — Quy tắc trình bày**: ngôn ngữ trang trọng, xưng "tôi", gọi người dùng là "Anh/Chị". Không dùng từ kỹ thuật như "database", "tool", "retrieve". Phân biệt rõ nguồn trích dẫn.

- **Phần D — Cấm tuyệt đối**: không bịa số điều, không nội suy nội dung từ tên văn bản, không trộn con số từ hai văn bản khác nhau. Đây là bộ quy tắc chống hallucination tích hợp trực tiếp vào prompt.

**Cơ chế vòng lặp Re-Act**:

Như Hình 2.5 đã minh họa, trong mỗi vòng lặp:

Trong mỗi vòng lặp:
1. **Thought**: LLM phân tích messages hiện tại (bao gồm lịch sử hội thoại + kết quả tool từ các vòng trước) và quyết định action tiếp theo.
2. **Action**: LLM trả về `tool_calls` (danh sách công cụ cần gọi với tham số). LangGraph nhận và thực thi tool.
3. **Observation**: kết quả tool được thêm vào `messages` dưới dạng `ToolMessage`. Agent nhận observation này trong vòng lặp kế tiếp.
4. **Quyết định**: Agent đánh giá — đủ thông tin trả lời chưa? Nếu chưa → sinh thêm `tool_calls`. Nếu đủ → trả về `AIMessage` (câu trả lời).

Giới hạn `MAX_ITERATIONS = 6` ngăn vòng lặp vô hạn. Khi đạt giới hạn, agent bị chuyển ngay sang `verification_node` với những gì đang có.

**Bảng 2.8. State input/output của Agent Node**

| | Trường | Mô tả |
|---|---|---|
| **Input** | `messages` | Lịch sử + SystemMessage phân tích + kết quả tool cũ |
| **Input** | `iteration_count` | Số vòng lặp hiện tại |
| **Output (tiếp tục)** | `messages` | Thêm `AIMessage` với `tool_calls` |
| **Output (tiếp tục)** | `iteration_count` | Tăng 1 |
| **Output (kết thúc)** | `messages` | Thêm `AIMessage` câu trả lời (không có `tool_calls`) |

### 2.3.6. Node 4 — Verification (Kiểm chứng chống hallucination)

Trong đồ thị ở Hình 2.4, Verification Node nằm ở cuối pipeline:

**Mục đích**: Đây là tầng bảo vệ chống hallucination cuối cùng trước khi trả về người dùng. Node sử dụng mô hình được cấu hình qua `verifier_model` để kiểm chứng độc lập câu trả lời của Agent. Thiết kế này tách vai trò "sinh câu trả lời" và "kiểm chứng câu trả lời" thành hai bước khác nhau; tuỳ môi trường triển khai có thể cấu hình verifier bằng model mạnh hơn để ưu tiên chất lượng, hoặc model nhẹ hơn để giảm độ trễ và chi phí.

**Cơ chế kiểm chứng**: Node trích xuất câu trả lời cuối cùng của Agent (AIMessage không có `tool_calls`), thu thập tất cả kết quả tool (ToolMessage), sau đó gọi verifier model với một prompt đặc biệt:

**Verification Prompt** (trích từ `nodes.py`):

```
Kiểm tra câu trả lời pháp luật có bịa đặt không.

KIỂM TRA mỗi trích dẫn pháp luật:
1. Số hiệu (Điều/Khoản/Điểm, tên văn bản) → có trong nguồn tra cứu không?
2. NỘI DUNG chi tiết → có nguyên văn/tương đương trong nguồn không?
3. KIỂM TRA TỪNG CON SỐ (cực kỳ quan trọng): Quét câu trả lời tìm MỌI
   con số — mức phạt tiền, thời hạn tước GPLX, số điểm trừ. Với MỖI con số:
   tìm chính xác trong KẾT QUẢ TRA CỨU. Nếu KHÔNG tìm thấy → BỊA ĐẶT.
4. VĂN BẢN CŨ/MỚI: Con số từ văn bản ⛔ CHỈ được phép xuất hiện trong
   section "SO SÁNH VỚI QUY ĐỊNH CŨ" với nhãn "(quy định cũ, đã hết hiệu lực)".
5. CẤM TRỘN ĐIỀU KHOẢN: Nhiều hình phạt trong một điều khoản → từng
   hình phạt phải có trong cùng điều khoản đó trong kết quả tra cứu.

XỬ LÝ:
- PASS → corrected_answer = "SAME"
- FAIL → corrected_answer = câu trả lời gốc nhưng XÓA các đoạn bịa đặt,
  giữ nguyên phần đúng. KHÔNG viết thêm nội dung mới.

JSON output: {"verdict":"PASS/FAIL","issues":["..."],"corrected_answer":"..."}
```

**Ưu điểm của thiết kế này**: Verifier không cần viết lại câu trả lời từ đầu (tiết kiệm token) — chỉ xóa các phần không có căn cứ. Nếu `verdict = PASS`, trả về câu trả lời gốc nguyên vẹn. Nếu `FAIL`, chỉ loại bỏ phần hallucinate. Cách tiếp cận "minimal correction" này nhanh hơn và giảm nguy cơ Verifier tự ý thêm thông tin sai.

**Bảng 2.9. State input/output của Verification Node**

| | Trường | Mô tả |
|---|---|---|
| **Input** | Agent's final AIMessage | Câu trả lời cần kiểm chứng |
| **Input** | Tất cả ToolMessages | Bằng chứng từ các tool (nguồn sự thật) |
| **Output (PASS)** | `messages` | AIMessage gốc không thay đổi |
| **Output (FAIL)** | `messages` | AIMessage đã sửa (loại bỏ phần hallucinate) |

---

## 2.4. Hai công cụ (Tools) của Agent

Trong graph ở mục 2.3, Agent chỉ có thể trả lời chính xác nếu được cấp quyền truy cập vào nguồn tri thức đáng tin cậy. Vì vậy, hệ thống giới hạn Agent trong hai công cụ chính: một công cụ tra cứu cơ sở dữ liệu nội bộ để lấy nguyên văn điều luật, và một công cụ tìm kiếm web để kiểm tra thông tin mới nhất.

### 2.4.1. Tool 1 — retrieve_internal_law

Công cụ tra cứu CSDL pháp luật nội bộ với pipeline truy xuất 2 giai đoạn.

**Đặc tả công cụ**:

```python
@tool
def retrieve_internal_law(query: str) -> str:
    """
    Tra cứu CSDL pháp luật nội bộ. Sử dụng query từ trường
    'internal_search_query' trong kết quả phân tích câu hỏi.
    Trả về danh sách điều luật phù hợp nhất kèm citation đầy đủ.
    """
```

**Tham số**: `query` — câu truy vấn tối ưu từ `query_analysis_node`, tối đa 15 từ, chứa thuật ngữ pháp lý cốt lõi.

**Pipeline xử lý nội bộ** (mô tả chi tiết tại mục 2.5):

[IMG:hinh_2_6.png]
*Hình 2.6. Pipeline truy xuất hai giai đoạn*

1. Mã hoá `query` bằng bi-encoder → vector 768 chiều.
2. ChromaDB cosine similarity search → top-60 chunks.
3. Cross-encoder rerank (`ms-marco-MiniLM-L-6-v2`) → blended score.
4. Year boost → ưu tiên văn bản mới.
5. Temporal Conflict Resolution → đánh dấu ⛔/✅.
6. Trả về top-10 kết quả liên quan nhất dưới dạng text có cấu trúc.

**Ví dụ output** của tool (dạng text trả về cho Agent):

```
[TÀI LIỆU 1 - Score: 0.92 - law_id: 168/2024/nd-cp - Năm: 2024] ✅
Tiêu đề: Điều 7. Xử phạt người điều khiển xe mô tô, xe gắn máy...
Nội dung: [trích đoạn nguyên văn điều khoản liên quan đến hành vi,
mức xử phạt và hình thức xử phạt bổ sung nếu có]

[TÀI LIỆU 2 - Score: 0.78 - law_id: 100/2019/nd-cp - Năm: 2019] ⛔
Tiêu đề: Điều 7. Xử phạt người điều khiển xe mô tô...
Nội dung: [trích đoạn quy định cũ có cùng chủ đề]
[ĐÃ BỊ THAY THẾ bởi Nghị định 168/2024/NĐ-CP]
```

### 2.4.2. Tool 2 — search_web_for_law

Công cụ tìm kiếm web real-time, kết hợp hai nguồn để tối đa độ phủ.

**Đặc tả công cụ**:

```python
@tool
def search_web_for_law(query: str) -> str:
    """
    Tìm kiếm thông tin pháp luật real-time từ web. Sử dụng query từ
    trường 'web_search_query' trong kết quả phân tích câu hỏi.
    Kết hợp Tavily Search (ưu tiên domain pháp luật) và Google Grounding.
    """
```

**Cơ chế hai nguồn**:

*(1) Tavily Search API* — tìm kiếm deep web với cấu hình:
- `search_depth = "advanced"`: Tavily thu thập nội dung chi tiết thay vì chỉ snippet.
- `include_domains`: ưu tiên domain pháp luật chính thức Việt Nam: `*.gov.vn`, `chinhphu.vn`, `quochoi.vn`, `thuvienphapluat.vn`, `luatvietnam.vn`, `moj.gov.vn`.
- Kết quả: nội dung đầy đủ hơn, độ tin cậy cao hơn.

*(2) Google Grounding API* — lấy nguồn Google Search:
- Ưu điểm: Google index đầy đủ và real-time nhất, không bị giới hạn domain.
- Bổ sung các trang pháp luật chưa có trong Tavily index.

**Kết hợp song song**: cả hai nguồn được gọi đồng thời qua `ThreadPoolExecutor` để giảm latency:

```python
with ThreadPoolExecutor(max_workers=2) as executor:
    tavily_future = executor.submit(search_tavily, query)
    google_future = executor.submit(search_google_grounding, query)
    tavily_result = tavily_future.result()
    google_result = google_future.result()
```

Kết quả từ hai nguồn được ghép lại và format thành text trả về cho Agent, trong đó phần Google Grounding thường được ưu tiên đặt trước vì có tính thời gian thực cao hơn.

**Bảng 2.10. So sánh hai nguồn web search**

| Tiêu chí | Tavily Search | Google Grounding |
|---|---|---|
| Phủ domain | Ưu tiên gov.vn, luatvietnam.vn | Toàn bộ Google index |
| Độ sâu nội dung | Full text (advanced mode) | Snippet |
| Real-time | Index theo giờ | Real-time gần nhất |
| Chi phí | Theo query | Theo provider grounding được cấu hình |
| Điểm mạnh | Văn bản pháp luật đầy đủ | Tin tức luật mới nhất |

---

## 2.5. Tối ưu RAG Pipeline — Truy xuất 2 Giai đoạn

Pipeline tổng quan đã được minh họa ở Hình 2.6.

Hai công cụ của Agent chỉ là giao diện ở mức cao; phần quyết định chất lượng tìm kiếm nằm ở pipeline truy xuất bên dưới. Đối với kho dữ liệu 690,360 vector chunks, hệ thống không thể dùng LLM đọc toàn bộ dữ liệu, cũng không thể chỉ tìm kiếm từ khóa đơn giản. Vì vậy, đồ án sử dụng chiến lược truy xuất hai giai đoạn để cân bằng giữa tốc độ và độ chính xác.

Hình 2.6 mô tả pipeline tìm kiếm theo hướng "lọc rộng trước, chấm sâu sau". Ở đầu pipeline, hệ thống dùng vector search để thu hẹp không gian tìm kiếm từ hàng trăm nghìn chunks xuống một tập ứng viên đủ nhỏ. Sau đó cross-encoder rerank lại tập ứng viên này để tăng độ chính xác trước khi đưa vào Agent. Bước conflict check và threshold ở cuối giúp đảm bảo các nguồn được đưa vào câu trả lời không chỉ liên quan về mặt ngữ nghĩa mà còn đủ tin cậy để trích dẫn.

Điểm quan trọng của thiết kế này là không để LLM quyết định toàn bộ việc tìm nguồn. LLM có khả năng diễn giải tốt nhưng không phù hợp để tự tìm kiếm trong kho dữ liệu lớn. Ngược lại, vector database và reranker làm tốt nhiệm vụ chọn candidate nhưng không tự giải thích pháp luật cho người dùng. Pipeline hai giai đoạn kết hợp ưu điểm của cả hai nhóm kỹ thuật: retrieval chịu trách nhiệm tìm bằng chứng, còn Agent chịu trách nhiệm suy luận và trình bày câu trả lời trên bằng chứng đó.

### 2.5.1. Hạn chế của Bi-encoder đơn độc

Bi-encoder (mô hình mã hoá hai chiều như `vietnamese-bi-encoder`) mã hoá query và document **độc lập** thành vector, sau đó tính cosine similarity. Cách tiếp cận này có ưu điểm lớn về tốc độ — mã hoá toàn bộ 690,360 chunks một lần, lưu vào ChromaDB, và query chỉ cần mã hoá query vector rồi tìm nearest neighbors trong O(log N) thời gian.

Tuy nhiên, bi-encoder có hạn chế: vì mã hoá **độc lập**, nó không bắt được sự tương tác tinh tế giữa từ trong query và từ trong document. Ví dụ, với query *"thủ tục đăng ký kết hôn người nước ngoài"*, bi-encoder có thể trả về các chunks về "đăng ký kết hôn" chung chung (liên quan về topic) mà bỏ sót chunks quan trọng về "người nước ngoài" (liên quan về ngữ nghĩa phức tạp hơn).

### 2.5.2. Cross-encoder Reranking

Cross-encoder (`ms-marco-MiniLM-L-6-v2`) chấm điểm từng **cặp (query, document)** — tức là query và document được concatenate và đưa vào cùng một transformer, cho phép mô hình bắt được tương tác tinh tế giữa chúng. Điểm số cao hơn đáng kể về chất lượng so với bi-encoder, nhưng chậm hơn nhiều vì phải chạy forward pass cho từng cặp.

**Chiến lược Two-Stage** giải quyết trade-off:
- **Giai đoạn 1 (Bi-encoder)**: nhanh, lọc từ 690,360 chunks xuống còn top-60 (`VECTOR_SEARCH_TOP_K = 60`). Chấp nhận một số false positive.
- **Giai đoạn 2 (Cross-encoder)**: chậm nhưng chính xác, chỉ cần xử lý tối đa 40 cặp (`ROUND2_CANDIDATES = 40`) thay vì toàn bộ 690,360 chunks. Loại bỏ false positive từ giai đoạn 1.

Việc chọn top-60 ở giai đoạn vector search và rerank tối đa 40 candidate là điểm cân bằng giữa chất lượng và độ trễ. Nếu lấy quá ít candidate, hệ thống có nguy cơ bỏ sót điều luật đúng ngay từ bước đầu; nếu lấy quá nhiều, cross-encoder sẽ làm tăng thời gian xử lý và ảnh hưởng trực tiếp tới trải nghiệm chat. Qua thiết kế này, vector search đóng vai trò "recall cao", còn cross-encoder đóng vai trò "precision cao".

### 2.5.3. Công thức Blended Score

Điểm số cuối cùng kết hợp cả hai nguồn:

$$\text{FinalScore} = 0.3 \times \text{BiEncoderScore} + 0.7 \times \text{CrossEncoderScore}$$

Trọng số 0.7 cho cross-encoder phản ánh độ tin cậy cao hơn của mô hình này. Bi-encoder với trọng số 0.3 đóng vai trò "neo" — đảm bảo các kết quả có semantic similarity cao không bị cross-encoder loại bỏ hoàn toàn nếu scoring lệch.

### 2.5.4. Year Boost — Ưu tiên văn bản mới

Đặc thù pháp luật Việt Nam: các nghị định, thông tư thường xuyên được thay thế bởi văn bản mới. Nếu chỉ dùng semantic similarity, hai văn bản về cùng chủ đề (ví dụ Nghị định 100/2019 và Nghị định 168/2024 về xử phạt giao thông) sẽ có score tương đương nhau. Year boost cộng thêm điểm để ưu tiên văn bản mới:

**Bảng 2.11. Tham số Year Boost**

| Độ mới văn bản | Điểm cộng thêm |
|---|---|
| 0-2 năm gần nhất | +0.05 |
| 3-5 năm gần nhất | +0.02 |
| 6-10 năm | 0.00 (không điều chỉnh) |
| Trên 10 năm | -0.03 |

### 2.5.5. Temporal Conflict Resolution — Giải quyết mâu thuẫn pháp lý

[IMG:hinh_2_7.png]
*Hình 2.7. Thuật toán phát hiện xung đột văn bản cũ và mới*

Đây là **tính năng đặc trưng** của hệ thống, giải quyết vấn đề đặc thù của pháp luật Việt Nam: cùng một quy định pháp luật nhưng có nhiều văn bản ở các năm khác nhau — và thông thường văn bản mới sẽ bãi bỏ (thay thế) văn bản cũ.

**Ví dụ thực tế**: Nghị định 100/2019/NĐ-CP và Nghị định 168/2024/NĐ-CP đều quy định mức xử phạt vi phạm giao thông. Nếu không có cơ chế xử lý, Agent sẽ nhận được cả hai kết quả và có thể nhầm lẫn áp dụng mức phạt của nghị định cũ đã hết hiệu lực.

**Thuật toán**:

1. Nhóm các kết quả top-N theo loại văn bản/suffix của `law_id` và topic chính trong metadata.
2. Với mỗi nhóm: nếu có ≥ 2 kết quả từ các năm khác nhau → phát hiện xung đột.
3. Trong nhóm xung đột: tìm `max(year)` → đánh dấu ✅ (còn hiệu lực).
4. Các kết quả còn lại trong nhóm → đánh dấu ⛔ (đã bị thay thế) kèm ghi chú.
5. Context được trả về cho Agent đã có nhãn rõ ràng → Agent và Verifier đều biết không dùng con số từ văn bản ⛔.

**Tác động**: Agent System Prompt có quy tắc cứng: *"Khi có văn bản ⛔ và ✅ cùng chủ đề, câu trả lời PHẢI dựa CHỦ YẾU vào quy định MỚI"*. Verifier kiểm tra lại: *"Con số từ văn bản ⛔ CHỈ được phép xuất hiện trong section 'SO SÁNH VỚI QUY ĐỊNH CŨ'"*. Hai lớp kiểm soát này đảm bảo người dùng không bao giờ nhận được thông tin về luật đã hết hiệu lực mà không được cảnh báo rõ ràng.

Hình 2.7 cũng cho thấy lý do không nên chỉ sắp xếp kết quả theo score. Một văn bản cũ có thể có nội dung gần giống câu hỏi hơn vì được diễn đạt trực tiếp, trong khi văn bản mới có thể dùng thuật ngữ khác hoặc cấu trúc khác. Nếu chỉ dùng semantic score, Agent có thể ưu tiên sai văn bản. Temporal Conflict Resolution bổ sung tri thức thời gian vào pipeline retrieval, giúp kết quả phù hợp hơn với bản chất "luật hiện hành" của bài toán.

### 2.5.6. Ngưỡng tin cậy (Confidence Thresholds)

**Bảng 2.12. Các ngưỡng tin cậy trong pipeline retrieval**

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `VECTOR_SEARCH_TOP_K` | 60 | Số kết quả từ ChromaDB đưa vào cross-encoder |
| `ROUND2_CANDIDATES` | 40 | Số candidate tối đa được cross-encoder rerank |
| `SCORE_THRESHOLD_DISPLAY` | 0.60 | Ngưỡng tối thiểu để kết quả xuất hiện làm "nguồn" cho người dùng |
| `SCORE_THRESHOLD_GENERATION` | 0.75 | Ngưỡng để LLM được phép sinh câu trả lời chuyên sâu |
| `METADATA_FILTER_LIMIT` | 200 | Số candidate sau metadata filter (Simple RAG mode) |

---

## 2.6. Luồng Tư vấn có Hướng dẫn (Guided Consultation)

[IMG:hinh_2_8.png]
*Hình 2.8. Luồng tư vấn có hướng dẫn gồm hai bước*

Agentic RAG phù hợp với các câu hỏi đầy đủ ngữ cảnh, nhưng nhiều câu hỏi pháp luật trong thực tế lại rất ngắn và thiếu thông tin quyết định. Vì vậy, ngoài chế độ chat tự do, hệ thống bổ sung một luồng tư vấn có hướng dẫn để chủ động hỏi lại người dùng trước khi tra cứu.

Hình 2.8 mô tả luồng Guided Consultation theo dạng pipeline nghiệp vụ. Khác với sơ đồ tuần tự, hình này không tập trung vào từng request giữa client và server, mà nhấn mạnh sự biến đổi của thông tin: từ câu hỏi ban đầu còn thiếu ngữ cảnh, hệ thống tạo câu hỏi làm rõ, người dùng bổ sung thông tin, sau đó backend mới lập kế hoạch tra cứu và tạo câu trả lời. Cách trình bày này phù hợp với Chương 2 vì chương này cần giải thích phương pháp thiết kế, còn các chi tiết request/response tuần tự sẽ được trình bày ở chương thiết kế.

### 2.6.1. Vấn đề và động lực thiết kế

Trong domain pháp luật, câu hỏi của người dùng thường thiếu ngữ cảnh quan trọng. Ví dụ: *"Vượt đèn đỏ phạt bao nhiêu?"* — câu trả lời phụ thuộc hoàn toàn vào **loại phương tiện** (ô tô, xe máy, xe đạp điện, xe đạp — mức phạt khác nhau hàng triệu đồng). Nếu để Agentic RAG xử lý trực tiếp, có hai vấn đề:

1. Agent sẽ phải trả lời tất cả các trường hợp → câu trả lời quá dài, khó theo dõi.
2. Hoặc Agent sẽ hỏi lại bằng text thuần → UX kém, không có giao diện trắc nghiệm trực quan.

Guided Consultation giải quyết bằng một quy trình **2 bước có cấu trúc**: trước tiên thu thập đủ ngữ cảnh (với giao diện trắc nghiệm trực quan), sau đó mới chạy pipeline AI với thông tin đầy đủ.

Về mặt trải nghiệm, guided consultation biến một câu hỏi mơ hồ thành một bài tư vấn có ngữ cảnh. Người dùng không cần biết phải tự cung cấp thông tin pháp lý nào; hệ thống chủ động hỏi lại bằng các lựa chọn cụ thể. Điều này đặc biệt hữu ích với người dùng phổ thông, vì họ thường không biết rằng cùng một hành vi có thể có mức phạt khác nhau theo phương tiện, độ tuổi, vai trò, địa điểm hoặc tình trạng giấy tờ.

Về mặt kỹ thuật, bước clarify cũng giúp giảm rủi ro hallucination. Nếu câu hỏi thiếu dữ kiện, Agentic RAG buộc phải suy đoán hoặc trả lời quá rộng. Khi guided flow đã thu thập dữ kiện chính, câu hỏi gửi sang Agent trở nên cụ thể hơn, retrieval query chính xác hơn và verifier có phạm vi kiểm chứng rõ hơn.

### 2.6.2. Kiến trúc Stateless

Guided Consultation được thiết kế **stateless** (không lưu lịch sử trên server). Toàn bộ ngữ cảnh (câu hỏi gốc + lựa chọn của người dùng) được truyền đầy đủ trong request của Bước 2. Thiết kế này giúp:
- Đơn giản hoá backend — không cần session management.
- Dễ retry nếu mạng gián đoạn.
- Mỗi request Bước 2 là độc lập, có thể scale ngang dễ dàng.

Thiết kế stateless cũng giúp tránh nhầm lẫn giữa nhiều phiên tư vấn. Nếu server lưu trạng thái tạm cho từng người dùng, backend phải quản lý timeout, session bị mất, người dùng đổi thiết bị hoặc mở nhiều tab. Trong đồ án này, lựa chọn stateless làm payload dài hơn một chút nhưng đổi lại dễ kiểm thử và dễ mở rộng. Mỗi lần gọi `answer/stream`, request đã chứa đủ `original_query`, `detected_topic` và danh sách câu trả lời làm rõ, nên RAG Service có thể xử lý độc lập.

### 2.6.3. Bước 1 — Clarify (Thu thập ngữ cảnh)

**Endpoint**: `POST /api/v1/guided/clarify`

**Input**: `{ "query": "Vượt đèn đỏ phạt bao nhiêu?" }`

**Xử lý**: Main Service forward sang RAG Service. RAG Service gọi LLM qua `LLMService` với prompt phân tích: *"Với câu hỏi pháp luật này, cần thêm thông tin gì để trả lời chính xác?"* Kết quả là danh sách câu hỏi trắc nghiệm dưới dạng JSON.

**Output**:
```json
{
  "detected_topic": "Giao thông đường bộ",
  "clarify_questions": [
    {
      "question": "Bạn điều khiển phương tiện gì?",
      "options": ["Ô tô", "Xe máy", "Xe đạp điện", "Xe đạp"]
    }
  ]
}
```

Mobile App nhận kết quả và render giao diện trắc nghiệm — người dùng chọn một hoặc nhiều đáp án. App thu thập lựa chọn thành `clarify_context` (ví dụ: `"Phương tiện: Xe máy"`).

Ở bước này, hệ thống chỉ tạo câu hỏi làm rõ, chưa đưa ra tư vấn pháp lý cuối cùng. Đây là một ranh giới quan trọng: câu hỏi làm rõ có thể được sinh nhanh, ít nguồn dữ liệu hơn, còn câu trả lời pháp lý cuối cùng bắt buộc phải qua retrieval và verifier. Cách tách này giúp UI phản hồi nhanh ở bước đầu, đồng thời vẫn giữ tiêu chuẩn chính xác cho kết quả tư vấn.

### 2.6.4. Bước 2 — Answer (Lập kế hoạch và Trả lời SSE)

**Endpoint**: `POST /api/v1/guided/answer/stream` (SSE streaming)

**Input**:
```json
{
  "original_query": "Vượt đèn đỏ phạt bao nhiêu?",
  "detected_topic": "Giao thông đường bộ",
  "clarify_context": "Phương tiện: Xe máy"
}
```

**Guided Graph** (khác với Agentic RAG graph):

```
START → planning_node → agent_node ↔ tools_node → verification_node → END
```

**Planning Node (Deterministic — Không dùng LLM)**: đây là điểm khác biệt quan trọng so với Agentic RAG thông thường. Planning Node là thuần xử lý logic — ghép `original_query + clarify_context + detected_topic` thành một retrieval plan có cấu trúc tối ưu mà không cần gọi LLM. Lý do:
- Tiết kiệm token (một vòng gọi LLM ít).
- Giảm latency thêm 1-2 giây.
- Khi đã có structured input (câu hỏi + context đầy đủ), không cần LLM để "lập kế hoạch" — thuật toán tiền định đủ hiệu quả.

**Agent Node và Verification Node**: tương tự như trong Agentic RAG graph nhưng với system prompt được điều chỉnh: *"Bạn đã biết đầy đủ ngữ cảnh từ người dùng — tập trung vào câu hỏi cụ thể thay vì câu hỏi tổng quát"*.

Ví dụ với câu hỏi ban đầu *"Vượt đèn đỏ phạt bao nhiêu?"*, nếu người dùng chọn "Xe máy", Planning Node có thể tạo truy vấn nội bộ tập trung vào mức phạt xe mô tô/xe gắn máy, đồng thời tạo truy vấn web kiểm tra nghị định hiện hành liên quan. Như vậy, Agent không cần trả lời cả ô tô, xe máy, xe đạp điện và xe đạp trong cùng một câu trả lời. Kết quả cuối cùng ngắn hơn, đúng ngữ cảnh hơn và dễ đọc hơn trên màn hình mobile.

Một tối ưu khác là Guided Graph không có guardrail riêng ở bước answer. Việc phân loại câu hỏi đã được thực hiện ở bước clarify; nếu câu hỏi không thuộc phạm vi pháp luật hoặc vi phạm chính sách, hệ thống có thể dừng ngay từ đầu. Do đó, bước answer tập trung vào lập kế hoạch, truy xuất và kiểm chứng, tránh lặp lại cùng một logic kiểm tra.

### 2.6.5. Cơ chế SSE Streaming

*(Chi tiết SSE client trên mobile xem mục _Frontend_Overview.md)*

Bước 2 trả về SSE stream với 3 loại event chính:

**Bảng 2.13. Các loại SSE event trong Guided Consultation**

| Event | Payload | Ý nghĩa |
|---|---|---|
| `progress` | `{"steps": [...]}` | Cập nhật ThinkingPanel theo các bước: chuẩn bị tra cứu, tra cứu nguồn, tổng hợp, kiểm chứng |
| `done` | `{"answer": "...", "sources": [...], "processing_time": ...}` | Kết thúc pipeline, trả câu trả lời cuối cùng và nguồn trích dẫn |
| `error` | `{"message": "..."}` | Thông báo lỗi khi RAG Service hoặc pipeline trả lời thất bại |

Mobile App nhận stream và cập nhật ThinkingPanel theo từng trạng thái xử lý. Khi nhận `done`, ứng dụng hiển thị câu trả lời hoàn chỉnh cùng danh sách nguồn. Thiết kế này minh bạch hơn so với loading spinner vì người dùng thấy hệ thống đang tra cứu và kiểm chứng, nhưng vẫn giữ response contract đơn giản: câu trả lời pháp lý chỉ được hiển thị sau khi đã qua verifier.

Trong quá trình streaming, các bước hiển thị cho người dùng được cố định ở mức dễ hiểu như "đang chuẩn bị tra cứu", "đang tra cứu nguồn", "đang tổng hợp" và "đang kiểm tra độ chính xác". Đây là cách che bớt chi tiết kỹ thuật của LangGraph nhưng vẫn tạo cảm giác minh bạch. Người dùng không cần biết node nào đang chạy, nhưng họ biết hệ thống không chỉ trả lời cảm tính mà đang đi qua các bước kiểm tra nguồn.

---

## 2.7. Pipeline Document Ingestion

[IMG:hinh_2_9.png]
*Hình 2.9. Pipeline Document Ingestion với Compensating Transaction*

Chất lượng tư vấn phụ thuộc trực tiếp vào chất lượng kho dữ liệu pháp luật. Vì vậy, ngoài việc xây dựng pipeline trả lời, hệ thống còn cần một phương pháp cập nhật dữ liệu mới từ tài liệu PDF, chuẩn hóa thành điều luật có cấu trúc và đồng bộ vào cả MongoDB lẫn ChromaDB.

Hình 2.9 mô tả luồng cập nhật văn bản mới theo hướng từ trái sang phải. Sơ đồ bắt đầu ở Admin Web, đi qua Main Service để tạo task, sau đó vào Document Processor để trích xuất và cấu trúc hóa nội dung, cuối cùng đồng bộ sang MongoDB và ChromaDB. Điểm cuối của sơ đồ là trạng thái task được trả về qua WebSocket. Như vậy, hình không chỉ thể hiện pipeline xử lý file, mà còn thể hiện cách backend giữ cho admin luôn biết tiến trình xử lý đang ở bước nào.

### 2.7.1. Tổng quan quy trình

Hệ thống cho phép Admin upload các văn bản pháp luật dưới dạng PDF để tự động parse thành điều luật có cấu trúc và đưa vào CSDL. Quy trình được thiết kế để **không chặn** — Admin nhận `task_id` ngay lập tức và theo dõi tiến trình qua WebSocket; xử lý thực tế diễn ra ở background.

**Các bước tổng quan**:
1. Admin upload file PDF qua form drag-and-drop trên Admin Web.
2. Main Service nhận file, tạo `DocumentTask` với `status = PENDING`, trả về `task_id` (202 Accepted).
3. Spawn background async task (`asyncio.create_task`).
4. Background task chạy `DocumentProcessor.process_from_upload()`.
5. WebSocket broadcast tiến trình theo từng bước.

Trong implementation hiện tại, endpoint chính là `/api/v1/documents/upload-v2`. Endpoint này không đợi xử lý xong mới phản hồi toàn bộ kết quả, mà tạo `DocumentTask` ngay từ đầu để admin có thể theo dõi. Đây là điểm quan trọng với tài liệu pháp luật vì một file PDF có thể mất từ vài chục giây đến vài phút để OCR, cấu trúc hóa, lưu MongoDB và ingest vector.

Trước khi chạy pipeline nặng, hệ thống có hai lớp pre-check:

- **Hash check**: tính SHA-256 của file để phát hiện upload lại đúng cùng một file.
- **Quick pre-check**: đọc một phần đầu tài liệu để nhận diện có phải văn bản pháp luật Việt Nam không và trích xuất nhanh `law_id`. Nếu `law_id` đã tồn tại, hệ thống trả `409 Conflict` sớm thay vì tốn thời gian parse toàn bộ văn bản.

Nhờ vậy, luồng cập nhật dữ liệu phía admin không chỉ tự động hóa việc thêm văn bản mới, mà còn giảm nguy cơ làm bẩn kho dữ liệu do upload nhầm tài liệu hoặc upload trùng văn bản đã có.

Thiết kế pre-check có ý nghĩa lớn trong vận hành thực tế. Nếu không có bước này, mỗi lần admin upload nhầm một file đã tồn tại, hệ thống vẫn phải OCR, gọi LLM, parse JSON và ingest vector rồi mới phát hiện trùng. Với các văn bản dài, chi phí xử lý này không nhỏ. Pre-check giúp chặn lỗi càng sớm càng tốt: hash check bắt trường hợp file giống hệt, còn quick law_id check bắt trường hợp cùng văn bản nhưng file có thể khác bytes do được tải từ nguồn khác.

### 2.7.2. Trích xuất văn bản và cấu trúc hóa PDF

Trong phiên bản hiện tại, pipeline xử lý PDF không phụ thuộc hoàn toàn vào khả năng đọc file trực tiếp của LLM. Hệ thống tách quá trình này thành hai pha rõ ràng:

1. **Self-hosted OCR / text extraction**: tự trích xuất chữ từ PDF bằng PyMuPDF; nếu trang là ảnh scan hoặc không có text layer thì dùng PaddleOCR, sau đó fallback sang Tesseract nếu PaddleOCR không khả dụng.
2. **LLM structuring**: gửi phần text sạch sang LLM để chuyển thành JSON có cấu trúc điều luật. Ở pha này LLM làm nhiệm vụ hiểu và cấu trúc hóa văn bản, không làm OCR chính.

Cách tách này thực tế hơn so với để LLM xử lý toàn bộ PDF:

- Giảm chi phí token và chi phí xử lý ảnh vì phần lớn PDF pháp luật có text layer.
- Chủ động kiểm soát chất lượng OCR tiếng Việt bằng các rule sửa lỗi phổ biến.
- Dễ log số trang digital/scanned, số ký tự trích xuất và thời gian từng bước.
- LLM tập trung vào nhiệm vụ mạnh nhất: hiểu cấu trúc pháp lý và chuẩn hóa thành JSON.

**LLM structuring** nhận text đã làm sạch và sinh ra JSON có cấu trúc:

```json
{
  "law_id": "168/2024/ND-CP",
  "articles": [
    {
      "article_id": "7",
      "title": "Điều 7. Xử phạt người điều khiển xe mô tô, xe gắn máy...",
      "text": "1. Phạt tiền từ 100.000 đồng đến 200.000 đồng đối với...",
      "metadata": {
        "topics": ["Xử phạt giao thông", "Xe máy"],
        "keywords": ["nồng độ cồn", "mức phạt", "xe mô tô"],
        "summary": "Quy định mức xử phạt vi phạm giao thông..."
      }
    },
    ...
  ]
}
```

Nếu pipeline OCR hoặc bước cấu trúc hóa text thất bại, hệ thống mới chuyển sang **LLM file/vision fallback** để xử lý trực tiếp tài liệu PDF. Thiết kế này giúp cân bằng giữa chi phí, tốc độ và độ ổn định: đường chính là self-hosted OCR + LLM structuring, đường dự phòng là xử lý trực tiếp file bằng LLM.

Kết quả parse không được lưu ngay mà phải đi qua bước validation. Validation kiểm tra các trường quan trọng như `law_id`, `article_id`, `title`, `text` và metadata. Đây là bước cần thiết vì output của LLM dù có cấu trúc JSON vẫn có thể thiếu trường, sai định dạng hoặc tạo ra article rỗng. Với dữ liệu pháp luật, lưu sai một điều luật có thể ảnh hưởng trực tiếp đến câu trả lời về sau, nên pipeline ưu tiên từ chối dữ liệu không đạt chuẩn thay vì cố lưu.

### 2.7.3. Xử lý song song (Concurrent Processing)

Hai tác vụ tốn thời gian nhất được chạy **song song** bằng background thread để không chặn event loop của FastAPI:

```python
cloud_task = asyncio.to_thread(upload_to_cloudinary, file_path)
ocr_result = await asyncio.to_thread(extract_text_from_pdf, file_path)

parse_result = await llm_structure_text(ocr_result.text)
cloud_result = await cloud_task
```

**Cloudinary upload**: lưu file PDF nguyên gốc lên cloud storage, nhận URL bền vững để các điều luật tham chiếu `source_url`.

**OCR extraction**: chạy trong background thread vì đây là tác vụ CPU-bound, có thể xử lý nhiều trang ảnh bằng PaddleOCR/Tesseract.

**LLM structuring**: nhận text sạch từ OCR và chuyển thành danh sách articles có cấu trúc.

Nhờ upload Cloudinary chạy song song với OCR, thời gian tổng giảm đáng kể so với xử lý tuần tự. Khi OCR thành công, hệ thống không cần gửi toàn bộ file PDF sang LLM; khi OCR thất bại, đường fallback xử lý trực tiếp file vẫn đảm bảo pipeline có cơ hội hoàn tất thay vì dừng ngay.

Về mặt backend, các tác vụ CPU-bound như OCR được đưa vào background thread để không chặn event loop của FastAPI. Nếu chạy OCR trực tiếp trong coroutine, server có thể bị nghẽn và ảnh hưởng tới các API khác như chat hoặc dashboard. Việc dùng `asyncio.to_thread` giúp giữ mô hình async của FastAPI cho I/O, đồng thời vẫn xử lý được các tác vụ nặng cần CPU.

### 2.7.4. Compensating Transaction

Như Hình 2.9 đã thể hiện, sau khi parse xong, hệ thống cần lưu dữ liệu vào hai DB:
- **MongoDB**: lưu articles (toàn văn + metadata).
- **ChromaDB**: lưu vector embeddings của các chunks.

MongoDB và ChromaDB không có distributed transaction tự nhiên (khác với PostgreSQL có ACID). Nếu MongoDB thành công nhưng ChromaDB lỗi (hoặc ngược lại), CSDL sẽ ở trạng thái **không nhất quán** — một điều luật có trong MongoDB nhưng không thể tìm kiếm qua vector search.

Hệ thống xử lý bằng **Compensating Transaction** (giao dịch bù trừ) — pattern chuẩn trong microservices:

```python
# Bước 1: Lưu MongoDB
mongo_result = await save_to_mongodb(articles)

try:
    # Bước 2: Chunk + embed + lưu ChromaDB
    await rag_client.ingest_articles(articles)
except Exception as e:
    # Bước 3 (nếu lỗi): Xoá MongoDB để đảm bảo nhất quán
    await rollback_mongodb(mongo_result.law_id)
    raise
```

Quy tắc ngược lại: nếu MongoDB lỗi ở bước 1, ChromaDB chưa được gọi → không cần rollback. Ngoài articles và vector chunks, hệ thống còn đồng bộ `laws_cache` để màn hình quản lý văn bản của Admin Web hiển thị đúng danh sách văn bản đã ingest. Nếu bước sync cache lỗi sau khi MongoDB và ChromaDB đã lưu thành công, backend rollback cả MongoDB articles và ChromaDB chunks để tránh trạng thái lệch giữa màn hình quản trị và khả năng tìm kiếm của Agent.

Trong hệ thống này, "thành công" của upload không chỉ là parse được PDF. Một văn bản chỉ được xem là cập nhật thành công khi cả ba điều kiện đều đạt: articles đã có trong MongoDB để admin xem và người dùng tra cứu; chunks đã có trong ChromaDB để Agent tìm kiếm ngữ nghĩa; và `laws_cache` đã được đồng bộ để dashboard/thư viện hiển thị đúng. Nếu một trong các bước cuối thất bại, task phải chuyển sang `failed` và dữ liệu đã ghi một phần phải được hoàn tác.

### 2.7.5. Chunking Strategy

Trước khi lưu ChromaDB, mỗi article phải được chia thành chunks vừa đủ:

- **Kích thước tối đa**: 1,000 từ mỗi chunk. Giới hạn này cân bằng giữa ngữ cảnh đủ rộng để embedding có ý nghĩa và context window không quá lớn khi đưa vào LLM.
- **Overlap**: 150 từ giữa hai chunks liền kề. Overlap đảm bảo thông tin tại ranh giới chunk không bị mất ngữ cảnh.
- **Naming convention**: `{law_id}_{article_id}_chunk{index}` — giúp dễ truy hồi về article gốc.

Với mức split này, 528,620 articles tạo ra 690,360 chunks (tỷ lệ 1.31 chunk/article — nghĩa là phần lớn articles ngắn không cần split, chỉ một số bài dài bị split).

Kích thước chunk được chọn để giữ cân bằng giữa độ đầy đủ của ngữ cảnh và độ chính xác của retrieval. Nếu chunk quá ngắn, một điều khoản có thể bị tách rời khỏi điều kiện áp dụng hoặc mức xử phạt, khiến Agent nhận thiếu thông tin. Nếu chunk quá dài, embedding trở nên kém đặc trưng và kết quả tìm kiếm có thể bị nhiễu. Overlap 150 từ giúp giảm rủi ro mất ngữ cảnh ở ranh giới chunk, đặc biệt với các điều luật dài có nhiều khoản liên tiếp.

---

## 2.8. Luồng Chat SSE và Quản lý Hội thoại

[IMG:hinh_2_10.png]
*Hình 2.10. Luồng chat SSE và lưu hội thoại*

Luồng chat tự do là chức năng trung tâm của hệ thống, vì đây là nơi người dùng đặt câu hỏi pháp luật theo ngôn ngữ tự nhiên và nhận câu trả lời có trích dẫn. Về mặt kiến trúc, phần chat không chỉ là một endpoint gọi AI, mà là một pipeline phối hợp giữa quản lý hội thoại, lưu lịch sử, chuyển tiếp tiến trình xử lý và đồng bộ nguồn trích dẫn.

Hình 2.10 mô tả luồng chat ở mức nghiệp vụ. Điểm đáng chú ý là hệ thống lưu user message trước khi gọi RAG Service, sau đó mới chuyển câu hỏi sang Agentic RAG. Khi RAG Service trả kết quả cuối cùng, Main Service lưu assistant message rồi mới phát `done` về Mobile App. Cách làm này đảm bảo giao diện người dùng và dữ liệu trong PostgreSQL luôn đồng nhất, kể cả khi người dùng rời màn hình hoặc tải lại hội thoại sau khi nhận câu trả lời.

### 2.8.1. Endpoint streaming cho chat

Mobile App gửi tin nhắn đến `POST /api/v1/chat/messages/stream`. Endpoint này trả về `StreamingResponse` với định dạng SSE, cho phép server đẩy nhiều event trong cùng một request HTTP. Luồng xử lý trong `ChatService.send_message_stream()` gồm các bước chính:

1. Nếu request chưa có `conversation_id`, Main Service tạo một hội thoại mới; nếu đã có `conversation_id`, service kiểm tra hội thoại có thuộc về người dùng hiện tại hay không.
2. Với hội thoại cũ, hệ thống lấy tối đa 6 tin nhắn gần nhất làm ngữ cảnh. Nội dung assistant dài được cắt ngắn để tránh đưa quá nhiều token vào prompt.
3. User message được lưu ngay vào PostgreSQL, sau đó server phát event `ready` để frontend có `message_id` và có thể render tin nhắn của người dùng tức thời.
4. Main Service gọi RAG Service qua `/api/v1/rag/agent-search/stream`, chuyển tiếp các event `progress` về Mobile App.
5. Khi RAG Service trả `done`, Main Service lưu assistant message gồm answer, sources và metadata, rồi mới phát event `done` cuối cùng về client.
6. Sau khi stream kết thúc, hệ thống tạo suggested questions trong background và cập nhật vào metadata của assistant message.

Luồng này được thiết kế theo nguyên tắc "persist before display" đối với câu trả lời cuối cùng. Nếu backend gửi câu trả lời về client trước rồi mới lưu database, có thể xảy ra trường hợp người dùng đã thấy câu trả lời nhưng backend lưu thất bại, dẫn tới mất lịch sử khi mở lại hội thoại. Ngược lại, với cách hiện tại, `done` chỉ xuất hiện sau khi assistant message đã được ghi nhận.

Một tối ưu nhỏ nhưng quan trọng là chỉ lấy một số tin nhắn gần nhất làm context, đồng thời cắt ngắn các câu trả lời assistant quá dài. Lịch sử chat có thể chứa nhiều đoạn tư vấn pháp luật rất dài; nếu gửi toàn bộ lịch sử sang RAG Service, request sẽ tốn token, tăng độ trễ và làm loãng trọng tâm câu hỏi hiện tại. Việc giới hạn context giúp Agent vẫn hiểu câu hỏi nối tiếp nhưng không bị kéo quá xa khỏi vấn đề chính.

### 2.8.2. Các event SSE trong luồng chat

**Bảng 2.14. Các event SSE của luồng chat**

| Event | Thời điểm phát | Nội dung chính | Vai trò trong UI |
|---|---|---|---|
| `ready` | Sau khi lưu user message | `conversation_id`, `is_new_conversation`, `user_message` | Render tin nhắn người dùng và gắn vào hội thoại đúng |
| `progress` | Khi RAG graph chuyển bước | Danh sách `steps` của pipeline | Cập nhật ThinkingPanel: kiểm tra, phân tích, tra cứu, tổng hợp, kiểm chứng |
| `done` | Sau khi assistant message đã được lưu | `assistant_message`, `sources`, metadata | Hiển thị câu trả lời cuối cùng và citation |
| `error` | Khi lỗi xác thực hội thoại, timeout hoặc lỗi RAG | `message` | Hiển thị lỗi và dừng trạng thái streaming |

Điểm quan trọng là `done` chỉ được phát sau khi câu trả lời đã được lưu vào PostgreSQL. Nhờ đó, khi Mobile App nhận `done`, dữ liệu trên giao diện và dữ liệu trong backend đã đồng nhất; nếu người dùng reload hoặc mở lại hội thoại, assistant message vẫn tồn tại đầy đủ.

Các event `progress` không phải là dữ liệu pháp lý cuối cùng mà là trạng thái pipeline. RAG Service gom các cập nhật nội bộ của LangGraph thành các bước dễ hiểu cho UI: kiểm tra câu hỏi, phân tích chủ đề, tra cứu nguồn, tổng hợp và kiểm chứng. Nhờ vậy, người dùng không phải nhìn một spinner tĩnh trong thời gian Agent chạy, đồng thời hệ thống vẫn tránh hiển thị câu trả lời chưa qua verifier.

### 2.8.3. Xử lý lịch sử hội thoại

Chat pháp luật khác với hỏi đáp một lượt vì người dùng thường hỏi tiếp theo ngữ cảnh trước đó, ví dụ: *"Nếu tôi là xe máy thì sao?"* sau câu hỏi ban đầu về vi phạm giao thông. Hệ thống xử lý bằng cách đưa lịch sử hội thoại gần nhất vào request gửi sang RAG Service, nhưng chỉ dùng lịch sử để hiểu ngữ cảnh, không dùng lịch sử làm căn cứ pháp lý.

Trong RAG Service, lịch sử được gói vào `HumanMessage` hiện tại với cảnh báo rõ: lịch sử chỉ để hiểu câu hỏi, còn mọi trích dẫn pháp lý phải đến từ tool trong lượt hiện tại. Thiết kế này giải quyết hai rủi ro:

- Agent vẫn hiểu được câu hỏi nối tiếp, không bắt người dùng lặp lại toàn bộ ngữ cảnh.
- Verifier không chấp nhận việc trích dẫn lại nguồn từ lượt chat cũ nếu lượt hiện tại chưa tra cứu lại, giúp giảm hallucination citation.

### 2.8.4. Suggested Questions

Sau khi assistant message được lưu, Main Service chạy tác vụ nền gọi `/api/v1/rag/suggested-questions`. Tác vụ này không chặn response chính vì suggested questions chỉ là thành phần hỗ trợ UX. Frontend có thể gọi `GET /api/v1/chat/messages/{message_id}/suggested-questions` sau đó; nếu background task chưa hoàn tất, API trả về danh sách rỗng.

Thiết kế này tách rõ hai mức ưu tiên: câu trả lời pháp lý chính phải hoàn tất và được lưu ngay trong stream, còn câu hỏi gợi ý được xử lý bất đồng bộ để không làm tăng độ trễ của luồng chat.

Về mặt trải nghiệm, suggested questions giúp kéo dài mạch hội thoại một cách tự nhiên. Sau khi nhận câu trả lời, người dùng thường có các câu hỏi tiếp theo như điều kiện áp dụng, thủ tục, mức phạt bổ sung hoặc giấy tờ cần chuẩn bị. Thay vì bắt người dùng tự nghĩ lại từ đầu, hệ thống sinh một số câu hỏi liên quan dựa trên câu hỏi và câu trả lời vừa có. Vì tác vụ này không ảnh hưởng đến tính đúng sai của câu trả lời chính, nó được đưa vào background để không làm chậm stream.

---

## 2.9. Phương pháp xây dựng lớp ứng dụng đa nền tảng

Sau khi thiết kế lõi backend và Agentic RAG, hệ thống cần một lớp ứng dụng đủ thuận tiện để người dùng cuối có thể đặt câu hỏi pháp luật, theo dõi quá trình suy luận của AI và kiểm tra nguồn trích dẫn. Đồng thời, quản trị viên cần một giao diện riêng để cập nhật văn bản pháp luật mới, theo dõi pipeline xử lý tài liệu và kiểm soát kho dữ liệu. Vì vậy, đồ án tách lớp frontend thành hai sản phẩm độc lập: **Mobile App** cho người dùng cuối và **Admin Web** cho quản trị viên.

### 2.9.1. Mobile App — Kotlin Multiplatform và Compose Multiplatform

Ứng dụng người dùng cuối được xây dựng bằng **Kotlin Multiplatform (KMP)** kết hợp **Compose Multiplatform**. Lựa chọn này xuất phát từ đặc thù chuyên ngành Phát triển phần mềm di động: hệ thống cần có ứng dụng native trên Android và iOS, nhưng vẫn phải tiết kiệm công sức phát triển, bảo trì và đồng bộ logic nghiệp vụ.

Thay vì viết hai ứng dụng riêng bằng Kotlin/Android và Swift/iOS, KMP cho phép chia sẻ phần lớn code ở tầng `commonMain`, bao gồm:

- Model dữ liệu domain: `Conversation`, `Message`, `LawDetail`, `ArticleDocument`, `GuidedAnswer`, `AISearchResult`.
- Repository interface và implementation: `AuthRepository`, `ChatRepository`, `LawRepository`, `GuidedRepository`.
- Network layer: Ktor Client, DTO request/response, SSE client.
- ViewModel và state management theo MVI.
- UI Compose dùng chung cho Android, iOS và JVM desktop.

Trong bối cảnh đồ án chuyên ngành mobile, lựa chọn KMP không chỉ nhằm "viết ít code hơn" mà còn nhằm chứng minh khả năng thiết kế kiến trúc ứng dụng đa nền tảng. Các phần dễ sai khác giữa nền tảng như UI native, permission hoặc lifecycle vẫn có thể tách riêng; còn domain model, repository, use case và state management được chia sẻ. Nhờ đó, các luồng quan trọng như chat SSE và guided consultation có hành vi giống nhau trên Android và iOS, giảm nguy cơ hai ứng dụng xử lý khác nhau cùng một API.

**Bảng 2.15. Lý do lựa chọn Kotlin Multiplatform cho Mobile App**

| Tiêu chí | Lý do |
|---|---|
| Chia sẻ logic nghiệp vụ | Repository, API client, mapper, validation và ViewModel dùng chung giữa Android/iOS |
| Trải nghiệm native | UI Compose chạy native, không phải WebView |
| Đồng bộ tính năng | Một thay đổi ở chat streaming hoặc guided consultation được áp dụng đồng thời cho nhiều nền tảng |
| Phù hợp đồ án mobile | Thể hiện năng lực thiết kế ứng dụng đa nền tảng thay vì chỉ xây backend |
| Dễ mở rộng | Có thể bổ sung desktop JVM để demo hoặc kiểm thử nhanh |

### 2.9.2. Mô hình MVI trong Mobile App

Mobile App sử dụng mô hình **MVI (Model - View - Intent)**. Mỗi màn hình thường gồm ba file: `Contract`, `ViewModel` và `Screen`. Trong đó:

- `State` mô tả toàn bộ trạng thái giao diện hiện tại.
- `Intent` mô tả hành động từ người dùng hoặc từ lifecycle.
- `Effect` mô tả sự kiện một lần như điều hướng, toast, snackbar.
- `ViewModel` nhận intent, gọi repository, cập nhật state và phát effect.
- `Screen` chỉ render UI theo state và gửi intent ngược về ViewModel.

Cách tổ chức này phù hợp với ứng dụng chat AI vì trạng thái UI thay đổi liên tục: đang gửi tin nhắn, đang nhận SSE, đang hiển thị ThinkingPanel, đang nhận câu trả lời cuối cùng, đang tải gợi ý câu hỏi, hoặc đang hiển thị lỗi kết nối.

**Bảng 2.16. Ánh xạ MVI vào các màn hình chính**

| Màn hình | State chính | Intent tiêu biểu | Effect tiêu biểu |
|---|---|---|---|
| Login | email, password, loading, error | nhập email, nhập mật khẩu, đăng nhập | điều hướng sang Home |
| ChatDetail | messages, input, streaming, pipeline steps | gửi tin nhắn, chọn suggested question | scroll xuống cuối, báo lỗi |
| Library | laws, filters, search query, ai results | tìm kiếm, đổi topic/year, mở chi tiết | điều hướng LawDetail |
| Guided | query, clarify questions, selected answers, answer stream | bắt đầu tư vấn, chọn đáp án, gửi answer | hiển thị kết quả hoặc lỗi |
| Setting/Profile | thông tin user, loading | cập nhật hồ sơ, đổi mật khẩu | thông báo thành công |

Với MVI, các luồng phức tạp như SSE streaming không bị trộn lẫn trực tiếp vào UI. `SseClient` chuyển từng event thành domain event, Repository map thành `ChatStreamEvent`, ViewModel cập nhật state, còn `Screen` chỉ hiển thị kết quả. Điều này giúp code dễ kiểm soát hơn khi có nhiều trạng thái song song.

MVI đặc biệt phù hợp với màn hình chat vì cùng một thời điểm có thể tồn tại nhiều trạng thái: tin nhắn người dùng vừa gửi, pipeline đang chạy, ThinkingPanel đang hiển thị bước hiện tại, câu trả lời cuối cùng chưa có, suggested questions có thể chưa tải xong. Nếu xử lý trực tiếp trong UI, code dễ bị rối và khó debug. Khi gom toàn bộ trạng thái vào `State`, mỗi lần nhận event từ SSE chỉ là một phép biến đổi state rõ ràng, giúp UI nhất quán hơn.

### 2.9.3. Thiết kế trải nghiệm chat streaming

Một vấn đề phổ biến của các chatbot dùng LLM là thời gian chờ lâu. Với Agentic RAG, hệ thống không chỉ gọi một LLM duy nhất mà còn phải chạy guardrail, query analysis, internal retrieval, web search và verifier. Nếu chỉ hiển thị loading spinner trong 10-15 giây, người dùng khó biết hệ thống còn hoạt động hay đã lỗi.

Đồ án giải quyết bằng **SSE streaming** kết hợp **ThinkingPanel**:

1. Khi người dùng gửi câu hỏi, Main Service tạo hoặc lấy conversation hiện tại, lưu user message và trả event `ready`.
2. RAG Service phát các event `progress`: kiểm tra câu hỏi, phân tích truy vấn, tra cứu cơ sở dữ liệu, tìm kiếm web, kiểm chứng câu trả lời.
3. Mobile App cập nhật ThinkingPanel theo từng bước, giúp người dùng thấy hệ thống đang làm gì.
4. Khi pipeline hoàn tất, Main Service lưu assistant message cùng answer, sources và metadata.
5. Event `done` kết thúc stream, kèm assistant message đã lưu để Mobile App hiển thị câu trả lời và citation.

**Bảng 2.17. Lợi ích của SSE trong trải nghiệm người dùng**

| Lợi ích | Giải thích |
|---|---|
| Giảm cảm giác chờ | Người dùng thấy tiến trình thay vì màn hình đứng yên |
| Minh bạch pipeline | Người dùng biết hệ thống có tra cứu nguồn và kiểm chứng |
| Phù hợp chat một chiều | Server chỉ cần đẩy event về client, không cần full-duplex như WebSocket |
| Dễ triển khai trên mobile | Ktor Client có thể đọc stream và parse từng event |
| Tối ưu UX | Tiến trình xử lý xuất hiện theo từng bước, câu trả lời chỉ hiển thị sau khi đã lưu và kiểm chứng |

### 2.9.4. Admin Web — Next.js Dashboard cho quản trị dữ liệu

Bên cạnh ứng dụng người dùng cuối, hệ thống có **Admin Web** để quản trị viên nạp và quản lý văn bản pháp luật. Frontend này được xây dựng bằng **Next.js 16**, **React 19**, **TypeScript**, **TailwindCSS 4** và bộ component kiểu shadcn/ui. Admin Web tách biệt với Mobile App vì đối tượng sử dụng, tần suất thao tác và yêu cầu giao diện hoàn toàn khác.

Các chức năng chính của Admin Web gồm:

- Đăng nhập với tài khoản `role = admin`.
- Xem dashboard thống kê: tổng số văn bản, tổng số điều luật, số task thành công/thất bại/đang xử lý, top chủ đề phổ biến.
- Quản lý văn bản pháp luật: phân trang, tìm kiếm, xem chi tiết, mở rộng từng điều luật, xóa văn bản.
- Upload PDF văn bản mới bằng drag-and-drop.
- Theo dõi tiến trình xử lý tài liệu qua WebSocket.
- Khôi phục trạng thái upload sau khi reload tab bằng localStorage và REST API.

Admin Web được thiết kế theo hướng dashboard vận hành thay vì giao diện người dùng phổ thông. Các thao tác như upload văn bản, xem task đang chạy, kiểm tra số điều luật và xoá văn bản đều có tác động trực tiếp tới kho tri thức của hệ thống. Vì vậy, giao diện admin cần ưu tiên tính rõ ràng, trạng thái xử lý và khả năng phục hồi khi thao tác bị gián đoạn. Ví dụ, khi reload tab trong lúc upload, frontend có thể đọc lại task hiện có qua REST API và tiếp tục hiển thị trạng thái thay vì mất hoàn toàn tiến trình.

**Bảng 2.18. So sánh vai trò Mobile App và Admin Web**

| Tiêu chí | Mobile App | Admin Web |
|---|---|---|
| Người dùng | Người dân, sinh viên, cán bộ, doanh nghiệp | Quản trị viên hệ thống |
| Mục tiêu | Hỏi đáp, tư vấn, tra cứu pháp luật | Cập nhật dữ liệu, giám sát pipeline |
| Kênh realtime chính | SSE cho chat/guided answer | WebSocket cho document task |
| Luồng quan trọng | Chat AI, Guided Consultation, Library AI Search | Upload PDF, task tracking, dashboard |
| Xác thực | JWT Bearer trong Ktor Client | JWT lưu cookie `admin_token` |

### 2.9.5. WebSocket cho tiến trình xử lý tài liệu

Khác với chat AI, pipeline upload PDF là tác vụ nền kéo dài và có nhiều bước không sinh text liên tục. Vì vậy, Admin Web sử dụng **WebSocket** thay vì SSE. WebSocket cho phép backend chủ động đẩy trạng thái task đến admin trong suốt quá trình xử lý.

Quy trình tổng quát:

1. Admin upload PDF qua `/documents/upload-v2`.
2. Backend tạo `DocumentTask` với `task_id`.
3. Frontend mở WebSocket `/api/v1/documents/ws?token=...`.
4. `DocumentProcessor` cập nhật progress thông qua callback.
5. `WebSocketManager` broadcast event cho đúng user/admin sở hữu task.
6. Frontend cập nhật progress bar, current step, toast thành công/thất bại.
7. Khi task kết thúc (`completed`, `failed`, `cancelled`), WebSocket tự đóng.

**Bảng 2.19. Các trạng thái DocumentTask**

| Trạng thái | Ý nghĩa |
|---|---|
| `pending` | Task vừa được tạo, chờ xử lý |
| `processing` | Đang OCR/parse/upload/ingest |
| `completed` | Đã lưu thành công vào MongoDB và ChromaDB |
| `failed` | Có lỗi trong quá trình xử lý |
| `cancelled` | Admin hủy tác vụ |

Việc scope WebSocket theo `user_id` giúp admin chỉ thấy tiến trình của chính mình, tránh lộ thông tin task giữa các tài khoản quản trị. Đây là điểm quan trọng khi hệ thống mở rộng cho nhiều quản trị viên cùng vận hành.

So với polling định kỳ, WebSocket phù hợp hơn cho upload pipeline vì trạng thái tiến trình không thay đổi theo chu kỳ cố định. Có bước mất vài giây, có bước có thể mất lâu hơn tùy số trang PDF và chất lượng OCR. Nếu dùng polling, frontend phải gọi API liên tục dù không có thay đổi; nếu polling thưa, UI lại cập nhật chậm. WebSocket cho phép backend chủ động đẩy trạng thái ngay khi có progress mới, vừa tiết kiệm request, vừa giúp admin thấy pipeline đang hoạt động.

### 2.9.6. Kết nối giữa frontend và backend

Hai frontend đều không giao tiếp trực tiếp với RAG Service. Mọi request đều đi qua Main Service. Cách thiết kế này có ba lợi ích:

- Bảo vệ RAG Service khỏi truy cập trực tiếp từ client.
- Tập trung logic xác thực, phân quyền và logging ở Main Service.
- Giữ API client đơn giản: frontend chỉ cần biết một base URL `/api/v1`.

Mobile App gọi các endpoint chính:

- `auth/login`, `auth/signup`, `auth/refresh`, `auth/me`.
- `chat/conversations`, `chat/messages/stream`, `chat/messages/{id}/suggested-questions`.
- `laws`, `laws/info`, `laws/detail`, `laws/by-law`, `laws/ai-search`.
- `guided/clarify`, `guided/answer/stream`.

Admin Web gọi các endpoint chính:

- `auth/login`, `auth/me`.
- `dashboard/stats`.
- `laws`, `laws/info`, `laws/detail`, `laws/{law_id}`.
- `documents/upload-v2`, `documents/tasks`, `documents/tasks/{task_id}/cancel`.
- `documents/ws` qua WebSocket.

Như vậy, lớp ứng dụng không chỉ là phần hiển thị giao diện mà còn là nơi thể hiện các quyết định kiến trúc quan trọng: phân tách người dùng cuối và quản trị viên, dùng SSE cho chat AI, dùng WebSocket cho task nền, dùng KMP để chia sẻ logic mobile đa nền tảng, và dùng Next.js dashboard để vận hành kho dữ liệu pháp luật.

---

## 2.10. Tổng kết chương 2

Chương 2 đã trình bày toàn diện phương pháp kỹ thuật được áp dụng trong hệ thống Vietnam Law Chatbot, từ kiến trúc Microservices tách biệt workload AI, qua luồng Agentic RAG với các kỹ thuật đặc thù như Two-Stage Retrieval, Temporal Conflict Resolution và Verifier chống hallucination, đến ba luồng nghiệp vụ trọng tâm: chat SSE, tư vấn có hướng dẫn và cập nhật văn bản pháp luật phía admin.

Điểm nhấn kỹ thuật quan trọng nhất của chương là **đồ thị Agentic RAG** — thiết kế Re-Act loop kết hợp với Verifier tạo nên một hệ thống có khả năng tự kiểm chứng, phù hợp với yêu cầu độ chính xác tuyệt đối của domain pháp luật. Kỹ thuật **Temporal Conflict Resolution** là đóng góp đặc trưng cho bài toán pháp luật Việt Nam — nơi các văn bản quy phạm pháp luật được sửa đổi, thay thế thường xuyên.

Bên cạnh lõi Agent, chương này cũng làm rõ cách hệ thống đưa Agent vào sản phẩm thực tế: luồng chat lưu đầy đủ hội thoại và stream trạng thái xử lý cho Mobile App; luồng Guided Consultation thu thập ngữ cảnh thiếu trước khi trả lời; và luồng Document Ingestion giúp admin cập nhật văn bản mới một cách có kiểm soát, có pre-check, WebSocket progress và rollback khi đồng bộ dữ liệu thất bại.

Chương 3 tiếp theo sẽ chuyển từ góc nhìn "phương pháp" sang "phân tích và thiết kế" — đặc tả đầy đủ các use case, thiết kế cơ sở dữ liệu chi tiết và đặc tả API của hệ thống.
