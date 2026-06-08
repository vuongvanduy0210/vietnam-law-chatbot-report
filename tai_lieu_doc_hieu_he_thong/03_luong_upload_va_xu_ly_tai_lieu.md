# Luồng upload và xử lý tài liệu pháp luật

Tài liệu này mô tả luồng admin upload một văn bản pháp luật dạng PDF vào hệ thống trợ lý ảo pháp luật, từ thời điểm chọn file cho đến khi nội dung điều luật được lưu đầy đủ trong cả MongoDB và ChromaDB và sẵn sàng phục vụ truy hồi cho luồng chat. Nội dung được viết theo hướng để người ngoài dự án vẫn có thể hiểu được cách hệ thống vận hành, các thành phần tham gia và lý do thiết kế của từng bước xử lý.

## 1. Vai trò của luồng upload và xử lý tài liệu

Luồng chat chính (mô tả ở tài liệu 01) chỉ có giá trị khi kho tri thức pháp luật phía sau được nạp đầy đủ và chính xác. Luồng upload chính là cơ chế nạp tri thức đó. Đây là luồng dành riêng cho admin: admin tải lên một file PDF văn bản pháp luật (Luật, Nghị định, Thông tư, Quyết định...), hệ thống đọc nội dung, tách thành từng điều luật có cấu trúc, gắn metadata, rồi lưu vào hai kho dữ liệu khác nhau phục vụ hai mục đích khác nhau.

Điểm cốt lõi của luồng này là một văn bản pháp luật sau khi xử lý sẽ tồn tại ở hai dạng song song:

- Dạng văn bản đầy đủ trong MongoDB: dùng cho việc tra cứu, hiển thị chi tiết điều luật cho người dùng, lọc theo lĩnh vực, theo năm.
- Dạng vector embedding của các đoạn nhỏ (chunk) trong ChromaDB: dùng cho tìm kiếm ngữ nghĩa trong luồng chat.

Vì dữ liệu được ghi vào hai kho riêng biệt, hệ thống phải đảm bảo tính nhất quán: hoặc cả hai kho cùng có dữ liệu, hoặc cả hai cùng không có. Không được phép xảy ra trạng thái MongoDB đã lưu nhưng ChromaDB chưa lưu, vì khi đó người dùng có thể thấy điều luật khi tra cứu nhưng luồng chat lại không truy hồi được, hoặc ngược lại. Đây là lý do toàn bộ luồng được bọc bởi cơ chế bù trừ giao dịch (compensating transaction): nếu bước sau thất bại, hệ thống chủ động xóa dữ liệu đã ghi ở bước trước để quay về trạng thái sạch.

Luồng này có ba lớp chính:

- Web admin: chọn file PDF, gửi lên Main Service, hiển thị tiến trình xử lý theo thời gian thực.
- Main Service: nhận file, kiểm tra trùng lặp, OCR và parse bằng Gemini, lưu MongoDB, điều phối ingest sang RAG Service, quản lý trạng thái task và phát tiến trình qua WebSocket.
- RAG Service: nhận danh sách điều luật đã parse, chia chunk, sinh embedding bằng bi-encoder và lưu vào ChromaDB.

## 2. Người dùng phải là admin và file phải hợp lệ

Khác với luồng chat mở cho mọi người dùng đã đăng nhập, luồng upload chỉ dành cho admin. Endpoint chính của luồng xử lý song song nằm trong `main-service/app/api/v1/documents.py`:

```http
POST /api/v1/documents/upload-v2
```

Endpoint này được bảo vệ bởi dependency `get_current_admin`, nghĩa là chỉ tài khoản có vai trò admin mới gọi được. Người dùng thường không có quyền nạp dữ liệu pháp luật vào hệ thống. Đây là quyết định thiết kế quan trọng vì dữ liệu pháp luật là dữ liệu nền tảng: một văn bản sai hoặc rác được nạp vào sẽ ảnh hưởng đến mọi câu trả lời chat sau đó.

Trước khi xử lý, hệ thống kiểm tra định dạng file. Chỉ chấp nhận PDF:

```python
# Allowed file extensions — chỉ PDF vì pipeline parse dùng Gemini Vision (pdf2image)
# và Gemini File API không hỗ trợ native .doc/.docx binary.
ALLOWED_EXTENSIONS = {".pdf"}

# Max file size (50MB default)
MAX_FILE_SIZE = settings.max_file_size_mb * 1024 * 1024
```

Lý do chỉ nhận PDF là toàn bộ pipeline đọc nội dung được thiết kế quanh PDF: bước OCR dùng PyMuPDF và PaddleOCR đọc trang PDF, còn bước dự phòng dùng Gemini Vision cần chuyển PDF thành ảnh. Các định dạng `.doc`/`.docx` không được hỗ trợ trực tiếp. Giới hạn dung lượng mặc định 50MB tránh các file quá lớn làm nghẽn pipeline.

File sau khi nhận được lưu tạm xuống đĩa với tên ngẫu nhiên để tránh trùng tên giữa các lần upload:

```python
ext = Path(file.filename).suffix.lower()
unique_filename = f"{uuid.uuid4()}{ext}"
file_path = UPLOAD_DIR / unique_filename
```

## 3. Tạo DocumentTask để theo dõi tiến trình

Ngay khi nhận file, trước khi làm bất cứ việc nặng nào, Main Service tạo một bản ghi `DocumentTask` trong PostgreSQL:

```python
task_repo = DocumentTaskRepository(db)
# ========== STEP 0: Create DB Task ==========
doc_task = await task_repo.create_task(
    filename=file.filename or "unknown.pdf",
    file_size_bytes=file.size,
    user_id=current_user.id,
)
```

`DocumentTask` là một bảng riêng đóng vai trò sổ theo dõi cho từng lần upload. Mỗi task ghi lại tên file, dung lượng, người upload, trạng thái hiện tại, phần trăm tiến độ, bước đang chạy, kết quả (law_id, số điều) và thông báo lỗi nếu có. Việc tạo task ngay từ đầu có ba lợi ích:

- Người upload có một định danh task để theo dõi và có thể hủy giữa chừng.
- Nếu quá trình xử lý lỗi ở bất kỳ bước nào, trạng thái lỗi vẫn được ghi lại để admin xem lại trong lịch sử upload.
- Dashboard có thể thống kê số lần upload thành công/thất bại dựa trên các task này.

Trạng thái của task được định nghĩa bằng enum trong `main-service/app/models/document_task.py`:

```python
class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

Đáng chú ý là khi tạo, task được đặt thẳng vào trạng thái `PROCESSING` chứ không phải `PENDING`, vì pipeline bắt đầu chạy ngay trong cùng request:

```python
task = DocumentTask(
    filename=filename,
    file_size_bytes=file_size_bytes,
    user_id=user_id,
    status=TaskStatus.PROCESSING,
    progress=0,
    current_step="Bắt đầu tải lên...",
)
```

Repository cũng có một quy ước nhỏ nhưng quan trọng: khi task chuyển sang một trong các trạng thái kết thúc (`COMPLETED`, `FAILED`, `CANCELLED`), trường `completed_at` được tự động đóng dấu thời gian:

```python
if "status" in update_data:
    if update_data["status"] in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
        update_data["completed_at"] = datetime.utcnow()
```

## 4. Kết nối WebSocket để nhận tiến trình realtime

Quá trình xử lý một PDF có thể mất từ vài chục giây đến vài phút (OCR, gọi Gemini, sinh embedding). Để admin không phải nhìn màn hình chờ tĩnh, hệ thống đẩy tiến trình realtime qua WebSocket.

Web admin mở kết nối WebSocket tới endpoint:

```http
GET /api/v1/documents/ws?token=<jwt>
```

Việc xác thực WebSocket được làm qua query param thay vì header, vì WebSocket API của trình duyệt không cho phép set Authorization header:

```python
@router.websocket("/ws")
async def websocket_document_tasks(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token (browsers không set được header cho WS)"),
):
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        await websocket.close(code=4401, reason="Invalid or expired token")
        return

    user_id = str(payload["sub"])
    await ws_manager.connect(websocket, user_id)
```

Điểm quan trọng là kết nối được scope theo `user_id`. Một admin chỉ nhận được tiến trình của chính mình, không thấy tiến trình upload của admin khác. Cơ chế này nằm trong `main-service/app/services/websocket_manager.py`, nơi quản lý nhiều kết nối theo từng user (một admin có thể mở nhiều tab):

```python
class ConnectionManager:
    def __init__(self):
        # user_id → list các WebSocket đang mở (hỗ trợ nhiều tab cùng user)
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Gửi message tới toàn bộ tab của 1 user duy nhất. Các user khác không nhận."""
        conns = self.active_connections.get(user_id)
        if not conns:
            return
        dead: List[WebSocket] = []
        for conn in conns:
            try:
                await conn.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to user={user_id}: {e}")
                dead.append(conn)
        for conn in dead:
            self.disconnect(conn, user_id)
```

Trong suốt pipeline, mọi cập nhật tiến trình được gửi qua hai loại message:

- `UPLOAD_PROGRESS`: cập nhật phần trăm và mô tả bước đang chạy.
- `UPLOAD_STATUS`: báo trạng thái kết thúc (completed/failed/cancelled).

## 5. Tiền kiểm tra trùng lặp trước khi parse

Bước parse một văn bản đầy đủ bằng Gemini có thể tốn 30 đến 120 giây và tiêu tốn token. Nếu file đã từng được nạp, chạy lại toàn bộ là lãng phí. Vì vậy trước khi parse, hệ thống thực hiện hai lớp tiền kiểm tra trùng lặp theo nguyên tắc rẻ trước, đắt sau.

### Lớp a: kiểm tra theo hash file (gần như 0 chi phí)

Hệ thống tính SHA-256 của toàn file rồi tra xem đã có văn bản nào được nạp với đúng hash này chưa. Hàm hash đọc theo từng khối để không nạp cả file lớn vào RAM:

```python
def _hash_file_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> Optional[str]:
    """Compute SHA-256 của file — dùng cho pre-check trùng file trước khi parse."""
    try:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to hash file {file_path}: {e}")
        return None
```

Nếu hash trùng, hệ thống đánh dấu task failed và trả lỗi 409 ngay, không gọi Gemini lần nào:

```python
existing_law_id = await law_repo.find_law_by_file_hash(file_hash)
if existing_law_id:
    err_msg = (
        f"Văn bản '{existing_law_id}' đã tồn tại trong hệ thống "
        f"(phát hiện qua file hash — file giống hệt file đã upload trước đó). "
        f"Văn bản pháp luật không được phép ghi đè."
    )
    await _fail_duplicate(err_msg)
    return error_response(
        code=ErrorCode.CONFLICT,
        message=err_msg,
        status_code=status.HTTP_409_CONFLICT,
    )
```

Lớp này chỉ bắt được trường hợp file giống hệt từng byte. Nếu cùng một văn bản nhưng được scan lại, nén lại hay đổi metadata PDF thì hash sẽ khác — lúc đó cần lớp b.

### Lớp b: quick precheck trang đầu bằng một lệnh gọi Gemini

Hệ thống đọc 1 đến 2 trang đầu của PDF và gửi cho Gemini trong một lệnh gọi duy nhất, vừa để phân loại (có phải văn bản pháp luật Việt Nam không) vừa để trích số hiệu văn bản (`law_id`):

```python
parser = get_document_parser()
quick_result = await parser.quick_precheck(str(file_path), max_pages=2)
```

Quick precheck phục vụ hai mục đích chặn sớm:

- Nếu Gemini xác định đây không phải văn bản pháp luật Việt Nam (ví dụ là sách, hợp đồng cá nhân, hóa đơn, slide), hệ thống reject ngay với mã 400, không parse tiếp.
- Nếu là văn bản pháp luật và trích được `law_id` đã tồn tại, hệ thống reject với mã 409.

```python
# (b.2) Extract law_id để dùng làm hint cho full parse + check trùng sớm
quick_law_id = quick_result.get("law_id") or None
if quick_law_id:
    quick_exists = await law_repo.exists_by_law_id(quick_law_id)
    if quick_exists:
        err_msg = (
            f"Văn bản '{quick_law_id}' đã tồn tại trong hệ thống. "
            f"Văn bản pháp luật không được phép ghi đè."
        )
        await _fail_duplicate(err_msg)
        return error_response(
            code=ErrorCode.CONFLICT,
            message=err_msg,
            status_code=status.HTTP_409_CONFLICT,
        )
```

Một chi tiết thiết kế quan trọng: nếu quick precheck thất bại (Gemini lỗi mạng, lỗi convert PDF...), hệ thống không dừng luồng mà fallback sang full parse như bình thường. Tiền kiểm tra chỉ là tối ưu, không phải điều kiện bắt buộc:

```python
try:
    parser = get_document_parser()
    quick_result = await parser.quick_precheck(str(file_path), max_pages=2)
except Exception as e:
    logger.warning(f"quick_precheck failed (fallback to full parse): {e}")
    quick_result = None
```

Số hiệu văn bản lấy được từ quick precheck (`quick_law_id`) còn được dùng làm gợi ý (hint) cho bước parse đầy đủ, giúp Gemini đọc đúng số hiệu kể cả khi phần số được viết tay.

## 6. Pipeline đọc nội dung: OCR tự host trước, Gemini Vision dự phòng

Sau khi vượt qua tiền kiểm tra, Main Service gọi `DocumentProcessor` để chạy pipeline đọc nội dung. Logic điều phối nằm trong `main-service/app/services/document_processor.py`, hàm `process_from_upload`.

Pipeline này không gửi thẳng PDF cho Gemini làm OCR (vì OCR bằng LLM tốn token và chậm). Thay vào đó nó dùng chiến lược hai tầng:

1. Tầng chính: OCR tự host bằng PyMuPDF và PaddleOCR để rút text sạch, rồi chỉ nhờ Gemini cấu trúc hóa text đó thành JSON. Gemini ở đây làm việc cấu trúc, không làm OCR.
2. Tầng dự phòng: nếu OCR tự host thất bại hoặc bước cấu trúc hóa thất bại, hệ thống mới dùng Gemini Vision đọc trực tiếp từ ảnh PDF.

Một điểm tối ưu nữa là việc upload PDF gốc lên Cloudinary chạy song song với OCR, vì hai việc này không phụ thuộc nhau:

```python
# Start Cloudinary upload in background (doesn't depend on OCR)
cloud_task = asyncio.to_thread(
    self._cloud_storage.upload_file,
    file_path=file_path,
    public_id=custom_public_id,
)

# Run OCR in thread (CPU-bound)
ocr_result = await asyncio.to_thread(self._ocr.extract_text, file_path)
```

OCR là tác vụ nặng CPU nên được đẩy sang thread bằng `asyncio.to_thread` để không chặn vòng lặp sự kiện async. Cloudinary upload là tác vụ chờ mạng, cũng chạy song song. Nhờ vậy thời gian chờ tổng thể xấp xỉ thời gian của tác vụ chậm hơn thay vì cộng dồn.

### OCR tự host hoạt động thế nào

Logic OCR nằm trong `main-service/app/services/ocr_service.py`. Nó phân loại từng trang PDF thành hai loại:

- Trang digital: PDF có sẵn lớp text, PyMuPDF rút text trực tiếp, nhanh và chính xác.
- Trang scan: trang chỉ là ảnh, không có lớp text, phải OCR bằng PaddleOCR (hoặc Tesseract dự phòng).

Ngưỡng phân loại dựa trên mật độ ký tự của trang:

```python
# Minimum text density to consider a page as "digital" (has real text layer)
MIN_CHARS_PER_PAGE = 50
```

```python
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text("text").strip()
    is_digital = len(text) >= MIN_CHARS_PER_PAGE
    pages.append((page_num, text, is_digital))
```

Sau khi rút text, hệ thống làm sạch (chuẩn hóa Unicode NFC, sửa các lỗi OCR phổ biến của tiếng Việt như "Điéu" thành "Điều", loại bỏ header/footer lặp lại, số trang) rồi đánh giá chất lượng. Nếu text quá ngắn, mật độ chữ quá thấp hoặc không tìm thấy dấu hiệu cấu trúc pháp lý (Điều, Khoản, Nghị định...), OCR bị coi là thất bại và pipeline chuyển sang tầng dự phòng:

```python
legal_markers = [
    r"Điều\s+\d+",
    r"Khoản\s+\d+",
    r"Nghị định|Thông tư|Luật|Quyết định",
]
marker_count = sum(
    1 for pattern in legal_markers
    if re.search(pattern, text)
)
if marker_count == 0:
    logger.warning("No Vietnamese legal markers found in text")
    return False
```

### Gemini cấu trúc hóa text sạch

Nếu OCR thành công, text sạch được gửi cho Gemini để cấu trúc hóa (không phải OCR):

```python
parse_result = await self._parser.parse(
    text=ocr_result.text,
    law_id_hint=law_id_hint,
)
```

### Tầng dự phòng: Gemini Vision đọc thẳng từ ảnh

Nếu OCR hoặc bước cấu trúc hóa thất bại, hệ thống dùng Gemini File API đọc thẳng PDF:

```python
# ── STEP 3 (FALLBACK): Gemini File API if OCR pipeline failed ──
if parse_result is None or not parse_result.success:
    used_fallback = True
    result.current_step = "Gemini Vision (fallback)"
    await self._notify(result)
    ...
    parse_result = await self._parser.parse_using_file_api(
        pdf_path=file_path,
        law_id_hint=law_id_hint,
    )
```

Sau khi có kết quả parse, pipeline chờ Cloudinary upload hoàn tất để lấy URL PDF gốc. Nếu Cloudinary lỗi, toàn bộ bị coi là thất bại vì sau này không có link để hiển thị văn bản gốc cho người dùng:

```python
# ── STEP 4: Wait for Cloudinary upload ──
cloud_result = await cloud_task

if not cloud_result.success:
    error_msg = f"Cloudinary upload failed: {cloud_result.error}"
    result.error = error_msg
    result.status = ProcessingStatus.FAILED
    return result

result.source_url = cloud_result.url
```

## 7. Gemini Vision parse và sinh metadata bằng regex

Phần parse nội dung pháp luật nằm trong `main-service/app/services/document_parser.py`. Đây là nơi định nghĩa prompt hướng dẫn Gemini trích xuất cấu trúc điều luật.

Điểm thiết kế quan trọng nhất của prompt là Gemini chỉ trích cấu trúc (số hiệu văn bản, năm, danh sách điều với tiêu đề và nội dung), KHÔNG sinh metadata (topics, keywords, summary). Metadata được sinh sau bằng regex:

```text
## NHIỆM VỤ
Đọc hình ảnh văn bản pháp luật và trích xuất CẤU TRÚC các điều luật dưới dạng JSON.
KHÔNG cần sinh metadata (topics/keywords/summary) — hệ thống sẽ tự xử lý phần đó.
```

Output bắt buộc là JSON thuần với cấu trúc:

```json
{
  "law_id": "08/2026/TT-BCT",
  "year": "2026",
  "articles": [
    {
      "article_id": "1",
      "title": "Điều 1. Sửa đổi, bổ sung khoản 2 của Điều 5...",
      "text": "Nội dung đầy đủ của điều..."
    }
  ]
}
```

Để ép Gemini trả về JSON đáng tin cậy, lệnh gọi API đặt nhiệt độ thấp và yêu cầu MIME type là JSON:

```python
request_body = {
    "contents": [{"parts": parts}],
    "generationConfig": {
        "temperature": 0.1,
        "topP": 0.95,
        "responseMimeType": "application/json"
    }
}
```

### Xử lý xung đột article_id với Quy chế kèm theo

Nhiều văn bản pháp luật có một Quy chế/Quy định/Điều lệ kèm theo, mà phần này lại có hệ thống Điều độc lập cũng bắt đầu từ Điều 1. Nếu không xử lý, sẽ có hai điều cùng `article_id = "1"`, vi phạm ràng buộc khóa chính trong MongoDB. Prompt yêu cầu Gemini gắn prefix `QC_`. Nhưng để phòng trường hợp Gemini không tuân thủ, hàm `_build_parsed_document` còn có lớp tự sửa:

```python
seen_ids: set = set()
for art_data in data.get("articles", []):
    article_id = str(art_data.get("article_id", "")).strip()
    title = art_data.get("title", "") or ""

    if article_id in seen_ids:
        new_id = f"QC_{article_id}"
        # Nếu vẫn trùng (văn bản có nhiều phụ lục), thêm số để unique
        counter = 2
        while new_id in seen_ids:
            new_id = f"QC{counter}_{article_id}"
            counter += 1
        ...
        article_id = new_id
    seen_ids.add(article_id)
```

### Sinh metadata bằng regex

Mỗi điều luật được gắn metadata bằng `metadata_enricher`, hoàn toàn deterministic, không tốn token và không bị Gemini bịa:

```python
# Enrich metadata bằng regex (không cần LLM)
meta = enrich_article(title=title, text=text)
```

Hàm `enrich_article` trong `main-service/app/services/metadata_enricher.py` chạy text qua các bảng regex để rút ra ba thông tin:

```python
def enrich_article(title: str, text: str) -> dict:
    combined = f"{title or ''} {text or ''}"
    return {
        "topics": extract_topics(combined, max_topics=3),
        "keywords": extract_keywords(combined, max_keywords=10),
        "summary": extract_summary(title, text),
    }
```

- `topics`: tối đa 3 chủ đề, ánh xạ từ các mẫu như "hình sự", "đất đai", "lao động" sang tên chủ đề chuẩn.
- `keywords`: tối đa 10 thuật ngữ pháp lý nhận dạng được.
- `summary`: dòng nội dung thực chất đầu tiên sau dòng "Điều X. Tiêu đề".

Quyết định dùng regex thay vì LLM cho metadata là một đánh đổi có chủ đích: regex kém linh hoạt hơn LLM nhưng nhanh, miễn phí, ổn định và quan trọng nhất là không hallucinate. Với metadata dùng để lọc và gợi ý, tính ổn định quan trọng hơn sự tinh tế.

### Multi-key rotation và retry

Vì Gemini có giới hạn rate, parser hỗ trợ nhiều API key và xoay vòng khi bị giới hạn:

```python
# Max retries = số lần thử = max(keys * 2, 5)
# → mỗi key được thử 2 lần, tối thiểu 5 lần tổng
self._max_retries = max(len(self._keys) * 2, 5) if self._keys else 5
# Delays ngắn hơn giữa các lần rotate key; backoff dài hơn khi đã xoay hết vòng
self._retry_delays = [2, 5, 10, 20, 40, 60, 90]
```

Hệ thống phân biệt lỗi nên retry (503, 429, overload, quota, timeout) với lỗi không nên retry (lỗi nội dung), để không phí thời gian thử lại với lỗi không thể khắc phục:

```python
@staticmethod
def _is_retryable(error_msg: str) -> bool:
    if not error_msg:
        return False
    err_lower = error_msg.lower()
    return any(
        x in err_lower
        for x in [
            "503", "unavailable", "overloaded", "429",
            "resource_exhausted", "quota", "deadline", "timeout",
        ]
    )
```

## 8. Cập nhật tiến trình qua callback

Toàn bộ pipeline trong `DocumentProcessor` báo tiến trình ra ngoài bằng một callback. Endpoint đăng ký callback này để vừa cập nhật DocumentTask trong PostgreSQL vừa đẩy WebSocket:

```python
async def on_progress(p_result):
    # Update Database
    await task_repo.update_task(
        doc_task.id,
        status=p_result.status.value,
        progress=p_result.progress,
        current_step=p_result.current_step,
    )
    # Push WebSocket
    await ws_manager.send_to_user(str(current_user.id), {
        "type": "UPLOAD_PROGRESS",
        "task_id": str(doc_task.id),
        "status": p_result.status.value,
        "progress": p_result.progress,
        "current_step": p_result.current_step,
        "filename": doc_task.filename
    })

processor.set_progress_callback(on_progress)
```

Các mốc phần trăm được set trong pipeline phản ánh các giai đoạn:

```text
5%   Kiểm tra trùng lặp (hash)
10%  Kiểm tra & nhận dạng văn bản (trang đầu)
30%  OCR xong, bắt đầu LLM Structuring
70%  Cấu trúc hóa xong
80%  Parse hoàn tất, chuẩn bị lưu
100% Hoàn tất (sau khi lưu Mongo + Chroma)
```

Một chi tiết đáng lưu ý: callback được bọc trong try/except và nuốt lỗi, vì lỗi gửi tiến trình (ví dụ WebSocket đã đóng) không được phép làm hỏng pipeline xử lý chính:

```python
async def _notify(self, result: ProcessingResult):
    if self._progress_callback:
        try:
            await self._progress_callback(result)
        except:
            pass
```

## 9. Cho phép hủy giữa chừng khi client ngắt kết nối

Pipeline chạy như một asyncio task. Endpoint chạy đồng thời một task giám sát xem client (web admin) có ngắt kết nối hay không, và dùng `asyncio.wait` với `FIRST_COMPLETED` để bên nào xong trước thì xử lý theo bên đó:

```python
process_task = asyncio.create_task(processor.process_from_upload(
    file_path=str(file_path),
    law_id_hint=quick_law_id,
))
_active_upload_tasks[doc_task.id] = process_task

# ========== STEP 3: Handle Client Disconnect ==========
async def check_disconnect():
    while True:
        if await request.is_disconnected():
            return True
        await asyncio.sleep(1)

disconnect_task = asyncio.create_task(check_disconnect())

done, pending = await asyncio.wait(
    [process_task, disconnect_task],
    return_when=asyncio.FIRST_COMPLETED
)
```

Nếu phát hiện client ngắt trước khi pipeline xong, hệ thống hủy pipeline, đánh dấu task là `cancelled` và báo WebSocket:

```python
if disconnect_task in done:
    logger.warning(f"⚠️ Client disconnected during upload. Cancelling process for {file.filename}")
    process_task.cancel()
    try:
        await process_task
    except asyncio.CancelledError:
        pass

    await task_repo.update_task(
        doc_task.id,
        status="cancelled",
        error_message="Quá trình bị huỷ bởi người quản trị."
    )
```

Handle của task đang chạy còn được lưu trong một dictionary toàn cục `_active_upload_tasks` để endpoint hủy thủ công (`POST /documents/tasks/{task_id}/cancel`) có thể gọi `cancel()` trực tiếp:

```python
if task_id in _active_upload_tasks:
    task = _active_upload_tasks[task_id]
    if not task.done():
        task.cancel()
        logger.info(f"🚫 User {current_user.id} đã yêu cầu huỷ task {task_id}")
        return success_response(message="Đã huỷ tiến trình đang chạy")
```

Khi pipeline bị hủy trong lúc đang upload Cloudinary, `DocumentProcessor` còn chủ động xóa file đã upload lên Cloudinary để không để lại rác:

```python
except asyncio.CancelledError:
    logger.warning(f"⚠️ Process cancelled. Cleaning up: {custom_public_id}")
    result.error = "Cancelled by user"
    result.status = ProcessingStatus.FAILED
    asyncio.create_task(
        asyncio.to_thread(self._cloud_storage.delete_file, public_id=custom_public_id)
    )
    raise
```

## 10. Validate kết quả parse trước khi lưu

Trước khi ghi vào database, kết quả parse phải qua một bước validate nghiêm ngặt trong `main-service/app/services/validators.py`:

```python
validation = validate_parsed_document(parsed_doc)
if not validation.is_valid:
    logger.warning(f"Validation failed for {parsed_doc.law_id}: {validation.to_dict()}")
    err_msg = f"Dữ liệu không hợp lệ ({validation.to_dict()['error_count']} lỗi): " + "; ".join([e.message for e in validation.errors[:5]])
    await task_repo.update_task(doc_task.id, status="failed", error_message=err_msg)
    ...
    return error_response(
        code=ErrorCode.VALIDATION_ERROR,
        message=err_msg,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
```

Validator kiểm tra các điều kiện cần để dữ liệu nhất quán:

- `law_id` không rỗng và đủ dài.
- Có ít nhất một điều luật và không có `article_id` trùng (lần nữa, vì `article_id` trùng sẽ gây trùng khóa chính trong MongoDB).
- Mỗi điều có `article_id`, `title`, `text` không rỗng; `text` tối thiểu 10 ký tự.
- `year` nếu có phải đúng 4 chữ số; `topics`/`keywords` phải là list.

```python
# Check for duplicate article_ids
article_ids = [a.article_id for a in doc.articles]
seen = set()
duplicates = set()
for aid in article_ids:
    if aid in seen:
        duplicates.add(aid)
    seen.add(aid)

if duplicates:
    result.add_error(
        "articles",
        f"Có điều luật trùng article_id: {', '.join(sorted(duplicates))}"
    )
```

Bước validate này là tuyến phòng thủ cuối trước khi ghi dữ liệu, đảm bảo không nạp dữ liệu rác vào kho tri thức pháp luật.

## 11. Kiểm tra trùng law_id lần cuối

Dù đã có tiền kiểm tra ở bước 5, sau khi parse đầy đủ hệ thống vẫn kiểm tra lại `law_id` thật một lần nữa, vì số hiệu đọc được từ full parse có thể chính xác hơn so với quick precheck:

```python
# ========== STEP 4: Check duplicate law_id ==========
law_repo = LawRepository()
exists = await law_repo.exists_by_law_id(parsed_doc.law_id)
if exists:
    err_msg = f"Văn bản '{parsed_doc.law_id}' đã tồn tại trong hệ thống. Văn bản pháp luật không được phép ghi đè."
    await task_repo.update_task(doc_task.id, status="failed", error_message=err_msg)
    ...
    return error_response(
        code=ErrorCode.CONFLICT,
        message=err_msg,
        status_code=status.HTTP_409_CONFLICT,
    )
```

Nguyên tắc văn bản pháp luật không được ghi đè là một quyết định nghiệp vụ. Nếu cần sửa, admin phải xóa văn bản cũ rồi nạp lại, không cho phép upload đè âm thầm làm sai lệch dữ liệu.

## 12. Lưu vào MongoDB

Nếu mọi kiểm tra qua hết, hệ thống dựng danh sách document để lưu MongoDB. Mỗi điều luật là một document, với khóa chính `_id` được ghép từ `law_id` và `article_id`:

```python
# ========== STEP 5: Save to MongoDB ==========
mongo_docs = []
cloudinary_url = result.source_url  # PDF link from Cloudinary
for article in parsed_doc.articles:
    doc_id = f"{parsed_doc.law_id}_{article.article_id}"
    doc = {
        "_id": doc_id,
        "law_id": parsed_doc.law_id,
        "article_id": article.article_id,
        "title": article.title,
        "text": article.text,
        "metadata": {
            "topics": article.metadata.topics,
            "keywords": article.metadata.keywords,
            "summary": article.metadata.summary,
            "year": article.metadata.year,
        },
        "full_content_search": f"{article.title} \n {article.text}",
    }
    # Gắn link PDF nếu có
    if cloudinary_url:
        doc["source_url"] = cloudinary_url
    mongo_docs.append(doc)

saved_count = await law_repo.save_articles(mongo_docs)
```

Cách tạo `_id` theo công thức `{law_id}_{article_id}` (ví dụ `01/2025/QH16_1`) là một thiết kế quan trọng: nó vừa đảm bảo mỗi điều luật là duy nhất, vừa tạo liên kết logic giữa MongoDB và ChromaDB (ChromaDB cũng dùng tiền tố tương tự cho chunk id). Trường `full_content_search` ghép tiêu đề và nội dung phục vụ tìm kiếm full-text.

Hàm `save_articles` trong `main-service/app/repositories/law_repository.py` ghi theo batch để hiệu quả với văn bản nhiều điều:

```python
# Batch insert (1000 per batch, matching original ingest script)
inserted = 0
batch_size = 1000
for i in range(0, len(articles), batch_size):
    batch = articles[i:i + batch_size]
    result = await collection.insert_many(batch)
    inserted += len(result.inserted_ids)
```

## 13. Gọi RAG Service để ingest vào ChromaDB

Sau khi MongoDB lưu xong, Main Service gửi cùng danh sách điều luật (không kèm `full_content_search`, vì RAG Service sẽ tự dựng nội dung chunk) sang RAG Service qua `rag_client.ingest_articles`:

```python
# ========== STEP 6: Send to RAG Service (ChromaDB) ==========
rag_articles = [
    {
        "law_id": parsed_doc.law_id,
        "article_id": article.article_id,
        "title": article.title,
        "text": article.text,
        "metadata": {
            "topics": article.metadata.topics,
            "keywords": article.metadata.keywords,
            "summary": article.metadata.summary,
            "year": article.metadata.year,
        },
    }
    for article in parsed_doc.articles
]

try:
    rag_result = await rag_client.ingest_articles(rag_articles)
    rag_success = rag_result.get("success", False)
except Exception as rag_err:
    rag_success = False
    rag_result = {"message": str(rag_err)}
```

`RAGClient` trong `main-service/app/services/rag_client.py` gọi RAG Service bằng API key nội bộ, đúng theo kiến trúc tách lớp xác thực (client xác thực với Main Service bằng JWT; Main Service xác thực với RAG Service bằng API key):

```python
async def ingest_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(
                f"{self.base_url}/api/v1/ingest/articles",
                json={"articles": articles},
                headers={"X-API-Key": settings.rag_service_api_key},
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {
                "success": False,
                "message": f"Không thể kết nối đến RAG Service: {str(e)}",
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "message": f"RAG Service error: {e.response.status_code} - {e.response.text}",
            }
```

Lưu ý cách xử lý lỗi ở đây: client không ném exception ra ngoài mà trả về dict với `success=False`. Điều này giúp endpoint phía Main Service luôn nhận được kết quả rõ ràng để quyết định có rollback hay không.

## 14. RAG Service chunk, embed và lưu ChromaDB

Endpoint nhận ingest nằm trong `rag-service/app/api/v1/ingest.py`. Quá trình gồm ba bước: chunk, encode, lưu.

### Chunking

Tham số chunking được định nghĩa cố định, khớp với script ingest gốc:

```python
MAX_CHUNK_WORDS = 1000
CHUNK_OVERLAP = 150
```

Mỗi điều luật được chunk theo chiến lược lai: nếu điều ngắn (≤ 1000 từ) thì giữ nguyên thành một chunk; nếu dài hơn thì cắt thành nhiều chunk có overlap 150 từ:

```python
def _chunk_article(article: ArticleRequest) -> List[Dict[str, Any]]:
    text = article.text
    word_count = _count_words(text)
    results = []

    if word_count <= MAX_CHUNK_WORDS:
        # Short article — keep as-is
        content = f"{article.title}\n\n{text}"
        metadata = _create_metadata(article, chunk_index=0, total_chunks=1)
        chunk_id = f"{article.law_id}_{article.article_id}_chunk0"
        results.append({"id": chunk_id, "content": content, "metadata": metadata})
    else:
        # Long article — split into chunks
        text_chunks = _split_text_with_overlap(text)
        total_chunks = len(text_chunks)

        for idx, chunk_text in enumerate(text_chunks):
            content = f"{article.title}\n\n{chunk_text}"
            metadata = _create_metadata(article, chunk_index=idx, total_chunks=total_chunks)
            chunk_id = f"{article.law_id}_{article.article_id}_chunk{idx}"
            results.append({"id": chunk_id, "content": content, "metadata": metadata})

    return results
```

Việc cắt chunk không cắt cứng giữa câu mà tìm dấu câu gần nhất để cắt tự nhiên, tránh làm đứt ngữ nghĩa:

```python
while start < len(words):
    end = min(start + max_words, len(words))
    chunk_words = words[start:end]
    chunk_text = ' '.join(chunk_words)

    # Find nearest punctuation for natural cut
    if end < len(words):
        for i in range(len(chunk_text) - 1, max(0, len(chunk_text) - 100), -1):
            if chunk_text[i] in '.!?;':
                chunk_text = chunk_text[:i + 1]
                break

    chunks.append(chunk_text.strip())
    start = end - overlap if end < len(words) else end
```

Overlap 150 từ giữa các chunk liền nhau đảm bảo một câu hoặc một ý nằm ở ranh giới chunk không bị mất ngữ cảnh: phần cuối chunk trước được lặp lại ở đầu chunk sau, nên truy vấn ngữ nghĩa vẫn bắt được dù khớp ở vùng giáp ranh.

Mỗi chunk có id theo công thức `{law_id}_{article_id}_chunk{index}` (ví dụ `01/2025/QH16_1_chunk0`). Công thức này khớp với `_id` trong MongoDB ở phần tiền tố, tạo nên mối liên kết: từ một chunk id trong ChromaDB có thể suy ra điều luật gốc trong MongoDB.

Metadata của chunk được dựng riêng cho ChromaDB. Vì ChromaDB chỉ hỗ trợ metadata kiểu scalar, các trường list như `topics`/`keywords` được serialize thành chuỗi JSON:

```python
def _create_metadata(article: ArticleRequest, chunk_index: int, total_chunks: int) -> Dict[str, Any]:
    """Create ChromaDB metadata (topics/keywords as JSON strings)."""
    return {
        "law_id": article.law_id,
        "article_id": article.article_id,
        "title": article.title,
        "chunk_index": chunk_index,
        "total_chunks": total_chunks,
        "year": article.metadata.year or "",
        "topics": json.dumps(article.metadata.topics, ensure_ascii=False),
        "keywords": json.dumps(article.metadata.keywords, ensure_ascii=False),
        "summary": article.metadata.summary or "",
    }
```

Đây cũng là điểm khác biệt cần nhớ giữa hai kho: cùng một metadata, trong MongoDB lưu dạng array gốc, còn trong ChromaDB lưu dạng JSON string.

### Encode embedding theo batch

Sau khi chunk toàn bộ điều luật, hệ thống gom tất cả nội dung chunk lại và encode một lần bằng bi-encoder:

```python
# 2. Encode embeddings in batch
logger.info(f"Encoding {total_chunks} chunks...")
embeddings = embedding_repo.encode_documents(all_contents)

# Convert numpy arrays to lists for ChromaDB
embedding_lists = [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings]
```

Encode theo batch (một lần cho cả danh sách) hiệu quả hơn nhiều so với encode từng chunk, vì mô hình tận dụng được tính song song trên GPU/CPU. Bi-encoder là `vietnamese-bi-encoder`, được nạp một lần dưới dạng singleton trong `rag-service/app/repositories/embedding_repository.py`:

```python
def encode_documents(self, documents: List[str]) -> np.ndarray:
    """Encode multiple documents to embedding vectors."""
    return self._bi_encoder.encode(documents)
```

Mỗi vector có 768 chiều (theo schema trong tài liệu kiến trúc). Cần chú ý: bi-encoder ở đây phải đúng là mô hình được dùng khi truy vấn trong luồng chat, nếu không vector lúc nạp và vector lúc tìm sẽ không cùng không gian, làm sai kết quả truy hồi.

### Lưu vào ChromaDB theo batch

Cuối cùng, các chunk được ghi vào ChromaDB theo batch 100:

```python
# 3. Insert into ChromaDB in batches
batch_size = 100
for i in range(0, len(all_ids), batch_size):
    end = min(i + batch_size, len(all_ids))
    chroma_repo.collection.add(
        ids=all_ids[i:end],
        documents=all_contents[i:end],
        embeddings=embedding_lists[i:end],
        metadatas=all_metadatas[i:end],
    )
```

Chia batch khi ghi tránh đẩy một payload quá lớn vào ChromaDB một lần, giảm rủi ro timeout hoặc quá tải bộ nhớ. ChromaRepository là singleton kết nối tới collection `vietnamese_law`, có thể là HTTP client (khi chạy ChromaDB qua Docker) hoặc PersistentClient (khi chạy local).

Kết quả trả về cho Main Service gồm tổng số điều và tổng số chunk:

```python
return IngestResponse(
    success=True,
    total_articles=total_articles,
    total_chunks=total_chunks,
    message=f"Đã lưu {total_articles} điều luật ({total_chunks} chunks) vào ChromaDB",
)
```

## 15. Cơ chế bù trừ giao dịch (compensating transaction)

Đây là phần quan trọng nhất về tính đúng đắn. MongoDB và ChromaDB là hai kho riêng, không có giao dịch phân tán giữa chúng. Vì vậy hệ thống dùng mẫu compensating transaction: nếu một bước thất bại, chủ động xóa dữ liệu đã ghi ở bước trước.

### Trường hợp 1: ChromaDB ingest thất bại sau khi MongoDB đã lưu

Nếu RAG Service báo lỗi, Main Service xóa toàn bộ articles vừa lưu trong MongoDB và xóa cache liên quan:

```python
if not rag_success:
    # ⚠️ ROLLBACK: ChromaDB failed → delete MongoDB data
    logger.error(
        f"❌ ChromaDB ingest failed for {parsed_doc.law_id}: "
        f"{rag_result.get('message', 'Unknown error')}. Rolling back MongoDB..."
    )
    try:
        rollback_count = await law_repo.delete_by_law_id(parsed_doc.law_id)
        mongodb = await get_mongodb()
        await mongodb.delete_law_cache(parsed_doc.law_id)
        logger.info(f"🔄 MongoDB rollback: deleted {rollback_count} articles + cache")
    except Exception as rb_err:
        logger.error(f"❌ MongoDB rollback ALSO failed: {rb_err}")

    err_msg = f"Lỗi khi lưu vào ChromaDB: {rag_result.get('message', 'Unknown')}. Dữ liệu đã được hoàn tác (rollback)."
    await task_repo.update_task(doc_task.id, status="failed", error_message=err_msg)
    ...
```

`delete_by_law_id` trong MongoDB xóa mọi điều luật có cùng `law_id`:

```python
async def delete_by_law_id(self, law_id: str) -> int:
    collection = await self._get_collection()
    result = await collection.delete_many({"law_id": law_id})
    logger.info(f"Deleted {result.deleted_count} articles for law_id={law_id}")
    return result.deleted_count
```

### Trường hợp 2: đồng bộ laws_cache thất bại sau khi cả Mongo và Chroma đã lưu

Sau khi cả hai kho lưu thành công, hệ thống còn cập nhật một bảng cache `laws_cache` phục vụ UI quản lý văn bản. Nếu bước này thất bại, hệ thống rollback cả hai kho để ba store luôn đồng bộ:

```python
except Exception as cache_err:
    logger.error(
        f"❌ laws_cache sync failed for {parsed_doc.law_id}: {cache_err}. "
        f"Rolling back MongoDB articles + ChromaDB..."
    )
    try:
        rollback_count = await law_repo.delete_by_law_id(parsed_doc.law_id)
        await rag_client.delete_by_law_id(parsed_doc.law_id)
        logger.info(f"🔄 Rollback completed: removed {rollback_count} articles + ChromaDB chunks")
    except Exception as rb_err:
        logger.error(f"❌ Rollback after laws_cache failure ALSO failed: {rb_err}")
```

Lý do rollback cả ba được giải thích ngay trong comment của code: nếu `articles` (kiểm tra trùng) và `laws_cache` (hiển thị UI) lệch nhau, sẽ sinh lỗi 409 ảo ở lần upload sau.

### Chiều ngược lại: xóa ChromaDB khi cần

`rag_client.delete_by_law_id` gọi sang RAG Service để xóa chunk khỏi ChromaDB. Endpoint xóa trong `ingest.py` lấy tất cả id theo `law_id` rồi xóa:

```python
@router.delete("/articles/{law_id:path}")
async def delete_articles_by_law_id(law_id: str, _: InternalAuth):
    try:
        chroma_repo = get_chroma_repository()

        # Get all documents with this law_id
        all_data = chroma_repo.collection.get(
            where={"law_id": law_id},
            include=[]
        )

        if not all_data["ids"]:
            return {"success": True, "deleted_count": 0, "message": "Không có documents nào cần xoá"}

        # Delete them
        chroma_repo.collection.delete(ids=all_data["ids"])
        deleted_count = len(all_data["ids"])
        ...
```

### Lưới an toàn ở các handler exception

Ngoài các nhánh rollback theo từng trường hợp, endpoint còn có hai handler bao trùm cho hủy giữa chừng (`CancelledError`) và lỗi không lường trước (`Exception`). Cả hai đều kiểm tra: nếu code đã chạy tới sau bước MongoDB lưu (`saved_count` đã tồn tại trong scope) thì rollback cả ba kho:

```python
except Exception as e:
    # ⚠️ Catch-all: if error happens after MongoDB save, rollback
    if 'parsed_doc' in locals() and 'saved_count' in locals():
        logger.error(f"❌ Unexpected error after DB save, rolling back {parsed_doc.law_id}...")
        try:
            law_repo = LawRepository()
            await law_repo.delete_by_law_id(parsed_doc.law_id)
            await rag_client.delete_by_law_id(parsed_doc.law_id)
            mongodb = await get_mongodb()
            await mongodb.delete_law_cache(parsed_doc.law_id)
            logger.info(f"🔄 Rollback completed for {parsed_doc.law_id}")
        except Exception as rb_err:
            logger.error(f"❌ Rollback failed: {rb_err}")
```

Việc kiểm tra `'saved_count' in locals()` là cách xác định rollback có cần thiết không: nếu lỗi xảy ra trước khi MongoDB lưu thì không có gì để hoàn tác.

## 16. Hoàn tất và trả kết quả

Khi mọi bước thành công, hệ thống cập nhật task sang `completed` với đầy đủ kết quả, gửi WebSocket trạng thái hoàn tất và trả response JSON:

```python
await task_repo.update_task(
    doc_task.id,
    status="completed",
    law_id=result.law_id,
    article_count=result.article_count,
    progress=100
)
await ws_manager.send_to_user(str(current_user.id), {
    "type": "UPLOAD_STATUS", "task_id": str(doc_task.id), "status": "completed",
    "law_id": result.law_id, "article_count": result.article_count
})
```

Trong khối `finally`, bất kể thành công hay thất bại, hệ thống dọn handle task khỏi dictionary toàn cục và bust cache dashboard để số liệu thống kê được làm mới:

```python
finally:
    _active_upload_tasks.pop(doc_task.id, None)
    # Bust dashboard cache: bất kể upload success/fail, task status đã đổi
    # → success_count/failed_count trong stats cần refresh.
    invalidate_dashboard_cache()
```

File PDF tạm trên đĩa cũng được xóa trong `finally` của `DocumentProcessor` để không tích lũy rác:

```python
finally:
    # Clean up temp file
    try:
        Path(file_path).unlink(missing_ok=True)
        logger.info(f"🗑️ Cleaned up temp file: {file_path}")
    except Exception:
        pass
```

## 17. Tóm tắt luồng xử lý

Toàn bộ luồng upload và xử lý tài liệu có thể tóm tắt như sau:

```text
Admin chọn PDF
-> POST /documents/upload-v2 (chỉ admin)
-> Validate định dạng + dung lượng
-> Tạo DocumentTask (PostgreSQL, status=processing)
-> Mở WebSocket nhận tiến trình realtime
-> Tiền kiểm tra trùng (a) hash file, (b) quick precheck trang đầu bằng Gemini
   -> Trùng / không phải VB pháp luật -> fail sớm (409 / 400)
-> Pipeline đọc nội dung (song song):
     OCR tự host (PyMuPDF + PaddleOCR) -> Gemini cấu trúc hóa
     (nếu fail) -> fallback Gemini Vision
     đồng thời upload PDF gốc lên Cloudinary
-> Gắn metadata bằng regex (topics, keywords, summary)
-> Validate kết quả parse (strict)
-> Kiểm tra trùng law_id lần cuối
-> Lưu MongoDB (full articles, _id = law_id_article_id)
-> Gọi RAG Service /ingest/articles:
     chunk (≤1000 từ, overlap 150) -> encode batch bi-encoder -> lưu ChromaDB batch 100
-> Đồng bộ laws_cache + gắn file_hash
-> Cập nhật task=completed, progress=100
-> Gửi WebSocket UPLOAD_STATUS completed
-> Trả JSON kết quả

(Bất kỳ bước nào sau khi đã ghi dữ liệu lỗi -> compensating transaction:
 xóa MongoDB articles + ChromaDB chunks + laws_cache để 3 store luôn đồng bộ)
```

Thiết kế này đạt ba mục tiêu chính. Thứ nhất, dữ liệu nhất quán giữa ba kho nhờ kiểm tra trùng nhiều lớp và cơ chế bù trừ giao dịch. Thứ hai, trải nghiệm admin tốt nhờ tiến trình realtime qua WebSocket và khả năng hủy giữa chừng. Thứ ba, tiết kiệm chi phí và thời gian nhờ tiền kiểm tra trùng trước khi gọi LLM, OCR tự host trước khi dùng Gemini Vision, và sinh metadata bằng regex thay vì LLM.

## 18. Các file code chính liên quan

Các file quan trọng của luồng upload và xử lý tài liệu gồm:

- `vietnam-law-service/main-service/app/api/v1/documents.py`: định nghĩa các endpoint upload (`/upload`, `/upload-v2`), WebSocket `/ws`, danh sách task, hủy task, preview, parse text. Đây là nơi điều phối toàn bộ luồng và chứa logic compensating transaction ở tầng endpoint.
- `vietnam-law-service/main-service/app/services/document_processor.py`: pipeline xử lý PDF, chạy OCR song song với Cloudinary, fallback Gemini Vision, phát tiến trình qua callback.
- `vietnam-law-service/main-service/app/services/document_parser.py`: gọi Gemini Vision/File API để trích cấu trúc điều luật, quick precheck trang đầu, multi-key rotation, repair JSON.
- `vietnam-law-service/main-service/app/services/ocr_service.py`: OCR tự host bằng PyMuPDF (trang digital) và PaddleOCR/Tesseract (trang scan), làm sạch và đánh giá chất lượng text.
- `vietnam-law-service/main-service/app/services/cloud_storage.py`: upload/download/delete file trên Cloudinary.
- `vietnam-law-service/main-service/app/services/metadata_enricher.py`: sinh topics, keywords, summary bằng regex (không cần LLM).
- `vietnam-law-service/main-service/app/services/validators.py`: validate ParsedDocument trước khi lưu.
- `vietnam-law-service/main-service/app/services/websocket_manager.py`: quản lý kết nối WebSocket theo từng user.
- `vietnam-law-service/main-service/app/services/rag_client.py`: client gọi RAG Service, có `ingest_articles` và `delete_by_law_id`.
- `vietnam-law-service/main-service/app/services/llm_parser.py`: parser dựa trên text thuần (dùng cho endpoint `/upload`, `/upload/preview`, `/parse-text`), với chunking theo ranh giới điều và xử lý song song.
- `vietnam-law-service/main-service/app/models/document_task.py` và `repositories/document_task_repo.py`: mô hình và truy cập dữ liệu cho DocumentTask trong PostgreSQL.
- `vietnam-law-service/main-service/app/repositories/law_repository.py`: lưu/xóa/kiểm tra articles trong MongoDB.
- `vietnam-law-service/rag-service/app/api/v1/ingest.py`: nhận articles, chunk, encode, lưu ChromaDB, và endpoint xóa phục vụ rollback.
- `vietnam-law-service/rag-service/app/repositories/embedding_repository.py`: bi-encoder và cross-encoder (singleton).
- `vietnam-law-service/rag-service/app/repositories/chroma_repository.py`: kết nối và thao tác với collection ChromaDB.

## 19. Các đoạn code kỹ thuật quan trọng

Phần này tổng hợp các điểm then chốt cần nắm để giải thích khi bảo vệ hoặc phản biện. Nhiều đoạn đã trích ở trên; phần này nhấn mạnh các đoạn còn lại và ý nghĩa của chúng.

### 19.1. Hai loại message WebSocket

Hệ thống dùng hai loại message khác nhau. `UPLOAD_PROGRESS` cập nhật phần trăm và bước đang chạy trong lúc xử lý; `UPLOAD_STATUS` báo trạng thái kết thúc:

```python
await ws_manager.send_to_user(str(current_user.id), {
    "type": "UPLOAD_STATUS", "task_id": str(doc_task.id), "status": "completed",
    "law_id": result.law_id, "article_count": result.article_count
})
```

Việc tách rõ progress và status giúp client phân biệt giữa cập nhật trung gian (cập nhật thanh tiến độ) và sự kiện kết thúc (đóng trạng thái loading, hiển thị kết quả).

### 19.2. Helper fail-duplicate dùng lại ở nhiều chỗ

Để tránh lặp code khi cần đánh dấu task failed và đẩy WebSocket, endpoint định nghĩa một closure dùng chung:

```python
async def _fail_duplicate(err_msg: str):
    """Helper: mark task failed + push WS + trả 409."""
    await task_repo.update_task(doc_task.id, status="failed", error_message=err_msg)
    await ws_manager.send_to_user(str(current_user.id), {
        "type": "UPLOAD_STATUS",
        "task_id": str(doc_task.id),
        "status": "failed",
        "error": err_msg,
        "filename": doc_task.filename,
    })
```

### 19.3. Convert PDF sang ảnh cho Gemini Vision

Khi dùng Gemini Vision, PDF được convert sang ảnh JPEG base64. Tham số `max_pages` cho phép quick precheck chỉ convert vài trang đầu:

```python
def _pdf_to_images(
    self,
    pdf_path: str,
    dpi: int = 150,
    max_pages: Optional[int] = None,
) -> List[str]:
    ...
    if max_pages and max_pages > 0:
        convert_kwargs["first_page"] = 1
        convert_kwargs["last_page"] = max_pages
    images = convert_from_path(pdf_path, **convert_kwargs)

    base64_images = []
    for i, img in enumerate(images):
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        b64 = base64.standard_b64encode(buffer.read()).decode("utf-8")
        base64_images.append(b64)
        buffer.close()
```

DPI 150 và quality 85 là sự cân bằng giữa độ rõ chữ (để Gemini đọc được cả phần viết tay) và kích thước payload (để không vượt giới hạn request).

### 19.4. Repair JSON khi Gemini trả về không chuẩn

LLM thỉnh thoảng trả JSON kèm markdown hoặc lỗi cú pháp nhỏ. Parser có lớp tự sửa trước khi parse:

```python
def _repair_json(self, text: str) -> str:
    ...
    # Remove markdown code blocks
    text = re.sub(r'^```json\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()

    # Extract JSON object (find outermost braces)
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]

    # Fix trailing commas
    text = re.sub(r',(\s*[}\]])', r'\1', text)

    # Fix missing commas between array elements
    text = re.sub(r'\}(\s*)\{', r'},\1{', text)
```

Đây là một lớp phòng thủ thực dụng: thay vì để cả pipeline thất bại chỉ vì một dấu phẩy thừa, hệ thống cố sửa các lỗi phổ biến trước.

### 19.5. Tách trang digital và trang scan để OCR đúng cách

OCR service không OCR mù toàn bộ. Trang nào có lớp text thì lấy thẳng từ PyMuPDF (nhanh, chính xác), chỉ những trang scan mới chuyển sang ảnh và OCR song song bằng PaddleOCR:

```python
if page_image_map:
    with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
        futures = {
            executor.submit(self._ocr_page_paddleocr, img_path): page_num
            for page_num, img_path in page_image_map
        }
        for future in as_completed(futures):
            page_num = futures[future]
            try:
                text = future.result()
                results[page_num] = text
            except Exception as e:
                logger.warning(f"OCR failed for page {page_num + 1}: {e}")
                results[page_num] = ""
```

Cách này tiết kiệm đáng kể thời gian với các văn bản pháp luật digital thuần (đa số), chỉ tốn chi phí OCR cho phần thực sự là ảnh scan.

### 19.6. Sinh summary bằng heuristic

Summary không gọi LLM mà lấy dòng nội dung thực chất đầu tiên sau tiêu đề điều, bỏ các prefix khoản/điểm:

```python
for line in lines:
    line = line.strip()
    # Bỏ prefix khoản: "1. ", "2. ", "a) ", "- "
    content = re.sub(r"^(?:\d+\.\s*|[a-zA-Z]\)\s*|-\s*)+", "", line).strip()
    # Phải có ít nhất 10 ký tự và 5 chữ cái
    if content and len(content) >= 10 and sum(c.isalpha() for c in content) >= 5:
        if len(content) > 200:
            content = content[:200] + "..."
        return content
```

### 19.7. Trích năm từ số hiệu văn bản

Năm ban hành thường nằm ngay trong số hiệu (ví dụ `08/2026/TT-BCT`), nên hệ thống rút bằng regex thay vì dựa vào LLM:

```python
def extract_year_from_law_id(law_id: str) -> str:
    if not law_id:
        return ""
    m = re.search(r"/(\d{4})/", law_id)
    return m.group(1) if m else ""
```

### 19.8. Singleton cho các mô hình nặng

Bi-encoder và cross-encoder được nạp đúng một lần nhờ mẫu singleton, vì nạp mô hình ML tốn vài giây và tốn RAM:

```python
class EmbeddingRepository:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        logger.info(f"Loading bi-encoder: {settings.embedding_model}")
        self._bi_encoder = SentenceTransformer(settings.embedding_model)
        ...
        self._initialized = True
```

ChromaRepository cũng theo cùng mẫu này. Nhờ vậy, mỗi lần ingest không phải nạp lại mô hình hay mở lại kết nối ChromaDB.

## 20. Các câu hỏi phản biện có thể gặp về luồng upload

### Vì sao chỉ admin được upload?

Vì dữ liệu pháp luật là dữ liệu nền tảng cho mọi câu trả lời chat. Một văn bản sai, giả hoặc rác nếu được nạp sẽ ảnh hưởng đến chất lượng truy hồi của toàn hệ thống. Giới hạn quyền upload cho admin là biện pháp kiểm soát chất lượng dữ liệu đầu vào.

### Vì sao phải lưu vào cả MongoDB và ChromaDB?

Hai kho phục vụ hai mục đích khác nhau. MongoDB lưu văn bản đầy đủ, có cấu trúc, để tra cứu, hiển thị chi tiết và lọc theo metadata. ChromaDB lưu vector embedding của các chunk để tìm kiếm ngữ nghĩa trong luồng chat. Không kho nào thay được kho kia: ChromaDB không phù hợp để hiển thị nguyên văn, còn MongoDB không làm được tìm kiếm theo độ tương đồng ngữ nghĩa.

### Nếu ghi MongoDB xong mà ChromaDB lỗi thì sao?

Hệ thống chạy compensating transaction: xóa toàn bộ articles vừa ghi trong MongoDB (qua `delete_by_law_id`) và xóa cache, đưa về trạng thái như chưa từng upload. Ngược lại, nếu lỗi xảy ra sau khi cả hai đã ghi (ví dụ đồng bộ laws_cache lỗi), hệ thống xóa cả MongoDB lẫn ChromaDB. Mục tiêu là ba kho luôn đồng bộ.

### Vì sao không dùng giao dịch phân tán thật sự?

MongoDB và ChromaDB là hai hệ khác nhau, không có giao dịch phân tán chung. Triển khai two-phase commit giữa chúng rất phức tạp và bản thân ChromaDB không hỗ trợ. Mẫu compensating transaction (làm rồi bù trừ khi lỗi) là cách thực dụng và đủ tốt cho bài toán này, nơi thao tác bù trừ (xóa theo law_id) đơn giản và idempotent.

### Chunk size 1000 từ và overlap 150 từ chọn thế nào?

Đây là tham số cố định khớp với script ingest gốc (`MAX_CHUNK_WORDS = 1000`, `CHUNK_OVERLAP = 150`). Chunk 1000 từ đủ lớn để giữ trọn ngữ cảnh một đoạn điều luật nhưng không quá lớn làm loãng vector embedding. Overlap 150 từ đảm bảo nội dung ở ranh giới giữa hai chunk không bị mất ngữ cảnh khi truy vấn. Điều ngắn hơn 1000 từ giữ nguyên một chunk để không cắt vụn không cần thiết.

### Vì sao parse tách làm hai tầng OCR thay vì dùng thẳng Gemini Vision?

Dùng Gemini Vision đọc OCR trực tiếp tốn token và chậm với văn bản dài. Đa số văn bản pháp luật là PDF digital (có lớp text sẵn), nên OCR tự host bằng PyMuPDF rút text gần như tức thời và miễn phí, rồi chỉ nhờ Gemini cấu trúc hóa. Gemini Vision chỉ được dùng làm tầng dự phòng cho các file scan hoặc khi OCR tự host thất bại. Đây là tối ưu chi phí và tốc độ mà vẫn giữ khả năng xử lý file scan khó.

### Vì sao metadata sinh bằng regex chứ không bằng LLM?

Metadata (topics, keywords, summary) dùng để lọc và gợi ý, không phải nội dung pháp lý cần độ tinh tế cao. Regex cho kết quả deterministic, nhanh, miễn phí và không hallucinate. Nếu để LLM sinh metadata, sẽ tốn thêm token output và có nguy cơ sinh chủ đề/từ khóa không có thật. Với loại metadata này, sự ổn định quan trọng hơn linh hoạt.

### Nếu admin đóng tab giữa chừng thì dữ liệu có bị nửa vời không?

Không. Endpoint giám sát client bằng task `check_disconnect`. Khi phát hiện ngắt kết nối, pipeline bị hủy, task chuyển sang `cancelled`, file Cloudinary đang upload dở bị xóa, và nếu đã ghi MongoDB thì handler `CancelledError` rollback cả ba kho. Trạng thái cuối cùng luôn sạch.

### Làm sao tránh nạp trùng cùng một văn bản?

Hệ thống có ba lớp chống trùng: (1) hash SHA-256 bắt file giống hệt từng byte với chi phí gần như 0; (2) quick precheck trang đầu trích law_id và kiểm tra trùng sớm trước khi parse đầy đủ; (3) kiểm tra law_id lần cuối sau full parse, ngay trước khi ghi MongoDB. Nguyên tắc nghiệp vụ là văn bản pháp luật không được ghi đè, nên mọi trường hợp trùng đều bị từ chối với mã 409.
