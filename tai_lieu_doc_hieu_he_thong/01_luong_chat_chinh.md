# Luồng chat chính của hệ thống

Tài liệu này mô tả luồng chat chính của hệ thống trợ lý ảo pháp luật từ thời điểm người dùng gửi câu hỏi cho đến khi nhận được câu trả lời cuối cùng. Nội dung được viết theo hướng để người ngoài dự án vẫn có thể hiểu được cách hệ thống vận hành, các thành phần tham gia và lý do thiết kế của từng bước xử lý.

## 1. Vai trò của luồng chat chính

Luồng chat chính là chức năng trung tâm của hệ thống. Người dùng có thể đặt câu hỏi pháp luật bằng ngôn ngữ tự nhiên, sau đó hệ thống phân tích câu hỏi, truy hồi căn cứ pháp lý liên quan, kiểm tra tính cập nhật của quy định và trả về câu trả lời có cấu trúc kèm nguồn tham chiếu.

Khác với chatbot thông thường chỉ gửi trực tiếp câu hỏi cho mô hình ngôn ngữ lớn, hệ thống này được xây dựng theo hướng Agentic RAG. LLMs không được phép tự trả lời ngay bằng kiến thức sẵn có, mà phải đi qua các bước kiểm tra, phân tích, truy hồi, tổng hợp và kiểm chứng. Cách thiết kế này giúp giảm rủi ro trả lời thiếu căn cứ, đặc biệt trong lĩnh vực pháp luật, nơi một điều khoản, mức phạt hoặc thời điểm hiệu lực sai có thể làm câu trả lời mất giá trị.

Luồng chat có ba lớp chính:

- Ứng dụng người dùng: hiển thị giao diện chat, gửi câu hỏi và nhận kết quả theo thời gian thực.
- Main Service: xác thực người dùng, quản lý hội thoại, lưu tin nhắn và điều phối request sang RAG Service.
- RAG Service: xử lý AI, truy hồi tri thức pháp luật, tìm kiếm nguồn cập nhật và kiểm chứng câu trả lời.

## 2. Người dùng gửi câu hỏi từ ứng dụng

Khi người dùng nhập câu hỏi và nhấn gửi, ứng dụng gọi API chat của Main Service. Hệ thống hiện có hai cách gửi tin nhắn:

```http
POST /api/v1/chat/messages
POST /api/v1/chat/messages/stream
```

Endpoint `/messages` dùng cho kiểu xử lý đồng bộ: client gửi câu hỏi và chờ đến khi câu trả lời hoàn tất. Endpoint `/messages/stream` dùng SSE streaming để phát tiến trình xử lý theo thời gian thực. Trong trải nghiệm chính của hệ thống, luồng streaming được ưu tiên vì câu trả lời pháp luật thường cần nhiều bước xử lý và có thể mất vài giây đến hàng chục giây.

Với SSE, người dùng không phải nhìn một màn hình chờ tĩnh. Thay vào đó, ứng dụng có thể hiển thị các trạng thái như đang kiểm tra câu hỏi, đang phân tích chủ đề, đang tra cứu nguồn, đang tổng hợp câu trả lời và đang kiểm tra độ chính xác.

Trước khi xử lý câu hỏi, Main Service kiểm tra JWT access token của người dùng. Token được gửi trong header:

```http
Authorization: Bearer <access_token>
```

Nếu token không hợp lệ, hết hạn hoặc tài khoản không còn hoạt động, request bị từ chối. Nếu token hợp lệ, Main Service xác định được `user_id` và dùng thông tin này để đảm bảo người dùng chỉ truy cập được các hội thoại của chính mình.

## 3. Main Service xác định hội thoại cần xử lý

Sau khi xác thực thành công, Main Service kiểm tra request có truyền `conversation_id` hay không.

Nếu không có `conversation_id`, hệ thống hiểu đây là một cuộc trò chuyện mới. Main Service tạo một bản ghi hội thoại mới trong PostgreSQL với tiêu đề tạm thời. Tiêu đề thật sẽ được cập nhật sau khi RAG Service phân tích được chủ đề chính của câu hỏi.

Nếu có `conversation_id`, Main Service kiểm tra hội thoại đó có tồn tại và có thuộc về người dùng hiện tại hay không. Đây là bước quan trọng để tránh trường hợp một người dùng cố tình gửi ID hội thoại của người khác. Nếu hội thoại không tồn tại hoặc không thuộc user hiện tại, hệ thống trả lỗi không tìm thấy hội thoại.

Ở luồng streaming, sau khi xác định hội thoại, Main Service lưu ngay tin nhắn của người dùng vào bảng `messages`. Việc lưu sớm này có hai lợi ích:

- Client nhận được `message_id` của tin nhắn người dùng ngay từ đầu.
- Lịch sử hội thoại vẫn ghi nhận câu hỏi kể cả khi quá trình sinh câu trả lời gặp lỗi ở các bước sau.

## 4. Lấy ngữ cảnh hội thoại gần nhất

Nếu đây là hội thoại cũ, Main Service lấy tối đa 6 tin nhắn gần nhất để làm ngữ cảnh cho câu hỏi hiện tại. Con số này tương ứng khoảng 3 cặp hỏi đáp gần nhất.

Việc chỉ lấy một phần lịch sử là một tối ưu quan trọng. Hội thoại pháp luật thường có câu trả lời dài, chứa nhiều căn cứ, phân tích và trích dẫn. Nếu gửi toàn bộ lịch sử sang RAG Service, request sẽ trở nên nặng, tốn token, tăng độ trễ và có thể làm nhiễu trọng tâm câu hỏi hiện tại.

Vì vậy, hệ thống chỉ giữ lại đoạn hội thoại gần nhất để hỗ trợ các câu hỏi nối tiếp như:

```text
Vậy trường hợp của tôi thì sao?
Quy định này áp dụng từ khi nào?
Nếu tôi đã nộp phạt rồi thì có bị xử lý thêm không?
```

Ngoài ra, nội dung từ phía assistant nếu quá dài sẽ bị cắt ngắn trước khi gửi sang RAG Service. Cách này giúp hệ thống vẫn giữ được ý chính của ngữ cảnh nhưng tránh đưa quá nhiều nội dung không cần thiết vào pipeline AI.

## 5. Main Service gọi RAG Service bằng kết nối nội bộ

Sau khi chuẩn bị câu hỏi và ngữ cảnh, Main Service gọi RAG Service qua endpoint streaming nội bộ:

```http
POST /api/v1/rag/agent-search/stream
```

Request gửi sang RAG Service có dạng:

```json
{
  "query": "Câu hỏi hiện tại của người dùng",
  "top_k": 5,
  "include_sources": true,
  "context": [
    {
      "role": "user",
      "content": "Tin nhắn trước đó"
    },
    {
      "role": "assistant",
      "content": "Tóm tắt câu trả lời trước đó"
    }
  ]
}
```

RAG Service không được gọi trực tiếp từ mobile app hoặc web admin. Main Service gọi RAG Service bằng header nội bộ:

```http
X-API-Key: <internal_api_key>
X-Internal-Service: main-service
```

Thiết kế này tách rõ hai lớp xác thực. Người dùng cuối xác thực với Main Service bằng JWT, còn giao tiếp giữa Main Service và RAG Service dùng API key nội bộ. Nhờ đó, RAG Service không phải phơi trực tiếp ra client và chỉ nhận request từ thành phần backend đáng tin cậy.

## 6. RAG Service chuẩn bị input cho Agentic RAG

Khi nhận request, RAG Service xây dựng đầu vào cho pipeline Agentic RAG. Nếu request có lịch sử hội thoại, hệ thống ghép lịch sử vào câu hỏi hiện tại theo hướng chỉ dùng để hiểu ngữ cảnh, không dùng lịch sử làm căn cứ pháp lý.

Ý nghĩa xử lý có thể mô tả như sau:

```text
LỊCH SỬ HỘI THOẠI TRƯỚC ĐÓ
Người dùng: ...
Trợ lý: ...

CÂU HỎI HIỆN TẠI CẦN TRẢ LỜI
...
```

Điểm quan trọng là hệ thống phân biệt rõ giữa ngữ cảnh hội thoại và nguồn pháp lý. Lịch sử chat chỉ giúp hiểu người dùng đang hỏi tiếp về vấn đề nào. Căn cứ pháp lý vẫn phải đến từ kết quả truy hồi văn bản pháp luật hoặc nguồn tra cứu hiện hành.

## 7. Pipeline Agentic RAG xử lý câu hỏi

Pipeline chat chính trong RAG Service được tổ chức thành một đồ thị xử lý gồm các node chính:

```text
Guardrail
-> Query Analysis
-> Agent
-> Tools
-> Agent
-> Verifier
-> End
```

Trong đó, node Agent và Tools có thể lặp lại nhiều vòng. Agent quyết định cần gọi công cụ nào, Tools thực hiện truy hồi, sau đó kết quả được đưa ngược lại cho Agent để tổng hợp câu trả lời. Hệ thống có giới hạn số vòng lặp để tránh trường hợp Agent chạy vô hạn.

Pipeline này không chỉ là một chuỗi gọi LLM đơn giản. Nó là một quy trình có kiểm soát, trong đó mỗi bước đảm nhiệm một vai trò riêng:

- Guardrail kiểm tra câu hỏi có thuộc phạm vi xử lý hay không.
- Query Analysis chuyển câu hỏi tự nhiên thành truy vấn pháp lý có cấu trúc.
- Agent lập luận và điều phối việc gọi công cụ.
- Tools truy hồi dữ liệu nội bộ và nguồn hiện hành.
- Verifier kiểm chứng câu trả lời cuối cùng.

> **Cách đọc các mục 8–14.** Mỗi node được phân tích theo một khuôn thống nhất để dễ đối chiếu với code: **Vai trò & vị trí trong đồ thị → Đầu vào (đọc gì từ `AgentState`) → Xử lý (mổ code từng phần) → Đầu ra (ghi gì vào `AgentState`) → Định tuyến sau node → Xử lý lỗi/fallback → Lý do thiết kế.** Trước khi đi vào từng node, cần nắm "trạng thái dùng chung" mà mọi node đọc/ghi.

Toàn bộ pipeline chia sẻ một đối tượng trạng thái `AgentState`, định nghĩa trong `rag-service/app/agent/state.py`:

```python
class AgentState(TypedDict):
    # LangGraph's default way to track conversation history
    # The `add_messages` reducer appends new messages rather than overwriting.
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Flag to determine if the query is safe/relevant to process
    is_valid_query: bool

    # Reason for rejection (used if Guardrail blocks the request)
    rejection_reason: str

    # Structured query analysis result (JSON string) from query_analysis_node
    # Used by agent to form optimized queries for both tools
    query_analysis: str

    # Iteration counter to guard against infinite agent↔tools loops
    iteration_count: int
```

Điểm cốt lõi để hiểu mọi node: trường `messages` dùng reducer `add_messages`. Nghĩa là khi một node `return {"messages": [X]}`, LangGraph **không ghi đè** danh sách tin nhắn mà **nối thêm** `X` vào cuối. Các trường còn lại (`is_valid_query`, `query_analysis`, `iteration_count`...) theo cơ chế mặc định là **ghi đè**. Nhờ đó lịch sử hội thoại (câu hỏi người dùng, kết quả phân tích, các lượt gọi tool, câu trả lời của agent) tích lũy dần qua từng node, còn các cờ điều khiển luôn phản ánh giá trị mới nhất.

## 8. Node Guardrail - kiểm tra câu hỏi đầu vào

**Vai trò & vị trí.** Guardrail là node đầu tiên (entry point của graph). Nó quyết định câu hỏi có thuộc phạm vi tư vấn pháp luật Việt Nam và có an toàn để xử lý hay không. Đây là "cửa khẩu" lọc bỏ sớm các câu hỏi lạc đề hoặc độc hại trước khi tốn chi phí truy hồi và sinh câu trả lời.

**Đầu vào.** Node chỉ đọc tin nhắn cuối cùng trong `messages` (chính là câu hỏi người dùng vừa gửi):

```python
def guardrail_node(state: AgentState) -> dict[str, Any]:
    messages = state["messages"]
    last_user_message = messages[-1].content

    start = time.time()
    res = check_guardrail(last_user_message)
    logger.info(f"[TIMING] guardrail: {time.time() - start:.2f}s")
```

**Xử lý.** Việc kiểm duyệt được ủy thác cho hàm `check_guardrail` trong `rag-service/app/tools/guardrail.py`. Hàm này gọi một lần LLM với prompt kiểm duyệt nghiêm ngặt và chỉ ép mô hình trả về đúng một từ `PASS` hoặc `REJECT`:

```python
def check_guardrail(query: str) -> GuardrailResult:
    llm = ChatGoogleGenerativeAI(
        model=settings.generative_model,
        google_api_key=settings.gemini_api_keys[0], # Use primary key for fast validation
        temperature=0.0
    )
    ...
    try:
        content = chain.invoke({"query": query}).content
        # Gemini 3+ có thể trả content dạng list thay vì str
        if isinstance(content, list):
            content = "\n".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        result = str(content).strip().upper()
        if "REJECT" in result:
            return {"status": "REJECT", "reason": "Câu hỏi vi phạm tiêu chuẩn an toàn hoặc nằm ngoài phạm vi tư vấn pháp luật (Out-of-Domain)."}
        return {"status": "PASS", "reason": ""}
    except Exception as e:
        # Nếu LLM chặn an toàn mặc định của Google GenAI trigger
        return {"status": "REJECT", "reason": f"Bị chặn bởi bộ lọc an toàn: {str(e)}"}
```

Có hai chi tiết kỹ thuật đáng chú ý:

- Node dùng model rẻ (`settings.generative_model`, mặc định `gemini-2.5-flash`) và chỉ dùng **API key chính** (`gemini_api_keys[0]`) — vì đây là tác vụ phân loại đơn giản, cần nhanh, không cần xoay vòng nhiều key.
- Đoạn xử lý `isinstance(content, list)` để gộp content khi Gemini trả về dạng danh sách phần tử thay vì chuỗi — một dạng phòng thủ lặp lại ở nhiều node để code không vỡ khi format đầu ra của model thay đổi.

Sau khi có kết quả, node phân nhánh:

```python
    if res["status"] == "REJECT":
        rejection_response = f"Là một trợ lý AI Tư vấn Pháp luật Việt Nam, tôi phải từ chối trả lời: {res['reason']}"
        return {
            "is_valid_query": False,
            "rejection_reason": res["reason"],
            "messages": [AIMessage(content=rejection_response)]
        }

    return {
        "is_valid_query": True,
        "rejection_reason": ""
    }
```

**Đầu ra.** Khi REJECT: ghi `is_valid_query=False`, `rejection_reason`, và **nối thẳng một `AIMessage` từ chối** vào `messages` (để nếu pipeline kết thúc tại đây thì vẫn có sẵn câu trả lời cho client). Khi PASS: chỉ ghi `is_valid_query=True`, không thêm tin nhắn nào.

**Định tuyến.** Hàm `route_after_guardrail` quyết định đi tiếp hay dừng dựa trên cờ vừa ghi:

```python
def route_after_guardrail(state: AgentState):
    if state.get("is_valid_query", False):
        return "query_analysis"
    return END
```

**Xử lý lỗi.** Guardrail thiết kế theo nguyên tắc **fail-closed** (an toàn khi lỗi): nếu lời gọi LLM ném exception (kể cả khi bộ lọc an toàn mặc định của Google chặn), `check_guardrail` trả về `REJECT` thay vì để câu hỏi lọt qua. Lựa chọn này phù hợp với miền pháp luật — thà từ chối nhầm còn hơn xử lý một câu hỏi đáng lẽ phải chặn.

**Lý do thiết kế.** Đặt một node lọc rẻ tiền ở đầu giúp dừng sớm các câu lạc đề/độc hại, tiết kiệm chi phí cho ChromaDB, web search và các lần gọi LLM đắt phía sau; đồng thời tách bạch trách nhiệm "kiểm duyệt" khỏi "trả lời".

## 9. Node Query Analysis - phân tích câu hỏi pháp lý

**Vai trò & vị trí.** Node thứ hai (chạy ngay sau Guardrail khi câu hỏi hợp lệ). Nhiệm vụ là chuyển câu hỏi tự nhiên thành **truy vấn pháp lý có cấu trúc**, đặc biệt là chuẩn bị sẵn hai truy vấn tối ưu: một cho tìm kiếm nội bộ (vector) và một cho tìm kiếm web. Việc này tách quyền "đặt truy vấn" ra khỏi Agent, để Agent không tự bịa từ khóa tìm kiếm tùy hứng.

**Đầu vào.** Đọc tin nhắn cuối cùng (câu hỏi người dùng):

```python
def query_analysis_node(state: AgentState) -> dict[str, Any]:
    messages = state["messages"]
    last_user_message = messages[-1].content

    llm_service = get_llm_service()
    start = time.time()
    analysis = llm_service.analyze_query_for_agent(last_user_message)
    logger.info(f"[TIMING] query_analysis: {time.time() - start:.2f}s")
```

**Xử lý.** Hàm `analyze_query_for_agent` (trong `rag-service/app/services/llm_service.py`) gọi LLM với `QUERY_ANALYSIS_PROMPT` ở chế độ `json_output=True`, `temperature=0.0`, và trả về một dict có cấu trúc. Điểm quan trọng là hàm này **không bao giờ ném lỗi ra node** — nó luôn có sẵn một `fallback` an toàn:

```python
def analyze_query_for_agent(self, query: str) -> Dict[str, Any]:
    fallback = {
        "legal_topic": query,
        "legal_domain": "",
        "relevant_laws": [],
        "internal_search_query": query,
        "web_search_query": query,
        "key_legal_terms": [w for w in query.split() if len(w) > 2],
        "analysis_summary": query,
    }

    if not self.available:
        return fallback

    try:
        response = self.generate(
            prompt=f"Câu hỏi của người dùng: {query}",
            system=QUERY_ANALYSIS_PROMPT,
            json_output=True,
            temperature=0.0,
        )
        if response:
            result = json.loads(response)
            ...
            return result
    except Exception as e:
        logger.warning(f"Query analysis for agent failed: {e}")

    return fallback
```

Nếu LLM không khả dụng hoặc parse JSON thất bại, hệ thống dùng **nguyên văn câu hỏi** làm cả `internal_search_query` lẫn `web_search_query` — pipeline vẫn chạy được, chỉ là chất lượng truy vấn kém hơn. Đây là dạng "graceful degradation".

Sau khi có kết quả, node **không trả dict thô** mà gói thành một `SystemMessage` chứa hướng dẫn ép Agent dùng đúng truy vấn đã tối ưu:

```python
    analysis_json = json.dumps(analysis, ensure_ascii=False, indent=2)
    ...
    analysis_message = SystemMessage(content=f"""KẾT QUẢ PHÂN TÍCH CÂU HỎI PHÁP LÝ:
{analysis_json}

HƯỚNG DẪN SỬ DỤNG:
- Khi gọi `retrieve_internal_law`: SỬ DỤNG CHÍNH XÁC giá trị "internal_search_query" làm tham số query.
- Khi gọi `search_web_for_law`: SỬ DỤNG CHÍNH XÁC giá trị "web_search_query" làm tham số query.
- KHÔNG tự sáng tạo query khác. Các query trên đã được tối ưu cho từng hệ thống tìm kiếm.""")

    return {
        "query_analysis": analysis_json,
        "messages": [analysis_message]
    }
```

**Đầu ra.** Ghi `query_analysis` (chuỗi JSON, sau này dùng để lấy `primary_topic` đặt tiêu đề hội thoại) và nối `SystemMessage` phân tích vào `messages`.

**Định tuyến.** Cạnh tĩnh `query_analysis → agent` (không rẽ nhánh).

**Lý do thiết kế.** Truy vấn nội bộ và truy vấn web cần dạng khác nhau: vector search cần cụm thuật ngữ pháp lý cô đọng, còn web search lại hợp với câu mang tính ngữ nghĩa tự nhiên. Tạo trước hai truy vấn riêng và **ép** Agent copy chính xác chúng giúp giảm nhiễu truy hồi và làm hành vi Agent ổn định, dễ tái lập hơn so với để Agent tự nghĩ từ khóa mỗi lần.

## 10. Node Agent - bộ não quyết định và tổng hợp

**Vai trò & vị trí.** Đây là node trung tâm, được gọi **lặp lại nhiều lần** trong vòng `agent ↔ tools`. Cùng một node đảm nhiệm hai vai trò tùy theo trạng thái hội thoại: (a) khi chưa đủ bằng chứng → quyết định gọi tool nào; (b) khi đã có đủ kết quả tool → tổng hợp câu trả lời cuối. Nó không tự trả lời bằng kiến thức sẵn có mà bị ràng buộc phải dựa trên kết quả tool.

**Đầu vào.** Đọc toàn bộ `messages` hiện có (gồm: câu hỏi gốc, `SystemMessage` phân tích, và mọi `ToolMessage` kết quả truy hồi của các vòng trước). Node ghép một system prompt rất dài lên đầu trước khi gọi LLM:

```python
def agent_node(state: AgentState) -> dict[str, Any]:
    tools = [retrieve_internal_law, search_web_for_law]
    today = datetime.now().strftime("%d/%m/%Y")
    system_prompt = f"""Bạn là một Luật sư Tư vấn Pháp luật Việt Nam cấp cao...
    ...
"""
    messages_to_pass = [{"role": "system", "content": system_prompt}] + list(state["messages"])

    iteration_count = state.get("iteration_count", 0) + 1
    start = time.time()
    response = _invoke_chat_agent_with_fallback(messages_to_pass, tools)
    logger.info(f"[TIMING] agent_invoke (iter {iteration_count}): {time.time() - start:.2f}s")

    return {"messages": [response], "iteration_count": iteration_count}
```

**Xử lý.** System prompt (chi tiết ở mục 21.11 và 21.12) mã hóa toàn bộ "luật chơi": ngày hiện tại để xác định hiệu lực văn bản; quy trình **bắt buộc gọi cả hai tool**; độ ưu tiên nguồn (web > nội bộ); cấu trúc câu trả lời; quy tắc xử lý văn bản cũ (⛔) và mới (✅); và phần "cấm tuyệt đối" chống bịa đặt. LLM được `bind_tools` để có thể phát ra `tool_calls`.

Việc gọi LLM đi qua `_invoke_chat_agent_with_fallback` — lớp chống chịu lỗi quan trọng. Nó thử lần lượt từng model trong chuỗi dự phòng, mỗi model thử lần lượt từng API key:

```python
def _invoke_chat_agent_with_fallback(messages_to_pass: list, tools: list):
    keys = settings.gemini_api_keys
    if not keys:
        raise RuntimeError("GEMINI_API_KEYS chưa cấu hình")

    primary = settings.agent_model
    model_chain: list[str] = [primary]
    for m in settings.fallback_models:
        if m and m not in model_chain:
            model_chain.append(m)

    last_error: Any = None
    for model_idx, model_name in enumerate(model_chain):
        for key_idx, key in enumerate(keys):
            try:
                llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=key, temperature=0.0, max_retries=2)
                llm_with_tools = llm.bind_tools(tools)
                response = llm_with_tools.invoke(messages_to_pass)
                return response
            except Exception as e:
                err_str = str(e).lower()
                last_error = e
                if "503" in err_str or "unavailable" in err_str or "overload" in err_str:
                    continue
                if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                    continue
                logger.error(f"[CHAT LLM] Fatal error model={model_name} key#{key_idx + 1}: {e}")
                raise
    raise last_error or RuntimeError("All models in chat fallback chain exhausted")
```

Logic xử lý lỗi rất rõ ràng: lỗi **503 (quá tải)** hoặc **429 (hết quota)** → bỏ qua, thử key/model kế tiếp (`continue`); lỗi khác (sai xác thực, request sai...) → ném ngay (`raise`) vì thử lại cũng vô ích. `temperature=0.0` để hành vi tất định.

**Đầu ra.** Nối `response` (một `AIMessage`, có thể kèm `tool_calls`) vào `messages`, và **tăng** `iteration_count`. Bộ đếm này chính là cơ sở cho cơ chế chống lặp vô hạn ở mục 13.

**Định tuyến.** Sau Agent là `route_after_agent` — phân tích kỹ ở mục 13.

**Lý do thiết kế.** Gộp "quyết định gọi tool" và "tổng hợp" vào cùng một node phản ánh đúng bản chất ReAct của LangGraph: model nhìn lại toàn bộ lịch sử (gồm kết quả tool) rồi tự quyết bước tiếp theo. Tách lớp `_invoke_chat_agent_with_fallback` giúp toàn bộ độ phức tạp về xoay key/đổi model nằm gọn một chỗ, không lẫn vào logic nghiệp vụ.

## 11. Tool retrieve_internal_law - truy hồi kho dữ liệu nội bộ

**Vai trò & vị trí.** Là một trong hai công cụ Agent gọi qua node `tools` (một `ToolNode` của LangGraph). Tool này truy hồi nguyên văn điều khoản từ ChromaDB. Khai báo của nó rất mỏng — chỉ là lớp vỏ gọi vào `RAGService`:

```python
@tool
def retrieve_internal_law(query: str) -> str:
    """Sử dụng công cụ này ĐẦU TIÊN để tìm kiếm các quy định pháp luật Việt Nam
    trong cơ sở dữ liệu nội bộ."""
    return _rag_service.retrieve_documents_for_agent(query=query, top_k=10)
```

**Đầu vào.** `query` — chính là giá trị `internal_search_query` mà Agent đã copy từ `SystemMessage` phân tích. Lưu ý: truy vấn này **đã được tối ưu**, nên `retrieve_documents_for_agent` không viết lại truy vấn nữa.

**Xử lý.** Trong `rag_service.py`, pipeline truy hồi cho Agent gồm 3 bước:

```python
# Step 1: Vector search (query already optimized by query_analysis_node)
r2 = self._vector_search(query)
# Step 2: Cross-Encoder Rerank
r3 = self._rerank(query, r2)
# Threshold 0.50: balanced
threshold = score_threshold or 0.50
docs = [d for d in r3 if d.get("score", 0) >= threshold][:top_k]
```

- `_vector_search`: encode truy vấn bằng bi-encoder rồi `query_by_embedding` trong ChromaDB lấy tối đa `vector_search_top_k` kết quả; điểm tương đồng tính bằng `score = max(0.0, 1.0 - distance)` (vì ChromaDB trả khoảng cách cosine).
- `_rerank`: chấm lại bằng cross-encoder, chuẩn hóa điểm về [0,1], rồi trộn `blended = (vector*0.3) + (cross_encoder*0.7)` và cộng/trừ nhẹ theo năm ban hành (công thức đầy đủ ở mục 21.14).
- Lọc theo ngưỡng `0.50` và lấy `top_k=10`.

Sau đó tool phát hiện xung đột thời gian giữa các văn bản cùng nhóm và **định dạng kết quả thành văn bản có ranh giới rõ ràng** kèm nhãn ⛔/✅ (chi tiết ở mục 21.15), để Agent không nhầm văn bản hết hiệu lực thành quy định hiện hành.

**Đầu ra.** Tool trả về **một chuỗi text**. `ToolNode` bọc chuỗi này thành một `ToolMessage` (với `name="retrieve_internal_law"`) và nối vào `messages`. Chính nhờ `name` này mà node định tuyến đếm được "tool nào đã gọi" (mục 13). Nếu không tìm thấy gì đạt ngưỡng, tool trả về câu gợi ý Agent chuyển sang dùng web search.

**Lý do thiết kế.** Trả về text đã định dạng (thay vì object thô) cho phép "nhúng" các chỉ dẫn/nhãn cảnh báo ngay trong ngữ cảnh mà Agent đọc — một kỹ thuật prompt-context để ràng buộc cách Agent dùng dữ liệu.

## 12. Tool search_web_for_law - tra cứu nguồn hiện hành trên web

**Vai trò & vị trí.** Công cụ thứ hai trong node `tools`. Mục tiêu là kiểm chứng trạng thái hiệu lực và tìm quy định mới nhất — bù cho nhược điểm "dữ liệu nội bộ có thể đã cũ".

**Đầu vào.** `query` — giá trị `web_search_query` Agent copy từ phân tích.

**Xử lý.** Điểm đặc trưng là **chạy song song hai nguồn** bằng `ThreadPoolExecutor` để giảm độ trễ:

```python
@tool
def search_web_for_law(query: str) -> str:
    ...
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        tavily_future = executor.submit(_search_tavily, query)
        google_future = executor.submit(_search_google_grounding, query)
        tavily_result = tavily_future.result()
        google_result = google_future.result()
    ...
    parts = []
    if google_result:
        parts.append(f"══ KẾT QUẢ TỪ GOOGLE SEARCH (REALTIME) ══\n{google_result}")
    if tavily_result:
        parts.append(f"══ KẾT QUẢ TỪ NGUỒN TIN PHÁP LUẬT ══\n{tavily_result}")
    if not parts:
        return "Không tìm thấy kết quả tra cứu web cho truy vấn này."
    return "\n\n".join(parts)
```

- `_search_tavily`: ưu tiên danh sách domain pháp luật chính thống (`VIETNAM_LAW_DOMAINS`: thuvienphapluat.vn, chinhphu.vn, quochoi.vn, moj.gov.vn...); nếu được ít hơn 2 kết quả thì nới rộng tìm kiếm chung.
- `_search_google_grounding`: dùng Google Search Grounding tích hợp trong Gemini, kèm yêu cầu ưu tiên văn bản mới nhất và trả nội dung cụ thể.
- Cả hai đều đi qua `_build_time_aware_query` để thêm năm hiện tại + "mới nhất" vào truy vấn, đẩy kết quả mới lên.

Khi gộp, **kết quả Google Grounding (realtime) đặt trước** kết quả Tavily, phản ánh đúng độ ưu tiên nguồn đã quy định trong prompt của Agent.

**Đầu ra.** Trả về chuỗi text gộp → `ToolNode` bọc thành `ToolMessage` (`name="search_web_for_law"`) và nối vào `messages`.

**Xử lý lỗi.** Mỗi nguồn tự bắt exception và trả chuỗi rỗng khi lỗi (`_search_tavily`/`_search_google_grounding` đều bọc try/except), nên một nguồn hỏng không làm hỏng cả tool — vẫn còn nguồn kia.

**Lý do thiết kế.** Chạy song song để tổng thời gian chờ xấp xỉ nguồn chậm hơn thay vì cộng dồn; giới hạn domain để web search không phải tìm kiếm tự do mà bám nguồn có thẩm quyền; ưu tiên realtime để bắt kịp thay đổi pháp luật.

## 13. Định tuyến quanh Agent và điều kiện chuyển sang Verifier

**Vai trò.** Đây không phải một node mà là **hàm định tuyến** `route_after_agent`, nhưng nó là "bộ điều khiển" quan trọng nhất của pipeline: quyết định Agent đi gọi tool, quay lại tự suy nghĩ, hay được phép trả lời.

```python
def route_after_agent(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    # If agent wants to call tools → allow it
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"

    # Agent wants to answer → check if both tools have been called
    tool_names_called = {
        m.name for m in messages
        if hasattr(m, "name") and getattr(m, "type", None) == "tool"
    }
    required_tools = {"retrieve_internal_law", "search_web_for_law"}

    # Guard against infinite loop: max 6 iterations
    iteration_count = state.get("iteration_count", 0)
    if iteration_count >= 6:
        return "verifier"

    if not required_tools.issubset(tool_names_called):
        # Not all tools called yet, send back to agent
        return "agent"

    # Both tools called → send to verifier for hallucination check + correction
    return "verifier"
```

Có thể đọc logic này như **ba lớp kiểm soát xếp chồng**:

1. **Lớp ưu tiên hành động tool.** Nếu tin nhắn cuối của Agent chứa `tool_calls`, đi tới `tools` ngay — Agent đang muốn tra cứu.
2. **Lớp chống lặp vô hạn.** Nếu `iteration_count >= 6`, ép sang `verifier` bất kể đã gọi đủ tool hay chưa. Đây là van an toàn: dù Agent có "lưỡng lự" mãi thì pipeline vẫn kết thúc.
3. **Lớp ép đủ bằng chứng.** Tập `tool_names_called` được dựng từ `name` của các `ToolMessage` trong lịch sử. Nếu chưa gọi đủ **cả hai** tool bắt buộc (`required_tools.issubset(...)` là False) → trả về `agent`, buộc Agent suy nghĩ tiếp (thường là để gọi nốt tool còn thiếu). Chỉ khi đã có đủ hai nhóm bằng chứng, Agent mới được sang `verifier`.

Đây chính là câu trả lời cho phản biện "dựa vào đâu Agent biết đã đủ bằng chứng": hệ thống **không tin tưởng tuyệt đối** vào quyết định của LLM, mà dùng graph để cưỡng chế quy trình tối thiểu (đủ 2 nguồn) và chặn lặp vô hạn.

**Lý do thiết kế.** Tách điều kiện dừng ra một hàm thuần (chỉ đọc state, không gọi LLM) giúp hành vi tất định, dễ kiểm thử và dễ giải thích khi bảo vệ — khác hẳn việc phó mặc cho prompt "hãy nhớ gọi đủ tool".

## 14. Node Verifier - kiểm chứng và sửa câu trả lời

**Vai trò & vị trí.** Node áp chót trước `END`. Nó vừa là **giám khảo** (phát hiện bịa đặt) vừa là **người sửa bài** (cắt bỏ phần vô căn cứ) trong một bước duy nhất, nên không cần vòng lặp thử lại.

**Đầu vào.** Node tự bóc tách hai thứ từ `messages`: (1) câu trả lời cuối của Agent — là `AIMessage` cuối cùng **không có** `tool_calls`; (2) toàn bộ kết quả tool, mỗi tool bị cắt còn tối đa 4000 ký tự để giảm độ trễ:

```python
    # 1. Extract agent's final answer (last AIMessage without tool_calls)
    agent_answer = None
    for m in reversed(messages):
        if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None):
            content = m.content
            if isinstance(content, list):
                content = "\n".join(... )  # gộp content dạng list
            agent_answer = content
            break

    # 2. Collect all tool results (truncated)
    MAX_TOOL_CHARS = 4000  # Per tool — concise context for fast verification
    tool_results = []
    for m in messages:
        if hasattr(m, "name") and getattr(m, "type", None) == "tool":
            content = m.content
            if len(content) > MAX_TOOL_CHARS:
                content = content[:MAX_TOOL_CHARS] + f"\n... [TRUNCATED — {len(m.content)} chars total]"
            tool_results.append(f"[Tool: {m.name}]\n{content}")
    tool_context = "\n\n".join(tool_results)
```

Nếu không tìm thấy câu trả lời nào (rỗng), node trả về ngay một thông điệp an toàn thay vì để pipeline trả về rỗng.

**Xử lý.** Verifier dùng model mạnh nhất (`settings.verifier_model`, mặc định `gemini-2.5-pro`) với chuỗi dự phòng giống Agent, nhưng cấu hình "chạy nhanh" — **tắt thinking** và giới hạn output:

```python
    def _build_verifier(model_name: str, key: str):
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=key,
            temperature=0.0,
            max_retries=2,
            max_output_tokens=4096,
            model_kwargs={"thinking_config": {"thinking_budget": 0}},
        )
```

Prompt kiểm chứng (chi tiết ở mục 21.18) yêu cầu đối chiếu từng trích dẫn, **từng con số** (mức phạt, thời hạn, số điểm trừ), quan hệ "Điều X sửa bởi Luật Y", và quy tắc tách bạch văn bản cũ ⛔ / mới ✅. Đầu ra của Verifier bị ép về JSON `{"verdict", "issues", "corrected_answer"}`. Node thử chuỗi model × key với cùng cơ chế bỏ qua 503/429.

Sau khi gọi xong, node parse JSON (có bóc cặp ```` ``` ```` nếu model lỡ bọc markdown) và quyết định:

```python
    if verdict == "PASS":
        return {"messages": [AIMessage(content=agent_answer)]}

    # FAIL → use the corrected answer from verifier
    if corrected_answer and corrected_answer.strip() and corrected_answer.strip().upper() != "SAME":
        return {"messages": [AIMessage(content=corrected_answer)]}

    # Corrected answer is empty or "SAME" → fallback to original
    return {"messages": [AIMessage(content=agent_answer)]}
```

**Đầu ra.** Nối vào `messages` một `AIMessage` là câu trả lời cuối cùng: giữ nguyên bản gốc nếu PASS, dùng bản đã sửa nếu FAIL.

**Định tuyến.** Cạnh tĩnh `verifier → END`. Verifier sửa tại chỗ nên không cần vòng lặp quay lại.

**Xử lý lỗi (fail-open).** Khác với Guardrail (fail-closed), Verifier thiết kế **fail-open**: nếu parse JSON thất bại, hoặc gặp lỗi không recover được, hoặc cạn toàn bộ model/key, node trả về **câu trả lời gốc của Agent** thay vì chặn người dùng. Triết lý: Verifier là lớp tăng cường chất lượng, không nên biến lỗi hạ tầng của riêng nó thành "mất câu trả lời".

**Lý do thiết kế.** Hợp nhất "chấm + sửa" trong một lần gọi loại bỏ nhu cầu vòng lặp retry (tránh tăng độ trễ và rủi ro dao động). Chiến lược **sửa tối thiểu** (chỉ xóa phần vô căn cứ, cấm viết thêm) tránh việc bước kiểm chứng lại tự sinh ra hallucination mới — một rủi ro thực tế khi yêu cầu LLM "viết lại cho đúng".

## 15. RAG Service trả kết quả về Main Service

Sau khi pipeline hoàn tất, RAG Service trả về sự kiện `done` cho Main Service. Kết quả gồm:

- Câu trả lời cuối cùng.
- Danh sách nguồn tham chiếu.
- Kết quả phân tích câu hỏi.
- Thời gian xử lý.
- Thông tin mô hình xử lý.

Trong luồng streaming, trước sự kiện `done`, RAG Service còn gửi nhiều sự kiện `progress`. Các sự kiện này được Main Service chuyển tiếp cho client để giao diện hiển thị tiến trình xử lý.

Các bước progress cố định của chat chính gồm:

```text
1. Đang kiểm tra câu hỏi
2. Đang phân tích chủ đề
3. Đang tra cứu nguồn
4. Đang tổng hợp câu trả lời
5. Đang kiểm tra độ chính xác
```

Nhờ đó người dùng không chỉ thấy câu trả lời cuối cùng, mà còn hiểu hệ thống đang làm gì trong quá trình xử lý.

## 16. Main Service lưu câu trả lời vào PostgreSQL

Khi Main Service nhận kết quả cuối cùng từ RAG Service, hệ thống lưu tin nhắn assistant vào bảng `messages`. Tin nhắn này gồm:

- Nội dung câu trả lời.
- Vai trò `assistant`.
- Danh sách nguồn tham chiếu.
- Metadata như thời gian xử lý, thông tin phân tích câu hỏi.

Nếu đây là hội thoại mới, Main Service cập nhật tiêu đề hội thoại. Tiêu đề được ưu tiên lấy từ chủ đề chính do RAG Service phân tích. Nếu không có chủ đề chính, hệ thống dùng một phần nội dung câu hỏi làm tiêu đề tạm.

Sau khi lưu assistant message thành công, Main Service mới gửi sự kiện `done` về client. Điều này đảm bảo câu trả lời người dùng nhìn thấy trên giao diện cũng đã được lưu trong cơ sở dữ liệu.

## 17. Sinh câu hỏi gợi ý sau khi trả lời

Sau khi câu trả lời chính hoàn tất, hệ thống chạy ngầm một tác vụ sinh câu hỏi gợi ý. Tác vụ này không chặn luồng trả lời chính.

Main Service gửi câu hỏi ban đầu và phần tóm tắt câu trả lời sang RAG Service để tạo danh sách câu hỏi tiếp theo phù hợp. Khi có kết quả, hệ thống cập nhật metadata của tin nhắn assistant trong PostgreSQL.

Client có thể gọi endpoint riêng để lấy danh sách câu hỏi gợi ý. Nếu background task chưa xử lý xong, endpoint trả về danh sách rỗng. Cách này giúp câu trả lời chính hiển thị nhanh hơn, còn phần gợi ý được bổ sung sau.

## 18. Client nhận và hiển thị kết quả

Ở phía ứng dụng, client nhận các sự kiện SSE từ Main Service.

Khi nhận `ready`, client biết hội thoại đã được tạo hoặc xác nhận, đồng thời có thông tin tin nhắn người dùng để hiển thị ngay trên giao diện.

Khi nhận `progress`, client cập nhật trạng thái Thinking Panel, cho người dùng thấy hệ thống đang kiểm tra, phân tích, tra cứu, tổng hợp hoặc kiểm chứng.

Khi nhận `done`, client hiển thị câu trả lời hoàn chỉnh, nguồn tham chiếu và cập nhật lại hội thoại.

Nếu nhận `error`, client hiển thị thông báo lỗi phù hợp thay vì để trạng thái loading kéo dài.

## 19. Tóm tắt luồng xử lý

Toàn bộ luồng chat chính có thể tóm tắt như sau:

```text
Người dùng gửi câu hỏi
-> Client gọi /chat/messages/stream với JWT
-> Main Service xác thực người dùng
-> Tạo hoặc kiểm tra hội thoại
-> Lấy 6 tin nhắn gần nhất làm ngữ cảnh
-> Lưu user message
-> Gửi request nội bộ sang RAG Service
-> RAG Service chạy Guardrail
-> Phân tích câu hỏi pháp lý
-> Agent truy hồi kho dữ liệu nội bộ
-> Agent tra cứu nguồn hiện hành trên web
-> Agent tổng hợp câu trả lời
-> Verifier kiểm chứng và sửa nếu cần
-> RAG Service trả answer, sources, metadata
-> Main Service lưu assistant message
-> Client nhận câu trả lời qua SSE
-> Background task sinh câu hỏi gợi ý
```

Thiết kế này giúp hệ thống đạt ba mục tiêu chính. Thứ nhất, câu trả lời có căn cứ vì được truy hồi từ nguồn dữ liệu pháp luật và nguồn cập nhật. Thứ hai, trải nghiệm người dùng tốt hơn nhờ SSE streaming và hiển thị tiến trình xử lý. Thứ ba, độ tin cậy được cải thiện nhờ bước kiểm chứng sau khi Agent tổng hợp câu trả lời.

## 20. Các file code chính liên quan

Các file quan trọng của luồng chat chính gồm:

- `vietnam-law-service/main-service/app/api/v1/chat.py`: định nghĩa API chat, bao gồm endpoint gửi tin nhắn thường và gửi tin nhắn streaming.
- `vietnam-law-service/main-service/app/services/chat_service.py`: xử lý nghiệp vụ hội thoại, lấy context, lưu tin nhắn, gọi RAG Service và lưu câu trả lời.
- `vietnam-law-service/main-service/app/services/rag_client.py`: client nội bộ để Main Service gọi RAG Service.
- `vietnam-law-service/rag-service/app/api/v1/rag_stream.py`: endpoint SSE streaming của RAG Service, phát progress và done event.
- `vietnam-law-service/rag-service/app/agent/graph.py`: định nghĩa đồ thị Agentic RAG.
- `vietnam-law-service/rag-service/app/agent/nodes.py`: triển khai các node Guardrail, Query Analysis, Agent và Verifier.
- `vietnam-law-service/rag-service/app/tools/internal_law_tool.py`: công cụ truy hồi kho dữ liệu pháp luật nội bộ.
- `vietnam-law-service/rag-service/app/tools/web_search.py`: công cụ tra cứu nguồn pháp luật hiện hành trên web.
- `vietnam-law-service/rag-service/app/services/rag_service.py`: xử lý vector search, rerank và định dạng kết quả truy hồi cho Agent.

## 21. Các đoạn code kỹ thuật quan trọng

Phần này ghi lại các đoạn code quan trọng nhất của luồng chat chính. Mục đích không phải là liệt kê toàn bộ source code, mà là chỉ ra những điểm then chốt cần nắm để giải thích khi bảo vệ hoặc phản biện.

### 21.1. Endpoint SSE của Main Service

Endpoint chính của luồng chat realtime nằm trong `main-service/app/api/v1/chat.py`. Đây là nơi nhận request từ client, xác thực user bằng JWT và trả về `StreamingResponse`.

```python
@router.post("/messages/stream")
async def send_message_stream(
        data: ChatRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
):
    chat_service = ChatService(db)
    user_id = str(current_user.id)

    async def event_stream():
        assistant_msg_id: str | None = None
        assistant_answer: str | None = None
        try:
            async for ev in chat_service.send_message_stream(
                user_id=user_id,
                content=data.message,
                conversation_id=data.conversation_id,
            ):
                if ev["event"] == "done":
                    msg = ev["data"].get("assistant_message") or {}
                    assistant_msg_id = msg.get("id")
                    assistant_answer = msg.get("content")
                yield f"event: {ev['event']}\ndata: {json.dumps(ev['data'], ensure_ascii=False)}\n\n"
        except Exception:
            yield f"event: error\ndata: {json.dumps({'message': 'Lỗi xử lý'}, ensure_ascii=False)}\n\n"
            return
```

Điểm cần hiểu ở đoạn này:

- `current_user` được lấy từ `get_current_user`, nghĩa là mọi request chat đều phải có access token hợp lệ.
- `event_stream()` là async generator, mỗi lần `yield` sẽ đẩy một SSE event về client.
- Khi nhận event `done`, Main Service ghi lại `assistant_msg_id` và `assistant_answer` để sau đó sinh câu hỏi gợi ý ở background.
- Nếu có lỗi trong quá trình stream, server không để kết nối treo mà trả về event `error`.

Cuối endpoint, Main Service trả response dạng SSE:

```python
return StreamingResponse(
    event_stream(),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
)
```

`X-Accel-Buffering: no` giúp tránh việc proxy buffer dữ liệu, đảm bảo event được đẩy dần về client thay vì chờ gom đủ response.

### 21.2. Tạo hoặc kiểm tra hội thoại

Trong `ChatService.send_message_stream`, bước đầu tiên là xác định hội thoại:

```python
is_new_conversation = False
if conversation_id:
    conv = await self.conv_repo.get_by_id(conversation_id)
    if not conv or str(conv.user_id) != user_id:
        yield {"event": "error", "data": {"message": "Không tìm thấy cuộc hội thoại"}}
        return
else:
    conv = await self.conv_repo.create(
        user_id=user_id,
        data=ConversationCreate(title=None),
    )
    is_new_conversation = True
```

Đoạn này thể hiện hai nguyên tắc quan trọng:

- Nếu là hội thoại cũ, hệ thống kiểm tra quyền sở hữu bằng cách so sánh `conv.user_id` với `user_id` hiện tại.
- Nếu là hội thoại mới, hệ thống tạo trước conversation với title rỗng, sau đó cập nhật title bằng chủ đề chính khi RAG Service trả kết quả.

Cách làm này giúp tránh lỗi bảo mật kiểu user A truy cập hội thoại của user B chỉ bằng cách đoán `conversation_id`.

### 21.3. Lấy context và cắt ngắn câu trả lời cũ

Với hội thoại cũ, hệ thống lấy 6 tin nhắn gần nhất:

```python
context_messages: List[Message] = []
if not is_new_conversation:
    context_messages, _ = await self.msg_repo.get_latest_messages(
        conversation_id=conv_id,
        limit=6,
    )
```

Sau đó, các câu trả lời của assistant nếu quá dài sẽ được cắt ngắn:

```python
ASSISTANT_CONTEXT_LIMIT = 300
context = []
for msg in context_messages:
    msg_content = msg.content
    if msg.role == "assistant" and len(msg_content) > ASSISTANT_CONTEXT_LIMIT:
        msg_content = msg_content[:ASSISTANT_CONTEXT_LIMIT] + "..."
    context.append({"role": msg.role, "content": msg_content})
```

Đây là một tối ưu kỹ thuật quan trọng. Lịch sử hội thoại giúp hệ thống hiểu câu hỏi nối tiếp, nhưng nếu đưa toàn bộ câu trả lời cũ vào prompt, hệ thống sẽ tốn token, tăng latency và dễ bị lệch trọng tâm. Vì vậy user message được giữ nguyên, còn assistant message dài được rút gọn.

### 21.4. Lưu user message trước khi gọi RAG Service

Ở luồng streaming, Main Service lưu tin nhắn người dùng trước khi gọi RAG Service:

```python
user_msg = await self.msg_repo.create(
    conversation_id=conv_id,
    role="user",
    content=content,
)

yield {
    "event": "ready",
    "data": {
        "conversation_id": conv_id,
        "is_new_conversation": is_new_conversation,
        "user_message": _msg_to_stream_dict(user_msg),
    },
}
```

Event `ready` có vai trò báo cho client rằng:

- Hội thoại đã được tạo hoặc xác nhận.
- Tin nhắn user đã được lưu.
- Client có thể hiển thị tin nhắn user ngay, không cần chờ RAG Service xử lý xong.

Cách này làm giao diện phản hồi nhanh hơn và giúp dữ liệu hội thoại không bị mất nếu phần sinh câu trả lời gặp lỗi.

### 21.5. Gọi RAG Service bằng streaming client

Main Service gọi RAG Service thông qua `rag_client.stream_agent_search`:

```python
async for event in rag_client.stream_agent_search(
    query=content,
    context=context,
    top_k=5,
    include_sources=True,
):
    if event["event"] == "done":
        final_payload = event["data"]
    elif event["event"] == "error":
        yield event
        return
    else:
        yield event
```

Ý nghĩa của đoạn này:

- Các event `progress` từ RAG Service được forward trực tiếp về client.
- Event `done` chưa forward ngay, vì Main Service cần lưu assistant message trước.
- Nếu RAG Service trả lỗi, Main Service dừng luồng và gửi lỗi về client.

Trong `rag_client.py`, request nội bộ được gửi như sau:

```python
async with client.stream(
    "POST",
    f"{self.base_url}/api/v1/rag/agent-search/stream",
    json={
        "query": query,
        "top_k": top_k,
        "include_sources": include_sources,
        "context": context,
    },
    headers={
        "X-API-Key": settings.rag_service_api_key,
        "X-Internal-Service": "main-service",
        "Accept": "text/event-stream",
    },
) as response:
    async for event in _parse_sse_lines(response):
        yield event
```

Đây là phần thể hiện rõ kiến trúc tách service: client không gọi RAG Service trực tiếp; Main Service gọi bằng internal API key.

### 21.6. Parse SSE frame từ RAG Service

RAG Service trả dữ liệu theo format SSE:

```text
event: progress
data: {"steps": [...]}

event: done
data: {"answer": "...", "sources": [...]}
```

Main Service đọc stream bằng `_parse_sse_lines`:

```python
event_name = "message"
data_buf: List[str] = []
async for line in response.aiter_lines():
    if line == "":
        if data_buf:
            raw = "\n".join(data_buf)
            data = json.loads(raw)
            yield {"event": event_name, "data": data}
        event_name = "message"
        data_buf = []
        continue
    if line.startswith("event:"):
        event_name = line[6:].strip()
    elif line.startswith("data:"):
        data_buf.append(line[5:].lstrip())
```

SSE frame kết thúc bằng một dòng rỗng. Hàm này gom các dòng `data:` lại, parse JSON và trả về object thống nhất cho `ChatService`.

### 21.7. Đồ thị LangGraph của Agentic RAG

Pipeline Agentic RAG được định nghĩa trong `rag-service/app/agent/graph.py`:

```python
workflow = StateGraph(AgentState)

workflow.add_node("guardrail", guardrail_node)
workflow.add_node("query_analysis", query_analysis_node)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tools_node)
workflow.add_node("verifier", verification_node)

workflow.set_entry_point("guardrail")
```

Các cạnh điều hướng:

```python
workflow.add_conditional_edges("guardrail", route_after_guardrail)
workflow.add_edge("query_analysis", "agent")
workflow.add_conditional_edges("agent", route_after_agent)
workflow.add_edge("tools", "agent")
workflow.add_edge("verifier", END)
```

Ý nghĩa:

- Luồng luôn bắt đầu từ `guardrail`.
- Nếu câu hỏi không hợp lệ, kết thúc sớm.
- Nếu hợp lệ, chuyển sang `query_analysis`.
- Agent có thể gọi tool, sau đó quay lại Agent.
- Khi đủ điều kiện, câu trả lời được chuyển sang `verifier`.

### 21.8. Điều kiện Agent được chuyển sang Verifier

Điểm phản biện rất quan trọng là: hệ thống dựa vào đâu để biết Agent đã thu thập đủ bằng chứng?

Trong code, cơ chế này nằm ở `route_after_agent`:

```python
tool_names_called = {
    m.name for m in messages
    if hasattr(m, "name") and getattr(m, "type", None) == "tool"
}
required_tools = {"retrieve_internal_law", "search_web_for_law"}

iteration_count = state.get("iteration_count", 0)
if iteration_count >= 6:
    return "verifier"

if not required_tools.issubset(tool_names_called):
    return "agent"

return "verifier"
```

Như vậy, hệ thống không chỉ để LLM tự do quyết định. Có ba lớp kiểm soát:

- Graph bắt buộc Agent phải gọi đủ hai tool: truy hồi nội bộ và tra cứu web.
- Nếu Agent chưa gọi đủ tool, graph ép quay lại node `agent`, không cho chuyển sang `verifier`.
- Nếu số vòng lặp quá nhiều, hệ thống chuyển sang `verifier` để tránh lặp vô hạn.

Sau khi hai nhóm bằng chứng tối thiểu đã có, Agent có thể tổng hợp câu trả lời. Tuy nhiên câu trả lời vẫn phải đi qua Verifier để kiểm chứng lại.

### 21.9. Guardrail node

Node Guardrail kiểm tra câu hỏi trước khi chạy toàn bộ pipeline:

```python
def guardrail_node(state: AgentState) -> dict[str, Any]:
    messages = state["messages"]
    last_user_message = messages[-1].content

    res = check_guardrail(last_user_message)

    if res["status"] == "REJECT":
        rejection_response = (
            f"Là một trợ lý AI Tư vấn Pháp luật Việt Nam, "
            f"tôi phải từ chối trả lời: {res['reason']}"
        )
        return {
            "is_valid_query": False,
            "rejection_reason": res["reason"],
            "messages": [AIMessage(content=rejection_response)]
        }

    return {
        "is_valid_query": True,
        "rejection_reason": ""
    }
```

Nếu `is_valid_query = False`, graph đi thẳng tới `END`. Điều này giúp hệ thống tiết kiệm tài nguyên vì không cần chạy truy hồi, web search hoặc verifier cho câu hỏi không thuộc phạm vi.

### 21.10. Query Analysis prompt

Sau Guardrail, hệ thống phân tích câu hỏi và inject kết quả vào message dưới dạng `SystemMessage`. Phần prompt quan trọng:

```python
analysis_message = SystemMessage(content=f"""KẾT QUẢ PHÂN TÍCH CÂU HỎI PHÁP LÝ:
{analysis_json}

HƯỚNG DẪN SỬ DỤNG:
- Khi gọi `retrieve_internal_law`: SỬ DỤNG CHÍNH XÁC giá trị "internal_search_query" làm tham số query.
- Khi gọi `search_web_for_law`: SỬ DỤNG CHÍNH XÁC giá trị "web_search_query" làm tham số query.
- KHÔNG tự sáng tạo query khác. Các query trên đã được tối ưu cho từng hệ thống tìm kiếm.""")
```

Đây là prompt then chốt vì nó giới hạn cách Agent gọi tool. Agent không tự viết lại query theo cảm tính, mà phải dùng đúng truy vấn đã được tối ưu cho từng hệ thống:

- `internal_search_query`: dùng cho vector search trong ChromaDB.
- `web_search_query`: dùng cho nguồn tra cứu hiện hành.

Thiết kế này giúp giảm nhiễu truy hồi. Câu hỏi tự nhiên của người dùng có thể dài, thiếu thuật ngữ pháp lý hoặc chứa nhiều chi tiết cá nhân; query analysis giúp rút về các cụm từ pháp lý có giá trị tìm kiếm cao hơn.

### 21.11. Agent prompt - quy tắc dùng công cụ

Prompt của Agent rất dài, nhưng các ràng buộc quan trọng nhất có thể tóm tắt bằng các đoạn sau:

```text
Bạn có 2 công cụ tra cứu:
1. retrieve_internal_law — Tra cứu nguyên văn điều khoản từ DB nội bộ.
2. search_web_for_law — Tìm kiếm quy định hiện hành.

QUY TRÌNH BẮT BUỘC:
1. TRA CỨU NGUYÊN VĂN: Gọi retrieve_internal_law.
2. XÁC MINH VÀ CẬP NHẬT: BẮT BUỘC gọi search_web_for_law.
```

Prompt cũng quy định thứ tự ưu tiên nguồn:

```text
ĐỘ ƯU TIÊN NGUỒN:
1. Kết quả web từ search_web_for_law.
2. Dữ liệu nội bộ từ retrieve_internal_law.
```

Lý do của quy tắc này là pháp luật có tính thời điểm. Dữ liệu nội bộ giúp lấy nội dung điều khoản có cấu trúc, nhưng nguồn web giúp kiểm tra hiệu lực và văn bản mới hơn. Nếu có mâu thuẫn, hệ thống ưu tiên nguồn phản ánh trạng thái hiện hành.

### 21.12. Agent prompt - quy tắc chống bịa đặt

Prompt của Agent cấm sinh câu trả lời không có căn cứ:

```text
Mọi quy định pháp luật, số điều, số khoản, nội dung điều luật trong câu trả lời
PHẢI có nguồn từ kết quả công cụ tìm kiếm. KHÔNG CÓ NGOẠI LỆ.

CẤM:
- Bịa số điều, khoản, điểm không xuất hiện trong kết quả.
- Thêm nội dung điều luật mà công cụ không trả về.
- Nói "Theo Điều X..." nếu Điều X không có trong kết quả.
- Sử dụng kiến thức riêng về luật pháp để bổ sung.
- Trình bày quy định cũ đã hết hiệu lực như thể vẫn còn hiệu lực.
```

Đây là phần rất quan trọng để giải thích vì sao hệ thống không coi LLMs là nguồn tri thức pháp luật độc lập. LLMs chỉ được dùng để lập luận và trình bày dựa trên bằng chứng đã được tool cung cấp.

### 21.13. Tool truy hồi nội bộ

Tool `retrieve_internal_law` nằm trong `internal_law_tool.py`:

```python
@tool
def retrieve_internal_law(query: str) -> str:
    """
    Sử dụng công cụ này ĐẦU TIÊN để tìm kiếm các quy định pháp luật Việt Nam
    trong cơ sở dữ liệu nội bộ.
    """
    return _rag_service.retrieve_documents_for_agent(query=query, top_k=10)
```

Tool này gọi vào `RAGService.retrieve_documents_for_agent`. Bên trong đó, luồng truy hồi gồm:

```python
r2 = self._vector_search(query)
r3 = self._rerank(query, r2)
threshold = score_threshold or 0.50
docs = [d for d in r3 if d.get("score", 0) >= threshold][:top_k]
```

Ý nghĩa:

- `_vector_search`: tìm các chunk liên quan bằng vector similarity trong ChromaDB.
- `_rerank`: sắp xếp lại ứng viên bằng cross-encoder reranking.
- `threshold = 0.50`: lọc bỏ kết quả có độ liên quan thấp.
- `top_k`: giới hạn số tài liệu đưa cho Agent.

### 21.14. Công thức điểm rerank

Trong `rag_service.py`, điểm cuối cùng được kết hợp từ vector score và cross-encoder score:

```python
ce_norm = (raw_scores[i] - ce_min) / ce_range
blended = (c["score"] * 0.3) + (ce_norm * 0.7)
```

Trong đó:

- `c["score"]`: điểm tương đồng vector từ ChromaDB.
- `ce_norm`: điểm rerank đã chuẩn hóa về khoảng 0-1.
- `0.3` và `0.7`: trọng số kết hợp, ưu tiên cross-encoder hơn vector score.

Hệ thống cũng cộng/trừ nhẹ theo năm ban hành:

```python
if years_old <= 2:
    blended += 0.05
elif years_old <= 5:
    blended += 0.02
elif years_old > 10:
    blended -= 0.03
```

Ý nghĩa kỹ thuật: vector search giúp lấy nhanh ứng viên liên quan, còn cross-encoder rerank đánh giá lại mức liên quan chính xác hơn. Year boost giúp ưu tiên nhẹ các văn bản mới hơn trong trường hợp điểm gần nhau.

### 21.15. Định dạng kết quả truy hồi cho Agent

Sau khi chọn được tài liệu phù hợp, RAG Service không trả object thô cho Agent mà định dạng thành văn bản có cấu trúc:

```python
result_text += f"Số hiệu: {law_id}\n"
result_text += f"Điều: {metadata.get('article_id', 'N/A')}\n"
result_text += f"Tên điều: {metadata.get('title', 'N/A')}\n"
result_text += f"Năm ban hành: {metadata.get('year', 'N/A')}\n"
result_text += f"Nội dung nguyên văn:\n{d.get('document', '')}\n"
```

Nếu phát hiện văn bản cũ trong nhóm kết quả, hệ thống đánh dấu:

```python
result_text += f"VĂN BẢN CŨ (ĐÃ BỊ THAY THẾ BỞI: {newer})\n"
```

Việc bọc kết quả bằng nhãn rõ ràng giúp Agent phân biệt đâu là nội dung có căn cứ, đâu là văn bản cũ, đâu là văn bản mới hơn. Đây là một kỹ thuật prompt-context quan trọng để giảm nguy cơ trộn quy định cũ và mới.

### 21.16. Tool tra cứu web

Tool `search_web_for_law` kết hợp hai nguồn tìm kiếm:

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    tavily_future = executor.submit(_search_tavily, query)
    google_future = executor.submit(_search_google_grounding, query)
    tavily_result = tavily_future.result()
    google_result = google_future.result()
```

Sau đó kết quả được gộp lại:

```python
if google_result:
    parts.append(f"══ KẾT QUẢ TỪ GOOGLE SEARCH (REALTIME) ══\n{google_result}")

if tavily_result:
    parts.append(f"══ KẾT QUẢ TỪ NGUỒN TIN PHÁP LUẬT ══\n{tavily_result}")
```

Lý do chạy song song là giảm latency. Nếu chạy tuần tự, tổng thời gian chờ sẽ bằng thời gian của cả hai nguồn cộng lại. Khi chạy song song, thời gian chờ xấp xỉ nguồn chậm hơn.

Tavily search ưu tiên các domain pháp luật Việt Nam:

```python
VIETNAM_LAW_DOMAINS = [
    "thuvienphapluat.vn",
    "luatvietnam.vn",
    "chinhphu.vn",
    "quochoi.vn",
    "vanban.chinhphu.vn",
    "congbao.chinhphu.vn",
    "moj.gov.vn",
    "bocongan.gov.vn",
    "dichvucong.gov.vn",
]
```

Đây là cơ sở để giải thích rằng web search không phải tìm kiếm tự do hoàn toàn, mà được ưu tiên vào các nguồn pháp luật/cơ quan chính thống.

### 21.17. Tracker progress 5 bước

RAG Service ánh xạ các node kỹ thuật của LangGraph thành 5 bước dễ hiểu cho UI:

```python
_CHAT_STEPS = [
    ("validate", "Đang kiểm tra câu hỏi"),
    ("analyze", "Đang phân tích chủ đề"),
    ("retrieve", "Đang tra cứu nguồn"),
    ("synthesize", "Đang tổng hợp câu trả lời"),
    ("verify", "Đang kiểm tra độ chính xác"),
]
```

Mapping giữa node và step:

```python
_CHAT_NODE_TO_STEP = {
    "guardrail": "validate",
    "query_analysis": "analyze",
    "agent": "synthesize",
    "tools": "retrieve",
    "verifier": "verify",
}
```

Khi LangGraph phát update từ một node, `PipelineTracker` cập nhật trạng thái step tương ứng:

```python
if target_idx > self.current_idx:
    for i, step in enumerate(self.steps):
        if i < target_idx:
            step["status"] = "done"
        elif i == target_idx:
            step["status"] = "running"
```

Lớp này giúp tách biệt giữa cấu trúc kỹ thuật phức tạp của graph và trải nghiệm người dùng. UI không cần biết các node LangGraph chi tiết, chỉ cần hiển thị 5 bước cố định.

### 21.18. Verifier prompt

Verifier kiểm tra câu trả lời cuối cùng dựa trên toàn bộ tool results. Phần prompt quan trọng:

```text
Kiểm tra câu trả lời pháp luật có bịa đặt không.

KIỂM TRA mỗi trích dẫn pháp luật:
1. Số hiệu, điều, khoản, điểm có trong nguồn tra cứu không?
2. Nội dung chi tiết có trong nguồn không?
3. Kiểm tra từng con số cụ thể: mức phạt, thời hạn, số điểm trừ, ngày hiệu lực.
4. Kiểm tra quan hệ giữa văn bản: "Điều X sửa bởi Luật Y" chỉ hợp lệ nếu nguồn nêu rõ.
5. Nếu có văn bản cũ và mới, không được đưa số liệu từ văn bản cũ vào phần quy định hiện hành.
```

Output của Verifier bị ép về JSON:

```json
{
  "verdict": "PASS/FAIL",
  "issues": ["..."],
  "corrected_answer": "SAME hoặc bản sửa"
}
```

Nếu `PASS`, hệ thống giữ nguyên câu trả lời gốc:

```python
if verdict == "PASS":
    return {"messages": [AIMessage(content=agent_answer)]}
```

Nếu `FAIL`, hệ thống dùng bản sửa:

```python
if corrected_answer and corrected_answer.strip().upper() != "SAME":
    return {"messages": [AIMessage(content=corrected_answer)]}
```

Điểm đáng chú ý là Verifier không được yêu cầu viết lại một câu trả lời mới hoàn toàn. Nó chỉ giữ phần đúng và xóa phần không có căn cứ. Đây là chiến lược sửa tối thiểu để tránh phát sinh hallucination mới ở bước kiểm chứng.

### 21.19. Lưu assistant message sau khi RAG hoàn tất

Sau khi nhận `done` từ RAG Service, Main Service lưu câu trả lời:

```python
answer = final_payload.get("answer", "")
sources = final_payload.get("sources", [])
metadata = {
    "model": final_payload.get("model"),
    "processing_time": final_payload.get("processing_time"),
    "query_analysis": final_payload.get("query_analysis"),
}
assistant_msg = await self.msg_repo.create(
    conversation_id=conv_id,
    role="assistant",
    content=answer,
    sources=sources,
    metadata=metadata,
)
```

Sau đó mới gửi event `done` về client:

```python
yield {
    "event": "done",
    "data": {
        "conversation_id": conv_id,
        "is_new_conversation": is_new_conversation,
        "assistant_message": _msg_to_stream_dict(assistant_msg),
        "suggested_questions": [],
    },
}
```

Nhờ vậy, dữ liệu client nhận được luôn khớp với dữ liệu đã lưu trong PostgreSQL. Nếu user mở lại hội thoại, câu trả lời hiển thị sẽ giống với nội dung đã nhận ở thời điểm stream kết thúc.

### 21.20. Cập nhật tiêu đề hội thoại mới

Nếu là hội thoại mới, tiêu đề được lấy từ `primary_topic` trong `query_analysis`:

```python
if is_new_conversation:
    primary_topic = None
    qa = metadata.get("query_analysis") or {}
    if qa:
        primary_topic = qa.get("primary_topic")
    if not primary_topic:
        primary_topic = content[:50] + "..." if len(content) > 50 else content
    await self.conv_repo.update(
        conv,
        ConversationUpdate(title=primary_topic),
    )
```

Cách này giúp danh sách hội thoại có tiêu đề ngắn gọn theo chủ đề pháp lý thay vì chỉ hiển thị nguyên văn câu hỏi đầu tiên.

### 21.21. Background task sinh câu hỏi gợi ý

Sau khi stream hoàn tất, Main Service tạo task ngầm để sinh suggested questions:

```python
asyncio.create_task(
    ChatService.fetch_suggested_questions_background(
        db_session_factory=async_session,
        message_id=assistant_msg_id,
        query=data.message,
        answer=assistant_answer,
    )
)
```

Task này gọi RAG Service:

```python
response = await client.post(
    f"{settings.rag_service_url}/api/v1/rag/suggested-questions",
    json={
        "query": query,
        "answer_summary": answer[:500],
    },
    headers={
        "X-API-Key": settings.rag_service_api_key,
        "X-Internal-Service": "main-service",
    },
)
```

Sau khi có kết quả, hệ thống lưu danh sách câu hỏi gợi ý vào metadata của message:

```python
await msg_repo.update_metadata(message_id, {"suggested_questions": questions})
```

Lý do tách thành background task là câu hỏi gợi ý không phải dữ liệu bắt buộc để trả lời người dùng. Nếu chờ sinh gợi ý xong mới trả response chính, latency của luồng chat sẽ tăng không cần thiết.

## 22. Các câu hỏi phản biện có thể gặp về luồng chat

### Vì sao không để LLM trả lời trực tiếp?

Vì lĩnh vực pháp luật yêu cầu căn cứ rõ ràng. Nếu để LLM trả lời trực tiếp, mô hình có thể bịa điều khoản, trộn quy định cũ với quy định mới hoặc đưa ra con số sai. Hệ thống dùng Agentic RAG để buộc LLMs phải truy hồi nguồn trước khi trả lời.

### Vì sao phải dùng cả dữ liệu nội bộ và web search?

Dữ liệu nội bộ cung cấp điều khoản đã được chuẩn hóa, có metadata và có thể truy hồi bằng vector search. Tuy nhiên pháp luật thay đổi theo thời gian. Web search giúp xác minh hiệu lực và phát hiện văn bản mới hơn. Hai nguồn bổ trợ cho nhau: nội bộ giúp có căn cứ chi tiết, web giúp kiểm tra tính hiện hành.

### Dựa vào đâu Agent biết đã đủ bằng chứng?

Agent không hoàn toàn tự quyết định. Graph bắt buộc Agent phải gọi đủ hai tool là `retrieve_internal_law` và `search_web_for_law`. Nếu chưa gọi đủ, graph không cho chuyển sang Verifier. Sau khi có đủ hai nhóm nguồn tối thiểu, Agent tổng hợp câu trả lời dựa trên prompt ràng buộc, rồi Verifier kiểm tra lại từng nội dung.

### Nếu nguồn nội bộ và web mâu thuẫn thì xử lý thế nào?

Prompt quy định ưu tiên nguồn hiện hành từ web. Dữ liệu nội bộ được xem là nguồn nguyên văn có cấu trúc, nhưng nếu web cho thấy văn bản mới hơn hoặc quy định đã thay đổi, câu trả lời phải dựa trên quy định hiện hành và phân biệt rõ quy định cũ nếu cần.

### Nếu Verifier phát hiện câu trả lời sai thì sao?

Verifier trả `FAIL` và cung cấp `corrected_answer`. Hệ thống dùng bản sửa này thay cho câu trả lời gốc. Bản sửa theo chiến lược tối thiểu: xóa hoặc loại bỏ phần không có căn cứ, không viết thêm nội dung mới ngoài nguồn.

### Vì sao cần SSE streaming?

Pipeline Agentic RAG có nhiều bước và có thể mất thời gian. SSE giúp client nhận được tiến trình xử lý theo thời gian thực. Người dùng thấy hệ thống đang làm gì thay vì chỉ chờ một response cuối cùng.

### Vì sao chỉ lấy 6 tin nhắn gần nhất làm context?

Lịch sử chat dài sẽ làm tăng token, tăng latency và dễ làm nhiễu câu hỏi hiện tại. Sáu tin gần nhất đủ để hỗ trợ các câu hỏi nối tiếp ngắn, đồng thời vẫn giữ request gọn và tập trung.
