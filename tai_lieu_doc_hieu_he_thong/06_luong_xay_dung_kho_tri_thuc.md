# Luồng xây dựng và cập nhật kho tri thức pháp luật (Data/ETL pipeline offline)

Tài liệu này mô tả luồng xây dựng và cập nhật kho tri thức pháp luật của hệ thống trợ lý ảo tư vấn pháp luật Việt Nam. Đây là pipeline xử lý dữ liệu chạy ngoại tuyến (offline), có nhiệm vụ biến hàng chục nghìn điều luật thô thành một cơ sở tri thức sẵn sàng cho việc truy hồi: dữ liệu được thu thập, chuẩn hóa, nạp vào MongoDB, làm giàu metadata, chia nhỏ thành chunk, sinh vector embedding, nạp vào ChromaDB, và cuối cùng được đánh giá chất lượng. Nội dung được viết để người ngoài dự án vẫn hiểu được vai trò của từng giai đoạn, lý do thiết kế và các thông số kỹ thuật thực tế lấy trực tiếp từ source code.

## 1. Vai trò của luồng xây dựng kho tri thức

Luồng chat chính (được mô tả trong tài liệu khác) chỉ hoạt động được khi đã có sẵn một kho dữ liệu pháp luật đã được xử lý: các điều luật phải nằm trong MongoDB để tra cứu nguyên văn, và các đoạn văn bản phải được embedding thành vector trong ChromaDB để tìm kiếm ngữ nghĩa. Luồng xây dựng kho tri thức chính là phần "hậu cần" tạo ra kho dữ liệu đó.

Khác với luồng chat (chạy realtime, phục vụ từng câu hỏi), luồng này chạy theo mẻ (batch), thường chỉ chạy khi cần dựng lại toàn bộ cơ sở dữ liệu hoặc bổ sung một lô văn bản mới. Mục tiêu của nó là đảm bảo ba điều:

- Mỗi điều luật được lưu một lần, có định danh duy nhất, có thể tra cứu nguyên văn.
- Mỗi đoạn văn bản dài được chia nhỏ hợp lý để embedding không bị mất ngữ cảnh.
- Mỗi chunk có vector chất lượng cao, gắn metadata đầy đủ (chủ đề, từ khóa, năm ban hành) để hỗ trợ lọc và xếp hạng khi truy hồi.

Pipeline này nằm trong một repository riêng tên là `vietnamese-law-rag`, tách biệt hoàn toàn với service production `vietnam-law-service`. Repository này mang tính chất công cụ ETL: nó chứa nhiều script thử nghiệm tích lũy qua quá trình phát triển, vì vậy phần lớn tài liệu sẽ tập trung vào chuỗi script thực sự cấu thành pipeline chính (canonical), đồng thời chỉ rõ đâu là script phụ trợ.

## 2. Mối quan hệ với service production vietnam-law-service

Đây là điểm quan trọng cần nắm trước khi đi vào chi tiết. Hệ thống có hai con đường để dữ liệu pháp luật đi vào kho tri thức, và cả hai cùng dẫn đến đúng một đích.

Con đường thứ nhất là pipeline offline trong repo `vietnamese-law-rag`. Đây là công cụ dựng dữ liệu hàng loạt: nạp một lần hàng nghìn văn bản đã thu thập sẵn từ các nguồn crawl. Nó phù hợp cho việc khởi tạo cơ sở dữ liệu ban đầu hoặc bổ sung một lô lớn.

Con đường thứ hai là luồng ingest tăng dần (incremental) bên trong service production `vietnam-law-service`. Khi quản trị viên upload từng file PDF văn bản luật mới qua giao diện admin, service production sẽ tự xử lý: tách điều, ghi vào MongoDB và ChromaDB ngay trong một transaction (có cơ chế bù trừ — rollback MongoDB nếu ChromaDB lỗi và ngược lại).

Mặc dù hai con đường được viết bằng code khác nhau, chúng phải thống nhất tuyệt đối về cấu trúc đích để luồng chat truy vấn được cả hai nguồn dữ liệu như nhau:

```text
Pipeline offline (vietnamese-law-rag)          Service production (vietnam-law-service)
   - Nạp hàng loạt từ file crawl                  - Nạp tăng dần từng PDF admin upload
                  \                              /
                   \                            /
                    v                          v
        MongoDB:  VietnamLawDB.articles  (điều luật nguyên văn + metadata)
        ChromaDB: collection vector       (chunk embedding để semantic search)
        Embedding model: bkai-foundation-models/vietnamese-bi-encoder
```

Cụ thể hơn, cả hai cùng:

- Ghi điều luật vào MongoDB database `VietnamLawDB`, collection `articles` (xác nhận trong `vietnamese-law-rag/config.py` với `DB_NAME = "VietnamLawDB"`, `COLLECTION_NAME = "articles"` và trong tài liệu kiến trúc `vietnam-law-service/CLAUDE.md` ghi rõ "Law articles as structured documents in `VietnamLawDB.articles`").
- Sinh embedding bằng cùng một mô hình bi-encoder tiếng Việt `bkai-foundation-models/vietnamese-bi-encoder`. Đây là điểm bắt buộc phải trùng: nếu hai con đường dùng model khác nhau, các vector sẽ không nằm cùng một không gian ngữ nghĩa và việc tìm kiếm sẽ sai lệch.

Có một khác biệt nhỏ về tên collection ChromaDB. Pipeline offline đặt collection là `vietnamese_law` (cấu hình `CHROMA_COLLECTION = "vietnamese_law"` trong `config.py`), trong khi service production cấu hình tên collection qua biến môi trường riêng. Về bản chất kỹ thuật, đây là cùng một loại collection lưu vector của các chunk điều luật; tài liệu này mô tả pipeline offline nên dùng tên `vietnamese_law` theo đúng code của repo `vietnamese-law-rag`.

## 3. Tổng quan các giai đoạn của pipeline chính

Sau khi khảo sát toàn bộ thư mục `vietnamese-law-rag/scripts/` và `vietnamese-law-rag/handle_data/`, có thể rút ra chuỗi giai đoạn cốt lõi của pipeline như sau:

```text
[Giai đoạn 0] Thu thập / crawl dữ liệu thô (ngoài repo + script download)
        |
        v
[Giai đoạn 1] Chuyển đổi & chuẩn hóa định dạng    -> convert_vbpl_crawl.py, filter_vld_new.py
        |
        v
[Giai đoạn 2] Làm giàu metadata                   -> enrich_metadata_regex.py (regex, mặc định)
              (topics / keywords / summary)            enrich_metadata.py (LLM Gemini, tùy chọn)
        |
        v
[Giai đoạn 3] Nạp điều luật vào MongoDB           -> ingest_to_mongo.py / ingest_new_data.py
              (VietnamLawDB.articles)
        |
        v
[Giai đoạn 4] Chunking + Embedding + nạp ChromaDB -> chunk_utils.py + embedding_to_chromadb.py
              (collection vietnamese_law)              hoặc ingest_new_data.py / smart_rebuild.py
        |
        v
[Giai đoạn 5] Đánh giá chất lượng                 -> evaluate_embeddings.py, test_retrieval.py
```

Trong các giai đoạn này, có ba script đóng vai trò trung tâm và cần đọc kỹ nhất:

- `scripts/chunk_utils.py`: logic chunking và sinh chunk_id dùng chung, là "nguồn chân lý" cho việc chia nhỏ văn bản.
- `scripts/embedding_to_chromadb.py`: pipeline full-rebuild kinh điển — đọc dữ liệu, chunk, embedding, nạp ChromaDB từ đầu.
- `scripts/ingest_new_data.py`: pipeline bổ sung dữ liệu mới mà không xóa dữ liệu cũ, dùng chung `chunk_utils.py`.

Toàn bộ tham số của pipeline được tập trung trong một file cấu hình duy nhất `vietnamese-law-rag/config.py`, để chỉ cần sửa một nơi là mọi script tự cập nhật theo.

## 4. File cấu hình tập trung config.py

Trước khi đi vào từng giai đoạn, cần hiểu file `config.py` vì nó quyết định hành vi của gần như mọi script. Các tham số quan trọng (copy nguyên văn từ `config.py`):

```python
# ChromaDB Connection
USE_DOCKER_CHROMA = True          # True = HTTP Client (Docker/Remote), False = Local Persistent
CHROMA_HOST = "localhost"         # Host của ChromaDB server
CHROMA_PORT = 4000                # Port đã map (4000:8000)
CHROMA_PATH = "./chroma_db"       # Chỉ dùng khi USE_DOCKER_CHROMA = False

# Collection
CHROMA_COLLECTION = "vietnamese_law"

# Xóa dữ liệu cũ
CLEAN_OLD_DATA = True             # True = Xóa collection cũ trước khi insert mới

# Embedding Model
EMBEDDING_MODEL = "bkai-foundation-models/vietnamese-bi-encoder"

# Chunking Strategy
MAX_CHUNK_LENGTH = 1000           # Số từ tối đa mỗi chunk
CHUNK_OVERLAP = 150               # Số từ overlap giữa các chunk
USE_HYBRID_CHUNKING = True        # True = chia articles dài, False = giữ nguyên

# MongoDB (cho embedding script)
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "VietnamLawDB"
COLLECTION_NAME = "articles"

# Retrieval Settings
TOP_K = 5                         # Số documents retrieve
MIN_SIMILARITY = 0.3              # Ngưỡng similarity tối thiểu (0-1)

# Processing
BATCH_SIZE = 100                  # Batch size cho embedding
```

Cần lưu ý một điểm dễ gây nhầm lẫn: các tài liệu hướng dẫn cũ trong repo (`README.md`, `EMBEDDING_GUIDE.md`) vẫn nhắc tới model `keepitreal/vietnamese-sbert`. Tuy nhiên cấu hình thực tế đang chạy trong `config.py` là `bkai-foundation-models/vietnamese-bi-encoder`. Đây mới là model đúng và trùng khớp với service production, nên khi giải thích hệ thống phải lấy giá trị từ `config.py`, không lấy từ tài liệu cũ.

LÝ DO THIẾT KẾ: Việc gom toàn bộ tham số vào một file giúp tránh tình trạng mỗi script một cấu hình khác nhau, dẫn đến chunk size hoặc model không nhất quán giữa các lần chạy. Đặc biệt với embedding, chỉ cần một lần lỡ dùng model khác là toàn bộ vector trong ChromaDB sẽ không còn so khớp được với vector query của luồng chat.

## 5. Giai đoạn 0 — Thu thập dữ liệu thô

Dữ liệu pháp luật được thu thập từ nhiều nguồn crawl khác nhau, mỗi nguồn có định dạng riêng. Trong repo có thể thấy dấu vết của ít nhất ba nguồn qua các file trong thư mục `raw/` và các script download:

- Nguồn `vbpl` (Cơ sở dữ liệu quốc gia về văn bản pháp luật): file thô `raw/vbpl_crawl.json`, xử lý bởi `scripts/convert_vbpl_crawl.py`.
- Nguồn `uts_vlc`: tải bởi `scripts/download_uts_vlc.py`, parse bởi `scripts/parse_uts_vlc.py`.
- Nguồn `vld`: tải bởi `scripts/download_vld.py`, lọc bởi `scripts/filter_vld_new.py`.

Kết quả tích lũy đầu tiên của toàn bộ quá trình thu thập và làm sạch là file `raw/legal_corpus_CLEANED.json` — đây là tập dữ liệu nền (corpus chính) đã được làm sạch. Các lô bổ sung về sau nằm trong các file đặt tên theo nguồn, ví dụ `raw/uts_vlc_NEW_LAWS.json`, `raw/vbpl_NEW_LAWS.json`, `raw/vld_NEW_LAWS.json`.

LÝ DO THIẾT KẾ: Việc tách rõ file corpus nền và các file lô mới giúp pipeline có thể vừa giữ dữ liệu gốc ổn định, vừa bổ sung dần dữ liệu mới mà không phải crawl lại từ đầu. Đây cũng là lý do tồn tại hai nhánh ingest khác nhau (full-rebuild và incremental) sẽ trình bày ở các giai đoạn sau.

## 6. Giai đoạn 1 — Chuyển đổi và chuẩn hóa định dạng

Dữ liệu thô từ crawl thường không sạch: tiếng Việt bị lỗi unicode, loại văn bản bị xuống dòng giữa chừng (`NGHỊ\r\nQUYẾT`), nhiều bản ghi rỗng hoặc ID sai định dạng. Script `scripts/convert_vbpl_crawl.py` chịu trách nhiệm biến file thô `vbpl_crawl.json` thành định dạng chuẩn giống `legal_corpus_CLEANED.json`.

Định dạng chuẩn mà toàn bộ pipeline thống nhất là một mảng các văn bản luật (law), mỗi law chứa một mảng các điều (article), mỗi article có các trường `article_id`, `title`, `text`, `metadata`. Đây là định dạng mà mọi giai đoạn sau (enrich, ingest mongo, chunking) đều giả định.

Các bước xử lý chính của `convert_vbpl_crawl.py` được mô tả ngay trong docstring và phần code lọc:

```python
for rec in data:
    law_id_raw = rec.get("id", "").strip()

    # Lọc ID không hợp lệ
    if not VALID_ID_RE.match(law_id_raw):
        skipped["bad_id"] += 1
        continue

    # Lọc content rỗng
    content = rec.get("content", "").strip()
    if not content:
        skipped["empty_content"] += 1
        continue

    # Lọc không có Điều
    article_str = rec.get("article", "").strip()
    article_id = extract_article_id(article_str)
    if not article_id:
        skipped["no_article_id"] += 1
        continue

    valid_records.append(rec)
```

Trong đó `VALID_ID_RE = re.compile(r"^\d+/\d{4}/")` đảm bảo `law_id` đúng dạng số hiệu văn bản (ví dụ `100/2015/QH13`), còn `ARTICLE_NUM_RE = re.compile(r"Điều\s+(\d+[a-z]?)")` dùng để trích số điều từ chuỗi như "Điều 1. Phạm vi điều chỉnh".

Script còn group các bản ghi phẳng (flat record) lại theo `law_id`, và khi gặp hai bản ghi trùng `article_id` thì giữ bản có nội dung dài hơn:

```python
# Tránh trùng article_id (giữ bản có content dài hơn)
if article_id not in group["articles"] or len(content) > len(group["articles"][article_id]["text"]):
    group["articles"][article_id] = {
        "article_id": article_id,
        "title": article_str,
        "text": content,
        "metadata": {
            "law_id": law_id,
            "article_id": article_id,
            "topics": [],
            "keywords": [],
            "summary": "",
            "year": year,
        },
        "law_id": law_id,
    }
```

LÝ DO THIẾT KẾ: Dữ liệu crawl gần như luôn bẩn. Nếu nạp thẳng vào hệ thống, các bản ghi rỗng hoặc ID sai sẽ tạo ra chunk vô nghĩa, làm nhiễu kết quả tìm kiếm và lãng phí chi phí embedding. Việc lọc sớm và chuẩn hóa về một định dạng duy nhất giúp các giai đoạn sau không phải xử lý ngoại lệ riêng cho từng nguồn. Đáng chú ý là ở bước này `metadata.topics`, `keywords`, `summary` vẫn để rỗng — chúng sẽ được điền ở giai đoạn làm giàu metadata.

Các script chuẩn hóa nguồn khác như `parse_uts_vlc.py`, `convert_uts_vlc_format.py`, `filter_vld_new.py` đóng vai trò tương tự cho các nguồn `uts_vlc` và `vld`. Chúng là script phụ trợ theo từng nguồn, nhưng tất cả đều quy về cùng một định dạng chuẩn nói trên.

## 7. Giai đoạn 2 — Làm giàu metadata (topics, keywords, summary)

Sau khi có dữ liệu định dạng chuẩn nhưng metadata còn rỗng, pipeline thực hiện bước làm giàu metadata để mỗi điều luật có thêm danh sách chủ đề (topics), từ khóa pháp lý (keywords) và tóm tắt ngắn (summary). Các trường này về sau được đưa vào metadata của chunk trong ChromaDB và được luồng chat dùng để lọc/xếp hạng.

Repo cung cấp hai cách làm giàu metadata, phục vụ hai tình huống khác nhau.

### 7.1. Cách 1 — Làm giàu bằng regex (mặc định, nhanh, miễn phí)

Script `scripts/enrich_metadata_regex.py` gắn metadata hoàn toàn bằng biểu thức chính quy, không cần gọi LLM. Nó định nghĩa sẵn một bảng ánh xạ từ mẫu regex sang tên chủ đề, ví dụ:

```python
TOPIC_PATTERNS = [
    # Hình sự / Tố tụng
    (r"hình sự|tội phạm|phạm tội", "Hình sự"),
    ...
    # Giao thông
    (r"giao thông|đường bộ|đường sắt|đường thủy|đường hàng không|phương tiện", "Giao thông vận tải"),
    ...
]

# Compile patterns
TOPIC_COMPILED = [(re.compile(p, re.IGNORECASE), t) for p, t in TOPIC_PATTERNS]
```

Việc trích topics cho mỗi article được giới hạn số lượng để tránh gắn quá nhiều chủ đề rời rạc:

```python
def extract_topics(text: str, max_topics: int = 4) -> list:
    """Trích xuất topics từ text."""
    found = []
    seen = set()
    for pattern, topic in TOPIC_COMPILED:
        if pattern.search(text) and topic not in seen:
            found.append(topic)
            seen.add(topic)
            if len(found) >= max_topics:
                break
    return found if found else ["Quy định pháp luật"]
```

Tóm tắt (summary) được tạo bằng cách bỏ phần "Điều X. Tên điều" ở đầu rồi lấy dòng nội dung thực sự đầu tiên, cắt tối đa 200 ký tự:

```python
def extract_summary(article: dict) -> str:
    ...
    # Bỏ phần "Điều X. Tên điều" ở đầu text
    cleaned = re.sub(r"^Điều\s+\d+[a-z]?\.\s*[^\n]*\n?", "", text).strip()
    ...
    for line in lines:
        line = line.strip()
        # Bỏ prefix khoản: "1. ", "2. ", "a) ", "- "
        content = re.sub(r"^(?:\d+\.\s*|[a-zA-Z]\)\s*|-\s*)+", "", line).strip()
        # Phải có ít nhất 10 ký tự chữ cái
        if content and len(content) >= 10 and sum(c.isalpha() for c in content) >= 5:
            if len(content) > 200:
                content = content[:200] + "..."
            return content
    ...
```

Script còn đánh giá `risk_level` (mức độ rủi ro) của văn bản dựa trên loại văn bản và sự xuất hiện của các từ khóa hình phạt:

```python
def assess_risk_level(law_type: str, full_text: str) -> str:
    """Đánh giá mức độ rủi ro."""
    if HIGH_RISK_KEYWORDS.search(full_text):
        return "Cao"
    if law_type in ("LUẬT", "NGHỊ ĐỊNH") or MEDIUM_RISK_KEYWORDS.search(full_text):
        return "Trung bình"
    return "Thấp"
```

Cách dùng: `python scripts/enrich_metadata_regex.py raw/<file>.json`, kết quả mặc định ghi ra `<file>_enriched.json`.

LÝ DO THIẾT KẾ: Với hàng chục nghìn điều luật, gọi LLM cho từng điều sẽ rất chậm và tốn chi phí (chưa kể rate limit). Regex chạy gần như tức thời (script in cả tốc độ "laws/s"), không cần khóa API, và đủ tốt cho mục đích gắn nhãn thô để phục vụ lọc. Đó là lý do regex được chọn làm cách mặc định.

### 7.2. Cách 2 — Làm giàu bằng LLM Gemini (tùy chọn, chất lượng cao hơn)

Khi cần metadata chính xác và "hiểu nghĩa" hơn, repo có `scripts/enrich_metadata.py` gọi Google Gemini để sinh topics/keywords/summary. Script này tái sử dụng cơ chế từ `handle_data/generate_article_tags.py`: rate limiter theo thuật toán token bucket, xoay vòng nhiều API key, đa luồng và resume-safe (lưu từng văn bản ra một file riêng trong thư mục tạm để chạy lại không mất tiến độ).

Model dùng cho việc này lấy từ `config.py` (`GENERATIVE_MODEL = "gemini-2.5-flash-lite"`), prompt ép trả về JSON:

```python
prompt += f"""QUAN TRỌNG: Trả về DUY NHẤT 1 JSON object (KHÔNG phải array).
Các key phải là: {ids}
Format:
{{
  "{article_batch[0]["article_id"]}": {{
    "topics": ["chủ đề 1", "chủ đề 2", "chủ đề 3"],
    "keywords": ["liệt kê tất cả từ khóa pháp lý quan trọng trong điều luật"],
    "summary": "tóm tắt ngắn"
  }}
}}"""
```

Cơ chế chống quá tải API là token bucket: mỗi key được cấp một số "token" theo phút và theo ngày, mỗi request tiêu một token, hết token thì chờ:

```python
class RateLimiter:
    def acquire(self):
        while True:
            with self.lock:
                now = datetime.now()
                if (now - self.minute_last_update).total_seconds() >= 60:
                    self.minute_tokens = self.rpm
                    self.minute_last_update = now
                while self.day_requests and (now - self.day_requests[0]) > timedelta(days=1):
                    self.day_requests.popleft()
                if self.minute_tokens > 0 and len(self.day_requests) < self.rpd:
                    self.minute_tokens -= 1
                    self.day_requests.append(now)
                    return
            time.sleep(1)
```

Giá trị giới hạn được đặt thận trọng dưới hạn mức free của Gemini: `REQUESTS_PER_MINUTE = 12` (thay vì 15) và `REQUESTS_PER_DAY = 1400` (thay vì 1500), với `MAX_WORKERS = 2` luồng song song.

LÝ DO THIẾT KẾ: LLM hiểu ngữ nghĩa tốt hơn regex (regex chỉ bắt được từ khóa bề mặt), nhưng đổi lại bị giới hạn rate và tốn chi phí. Vì vậy LLM được dùng như một tùy chọn nâng cấp cho các lô dữ liệu mới quan trọng, còn corpus nền lớn dùng regex. Toàn bộ cơ chế resume-safe và rate limit là để có thể chạy enrich qua nhiều giờ mà không sợ mất tiến độ khi gặp lỗi mạng hay hết quota.

Lưu ý: `handle_data/generate_article_tags.py` là phiên bản tiền nhiệm dùng SDK cũ `google.generativeai` và model `gemini-2.5-flash`; `scripts/enrich_metadata.py` là phiên bản kế thừa dùng SDK mới `google.genai`. Cả hai cùng triết lý, nên xem `enrich_metadata.py` là bản chính.

## 8. Giai đoạn 3 — Nạp điều luật vào MongoDB

Sau khi đã có file `*_enriched.json`, pipeline nạp từng điều luật vào MongoDB. MongoDB đóng vai trò là kho lưu trữ điều luật nguyên văn — luồng chat sẽ dùng nó để lấy nội dung điều khoản đầy đủ sau khi tìm được chunk phù hợp.

Script kinh điển cho việc nạp toàn bộ là `scripts/ingest_to_mongo.py` (và bản tương đương `handle_data/ingest_mongo_raw.py`). Logic cốt lõi:

```python
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
col = db[COLLECTION_NAME]

print("🧹 Xóa DB cũ...")
col.delete_many({})
...
for law in tqdm(data, desc="Processing"):
    law_id = law.get('law_id', 'Unknown')
    for art in law.get('articles', []):
        doc_id = f"{law_id}_{art['article_id']}"
        record = {
            "_id": doc_id,
            "law_id": law_id,
            "article_id": art['article_id'],
            "title": art['title'],
            "text": art['text'],
            "metadata": art.get('metadata', {}),
            "full_content_search": f"{art['title']} \n {art['text']}"
        }
        docs.append(record)
```

Có ba điểm kỹ thuật cần chú ý:

- Định danh document MongoDB là `_id = f"{law_id}_{art['article_id']}"`. Việc dùng cặp (số hiệu văn bản, số điều) làm khóa chính giúp mỗi điều luật là duy nhất và idempotent: nạp lại cùng dữ liệu không tạo ra bản ghi trùng.
- Trường `full_content_search` ghép title và text lại để hỗ trợ tìm kiếm văn bản cơ bản (full-text) trong MongoDB nếu cần, độc lập với tìm kiếm vector.
- `col.delete_many({})` xóa sạch collection trước khi nạp — đây là hành vi full-rebuild.

Việc insert được chia mẻ 1000 bản ghi để nhẹ bộ nhớ:

```python
# Insert batch 1000
for i in range(0, len(docs), 1000):
    col.insert_many(docs[i:i + 1000])
```

LÝ DO THIẾT KẾ: MongoDB lưu điều luật ở dạng có cấu trúc (mỗi điều một document) thay vì lưu cả văn bản như một khối. Điều này phù hợp với cách luồng chat tham chiếu nguồn: nó cần trả về chính xác "Điều X của văn bản Y", nên việc đánh khóa theo cặp (law_id, article_id) là thiết kế tự nhiên. Việc xóa sạch rồi nạp lại chỉ hợp lý cho lần dựng đầu hoặc dựng lại toàn bộ; với dữ liệu bổ sung, pipeline dùng một script khác (giai đoạn sau) để không xóa dữ liệu cũ.

## 9. Giai đoạn 4 — Chunking, sinh embedding và nạp ChromaDB

Đây là giai đoạn trung tâm và quan trọng nhất. Văn bản được chia nhỏ thành chunk, mỗi chunk được mã hóa thành vector bằng model bi-encoder, rồi nạp vào ChromaDB cùng metadata.

### 9.1. Logic chunking dùng chung — chunk_utils.py

Toàn bộ logic chia nhỏ được tập trung trong `scripts/chunk_utils.py` để mọi script chunking dùng chung một cách thống nhất. Chiến lược là "hybrid chunking": điều luật ngắn giữ nguyên một chunk, điều luật dài mới chia nhỏ với overlap.

```python
def split_text_with_overlap(text, max_words=1000, overlap=150):
    """Split text into chunks of max_words with overlap."""
    words = text.split()
    if len(words) <= max_words:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        # Try to break at sentence boundaries if possible
        if end < len(words):
            for i in range(len(chunk_text) - 1, max(0, len(chunk_text) - 100), -1):
                if chunk_text[i] in ".!?;":
                    chunk_text = chunk_text[:i + 1]
                    break
        chunks.append(chunk_text.strip())
        start = end - overlap if end < len(words) else end
    return chunks
```

Các thông số thực tế: tối đa **1000 từ/chunk** (`MAX_CHUNK_LENGTH`), **overlap 150 từ** (`CHUNK_OVERLAP`), và chỉ chia khi `USE_HYBRID_CHUNKING = True`. Hàm còn cố gắng cắt tại dấu câu (`.!?;`) gần cuối chunk để không cắt giữa câu.

Hàm `make_chunks` tạo ra danh sách tuple `(chunk_id, content, metadata)` cho mỗi article:

```python
def make_chunks(article, art_idx=None):
    ...
    base_metadata = {
        "law_id": law_id,
        "article_id": str(article_id),
        "title": title,
        "year": meta.get("year", ""),
        "topics": json.dumps(meta.get("topics", []), ensure_ascii=False),
        "keywords": json.dumps(meta.get("keywords", []), ensure_ascii=False),
        "summary": meta.get("summary", ""),
    }

    # Pre-calculate base ID prefix
    if art_idx is not None:
        id_prefix = f"{law_id}_art{art_idx}_{article_id}"
    else:
        # Fallback for backward compatibility (may cause collisions)
        id_prefix = f"{law_id}_{article_id}"

    word_count = len(text.split())
    results = []

    if USE_HYBRID_CHUNKING and word_count > MAX_CHUNK_LENGTH:
        text_chunks = split_text_with_overlap(text, MAX_CHUNK_LENGTH, CHUNK_OVERLAP)
        for idx, chunk_text in enumerate(text_chunks):
            chunk_id = f"{id_prefix}_chunk{idx}"
            content = f"{title}\n\n{chunk_text}"
            cm = {**base_metadata, "chunk_index": idx, "total_chunks": len(text_chunks)}
            results.append((chunk_id, content, cm))
    else:
        chunk_id = f"{id_prefix}_chunk0"
        content = f"{title}\n\n{text}"
        cm = {**base_metadata, "chunk_index": 0, "total_chunks": 1}
        results.append((chunk_id, content, cm))

    return results
```

Có ba chi tiết then chốt ở đây:

- **Cách sinh chunk_id**: `f"{law_id}_art{art_idx}_{article_id}_chunk{idx}"`. Tham số `art_idx` là vị trí (thứ tự) của điều trong văn bản. Docstring nói rõ tham số này "CRITICAL to provide... to ensure unique chunk_ids across sub-documents" — bởi vì một số văn bản có nhiều điều cùng `article_id` (ví dụ các điều bổ sung "10a"), nếu không có `art_idx` thì chunk_id sẽ bị trùng và ChromaDB sẽ ghi đè mất chunk. Nhánh fallback (không có `art_idx`) được giữ lại để tương thích ngược nhưng được cảnh báo là có thể gây va chạm ID.
- **Nội dung chunk**: luôn được ghép theo dạng `f"{title}\n\n{chunk_text}"`, tức là tiêu đề điều luôn đứng đầu mỗi chunk. Điều này giúp model embedding có thêm ngữ cảnh về điều đang nói đến, kể cả ở các chunk thứ hai trở đi của một điều dài.
- **Metadata**: `topics` và `keywords` được lưu dưới dạng chuỗi JSON (`json.dumps`) chứ không phải list, vì ChromaDB chỉ chấp nhận giá trị metadata là kiểu vô hướng (string/number/bool), không nhận list.

LÝ DO THIẾT KẾ chiến lược hybrid: nếu chia nhỏ mọi điều luật một cách máy móc thì các điều ngắn (đa số) bị cắt vụn không cần thiết, làm mất tính toàn vẹn của một điều. Ngược lại nếu giữ nguyên cả điều thì các điều rất dài sẽ vượt giới hạn ngữ cảnh của model embedding, khiến phần cuối điều không được mã hóa tốt. Hybrid dung hòa: giữ nguyên điều ngắn (đảm bảo trọn vẹn), chỉ chia điều dài và cho overlap 150 từ để không mất ngữ cảnh ở ranh giới giữa hai chunk.

### 9.2. Pipeline full-rebuild — embedding_to_chromadb.py

Script `scripts/embedding_to_chromadb.py` là pipeline kinh điển dựng ChromaDB từ đầu. Đáng chú ý là script này đọc dữ liệu trực tiếp từ file JSON `raw/legal_corpus_CLEANED.json` (không qua MongoDB), tự chunk và embedding rồi nạp.

Khởi tạo model và kết nối ChromaDB (Docker hoặc local) theo `config.py`:

```python
print(f"🤖 Đang tải model: {EMBEDDING_MODEL}")
...
model = SentenceTransformer(EMBEDDING_MODEL)
print(f"✅ Model đã sẵn sàng! Dimension: {model.get_sentence_embedding_dimension()}\n")
...
if USE_DOCKER_CHROMA:
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    chroma_client.heartbeat()
else:
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
```

Nếu `CLEAN_OLD_DATA = True`, script xóa collection cũ trước khi tạo lại — đây là điểm khiến nó là pipeline "rebuild toàn bộ":

```python
if CHROMA_COLLECTION in collection_names:
    print(f"🧹 Đang xóa collection cũ: {CHROMA_COLLECTION}")
    chroma_client.delete_collection(CHROMA_COLLECTION)
...
collection = chroma_client.create_collection(
    name=CHROMA_COLLECTION,
    metadata={"description": "Vietnamese Legal Documents RAG"}
)
```

Vòng lặp chính chunk → embedding → gom mẻ → nạp:

```python
batch_size = 100
...
for article in tqdm(all_articles, desc="Processing", total=total_articles):
    chunks = chunk_article(article, use_hybrid=USE_HYBRID_CHUNKING,
                           max_words=MAX_CHUNK_LENGTH, overlap=CHUNK_OVERLAP)
    for content, metadata in chunks:
        chunk_id = f"{article['law_id']}_{article['article_id']}_chunk{metadata['chunk_index']}"
        embedding = model.encode(content, convert_to_numpy=True).tolist()
        all_ids.append(chunk_id)
        all_embeddings.append(embedding)
        all_documents.append(content)
        all_metadatas.append(metadata)
        total_chunks += 1
    ...
    if len(all_ids) >= batch_size:
        collection.add(ids=all_ids, embeddings=all_embeddings,
                       documents=all_documents, metadatas=all_metadatas)
        all_ids = []; all_embeddings = []; all_documents = []; all_metadatas = []
```

Lưu ý kỹ thuật: bản thân `embedding_to_chromadb.py` có hàm `chunk_article` riêng (logic tương đương `chunk_utils.py`), và sinh chunk_id theo dạng `f"{law_id}_{article_id}_chunk{idx}"` — tức là **không có `art_idx`**. Đây chính là nhánh có nguy cơ va chạm ID mà `chunk_utils.py` cảnh báo, và là lý do các script ingest đời sau (`ingest_new_data.py`, `smart_rebuild.py`) đã chuyển sang dùng `make_chunks` với `art_idx`.

LÝ DO THIẾT KẾ batching: mỗi lần gọi `collection.add` đều có chi phí cố định (network nếu chạy ChromaDB Docker, ghi đĩa nếu local). Gom 100 chunk rồi nạp một lần giúp giảm số lần gọi và tăng tốc đáng kể so với nạp từng chunk một.

### 9.3. Pipeline bổ sung dữ liệu mới — ingest_new_data.py

Đây là script ingest được dùng cho luồng cập nhật (không phải dựng lại từ đầu). Nó nạp đồng thời vào cả MongoDB và ChromaDB, **không xóa dữ liệu cũ**, và bỏ qua những bản ghi đã tồn tại.

Phía MongoDB, nó tải sẵn toàn bộ `_id` đang có rồi chỉ insert những điều chưa tồn tại:

```python
existing_ids = set()
for doc in col.find({}, {"_id": 1}):
    existing_ids.add(doc["_id"])
...
for art in all_articles:
    doc_id = f"{law_id}_{article_id}"
    if doc_id in existing_ids:
        skipped += 1
        continue
    ...
    new_docs.append(record)
```

Phía ChromaDB, nó dùng `make_chunks` (có `art_idx`) và encode theo mẻ lớn để nhanh hơn:

```python
for art in tqdm(all_articles, desc="  Chunking"):
    art_idx = art.pop("_art_idx", None)
    chunks = make_chunks(art, art_idx=art_idx)
    for chunk_id, content, metadata in chunks:
        new_chunks.append((chunk_id, content, metadata))
...
batch_size = 256  # Batch lớn hơn cho encoding nhanh hơn
chroma_batch = 500  # ChromaDB insert batch
...
for i in tqdm(range(0, len(all_docs), batch_size), desc="  Encoding"):
    batch_docs = all_docs[i:i + batch_size]
    emb = model.encode(batch_docs, convert_to_numpy=True, batch_size=batch_size, show_progress_bar=False)
    all_embeddings.extend(emb.tolist())
```

Khi nạp vào ChromaDB, nếu một mẻ lỗi thì có fallback nạp từng cái một để không mất toàn bộ mẻ:

```python
try:
    collection.add(ids=all_ids[i:end], embeddings=all_embeddings[i:end],
                   documents=all_docs[i:end], metadatas=all_metas[i:end])
    inserted += end - i
except Exception as e:
    print(f"\n  Error batch {i}: {e}")
    # Fallback: từng cái một
    for j in range(i, end):
        try:
            collection.add(ids=[all_ids[j]], embeddings=[all_embeddings[j]],
                           documents=[all_docs[j]], metadatas=[all_metas[j]])
            inserted += 1
        except Exception:
            pass
```

Script này cũng có các tham số chạy linh hoạt: `--dry-run` (chỉ kiểm tra), `--mongo-only`, `--chroma-only`, và `--files` để chỉ định file đầu vào. Mặc định nó đọc các file lô mới đã enrich (`uts_vlc_NEW_LAWS_enriched.json`, `vbpl_NEW_LAWS_enriched.json`).

LÝ DO THIẾT KẾ: Khác với full-rebuild, bổ sung dữ liệu mới cần idempotent và không phá hủy dữ liệu cũ. Việc tải trước tập `_id` rồi so khớp giúp tránh trùng lặp mà không phải truy vấn MongoDB cho từng điều. Batch encode lớn (256) tận dụng khả năng xử lý vector hóa hàng loạt của sentence-transformers, nhanh hơn nhiều so với encode từng chunk như trong `embedding_to_chromadb.py`.

### 9.4. Tối ưu dựng lại — smart_rebuild.py

`scripts/smart_rebuild.py` là một biến thể thông minh của full-rebuild: nó dựng lại toàn bộ ChromaDB với chunk_id mới (có `art_idx`) nhưng **tái sử dụng embedding cũ** để khỏi phải encode lại từ đầu. Ý tưởng là embedding chỉ phụ thuộc vào nội dung chunk, nên nếu nội dung không đổi thì vector cũng không đổi.

Cơ chế: nó băm nội dung mỗi chunk bằng MD5 để làm khóa tra cứu embedding cũ.

```python
def get_content_hash(text):
    """Tạo hash MD5 cho nội dung text để match embedding."""
    if not isinstance(text, str):
        text = str(text)
    return hashlib.md5(text.encode('utf-8')).hexdigest()
```

Sau đó trích toàn bộ embedding hiện có ra một dict `hash_to_embedding`, rồi khi dựng chunk mới, chunk nào có hash trùng thì dùng lại vector cũ, chunk nào mới thì mới encode:

```python
for i, doc in enumerate(all_docs):
    h = get_content_hash(doc)
    if h in hash_to_embedding:
        final_embeddings[i] = hash_to_embedding[h]
        reuse_count += 1
    else:
        docs_to_encode.append(doc)
        indices_to_encode.append(i)
```

Script cũng kiểm tra tính duy nhất của toàn bộ chunk_id sau khi dựng, đúng với mục tiêu sửa lỗi va chạm ID:

```python
unique_ids = set(all_ids)
if len(unique_ids) < len(all_ids):
    print(f"  [WARNING] Found {len(all_ids) - len(unique_ids):,} duplicate IDs even with art_idx fix!")
    ...
else:
    print(f"  ✓ Chunk IDs are 100% unique.")
```

LÝ DO THIẾT KẾ: Encode embedding cho toàn bộ corpus là phần tốn thời gian nhất (docstring nói có thể mất tới 15 tiếng). Khi chỉ cần đổi cách đánh chunk_id (để sửa lỗi trùng ID) chứ không đổi nội dung, việc encode lại từ đầu là lãng phí. `smart_rebuild.py` giải quyết bằng cách dùng MD5 nội dung làm cầu nối, giảm thời gian xuống còn 1-2 tiếng. Đây là một tối ưu vận hành rất thực dụng, đồng thời cho thấy lịch sử của repo: chuỗi script ingest đã tiến hóa để khắc phục vấn đề trùng chunk_id của phiên bản đầu.

## 10. Giai đoạn 5 — Đánh giá chất lượng (evaluation)

Sau khi dựng xong, pipeline có bước đánh giá để kiểm tra dữ liệu có "lành mạnh" không trước khi đưa vào sử dụng. Script chính là `scripts/evaluate_embeddings.py`, cung cấp nhiều chế độ qua tham số dòng lệnh (`stats`, `retrieval`, `chunks`, `duplicates`, `export`, `full`).

Chế độ thống kê đọc toàn bộ metadata từ ChromaDB và tính các con số tổng quan:

```python
results = self.collection.get(include=['metadatas'])
metadatas = results['metadatas']
...
for meta in metadatas:
    law_ids.add(meta['law_id'])
    years[meta['year']] += 1
    article_key = f"{meta['law_id']}_{meta['article_id']}"
    chunks_per_article[article_key] = max(
        chunks_per_article[article_key],
        meta['total_chunks']
    )
...
print(f"\n📦 Tổng số chunks: {total_chunks:,}")
print(f"📚 Tổng số luật: {len(law_ids)}")
print(f"📄 Tổng số articles: {len(chunks_per_article)}")
```

Nó cũng thống kê tỷ lệ điều được chia nhỏ và phân bố theo năm — những con số giúp phát hiện bất thường (ví dụ nếu gần như mọi điều đều bị chia nhỏ thì có thể `MAX_CHUNK_LENGTH` đang quá nhỏ).

Ngoài ra repo còn có các script kiểm thử nhẹ hơn như `scripts/test_retrieval.py` và `scripts/test_query.py` để thử truy vấn thực tế và xem top kết quả, đối chiếu trực quan xem retrieval có trả về đúng điều luật mong đợi không.

LÝ DO THIẾT KẾ: Pipeline xử lý dữ liệu rất dễ "hỏng âm thầm" — ví dụ một thay đổi nhỏ ở bước chunking có thể làm trùng chunk_id và mất dữ liệu mà không báo lỗi. Bước evaluation đóng vai trò kiểm tra sức khỏe cuối cùng: đếm số chunk, số luật, số article, tỷ lệ chia nhỏ, trùng lặp; đồng thời chạy thử vài truy vấn mẫu để xác nhận chất lượng truy hồi trước khi tin tưởng kho dữ liệu.

## 11. Các script phụ trợ và thử nghiệm (không thuộc pipeline chính)

Repo `vietnamese-law-rag` tích lũy nhiều script qua quá trình phát triển. Để tránh hiểu lầm, dưới đây là những file KHÔNG nằm trong chuỗi pipeline canonical mà chỉ là công cụ phụ trợ hoặc bản thử nghiệm:

- `scripts/rag_system.py`, `scripts/multi_round_rag.py`, `scripts/multi_round_rag_langsmith.py`, `scripts/multi_round_update_filtering_topic_rag.py`, `scripts/superlinked_rag.py`: các bản thử nghiệm pipeline RAG/truy vấn chạy thẳng trên repo này. Đây là nơi thử nghiệm thuật toán truy hồi trước khi triển khai chính thức trong `vietnam-law-service`. Chúng không tham gia vào việc dựng dữ liệu.
- `scripts/check_dupes.py`, `scripts/check_duplicates.py`, `scripts/check_skipped.py`, `scripts/verify_enrichment.py`, `scripts/analyze_uts_vlc.py`: công cụ kiểm tra/chẩn đoán dữ liệu.
- `scripts/rebuild_chromadb.py`, `scripts/reingest_new_data.py`, `scripts/ingest_uts_vlc.py`, `scripts/ingest_vld.py`, `scripts/fix_uts_dupes.py`: các biến thể ingest theo từng nguồn hoặc theo từng đợt sửa lỗi cụ thể.
- `handle_data/handle_vector/` (gồm `clean_data.py`, `ingest_docker_final.py`, `test_chunking_logic.py`, `repair_data_with_gemini.py`...): thư mục chứa các phiên bản đời đầu của bước làm sạch, chunking và ingest. Đây là tiền thân của các script trong `scripts/`.
- Thư mục `scripts/ocr/`: liên quan tới việc trích xuất văn bản từ ảnh/PDF (nguồn dữ liệu cần OCR), thuộc khâu thu thập.

Khi giải thích hệ thống, nên trình bày chuỗi canonical (mục 3) và xem các file trên là bối cảnh lịch sử/thử nghiệm.

## 12. Tóm tắt luồng xử lý

Toàn bộ luồng xây dựng và cập nhật kho tri thức có thể tóm tắt như sau:

```text
Crawl nhiều nguồn (vbpl, uts_vlc, vld) -> file JSON thô trong raw/
-> Chuẩn hóa định dạng (convert_vbpl_crawl.py, parse/filter theo nguồn)
   -> mảng law -> article {article_id, title, text, metadata}
-> Làm giàu metadata
   -> enrich_metadata_regex.py (mặc định, nhanh)  HOẶC  enrich_metadata.py (LLM Gemini)
   -> điền topics / keywords / summary / risk_level -> *_enriched.json
-> Nạp MongoDB (VietnamLawDB.articles)
   -> ingest_to_mongo.py (full-rebuild, xóa cũ)  HOẶC  ingest_new_data.py (bổ sung, không xóa)
   -> _id = law_id + "_" + article_id
-> Chunking (chunk_utils.make_chunks): hybrid 1000 từ / overlap 150 từ
   -> chunk_id = law_id_art{idx}_{article_id}_chunk{n}
-> Embedding bằng bkai-foundation-models/vietnamese-bi-encoder
-> Nạp ChromaDB collection vietnamese_law (batch)
   -> embedding_to_chromadb.py / ingest_new_data.py / smart_rebuild.py
-> Đánh giá chất lượng (evaluate_embeddings.py, test_retrieval.py)
-> Kho tri thức sẵn sàng cho luồng chat truy vấn
```

Thiết kế này đạt được các mục tiêu: dữ liệu được làm sạch và chuẩn hóa trước khi vào hệ thống; metadata được gắn để hỗ trợ lọc và xếp hạng; chunking hybrid cân bằng giữa toàn vẹn điều luật và giới hạn ngữ cảnh model; embedding nhất quán với service production; và mọi thứ được kiểm tra lại trước khi sử dụng.

## 13. Các file code chính liên quan

Các file quan trọng của luồng xây dựng kho tri thức gồm:

- `vietnamese-law-rag/config.py`: cấu hình tập trung — model embedding, chunk size, overlap, kết nối Mongo/Chroma, tên collection.
- `vietnamese-law-rag/scripts/convert_vbpl_crawl.py`: chuẩn hóa dữ liệu crawl vbpl về định dạng chuẩn.
- `vietnamese-law-rag/scripts/enrich_metadata_regex.py`: làm giàu metadata bằng regex (cách mặc định).
- `vietnamese-law-rag/scripts/enrich_metadata.py`: làm giàu metadata bằng LLM Gemini (tùy chọn nâng cấp).
- `vietnamese-law-rag/handle_data/generate_article_tags.py`: phiên bản tiền nhiệm của enrich bằng Gemini.
- `vietnamese-law-rag/scripts/ingest_to_mongo.py` và `vietnamese-law-rag/handle_data/ingest_mongo_raw.py`: nạp điều luật vào MongoDB (full-rebuild).
- `vietnamese-law-rag/scripts/chunk_utils.py`: logic chunking và sinh chunk_id dùng chung.
- `vietnamese-law-rag/scripts/embedding_to_chromadb.py`: pipeline full-rebuild ChromaDB từ file JSON.
- `vietnamese-law-rag/scripts/ingest_new_data.py`: pipeline bổ sung dữ liệu mới vào cả MongoDB và ChromaDB.
- `vietnamese-law-rag/scripts/smart_rebuild.py`: dựng lại ChromaDB có tái sử dụng embedding cũ.
- `vietnamese-law-rag/scripts/evaluate_embeddings.py`: đánh giá chất lượng embedding và chunking.
- `vietnam-law-service/CLAUDE.md`: tài liệu kiến trúc service production, dùng để đối chiếu tên DB/collection/model.

## 14. Các câu hỏi phản biện có thể gặp

### Vì sao cần một repo ETL riêng tách khỏi service production?

Vì hai bài toán khác nhau. Service production cần nạp tăng dần, có transaction, có rollback, chịu tải realtime. Pipeline offline cần nạp hàng loạt hàng chục nghìn điều luật một lần, ưu tiên tốc độ batch và khả năng chạy lại khi lỗi. Tách riêng giúp mỗi bên tối ưu cho mục tiêu của mình mà không làm phức tạp bên kia. Quan trọng là cả hai cùng ghi vào `VietnamLawDB.articles` và cùng dùng model `bkai-foundation-models/vietnamese-bi-encoder`, nên dữ liệu từ hai con đường hoàn toàn tương thích khi luồng chat truy vấn.

### Vì sao chọn chunking hybrid 1000 từ với overlap 150?

Đa số điều luật ngắn hơn 1000 từ nên được giữ nguyên một chunk, đảm bảo trọn vẹn ngữ nghĩa của điều. Chỉ những điều rất dài mới chia nhỏ để không vượt giới hạn ngữ cảnh của model embedding. Overlap 150 từ giữ phần giao giữa hai chunk liên tiếp, tránh trường hợp một quy định bị cắt đôi giữa ranh giới chunk làm mất ngữ cảnh. Hàm chia còn cố gắng cắt tại dấu câu để không cắt giữa câu.

### Cách sinh chunk_id đảm bảo duy nhất như thế nào?

`chunk_utils.make_chunks` tạo chunk_id dạng `law_id_art{art_idx}_{article_id}_chunk{n}`, trong đó `art_idx` là thứ tự của điều trong văn bản. Đây là điểm sửa lỗi quan trọng: một số văn bản có nhiều điều cùng số (ví dụ điều bổ sung), nếu chỉ dùng `law_id + article_id` thì ID sẽ trùng và ChromaDB ghi đè mất dữ liệu. `smart_rebuild.py` còn kiểm tra lại tính duy nhất của toàn bộ ID sau khi dựng. Lưu ý bản cũ `embedding_to_chromadb.py` vẫn dùng ID không có `art_idx`, đó là lý do nó được thay thế bởi các script ingest đời sau.

### Làm giàu metadata bằng regex hay LLM — chọn cái nào?

Mặc định dùng regex (`enrich_metadata_regex.py`) vì nhanh, miễn phí, đủ tốt cho mục đích lọc thô và xử lý được toàn bộ corpus lớn. LLM (`enrich_metadata.py` với Gemini) là tùy chọn nâng cấp cho chất lượng cao hơn, nhưng bị giới hạn rate (token bucket, 12 request/phút/key) và tốn chi phí, nên thường chỉ dùng cho các lô dữ liệu mới quan trọng. Cả hai cùng sinh ra ba trường topics/keywords/summary với cùng cấu trúc.

### Vì sao topics và keywords được lưu dưới dạng chuỗi JSON trong metadata chunk?

Vì ChromaDB chỉ chấp nhận giá trị metadata là kiểu vô hướng (string, number, bool), không nhận list. Do đó `make_chunks` dùng `json.dumps(..., ensure_ascii=False)` để serialize list topics/keywords thành chuỗi. Khi truy hồi, phía đọc sẽ parse ngược lại từ chuỗi JSON.

### Nếu chạy lại pipeline thì dữ liệu cũ có bị trùng không?

Tùy nhánh. Nhánh full-rebuild (`ingest_to_mongo.py`, `embedding_to_chromadb.py` với `CLEAN_OLD_DATA = True`) xóa sạch rồi nạp lại nên không trùng. Nhánh bổ sung (`ingest_new_data.py`) không xóa cũ, nhưng nó tải trước tập `_id` đang có trong MongoDB và bỏ qua những điều đã tồn tại, đồng thời chunk_id mang tính xác định (cùng nội dung cho cùng ID) nên nạp lại cũng idempotent ở mức ChromaDB.

### Vì sao smart_rebuild tái sử dụng embedding lại an toàn?

Vì embedding chỉ phụ thuộc vào nội dung chunk và model. `smart_rebuild.py` băm nội dung chunk bằng MD5 và chỉ dùng lại vector cũ khi hash trùng (tức nội dung y hệt). Chunk nào có nội dung mới hoặc thay đổi thì vẫn được encode lại. Nhờ vậy việc dựng lại chỉ để đổi cách đánh chunk_id không cần encode lại toàn bộ, giảm thời gian từ khoảng 15 tiếng xuống 1-2 tiếng mà không ảnh hưởng chất lượng vector.

### Pipeline offline và service production có thể chạy lệch model embedding không?

Về nguyên tắc là rủi ro nếu ai đó sửa `config.py` mà quên đồng bộ với cấu hình service production. Hiện tại cả hai cùng khai báo `bkai-foundation-models/vietnamese-bi-encoder` (offline trong `config.py`, production trong `CLAUDE.md`/.env), nên các vector nằm chung không gian ngữ nghĩa. Đây là ràng buộc bắt buộc phải giữ: nếu hai bên dùng model khác nhau, vector của dữ liệu nạp offline sẽ không so khớp đúng với vector query sinh bởi service production, làm hỏng kết quả tìm kiếm.
