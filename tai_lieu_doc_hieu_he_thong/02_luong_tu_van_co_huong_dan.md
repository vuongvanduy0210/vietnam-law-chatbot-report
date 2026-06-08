# Luồng tư vấn có hướng dẫn (Guided Consultation)

Tài liệu này mô tả luồng tư vấn có hướng dẫn của hệ thống trợ lý ảo pháp luật. Đây là một luồng riêng biệt, song song với luồng chat chính, dành cho trường hợp người dùng đặt câu hỏi pháp lý nhưng còn thiếu nhiều thông tin chi tiết. Thay vì trả lời ngay một cách chung chung, hệ thống sinh ra các câu hỏi làm rõ dạng trắc nghiệm, người dùng chọn đáp án, rồi hệ thống mới tổng hợp câu trả lời cuối cùng đã được cá thể hóa theo tình huống cụ thể. Nội dung được viết theo hướng để người ngoài dự án vẫn hiểu được cách hệ thống vận hành và lý do thiết kế của từng bước.

## 1. Vai trò của luồng tư vấn có hướng dẫn

Trong luồng chat chính, người dùng gửi một câu hỏi tự do và nhận lại câu trả lời. Cách làm này phù hợp khi câu hỏi đã đủ rõ ràng. Tuy nhiên, trong lĩnh vực pháp luật, một câu hỏi tự nhiên thường thiếu các yếu tố định khung quan trọng. Ví dụ, câu hỏi "vượt đèn đỏ bị phạt bao nhiêu" không cho biết loại phương tiện là ô tô, xe máy hay xe đạp; có gây tai nạn không; đã bị lập biên bản chưa. Mỗi yếu tố này lại dẫn tới một mức phạt và một quy trình xử lý khác nhau. Nếu trả lời ngay, hệ thống buộc phải liệt kê toàn bộ các khung phạt cho mọi loại phương tiện, khiến câu trả lời dài, chung chung và khó áp dụng.

Luồng tư vấn có hướng dẫn giải quyết đúng vấn đề này. Nó chia quá trình tư vấn thành hai chặng:

- Chặng làm rõ (clarify): hệ thống đọc câu hỏi ban đầu, xác định chủ đề pháp lý, rồi sinh ra từ 3 đến 5 câu hỏi trắc nghiệm để thu thập các thông tin còn thiếu.
- Chặng trả lời (answer): sau khi người dùng chọn đáp án cho các câu hỏi trắc nghiệm, hệ thống chạy một pipeline Agentic RAG riêng để tổng hợp câu trả lời cuối, áp dụng trực tiếp các thông tin người dùng vừa cung cấp.

So với luồng chat chính, luồng này có ba đặc điểm khác biệt cốt lõi, sẽ được giải thích kỹ ở các mục sau:

- Có thêm bước sinh câu hỏi làm rõ trước khi trả lời.
- Đồ thị xử lý (graph) riêng, không dùng node guardrail và query_analysis như chat; thay vào đó gộp logic chuẩn bị vào một node planning xác định (deterministic), không gọi LLM.
- Hoàn toàn stateless: không tạo hội thoại, không lưu tin nhắn vào cơ sở dữ liệu. Mỗi request độc lập, không có lịch sử.

## 2. Hai chặng và ba endpoint

Luồng này được phơi ra cho ứng dụng người dùng (chủ yếu là mobile) qua ba endpoint của Main Service, tất cả nằm dưới tiền tố `/api/v1/guided`:

```http
POST /api/v1/guided/clarify
POST /api/v1/guided/answer
POST /api/v1/guided/answer/stream
```

Ý nghĩa từng endpoint:

- `/clarify`: nhận câu hỏi tự do ban đầu, trả về trạng thái phân loại và danh sách câu hỏi làm rõ.
- `/answer`: nhận câu hỏi gốc cùng các đáp án người dùng đã chọn, trả về câu trả lời cuối ở dạng đồng bộ (chờ tới khi hoàn tất).
- `/answer/stream`: phiên bản SSE streaming của `/answer`, phát tiến trình xử lý theo thời gian thực.

Cả ba endpoint đều yêu cầu người dùng đã đăng nhập. Tham số `current_user` được lấy qua `Depends(get_current_user)`, nghĩa là mọi request đều phải mang JWT access token hợp lệ giống luồng chat. Tuy nhiên, điểm khác biệt là dù có xác thực người dùng, hệ thống không gắn request vào hội thoại nào và không ghi gì vào PostgreSQL.

Trình tự sử dụng trên giao diện thường là: người dùng nhập câu hỏi, ứng dụng gọi `/clarify`, hiển thị các câu hỏi trắc nghiệm; người dùng chọn đáp án, ứng dụng gọi `/answer/stream` để vừa hiển thị tiến trình vừa nhận câu trả lời cuối.

## 3. So sánh nhanh với luồng chat chính

Trước khi đi vào chi tiết, bảng so sánh dưới đây giúp định vị nhanh các khác biệt giữa hai luồng.

```text
                        | Luồng chat chính        | Luồng tư vấn có hướng dẫn
------------------------|-------------------------|-----------------------------
Bước làm rõ câu hỏi     | Không có                | Có (endpoint /clarify)
Lưu hội thoại/tin nhắn  | Có (PostgreSQL)         | Không (stateless)
Node guardrail riêng    | Có                      | Không (validate ở /clarify)
Node query_analysis     | Có (gọi LLM)            | Thay bằng planning (không LLM)
Graph / State           | graph.py / AgentState   | guided_graph.py / GuidedAgentState
Ép gọi đủ 2 tool        | Có                      | Có (giữ nguyên cơ chế)
Verifier                | Có                      | Có (thêm kiểm tra áp dụng clarify)
Số bước progress UI     | 5 bước                  | 4 bước
```

Điểm cần nhấn mạnh: tuy luồng guided lược bỏ guardrail và query_analysis, nó vẫn giữ nguyên hai cơ chế an toàn quan trọng nhất của Agentic RAG là ép Agent gọi đủ cả hai công cụ truy hồi và bước Verifier kiểm chứng. Như vậy, việc lược bỏ không làm giảm độ tin cậy của câu trả lời, mà chỉ chuyển công đoạn kiểm tra đầu vào sang chặng `/clarify`.

## 4. Chặng 1 - Người dùng gửi câu hỏi ban đầu tới /clarify

Khi người dùng nhập câu hỏi và bắt đầu phiên tư vấn, ứng dụng gọi `/api/v1/guided/clarify`. Request rất đơn giản, chỉ gồm một trường `query`:

```json
{
  "query": "Vượt đèn đỏ bị phạt bao nhiêu tiền?"
}
```

Schema đầu vào ở Main Service ràng buộc độ dài câu hỏi để tránh đầu vào rỗng hoặc quá lớn:

```python
class GuidedClarifyRequest(BaseModel):
    """Mobile sends initial free-text query to start guided consultation."""

    query: str = Field(..., min_length=3, max_length=1000)
```

Main Service không tự xử lý nội dung câu hỏi mà chuyển tiếp sang RAG Service qua client nội bộ `rag_client.guided_clarify`. Đây là điểm giống luồng chat: Main Service đóng vai trò cổng vào và lớp xác thực người dùng, còn toàn bộ phần xử lý AI nằm ở RAG Service.

## 5. Main Service gọi RAG Service để sinh câu hỏi làm rõ

Trong `main-service/app/api/v1/guided.py`, endpoint `/clarify` gọi RAG Service rồi định hình lại kết quả thành cấu trúc mà mobile dễ tiêu thụ:

```python
@router.post("/clarify")
async def clarify(
        data: GuidedClarifyRequest,
        current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        result = await rag_client.guided_clarify(query=data.query)
    except Exception as e:
        logger.exception(f"guided_clarify upstream failure: {e}")
        return error_response(
            code=ErrorCode.RAG_SERVICE_ERROR,
            message="Không thể xử lý câu hỏi lúc này. Vui lòng thử lại sau.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    questions = []
    for q in result.get("questions", []):
        questions.append(ClarifyQuestion(
            id=q["id"],
            label=q["label"],
            options=[ClarifyOption(id=o["id"], label=o["label"]) for o in q.get("options", [])],
        ))

    response_data = {
        "status": result.get("status", "OK"),
        "reason": result.get("reason"),
        "detected_topic": result.get("detected_topic"),
        "detected_domain": result.get("detected_domain"),
        "questions": [q.model_dump() for q in questions],
    }
```

Các điểm cần hiểu ở đoạn này:

- Trường `status` quyết định hành vi của giao diện. Có ba giá trị: `OK`, `NOT_LEGAL`, `OFF_POLICY`.
- Với `OK`, danh sách `questions` khác rỗng và ứng dụng hiển thị các câu hỏi trắc nghiệm.
- Với `NOT_LEGAL` hoặc `OFF_POLICY`, danh sách `questions` rỗng, ứng dụng hiển thị `reason` và không cho đi tiếp.
- `detected_topic` và `detected_domain` là chủ đề và lĩnh vực pháp lý mà hệ thống suy ra từ câu hỏi; cả hai sẽ được dùng lại ở chặng trả lời.

Trong `rag_client.guided_clarify`, request nội bộ được gửi bằng API key, đúng mô hình tách lớp xác thực của hệ thống:

```python
async def guided_clarify(self, query: str) -> Dict[str, Any]:
    """Call RAG Service /guided-clarify — validate + classify + generate clarifying questions."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{self.base_url}/api/v1/rag/guided-clarify",
                json={"query": query},
                headers={
                    "X-API-Key": settings.rag_service_api_key,
                    "X-Internal-Service": "main-service",
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {
                "status": "OK",
                "reason": None,
                "detected_topic": None,
                "detected_domain": None,
                "questions": [],
                "_error": f"Không thể kết nối RAG Service: {str(e)}",
            }
```

Một chi tiết thiết kế đáng chú ý: khi không kết nối được RAG Service hoặc RAG trả lỗi HTTP, client không ném exception mà trả về một cấu trúc có `status = OK` và `questions` rỗng kèm trường `_error`. Cách này giúp giao diện không bị treo và không hiển thị lỗi kỹ thuật thô cho người dùng, dù trong trường hợp đó danh sách câu hỏi sẽ rỗng.

## 6. RAG Service sinh câu hỏi làm rõ chỉ bằng một lần gọi LLM

Phía RAG Service, endpoint `guided-clarify` gói gọn ba việc vào một lần gọi mô hình: xác thực câu hỏi có thuộc phạm vi pháp luật hay không, phân loại chủ đề, và sinh câu hỏi kèm đáp án.

```python
@router.post("/guided-clarify", response_model=GuidedClarifyResponse)
async def guided_clarify(
        request: GuidedClarifyRequest,
        _: InternalAuth,
):
    """
    Generate clarifying multiple-choice questions from an initial user query.

    Flow: 1 Gemini call performs validate + topic classification + question+options generation.
    Fallback: on LLM failure or invalid output, returns a generic set of 3 clarifying questions
    so the UX does not dead-end.
    """
    try:
        llm_service = get_llm_service()
        result = llm_service.generate_clarifying_questions(request.query)
        ...
```

Đây chính là nơi guardrail của luồng chat được thay thế. Trong luồng chat, guardrail là một node riêng chạy mỗi lần đặt câu hỏi. Trong luồng guided, việc kiểm tra phạm vi được thực hiện một lần duy nhất tại chặng clarify, nhờ chính prompt sinh câu hỏi đã bao gồm quy tắc phân loại. Nhờ đó, đến chặng trả lời, hệ thống coi câu hỏi đã được kiểm duyệt và không cần guardrail nữa.

### 6.1. Prompt phân loại và sinh câu hỏi

Logic phân loại nằm trong `GUIDED_CLARIFY_PROMPT` của `llm_service.py`. Phần quy tắc phân loại trạng thái:

```text
QUY TẮC PHÂN LOẠI TRẠNG THÁI:
1. "NOT_LEGAL" — câu hỏi KHÔNG liên quan đến pháp luật Việt Nam (VD: hỏi thời tiết, lập trình, nấu ăn, toán học...).
2. "OFF_POLICY" — câu hỏi vi phạm đạo đức/an toàn (VD: hướng dẫn phạm tội cụ thể, trốn thuế, bạo lực, ma tuý, sản xuất vũ khí, đe doạ người khác...).
3. "OK" — câu hỏi pháp lý hợp lệ, có thể tư vấn được.
```

Điểm tinh tế của prompt này là cách nó hướng dẫn mô hình tư duy trước khi sinh câu hỏi. Mô hình được yêu cầu trước hết xác định chính xác tội danh hoặc quan hệ pháp luật, sau đó liệt kê các yếu tố định khung cần biết, rồi chỉ hỏi những yếu tố mà người dùng chưa nêu:

```text
Bước 1: Xác định CHÍNH XÁC tội danh / quan hệ pháp luật / vấn đề pháp lý cụ thể.
   VD: "vượt đèn đỏ" → vi phạm Luật Trật tự ATGT đường bộ + Nghị định 168/2024 về xử phạt vi phạm hành chính giao thông.
   ...
Bước 2: Liệt kê các YẾU TỐ ĐỊNH KHUNG / CẤU THÀNH cần biết để tư vấn chính xác.
   VD vượt đèn đỏ: loại phương tiện (ô tô/xe máy/xe đạp), có gây tai nạn không, đã bị lập biên bản chưa, có bị tước GPLX/trừ điểm bằng lái không.
   ...
Bước 3: CHỈ hỏi những YẾU TỐ user CHƯA NÊU trong câu hỏi gốc.
```

Prompt còn liệt kê rõ các anti-pattern, tức các câu hỏi cần tuyệt đối tránh vì chúng có thể dán vào bất kỳ tình huống pháp lý nào mà vẫn nghe hợp lý:

```text
❌ "Anh/Chị đang ở vai trò nào trong tình huống này?" (chung chung, không gắn topic)
❌ "Sự việc xảy ra vào thời gian nào?" (template, trừ khi thời điểm thực sự ảnh hưởng — VD: thời hiệu khởi kiện)
❌ "Anh/Chị muốn được tư vấn về vấn đề gì?" (đẩy ngược câu hỏi cho user)
```

Lý do thiết kế: chất lượng của toàn bộ luồng phụ thuộc vào chất lượng các câu hỏi làm rõ. Nếu câu hỏi rỗng, người dùng chọn đáp án nhưng thông tin thu được không có giá trị định khung, và câu trả lời cuối vẫn chung chung. Việc ép mô hình gắn mỗi câu hỏi với một yếu tố pháp lý cụ thể là cách giữ cho clarify thực sự hữu ích.

### 6.2. Ràng buộc định dạng câu hỏi và đáp án

Prompt quy định cấu trúc cứng để Main Service và mobile có thể hiển thị nhất quán:

```text
QUY TẮC SINH CÂU HỎI (chỉ khi status = "OK"):
- Sinh CHÍNH XÁC từ 3 đến 5 câu hỏi clarifying.
- Mỗi câu hỏi có CHÍNH XÁC từ 3 đến 5 options.
- Option cuối cùng của MỌI câu hỏi PHẢI là "Không rõ / Không áp dụng" (id cuối).
- ID câu hỏi: "q1", "q2", "q3", "q4", "q5".
- ID option: "A", "B", "C", "D", "E" (theo thứ tự).
```

Quy tắc bắt buộc luôn có đáp án "Không rõ / Không áp dụng" rất quan trọng về mặt trải nghiệm: người dùng không phải lúc nào cũng biết câu trả lời cho một yếu tố pháp lý, và cần một lối thoát để không bị ép chọn sai. Output cũng bị ép về JSON thuần, không kèm markdown, để hệ thống parse được tin cậy.

### 6.3. Xác thực kết quả và cơ chế fallback

Sau khi gọi LLM, hàm `generate_clarifying_questions` không tin tưởng mù quáng vào output mà kiểm tra lại từng lớp. Nếu `status` không nằm trong tập hợp lệ, hoặc danh sách câu hỏi rỗng, hoặc sau khi lọc còn quá ít câu, hệ thống chuyển sang fallback:

```python
result = json.loads(response)
status = result.get("status")
if status not in ("OK", "NOT_LEGAL", "OFF_POLICY"):
    logger.warning(f"[CLARIFY] Invalid status '{status}'. Raw response (first 800 chars):\n{response[:800]}")
    return self._build_clarify_fallback(query)

if status in ("NOT_LEGAL", "OFF_POLICY"):
    return {
        "status": status,
        "reason": result.get("reason") or "Câu hỏi không phù hợp để tư vấn pháp luật.",
        "detected_topic": None,
        "detected_domain": None,
        "questions": [],
    }
```

Phần xác thực câu hỏi áp dụng nguyên tắc nới lỏng có kiểm soát. Thay vì từ chối toàn bộ khi mô hình trả sai số lượng, hệ thống cắt bớt cho vừa giới hạn và chỉ cần tối thiểu hai câu hợp lệ là chấp nhận:

```python
# Relax: trim instead of reject — nếu LLM trả 6+ câu, lấy 5 câu đầu (vẫn dùng được)
if len(questions_raw) > 5:
    logger.info(f"[CLARIFY] LLM trả {len(questions_raw)} câu, trim xuống 5")
    questions_raw = questions_raw[:5]
...
# Relax: chỉ cần >= 2 câu hợp lệ là chấp nhận (thay vì BẮT BUỘC 3-5)
if len(validated) < 2:
    logger.warning(...)
    return self._build_clarify_fallback(query, detected_topic)
```

Khi LLM không khả dụng, trả về rỗng, JSON hỏng, hoặc bị rate limit, hàm `_build_clarify_fallback` trả về một bộ câu hỏi mặc định để giao diện không rơi vào ngõ cụt:

```python
def _build_clarify_fallback(self, query: str, detected_topic: Optional[str] = None) -> Dict[str, Any]:
    """Smarter fallback khi LLM fail: gắn topic vào câu đầu để KHÔNG hoàn toàn generic.

    Vẫn là fallback (cuối cùng), nhưng câu Q1 giờ tham chiếu trực tiếp đến topic
    user hỏi → user biết hệ thống đã hiểu vấn đề (chưa phải template rỗng tuột).
    """
    topic = (detected_topic or query)[:80].strip()
    return {
        "status": "OK",
        ...
        "questions": [
            {
                "id": "q1",
                "label": f"Để tư vấn chính xác về \"{topic}\", Anh/Chị có thể cho biết tình huống đang ở giai đoạn nào?",
                ...
```

Lý do thiết kế: clarify là cửa ngõ của toàn luồng. Nếu bước này thất bại cứng, người dùng không thể tiếp tục. Fallback đảm bảo luồng luôn đi tiếp được, dù chất lượng câu hỏi mặc định thấp hơn câu hỏi do LLM sinh đúng ngữ cảnh. Đây là biểu hiện của nguyên tắc graceful degradation đã nêu trong tài liệu kiến trúc.

## 7. Người dùng chọn đáp án và gửi lên /answer

Sau khi hiển thị câu hỏi trắc nghiệm, ứng dụng thu thập lựa chọn của người dùng và gọi `/answer` hoặc `/answer/stream`. Request mang theo câu hỏi gốc, chủ đề đã phát hiện và danh sách đáp án:

```python
class ClarifyAnswer(BaseModel):
    question_id: str
    question_label: str
    selected_option_label: str


class GuidedAnswerRequest(BaseModel):
    original_query: str = Field(..., min_length=3, max_length=1000)
    detected_topic: Optional[str] = None
    answers: List[ClarifyAnswer] = Field(default_factory=list)
```

Một quyết định thiết kế đáng chú ý: mỗi đáp án gửi lên không chỉ gồm id mà còn gồm cả `question_label` (nội dung câu hỏi) và `selected_option_label` (nội dung đáp án đã chọn) ở dạng văn bản. Nhờ đó RAG Service không cần lưu lại các câu hỏi đã sinh ở chặng clarify; toàn bộ ngữ cảnh cần thiết đều nằm trong request. Đây chính là cơ chế giúp luồng giữ được tính stateless: mỗi request `/answer` tự mang đủ thông tin để xử lý độc lập, không phụ thuộc vào trạng thái phía server từ lần gọi `/clarify` trước đó.

Vì `answers` mặc định là danh sách rỗng, người dùng có thể bỏ qua tất cả câu hỏi clarify mà vẫn nhận được câu trả lời. Trong trường hợp đó, hệ thống xử lý như một câu hỏi không có thông tin bổ sung.

## 8. Main Service chuyển tiếp tới pipeline trả lời

Ở chế độ đồng bộ, endpoint `/answer` gọi `rag_client.guided_answer` rồi định hình lại danh sách nguồn cho mobile:

```python
@router.post("/answer")
async def answer(
        data: GuidedAnswerRequest,
        current_user: Annotated[User, Depends(get_current_user)],
):
    """Generate final legal answer using original query + user-selected clarifying answers."""
    try:
        result = await rag_client.guided_answer(
            original_query=data.original_query,
            detected_topic=data.detected_topic,
            answers=[a.model_dump() for a in data.answers],
        )
    except Exception as e:
        ...

    sources = []
    for s in result.get("sources", []):
        meta = s.get("metadata") or {}
        sources.append(GuidedAnswerSource(
            id=s.get("id", "?"),
            content=s.get("content", ""),
            law_id=meta.get("law_id"),
            article_id=meta.get("article_id"),
            title=meta.get("title"),
            url=meta.get("url"),
            score=float(s.get("score", 0.0)),
        ))
```

Việc Main Service làm phẳng cấu trúc nguồn (đưa `law_id`, `article_id`, `title`, `url` từ trong `metadata` ra cấp ngoài) là một bước thích nghi cho mobile, giúp ứng dụng đọc trường đồng nhất mà không phải lội vào object lồng nhau.

Trong `rag_client.guided_answer`, request nội bộ đặt timeout rất dài để chịu được trường hợp xấu nhất khi Gemini quá tải và chuỗi model dự phòng phải kích hoạt:

```python
async def guided_answer(
    self,
    original_query: str,
    detected_topic: str | None,
    answers: List[Dict[str, Any]],
    top_k: int = 5,
) -> Dict[str, Any]:
    """Call RAG Service /guided-answer — agentic pipeline (planning → agent ↔ tools → verifier).

    Timeout 600s để đủ cho worst case khi Gemini 503 + fallback model chain kích hoạt.
    """
    async with httpx.AsyncClient(timeout=600.0) as client:
        ...
```

## 9. Pipeline guided trên RAG Service

Khi nhận request, endpoint `guided-answer` của RAG Service dựng đầu vào cho một đồ thị LangGraph riêng rồi chạy nó. Trước tiên, hệ thống ghép các đáp án người dùng thành một đoạn ngữ cảnh dạng gạch đầu dòng:

```python
# Build clarify context (used by planning node + verifier)
clarify_lines = []
for ans in request.answers:
    clarify_lines.append(f"- {ans.question_label}: {ans.selected_option_label}")
clarify_context = "\n".join(clarify_lines)

# Initial human message: tóm tắt mô tả tình huống cho agent reasoning
if clarify_context:
    human_content = (
        f"Câu hỏi của tôi: {request.original_query}\n\n"
        f"Thông tin bổ sung tôi đã cung cấp:\n{clarify_context}"
    )
else:
    human_content = request.original_query

initial_state = {
    "messages": [HumanMessage(content=human_content)],
    "original_query": request.original_query,
    "detected_topic": request.detected_topic or "",
    "clarify_context": clarify_context,
    "internal_search_query": "",
    "web_search_query": "",
    "iteration_count": 0,
}

result = await guided_app.ainvoke(initial_state)
```

Điểm cần hiểu:

- `clarify_context` là chuỗi nhiều dòng dạng `- <câu hỏi>: <đáp án>`. Chuỗi này được dùng cả ở node planning lẫn node verifier.
- `human_content` ghép câu hỏi gốc với phần thông tin bổ sung, tạo thành tin nhắn người dùng đầu tiên đưa cho Agent.
- `initial_state` là trạng thái khởi tạo của graph, có các trường đặc trưng cho guided như `detected_topic`, `clarify_context`, hai trường truy vấn rỗng để planning điền vào, và `iteration_count` để chặn vòng lặp.

Docstring của endpoint nêu rõ triết lý tách biệt và lý do bỏ guardrail:

```text
Pipeline: planning (deterministic) → agent (LLM + tools) ↔ tools (internal + web) → verifier.
Tách hoàn toàn khỏi luồng chat — dùng GuidedAgentState/guided_app riêng, không ảnh hưởng
chat agent. Không cần guardrail vì query đã validate ở /guided-clarify.
```

> **Cách đọc các mục 11–14.** Mỗi node được phân tích theo cùng khuôn với tài liệu luồng chat: **Vai trò & vị trí → Đầu vào (đọc gì từ `GuidedAgentState`) → Xử lý (mổ code) → Đầu ra (ghi gì vào state) → Định tuyến → Xử lý lỗi/fallback → Lý do thiết kế.** Trước hết cần nắm đối tượng trạng thái dùng chung của luồng guided.

## 10. Đồ thị guided, trạng thái GuidedAgentState và điểm khác so với chat

### Trạng thái GuidedAgentState

Toàn bộ pipeline guided chia sẻ một state riêng, **tách hoàn toàn** khỏi `AgentState` của chat (định nghĩa trong `rag-service/app/agent/guided_state.py`):

```python
class GuidedAgentState(TypedDict):
    """State cho Guided Consultation pipeline (tách biệt hoàn toàn với chat AgentState)."""

    # Conversation history — add_messages reducer append thay vì overwrite
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Câu hỏi gốc của user (trước khi clarify)
    original_query: str

    # Chủ đề pháp lý đã detect từ /guided-clarify
    detected_topic: str

    # Formatted Q&A context: "- Câu hỏi 1: Lựa chọn A\n- Câu hỏi 2: ..."
    clarify_context: str

    # Query đã optimize cho internal vector search (deterministic, không cần LLM)
    internal_search_query: str

    # Query đã optimize cho web search (deterministic, không cần LLM)
    web_search_query: str

    # Iteration counter để guard agent↔tools loop
    iteration_count: int
```

Hai khác biệt về state so với chat cần ghi nhớ:

- Guided **không có** `is_valid_query` / `rejection_reason` — vì câu hỏi đã được validate ở chặng `/guided-clarify` trước đó, không cần node guardrail nữa.
- Guided **có thêm** `original_query`, `detected_topic`, `clarify_context` (thông tin có cấu trúc từ chặng clarify) và hai trường `internal_search_query` / `web_search_query` để node `planning` ghi truy vấn đã tối ưu vào.

Giống chat, trường `messages` dùng reducer `add_messages` (nối thêm, không ghi đè), còn các trường còn lại theo cơ chế ghi đè mặc định.

### Đồ thị và các cạnh điều hướng

Đồ thị guided được định nghĩa trong `rag-service/app/agent/guided_graph.py`. Topology của nó như sau:

```text
START -> planning -> agent <-> tools -> verifier -> END
```

So với đồ thị chat (`guardrail -> query_analysis -> agent <-> tools -> verifier -> END`), guided bỏ hai node đầu và thay bằng một node `planning` duy nhất. Cấu trúc graph trong code:

```python
guided_workflow = StateGraph(GuidedAgentState)

guided_workflow.add_node("planning", guided_planning_node)
guided_workflow.add_node("agent", guided_agent_node)
guided_workflow.add_node("tools", guided_tools_node)
guided_workflow.add_node("verifier", guided_verification_node)

guided_workflow.set_entry_point("planning")
```

Các cạnh điều hướng:

```python
guided_workflow.add_edge("planning", "agent")
guided_workflow.add_conditional_edges("agent", route_after_guided_agent)
guided_workflow.add_edge("tools", "agent")
guided_workflow.add_edge("verifier", END)
```

Phần đầu file ghi chú rõ nguyên tắc tách biệt hoàn toàn khỏi chat:

```text
Tách hoàn toàn khỏi chat's graph.py — KHÔNG import từ app.agent.graph hoặc app.agent.nodes.
Tools được reuse vì là pure function (không chứa logic chat-specific).
...
Khác chat:
- Không có guardrail node (đã validate ở /guided-clarify)
- Planning thay query_analysis (deterministic, không LLM call)
```

**Lý do thiết kế tách biệt.** Hai luồng có yêu cầu khác nhau (guided có structured input từ clarify, chat có lịch sử hội thoại), nên dùng hai state và hai bộ node riêng giúp thay đổi một bên không gây tác dụng phụ lên bên kia. Tuy nhiên, hai công cụ truy hồi (`retrieve_internal_law`, `search_web_for_law`) được dùng chung vì chúng là hàm thuần, không mang logic riêng của chat. Đây là cách cân bằng giữa tách biệt và tái sử dụng: tách phần có logic khác nhau, dùng chung phần trung lập.

## 11. Node planning - chuẩn bị truy vấn không cần LLM

**Vai trò & vị trí.** Node đầu tiên (entry point), thay thế cho **cả** guardrail lẫn query_analysis của chat. Khác biệt then chốt: query_analysis của chat gọi LLM để phân tích câu hỏi thành truy vấn; planning của guided là một bước **xác định (deterministic), không gọi LLM** — nó tận dụng thông tin đã có sẵn từ chặng clarify để ghép ra truy vấn.

**Đầu vào.** Đọc ba trường structured đã được điền sẵn từ endpoint: `original_query`, `detected_topic`, `clarify_context`.

```python
def guided_planning_node(state: GuidedAgentState) -> dict[str, Any]:
    """Planning node — thay thế guardrail + query_analysis của chat."""
    start = time.time()

    original_query = state["original_query"]
    detected_topic = state.get("detected_topic") or ""
    clarify_context = state.get("clarify_context") or ""

    # Build internal search query: topic + query gốc (vector search cần từ khóa pháp lý)
    if detected_topic:
        internal_query = f"{detected_topic} — {original_query}"
    else:
        internal_query = original_query

    # Build web search query: query gốc + topic (web search thiên về semantic tự nhiên)
    if detected_topic:
        web_query = f"{original_query} {detected_topic}".strip()
    else:
        web_query = original_query
```

**Xử lý.** Hai truy vấn được ghép theo hai chiến lược khác nhau, đúng với đặc tính từng nguồn:

- Truy vấn nội bộ dạng `chủ đề — câu hỏi gốc`, đưa thuật ngữ pháp lý lên trước vì vector search trong ChromaDB đáp ứng tốt với từ khóa pháp lý.
- Truy vấn web dạng `câu hỏi gốc + chủ đề`, giữ giọng tự nhiên hơn vì Tavily/Google thiên về tìm kiếm ngữ nghĩa tự nhiên.
- Nếu không có `detected_topic`, cả hai lùi về dùng nguyên câu hỏi gốc — đảm bảo node không bao giờ tạo truy vấn rỗng.

Vì không gọi LLM, node này gần như tức thời; log ghi rõ điều đó:

```python
logger.info(f"[TIMING] guided_planning: {time.time() - start:.3f}s (no LLM call)")
```

**Đầu ra.** Node nối một `SystemMessage` (chứa bối cảnh + hướng dẫn dùng công cụ + yêu cầu áp dụng clarify) vào `messages`, và ghi hai truy vấn đã chuẩn bị vào state:

```python
    return {
        "messages": [planning_message],
        "internal_search_query": internal_query,
        "web_search_query": web_query,
    }
```

Nội dung `planning_message` ép Agent dùng đúng truy vấn đã tối ưu và yêu cầu áp dụng trực tiếp thông tin clarify:

```text
- Khi gọi `retrieve_internal_law`: SỬ DỤNG CHÍNH XÁC query sau: "{internal_query}"
- Khi gọi `search_web_for_law`: SỬ DỤNG CHÍNH XÁC query sau: "{web_query}"
- KHÔNG tự sáng tạo query khác. Các query trên đã được tối ưu cho tình huống này.
...
User đã bỏ công trả lời các câu hỏi trắc nghiệm để cung cấp thông tin cụ thể. Câu trả lời PHẢI:
1. ÁP DỤNG TRỰC TIẾP từng thông tin trong "THÔNG TIN BỔ SUNG" vào phân tích — KHÔNG được trả
   lời generic như chưa biết các thông tin đó. VD: user nói đi ô tô vượt đèn đỏ → phải nêu
   mức phạt CỤ THỂ cho ô tô (không liệt kê mức phạt chung cho mọi loại xe).
```

**Định tuyến.** Cạnh tĩnh `planning → agent`.

**Lý do thiết kế.** Bỏ LLM ở bước này là hợp lý vì chủ đề và ngữ cảnh đã được mô hình phân tích ở chặng clarify; gọi LLM lần nữa chỉ để sinh truy vấn là dư thừa. Loại bỏ một lần gọi LLM giúp giảm độ trễ, giảm chi phí, và bớt một điểm có thể phát sinh lỗi 503. Vì là deterministic, hành vi node hoàn toàn tái lập được.

## 12. Node agent - bộ não tổng hợp và ép gọi đủ công cụ

**Vai trò & vị trí.** Node trung tâm, gọi lặp lại trong vòng `agent ↔ tools`. Dùng cùng model với chat (mặc định `gemini-2.5-flash`) nhưng **system prompt tùy biến** cho guided.

**Đầu vào.** Đọc toàn bộ `messages` (gồm `SystemMessage` planning và các `ToolMessage` từ vòng trước). Node ghép một system prompt riêng lên đầu. Prompt nhấn mạnh đặc thù guided — người dùng đã cung cấp thông tin có cấu trúc qua clarify nên câu trả lời phải áp dụng cụ thể — và định nghĩa cấu trúc bắt buộc của câu trả lời cuối:

```text
CẤU TRÚC BẮT BUỘC:

1. TỔNG KẾT TÌNH HUỐNG CỦA USER (dựa trên clarify Q&A):
   Nhắc lại các thông tin user đã cung cấp dưới dạng tóm tắt — ngắn gọn 2-3 câu. Mục đích:
   để user biết hệ thống đã hiểu đúng tình huống.
...
2. CĂN CỨ PHÁP LÝ HIỆN HÀNH:
   Trích dẫn quy định ÁP DỤNG ĐÚNG với tình huống user (không liệt kê lan man tất cả khung).
...
3. ÁP DỤNG CỤ THỂ VÀO TÌNH HUỐNG:
   Phân tích từng thông tin user cung cấp và gắn với quy định tương ứng.
```

Đồng thời prompt giữ nguyên các quy tắc cốt lõi của Agentic RAG mà luồng chat cũng áp dụng: bắt buộc gọi cả hai công cụ, ưu tiên nguồn web hiện hành hơn dữ liệu nội bộ, và cấm bịa đặt:

```text
QUY TRÌNH BẮT BUỘC:
1. BƯỚC 1: Gọi `retrieve_internal_law` để lấy nguyên văn điều khoản.
2. BƯỚC 2: BẮT BUỘC gọi `search_web_for_law` để xác minh hiệu lực và tìm quy định mới nhất.

ĐỘ ƯU TIÊN NGUỒN (cao → thấp):
① Kết quả web (realtime, trạng thái hiện hành)
② Dữ liệu nội bộ (nguyên văn, chỉ dùng khi web xác nhận còn hiệu lực)
```

Phần cấm tuyệt đối bổ sung hai điều đặc trưng cho guided so với chat:

```text
- TRẢ LỜI GENERIC, không áp dụng các thông tin user đã cung cấp qua clarify
- BỎ QUA phần "TỔNG KẾT TÌNH HUỐNG CỦA USER" ở đầu câu trả lời
```

**Xử lý.** Node ghép system prompt vào trước toàn bộ message của state, tăng `iteration_count`, rồi gọi LLM qua hàm có chuỗi model dự phòng:

```python
    messages_to_pass = [{"role": "system", "content": system_prompt}] + list(state["messages"])

    iteration_count = state.get("iteration_count", 0) + 1
    start = time.time()
    response = _invoke_agent_with_fallback(messages_to_pass, tools)
    logger.info(f"[TIMING] guided_agent_invoke (iter {iteration_count}): {time.time() - start:.2f}s")

    return {"messages": [response], "iteration_count": iteration_count}
```

**Đầu ra.** Nối `response` (AIMessage, có thể kèm `tool_calls`) vào `messages` và tăng `iteration_count`.

**Định tuyến.** Hàm `route_after_guided_agent` — phân tích ở mục 12.1.

### 12.1. Định tuyến: ép gọi đủ hai công cụ trước khi trả lời

Cũng giống chat, guided không cho Agent tự ý kết thúc khi chưa truy hồi đủ nguồn. Logic này là hàm thuần `route_after_guided_agent` (chỉ đọc state, không gọi LLM):

```python
def route_after_guided_agent(state: GuidedAgentState):
    """Route to tools or verifier — enforce that both tools must be called before answer."""
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"

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

Ba lớp kiểm soát, gần như sao chép từ chat:

- **Ưu tiên hành động tool:** nếu LLM vừa yêu cầu gọi tool (`tool_calls` khác rỗng) → đi tới `tools`.
- **Chống lặp vô hạn:** nếu `iteration_count >= 6` → ép sang `verifier` bất kể đã đủ tool hay chưa.
- **Ép đủ bằng chứng:** tập `tool_names_called` dựng từ `name` của các `ToolMessage`; nếu chưa gọi đủ cả hai tool bắt buộc → ép quay lại `agent`; chỉ khi đủ mới sang `verifier`.

Đây là điểm cần nhấn mạnh khi phản biện: việc guided bỏ guardrail và query_analysis **không** nới lỏng kiểm soát chất lượng. Ràng buộc nghiêm ngặt nhất — bắt buộc có cả căn cứ nội bộ lẫn xác minh web trước khi trả lời — vẫn được giữ nguyên.

### 12.2. Xử lý lỗi: chuỗi model dự phòng chống quá tải

Việc gọi LLM đi qua `_invoke_agent_with_fallback`. Nó thử lần lượt từng model trong chuỗi dự phòng, mỗi model thử lần lượt từng API key, xoay vòng khi gặp 503/429 và chỉ ném ngay với lỗi không recover được:

```python
    primary = settings.agent_model
    model_chain = [primary]
    for m in settings.fallback_models:
        if m and m not in model_chain:
            model_chain.append(m)

    last_error: Any = None
    for model_idx, model_name in enumerate(model_chain):
        for key_idx, key in enumerate(keys):
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=key,
                    temperature=0.0,
                    max_retries=2,
                )
                llm_with_tools = llm.bind_tools(tools)
                ...
                return response
            except Exception as e:
                err_str = str(e).lower()
                last_error = e
                if "503" in err_str or "unavailable" in err_str or "overload" in err_str:
                    ...
                    continue
                if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                    ...
                    continue
                logger.error(...)
                raise
```

Đây là lý do timeout của client phía Main Service được đặt rộng: trong tình huống xấu, nhiều key và nhiều model phải thử lần lượt, tổng thời gian có thể kéo dài.

## 13. Node tools - truy hồi nội bộ và tra cứu web

**Vai trò & vị trí.** Node `tools` là một `ToolNode` của LangGraph, được node `agent` kích hoạt khi phát ra `tool_calls`. Nó tái sử dụng đúng hai công cụ của chat:

```python
tools = [retrieve_internal_law, search_web_for_law]
guided_tools_node = ToolNode(tools)
```

**Đầu vào / Đầu ra.** Đầu vào là các `tool_calls` trong AIMessage cuối của Agent (mỗi call kèm tham số `query` mà Agent đã copy từ planning message). Đầu ra là các `ToolMessage` (mang `name` của tool) được nối vào `messages` — chính `name` này là căn cứ để `route_after_guided_agent` đếm "tool nào đã gọi".

**Xử lý.** Vì hai công cụ là hàm thuần, hành vi của chúng trong guided giống hệt trong chat:

- `retrieve_internal_law` → vector search trong ChromaDB rồi rerank bằng cross-encoder (trộn `0.3` vector + `0.7` cross-encoder, year boost, ngưỡng `0.50`, `top_k=10`), trả về text có nhãn ⛔/✅ phân biệt văn bản cũ/mới.
- `search_web_for_law` → chạy **song song** Google Search Grounding (realtime) và Tavily (giới hạn domain pháp luật chính thống), ưu tiên kết quả realtime khi gộp.

Tài liệu luồng chat (mục 11–12 và 21.13–21.16) đã mổ chi tiết hai công cụ này, nên ở đây chỉ cần nắm: chúng được dùng lại **nguyên vẹn**. Khác biệt giữa hai luồng nằm ở phần điều phối và prompt, không nằm ở công cụ.

**Lý do thiết kế.** Tái sử dụng tool thuần giúp tránh trùng lặp code và đảm bảo cả hai luồng truy hồi nhất quán; mọi cải tiến chất lượng truy hồi áp dụng cho chat tự động có hiệu lực cho guided.

## 14. Node verifier - kiểm chứng và kiểm tra áp dụng clarify

**Vai trò & vị trí.** Node áp chót trước `END`. Làm hai việc: kiểm tra chống bịa đặt (giống chat) **và** bổ sung kiểm tra đặc thù — câu trả lời có thực sự áp dụng thông tin clarify hay không. Mục tiêu của phần bổ sung là bắt trường hợp Agent vẫn trả lời chung chung dù người dùng đã cung cấp thông tin cụ thể.

**Đầu vào.** Node bóc tách từ `messages`: câu trả lời cuối của Agent (AIMessage cuối không có `tool_calls`) và các kết quả tool đã cắt ngắn; đồng thời đọc `clarify_context` từ state để làm chuẩn đối chiếu.

```python
    clarify_context = state.get("clarify_context", "")

    # Extract agent's final answer (last AIMessage without tool_calls)
    agent_answer = None
    for m in reversed(messages):
        if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None):
            ...
            agent_answer = content
            break
```

**Xử lý.** Verifier dùng `settings.verifier_model` với cấu hình chạy nhanh (tắt thinking, `max_output_tokens=4096`) và chuỗi model dự phòng riêng. Prompt giữ các quy tắc chống hallucination của chat (đối chiếu từng số hiệu, từng con số, phân biệt văn bản cũ ⛔ / mới ✅) rồi thêm các kiểm tra riêng cho guided:

```text
KIỂM TRA RIÊNG CHO GUIDED (ngoài các rule trên):
6. ÁP DỤNG THÔNG TIN CLARIFY: Câu trả lời có THỰC SỰ áp dụng từng thông tin user cung cấp không?
   Thông tin user đã cung cấp qua clarify:
{clarify_context or '(không có clarify info)'}
   - Nếu câu trả lời trả lời generic, không nhắc đến các thông tin cụ thể trên → FAIL (issue: "không áp dụng thông tin clarify")
   - Nếu user nói rõ "ô tô" mà câu trả lời liệt kê khung phạt cho cả xe máy, xe đạp lan man → FAIL
   - Nếu có phần "TỔNG KẾT TÌNH HUỐNG CỦA USER" hoặc tương đương nhắc lại thông tin user → OK
```

Đây là lý do `clarify_context` được truyền xuyên suốt pipeline từ endpoint tới tận verifier: nó là tiêu chuẩn để verifier đối chiếu xem câu trả lời có bám sát thông tin người dùng cung cấp không.

**Đầu ra.** Nối vào `messages` một `AIMessage` là câu trả lời cuối. PASS thì giữ nguyên bản gốc; FAIL thì dùng bản sửa theo chiến lược tối thiểu (xóa phần vô căn cứ, không viết thêm nội dung pháp luật mới):

```python
    if verdict == "PASS":
        logger.info("[GUIDED] Verification PASSED")
        return {"messages": [AIMessage(content=agent_answer)]}

    # FAIL → use corrected answer
    ...
    if corrected_answer and corrected_answer.strip() and corrected_answer.strip().upper() != "SAME":
        return {"messages": [AIMessage(content=corrected_answer)]}

    return {"messages": [AIMessage(content=agent_answer)]}
```

**Định tuyến.** Cạnh tĩnh `verifier → END`.

**Xử lý lỗi (fail-open).** Nếu mọi model và key đều cạn, hoặc parse JSON thất bại, verifier **không** làm hỏng luồng mà bỏ qua kiểm chứng và trả về câu trả lời gốc của Agent:

```python
    if response is None:
        logger.warning(f"[GUIDED VERIFIER] All models/keys exhausted: {last_err}. Skipping.")
        return {"messages": [AIMessage(content=agent_answer)]}
```

**Lý do thiết kế.** Lựa chọn fail-open ưu tiên việc luôn có câu trả lời cho người dùng hơn là chặn cứng khi không kiểm chứng được — câu trả lời gốc vốn đã bị ràng buộc bởi prompt chống bịa đặt ở node agent. Hợp nhất "chấm + sửa" trong một lần gọi giúp không cần vòng lặp retry, còn kiểm tra "áp dụng clarify" là điểm khác biệt cốt lõi khiến guided cho câu trả lời sát tình huống hơn chat.

## 15. Trích xuất câu trả lời và nguồn

Sau khi graph chạy xong, endpoint trích câu trả lời cuối từ AIMessage cuối không có tool_calls, rồi gom nguồn từ kết quả của hai công cụ:

```python
    result = await guided_app.ainvoke(initial_state)

    # Extract final answer from last AIMessage (without tool_calls)
    messages = result["messages"]
    answer = ""
    for m in reversed(messages):
        if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None):
            ...
            answer = content
            break

    # Reuse extractor helpers (pure functions, không phải chat-specific)
    internal_sources = _extract_sources_from_agent(messages)
    web_sources = _extract_sources_from_web_search(messages)
    sources = internal_sources + web_sources
    ...
    if answer and sources:
        before_count = len(sources)
        sources = _filter_relevant_sources(answer, sources)
```

Hệ thống còn dựng `enriched_query` để hiển thị/debug, ghép hai truy vấn mà planning đã sinh:

```python
    enriched_query_parts = [
        f"Internal search: {result.get('internal_search_query', '')}",
        f"Web search: {result.get('web_search_query', '')}",
    ]
    enriched_query = " | ".join(p for p in enriched_query_parts if p.split(": ", 1)[1])
```

Kết quả trả về gồm câu trả lời, danh sách nguồn, truy vấn đã làm giàu, thời gian xử lý và tên model kết hợp (agent + verifier kèm nhãn guided). Vì luồng stateless, đến đây mọi thứ kết thúc: không có bước lưu tin nhắn, không cập nhật tiêu đề hội thoại như luồng chat.

## 16. Chế độ streaming và tiến trình 4 bước

Endpoint `/answer/stream` cho trải nghiệm realtime. Phía Main Service, nó forward các sự kiện từ RAG Service và định hình lại nguồn ở sự kiện `done` cho đồng nhất với endpoint không stream:

```python
    async def event_stream():
        try:
            async for ev in rag_client.stream_guided_answer(
                original_query=data.original_query,
                detected_topic=data.detected_topic,
                answers=[a.model_dump() for a in data.answers],
            ):
                if ev["event"] == "done":
                    # Reshape sources giống endpoint non-stream để mobile đọc đồng nhất.
                    raw_sources = ev["data"].get("sources", [])
                    sources = []
                    for s in raw_sources:
                        meta = s.get("metadata") or {}
                        sources.append({
                            "id": s.get("id", "?"),
                            ...
                        })
                    payload = {
                        "answer": ev["data"].get("answer", ""),
                        "sources": sources,
                        "processing_time": float(ev["data"].get("processing_time", 0.0)),
                    }
                    yield f"event: done\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                else:
                    yield f"event: {ev['event']}\ndata: {json.dumps(ev['data'], ensure_ascii=False)}\n\n"
```

Phía RAG Service, hàm `_stream_guided_pipeline` chạy graph ở chế độ stream theo từng node update, và dùng `PipelineTracker` để ánh xạ node kỹ thuật thành các bước dễ hiểu cho UI. Khác với chat (5 bước), guided chỉ có 4 bước vì không có node guardrail và query_analysis riêng:

```python
_GUIDED_STEPS: List[Tuple[str, str]] = [
    ("validate", "Đang chuẩn bị tra cứu"),
    ("retrieve", "Đang tra cứu nguồn"),
    ("synthesize", "Đang tổng hợp câu trả lời"),
    ("verify", "Đang kiểm tra độ chính xác"),
]
```

Bảng ánh xạ node sang bước của guided:

```python
_GUIDED_NODE_TO_STEP = {
    "planning": "validate",
    "agent": "synthesize",
    "tools": "retrieve",
    "verifier": "verify",
}
```

So với chat (`guardrail -> validate`, `query_analysis -> analyze`, ...), guided gộp node planning vào bước "validate" với nhãn "Đang chuẩn bị tra cứu", và không có bước "analyze". Vòng lặp stream chính:

```python
    final_state: dict = {"messages": list(initial_state["messages"])}

    try:
        async for update in guided_app.astream(initial_state, stream_mode="updates"):
            for node_name, delta in update.items():
                _accumulate_state(final_state, delta or {})
                if tracker.on_node(node_name, delta or {}):
                    yield _sse("progress", {"steps": tracker.snapshot()})
    except Exception as e:
        logger.exception(f"[STREAM GUIDED] pipeline error: {e}")
        yield _sse("error", {"message": str(e)})
        return

    tracker.mark_all_done()
    yield _sse("progress", {"steps": tracker.snapshot()})
```

Mỗi khi một node của graph phát update, tracker cập nhật trạng thái bước tương ứng và đẩy một sự kiện `progress`. Node `tools` còn thêm sub-step cho từng công cụ ("Văn bản pháp luật", "Tìm kiếm Internet") để người dùng thấy hệ thống đang tra cứu nguồn nào. Khi graph kết thúc, hàm trích câu trả lời, gom nguồn và phát sự kiện `done`:

```python
    yield _sse("done", {
        "answer": answer or "Không thể tạo câu trả lời.",
        "sources": [s.model_dump() for s in sources],
        "enriched_query": enriched_query or request.original_query,
        "processing_time": processing_time,
        "model": f"{settings.agent_model} + {settings.verifier_model} (guided)",
    })
```

`PipelineTracker` là lớp dùng chung cho cả chat lẫn guided; nó được khởi tạo với bộ bước và bảng ánh xạ khác nhau cho mỗi luồng (`PipelineTracker(_GUIDED_STEPS, _GUIDED_NODE_TO_STEP)`). Đây là một ví dụ tái sử dụng tốt: cùng một cơ chế theo dõi tiến trình, chỉ thay cấu hình bước.

## 17. Tóm tắt luồng xử lý

Toàn bộ luồng tư vấn có hướng dẫn có thể tóm tắt như sau:

```text
Người dùng nhập câu hỏi ban đầu
-> Client gọi /guided/clarify với JWT
-> Main Service xác thực người dùng
-> Main Service gọi RAG Service /guided-clarify
-> RAG Service: 1 lần gọi LLM vừa validate + phân loại + sinh câu hỏi
   -> NOT_LEGAL / OFF_POLICY: trả reason, questions rỗng, dừng
   -> OK: trả detected_topic + danh sách câu hỏi trắc nghiệm
-> Client hiển thị câu hỏi, người dùng chọn đáp án
-> Client gọi /guided/answer/stream với câu hỏi gốc + đáp án đã chọn
-> Main Service gọi RAG Service /guided-answer/stream
-> RAG Service dựng GuidedAgentState + clarify_context
-> Chạy guided graph: planning -> agent <-> tools -> verifier
   -> planning: ghép truy vấn nội bộ + web (không gọi LLM)
   -> agent: bắt buộc gọi đủ retrieve_internal_law + search_web_for_law
   -> verifier: kiểm chứng + kiểm tra áp dụng clarify
-> Phát progress 4 bước qua SSE
-> Trích answer + sources, phát done
-> Client hiển thị câu trả lời cuối (không lưu DB)
```

Thiết kế này đạt ba mục tiêu. Thứ nhất, câu trả lời được cá thể hóa theo tình huống cụ thể của người dùng nhờ thông tin thu thập từ clarify. Thứ hai, chất lượng và độ tin cậy vẫn được đảm bảo nhờ giữ nguyên cơ chế ép gọi đủ công cụ và bước verifier. Thứ ba, kiến trúc tách biệt với chat giúp luồng này tiến hóa độc lập mà không gây rủi ro cho luồng chat chính.

## 18. Các file code chính liên quan

Các file quan trọng của luồng tư vấn có hướng dẫn gồm:

- `vietnam-law-service/main-service/app/api/v1/guided.py`: định nghĩa ba endpoint phía người dùng `/clarify`, `/answer`, `/answer/stream`.
- `vietnam-law-service/main-service/app/schemas/guided.py`: schema request/response phía Main Service (request clarify, request answer, source làm phẳng cho mobile).
- `vietnam-law-service/main-service/app/services/rag_client.py`: các method nội bộ `guided_clarify`, `guided_answer`, `stream_guided_answer` gọi sang RAG Service.
- `vietnam-law-service/rag-service/app/api/v1/rag.py`: endpoint `guided-clarify` và `guided-answer` (đồng bộ) trên RAG Service.
- `vietnam-law-service/rag-service/app/api/v1/rag_stream.py`: hàm `_stream_guided_pipeline`, định nghĩa `_GUIDED_STEPS` và bảng `_GUIDED_NODE_TO_STEP`, endpoint `guided-answer/stream`.
- `vietnam-law-service/rag-service/app/agent/guided_graph.py`: định nghĩa đồ thị LangGraph riêng của guided và hàm điều hướng `route_after_guided_agent`.
- `vietnam-law-service/rag-service/app/agent/guided_nodes.py`: triển khai ba node `guided_planning_node`, `guided_agent_node`, `guided_verification_node` cùng hàm fallback `_invoke_agent_with_fallback`.
- `vietnam-law-service/rag-service/app/agent/guided_state.py`: định nghĩa `GuidedAgentState`.
- `vietnam-law-service/rag-service/app/schemas/guided_clarify.py`: schema phía RAG Service cho clarify và answer.
- `vietnam-law-service/rag-service/app/services/llm_service.py`: `GUIDED_CLARIFY_PROMPT`, hàm `generate_clarifying_questions` và `_build_clarify_fallback`.

## 19. Các đoạn code kỹ thuật quan trọng

Phần này tổng hợp lại các đoạn then chốt nhất, dùng để giải thích khi bảo vệ hoặc phản biện.

### 19.1. GuidedAgentState - state riêng của luồng guided

```python
class GuidedAgentState(TypedDict):
    """State cho Guided Consultation pipeline (tách biệt hoàn toàn với chat AgentState)."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    original_query: str
    detected_topic: str
    clarify_context: str
    internal_search_query: str
    web_search_query: str
    iteration_count: int
```

So với `AgentState` của chat, state này có thêm `original_query`, `detected_topic`, `clarify_context` (các trường structured input đến từ clarify) và không có `is_valid_query` / `rejection_reason` vì không có guardrail. `messages` dùng reducer `add_messages` nên các node nối thêm tin nhắn thay vì ghi đè.

### 19.2. Stateless - request answer tự mang đủ ngữ cảnh

```python
class ClarifyAnswer(BaseModel):
    question_id: str
    question_label: str
    selected_option_label: str
```

Việc gửi cả nội dung câu hỏi và đáp án dạng văn bản (không chỉ id) là chìa khóa của tính stateless. RAG Service không cần nhớ các câu hỏi đã sinh ở `/clarify`; nó ghép trực tiếp `question_label` và `selected_option_label` thành `clarify_context`. Nhờ đó hai endpoint clarify và answer hoàn toàn độc lập, không chia sẻ trạng thái server.

### 19.3. Planning sinh truy vấn không cần LLM

```python
    if detected_topic:
        internal_query = f"{detected_topic} — {original_query}"
    else:
        internal_query = original_query
    ...
    logger.info(f"[TIMING] guided_planning: {time.time() - start:.3f}s (no LLM call)")
```

Đây là điểm khác biệt rõ nhất so với query_analysis của chat. Vì chủ đề đã được phân tích ở clarify, planning chỉ cần ghép chuỗi để tạo truy vấn, bỏ hẳn một lần gọi LLM, giảm độ trễ và giảm nguy cơ lỗi.

### 19.4. Ép gọi đủ hai công cụ

```python
    required_tools = {"retrieve_internal_law", "search_web_for_law"}

    iteration_count = state.get("iteration_count", 0)
    if iteration_count >= 6:
        return "verifier"

    if not required_tools.issubset(tool_names_called):
        return "agent"

    return "verifier"
```

Logic này giống hệt chat, khẳng định rằng dù bỏ guardrail/query_analysis, guided vẫn giữ ràng buộc cốt lõi: phải có cả căn cứ nội bộ lẫn xác minh web trước khi tổng hợp, và có ngưỡng lặp để chống vô hạn.

### 19.5. Verifier kiểm tra áp dụng clarify

```text
6. ÁP DỤNG THÔNG TIN CLARIFY: Câu trả lời có THỰC SỰ áp dụng từng thông tin user cung cấp không?
   Thông tin user đã cung cấp qua clarify:
{clarify_context or '(không có clarify info)'}
   - Nếu câu trả lời trả lời generic, không nhắc đến các thông tin cụ thể trên → FAIL
```

Đây là phần verifier khác chat: ngoài chống bịa đặt, nó còn ép câu trả lời phải cá thể hóa. Nếu Agent trả lời chung chung dù người dùng đã clarify, verifier đánh FAIL và yêu cầu bản sửa.

### 19.6. Bốn bước tiến trình cho UI

```python
_GUIDED_STEPS: List[Tuple[str, str]] = [
    ("validate", "Đang chuẩn bị tra cứu"),
    ("retrieve", "Đang tra cứu nguồn"),
    ("synthesize", "Đang tổng hợp câu trả lời"),
    ("verify", "Đang kiểm tra độ chính xác"),
]
```

Bốn bước thay vì năm bước như chat, phản ánh đúng việc guided không có node guardrail và query_analysis riêng. Tracker là cùng một lớp `PipelineTracker` dùng chung, chỉ khác cấu hình bước và bảng ánh xạ.

## 20. Các câu hỏi phản biện có thể gặp về luồng guided

### Vì sao cần luồng riêng thay vì cải tiến luồng chat?

Vì hai luồng có đầu vào và mục tiêu khác nhau. Chat làm việc với câu hỏi tự do và lịch sử hội thoại, được lưu DB. Guided làm việc với câu hỏi đã được làm rõ qua trắc nghiệm, có structured input và stateless. Tách thành state và graph riêng (`GuidedAgentState`, `guided_graph.py`) giúp thay đổi một bên không ảnh hưởng bên kia, đúng như ghi chú trong code là tách hoàn toàn, không import từ module của chat.

### Bỏ guardrail và query_analysis có làm giảm an toàn không?

Không. Guardrail được thay bằng bước phân loại trạng thái (`NOT_LEGAL`/`OFF_POLICY`/`OK`) ngay trong lần gọi LLM ở `/clarify`; câu hỏi không hợp lệ bị chặn ngay từ chặng đầu. Query_analysis được thay bằng planning xác định. Quan trọng hơn, hai cơ chế an toàn cốt lõi là ép gọi đủ hai công cụ và verifier vẫn được giữ nguyên.

### Tính stateless được đảm bảo bằng cách nào?

Bằng cách để mỗi request tự mang đủ ngữ cảnh. Endpoint không tạo conversation, không ghi PostgreSQL. Request `/answer` gửi kèm `original_query`, `detected_topic` và toàn bộ đáp án ở dạng văn bản (cả câu hỏi lẫn lựa chọn), nên RAG Service không cần nhớ gì giữa hai lần gọi clarify và answer.

### Planning không gọi LLM thì truy vấn có đủ tốt không?

Truy vấn được ghép từ `detected_topic` (do LLM phân tích ở clarify) và câu hỏi gốc. Vì chủ đề đã được mô hình xác định chính xác ở chặng trước, việc ghép chuỗi là đủ để tạo truy vấn có thuật ngữ pháp lý cho vector search và truy vấn tự nhiên cho web search. Nếu thiếu chủ đề, hệ thống lùi về dùng câu hỏi gốc.

### Nếu Gemini quá tải thì luồng có hỏng không?

Có nhiều lớp chống chịu. Ở clarify, khi LLM lỗi hoặc rate limit, hệ thống trả bộ câu hỏi fallback để không dead-end. Ở agent và verifier, có chuỗi model dự phòng kết hợp xoay vòng API key khi gặp 503/429. Nếu verifier cạn mọi model/key, nó bỏ qua kiểm chứng và trả câu trả lời gốc thay vì làm hỏng luồng. Timeout client được đặt 600 giây để chịu được trường hợp xấu nhất.

### Vì sao guided có 4 bước progress còn chat có 5 bước?

Vì số bước UI ánh xạ từ số nhóm node. Chat có guardrail (validate) và query_analysis (analyze) là hai node riêng, nên có thêm bước. Guided gộp việc chuẩn bị vào node planning (bước "Đang chuẩn bị tra cứu") và không có bước phân tích riêng, nên còn 4 bước.

### Verifier FAIL trong guided khác gì trong chat?

Trong chat, FAIL chủ yếu do bịa đặt. Trong guided, FAIL còn có thể do câu trả lời generic, không áp dụng thông tin clarify mà người dùng đã cung cấp. Bản sửa theo cùng chiến lược tối thiểu: giữ phần đúng, xóa phần không căn cứ, và cố gắng bổ sung phần nhắc lại thông tin người dùng nếu có sẵn nguyên liệu, nhưng không được viết thêm nội dung pháp luật mới ngoài kết quả tra cứu.
