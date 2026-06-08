# Luồng tra cứu và duyệt văn bản luật

Tài liệu này mô tả luồng tra cứu và duyệt văn bản pháp luật của hệ thống trợ lý ảo tư vấn pháp luật. Đây là phần chức năng giúp người dùng và quản trị viên có thể duyệt danh sách các văn bản luật đã được nạp vào hệ thống, xem chi tiết từng điều luật, lọc theo chủ đề, năm ban hành và từ khóa, tìm kiếm toàn văn (full-text search), và đặc biệt là tìm kiếm ngữ nghĩa bằng AI (semantic search). Nội dung được viết để người ngoài dự án vẫn có thể hiểu được cách hệ thống vận hành, các thành phần tham gia và lý do thiết kế của từng bước.

Khác với luồng chat chính (Agentic RAG) vốn tập trung vào việc sinh câu trả lời pháp lý, luồng tra cứu văn bản tập trung vào việc duyệt và truy hồi nguyên văn điều luật từ cơ sở dữ liệu. Dữ liệu gốc của điều luật nằm trong MongoDB (collection `articles`), còn phần tìm kiếm ngữ nghĩa được ủy thác sang rag-service vì rag-service mới là nơi nắm giữ vector embedding trong ChromaDB.

## 1. Vai trò của luồng tra cứu văn bản luật

Luồng tra cứu văn bản luật phục vụ hai nhóm người dùng:

- Người dùng cuối: muốn tự tra cứu nguyên văn điều luật, duyệt danh sách văn bản theo chủ đề hoặc năm, hoặc nhập một câu hỏi tự nhiên để hệ thống gợi ý các điều luật liên quan nhất.
- Quản trị viên: quản lý kho văn bản, xóa một văn bản đã nạp sai, và rebuild lại cache sau khi nạp dữ liệu mới.

Khác với luồng chat, luồng này không sinh câu trả lời bằng LLMs. Mục tiêu của nó là trả về dữ liệu có cấu trúc: danh sách văn bản, danh sách điều luật, nội dung nguyên văn của một điều, hoặc danh sách điều luật khớp với một truy vấn. Vì vậy đây là luồng đọc dữ liệu thuần (read-heavy), được tối ưu mạnh bằng cache và index.

Luồng có ba lớp chính:

- Ứng dụng người dùng: hiển thị màn hình thư viện văn bản (Library), danh sách điều, ô tìm kiếm và bộ lọc.
- Main Service: nhận request, xác thực JWT, truy vấn MongoDB qua repository, và với tìm kiếm AI thì gọi sang RAG Service.
- RAG Service: chỉ tham gia khi cần tìm kiếm ngữ nghĩa. Nó thực hiện vector search trong ChromaDB và rerank bằng cross-encoder, sau đó trả về danh sách điều luật liên quan.

Một điểm thiết kế cốt lõi cần nắm ngay: hệ thống phân biệt rõ hai loại tìm kiếm hoàn toàn khác nhau.

```text
1. Full-text search  → MongoDB (text index trên full_content_search + regex law_id)
                     → khớp theo từ khóa/chuỗi ký tự, nhanh, chạy hoàn toàn trong main-service

2. AI semantic search → RAG Service (vector bi-encoder + cross-encoder rerank trên ChromaDB)
                     → khớp theo ý nghĩa, hiểu câu hỏi tự nhiên, cần GPU/model embedding
```

Sự phân biệt này quyết định kiến trúc: tìm kiếm theo từ khóa được giải quyết ngay trong MongoDB, còn tìm kiếm theo ý nghĩa phải đi sang rag-service vì chỉ rag-service có model embedding và ChromaDB.

## 2. Người dùng mở màn hình thư viện văn bản

Khi người dùng mở màn hình thư viện, ứng dụng gọi endpoint danh sách văn bản của Main Service:

```http
GET /api/v1/laws?page=1&limit=20
```

Mọi endpoint trong nhóm `/laws` đều yêu cầu access token hợp lệ. Trong code, ràng buộc này được thể hiện qua dependency `get_current_user` ở mọi route. Ví dụ route danh sách:

```python
@router.get("")
async def get_laws(
        current_user: Annotated[User, Depends(get_current_user)],
        page: int = Query(default=1, ge=1, description="Số trang"),
        limit: int = Query(default=20, ge=1, le=100, description="Số bản ghi mỗi trang"),
        q: Optional[str] = Query(None, max_length=200, description="Tìm kiếm theo mã hoặc tên văn bản"),
        year: Optional[str] = Query(None, max_length=4, description="Lọc theo năm"),
        topics: Optional[List[str]] = Query(None, description="Lọc theo chủ đề"),
):
```

Vì `current_user` được khai báo như một tham số phụ thuộc, FastAPI sẽ chạy `get_current_user` trước khi vào hàm. Nếu token không hợp lệ, request bị từ chối ngay, hàm không bao giờ chạy. Đây là lý do tài liệu không nhắc lại bước xác thực ở từng endpoint phía sau, nhưng cần hiểu rằng tất cả đều đi qua bước này.

Endpoint `/laws` trả về danh sách văn bản đã được nhóm theo `law_id`, kèm phân trang. Mỗi phần tử gồm mã văn bản, năm ban hành, số điều luật và phần tóm tắt. Các tham số `q`, `year`, `topics` cho phép lọc ngay tại bước này.

### LÝ DO THIẾT KẾ

Màn hình thư viện cần hiển thị danh sách văn bản chứ không phải danh sách hàng nghìn điều luật rời rạc. Một văn bản (ví dụ một bộ luật) có thể có hàng trăm điều, mỗi điều là một document riêng trong MongoDB. Nếu liệt kê từng điều thì người dùng sẽ bị ngợp. Vì vậy hệ thống nhóm theo `law_id` và chỉ hiển thị thông tin tổng quan của từng văn bản. Việc nhóm này không thực hiện trực tiếp trên collection `articles` mỗi lần gọi, mà dựa vào một bảng cache riêng (`laws_cache`) sẽ được giải thích ở mục 8.

## 3. Cấu trúc dữ liệu trong MongoDB

Trước khi đi tiếp, cần hiểu cách dữ liệu điều luật được lưu. Database là `VietnamLawDB`, collection chính là `articles`. Mỗi document tương ứng với một điều luật, theo schema (trích từ docstring của `LawRepository.save_articles`):

```python
{
    "_id": "{law_id}_{article_id}",
    "law_id": str,
    "article_id": str,
    "title": str,
    "text": str,
    "metadata": { topics, keywords, summary, year },
    "full_content_search": "{title} \n {text}"
}
```

Các điểm quan trọng:

- `_id` được ghép từ `law_id` và `article_id`. Nhờ vậy, ID của một điều luật là duy nhất và có thể đoán được, ví dụ `01/2009/tt-bnn_15` là Điều 15 của văn bản `01/2009/tt-bnn`.
- `law_id` là mã văn bản, dùng để nhóm tất cả điều của cùng một văn bản.
- `text` là nội dung nguyên văn của điều luật.
- `metadata.topics` và `metadata.keywords` là mảng (array) các chủ đề và từ khóa.
- `metadata.year` là năm ban hành (lưu dạng chuỗi).
- `full_content_search` là một trường được dựng sẵn bằng cách ghép `title` và `text`. Đây chính là trường được đánh text index để phục vụ full-text search.

### LÝ DO THIẾT KẾ

Việc tạo sẵn trường `full_content_search` thay vì đánh text index trực tiếp lên cả `title` lẫn `text` giúp gom toàn bộ nội dung cần tìm vào một chỗ và kiểm soát được những gì lọt vào index. Ngoài ra, vì `topics`/`keywords` ở MongoDB là array gốc nên có thể truy vấn bằng toán tử `$in` một cách tự nhiên, khác với ChromaDB nơi các trường này phải lưu dưới dạng JSON string (do ChromaDB metadata chỉ hỗ trợ kiểu scalar).

## 4. Các index trên MongoDB

Để các truy vấn danh sách, lọc và tìm kiếm nhanh, hệ thống tạo sẵn các index khi khởi động. Trong `main-service/app/db/mongodb.py`, hàm `_ensure_indexes` định nghĩa:

```python
indexes_to_create = {
    "idx_law_id": ([("law_id", 1)], {}),
    "idx_year_law": ([("metadata.year", -1), ("law_id", 1)], {}),
    "idx_topics": ([("metadata.topics", 1)], {}),
    "idx_keywords": ([("metadata.keywords", 1)], {}),
    "idx_law_article": ([("law_id", 1), ("article_id", 1)], {}),
    "idx_title_text": ([("title", "text"), ("full_content_search", "text")], {}),
}
```

Điểm cần chú ý:

- `idx_title_text` là **text index** đặt đồng thời trên `title` và `full_content_search`. Đây là index giúp `$text` search hoạt động. MongoDB chỉ cho phép tối đa một text index trên mỗi collection, nên code có thêm đoạn kiểm tra để bỏ qua việc tạo text index nếu đã tồn tại một text index khác:

```python
for name, (keys, opts) in indexes_to_create.items():
    if name not in existing:
        # Skip text index if one already exists
        if any(k[1] == "text" for k in keys):
            has_text = any(
                "textScoreOrder" in str(v) or v.get("textIndexVersion")
                for v in existing.values()
            )
            if has_text:
                continue
        await col.create_index(keys, name=name, background=True, **opts)
```

- `idx_year_law` là index ghép theo năm (giảm dần) rồi tới `law_id`. Nó phục vụ cho việc sắp xếp danh sách văn bản mới nhất lên đầu.
- `idx_topics` và `idx_keywords` phục vụ lọc theo chủ đề và từ khóa bằng `$in`.

### LÝ DO THIẾT KẾ

Việc tạo index khi khởi động (idempotent — chỉ tạo nếu chưa có) giúp hệ thống không phải quản lý migration thủ công cho MongoDB. Cờ `background=True` đảm bảo việc tạo index không khóa collection. Toàn bộ khối được bọc trong `try/except` và chỉ log cảnh báo (non-fatal) nếu lỗi, vì index là tối ưu hiệu năng chứ không phải điều kiện bắt buộc để service chạy.

## 5. Xem chi tiết một văn bản và danh sách điều luật

Khi người dùng chọn một văn bản trong danh sách, ứng dụng gọi:

```http
GET /api/v1/laws/info?law_id=01/2025/QH16
```

Endpoint này trả về thông tin tổng hợp của văn bản, gồm năm ban hành, số điều, danh sách chủ đề, danh sách từ khóa (gộp từ tất cả các điều), tóm tắt, và danh sách các điều luật (mỗi điều gồm `id`, `article_id`, `title`).

Phần nặng nhất của endpoint này là một aggregation pipeline trong `LawRepository.get_law_detail`:

```python
pipeline = [
    {"$match": {"law_id": law_id}},
    {"$sort": {"article_id": 1}},
    {
        "$group": {
            "_id": "$law_id",
            "year": {"$first": "$metadata.year"},
            "keywords": {"$addToSet": "$metadata.keywords"},
            "article_count": {"$sum": 1},
            # Lấy summary của điều đầu tiên
            "summary": {"$first": "$metadata.summary"},
            "first_title": {"$first": "$title"},
            "source_url": {"$first": "$source_url"},
            "articles": {
                "$push": {
                    "id": "$_id",
                    "article_id": "$article_id",
                    "title": "$title",
                }
            },
        }
    },
    {
        "$project": {
            "_id": 0,
            "law_id": "$_id",
            "year": 1,
            "article_count": 1,
            "summary": {
                "$ifNull": ["$summary", "$first_title"]
            },
            "keywords": {
                "$reduce": {
                    "input": "$keywords",
                    "initialValue": [],
                    "in": {"$setUnion": ["$$value", "$$this"]}
                }
            },
            "source_url": 1,
            "articles": 1,
        }
    },
]
```

Cách pipeline hoạt động:

- `$match` lọc tất cả điều của đúng `law_id`.
- `$sort` theo `article_id` để danh sách điều theo thứ tự.
- `$group` gom các điều về một bản ghi theo `law_id`:
  - `year`, `summary`, `first_title`, `source_url` lấy giá trị của điều đầu tiên bằng `$first`.
  - `article_count` đếm số điều bằng `$sum: 1`.
  - `keywords` dùng `$addToSet` để gom mảng keywords của từng điều thành một mảng các mảng.
  - `articles` dùng `$push` để dồn thông tin từng điều thành một danh sách.
- `$project` định dạng đầu ra:
  - `summary` dùng `$ifNull` để fallback sang `first_title` nếu điều đầu không có tóm tắt.
  - `keywords` dùng `$reduce` + `$setUnion` để làm phẳng mảng các mảng thành một mảng keyword duy nhất, đã loại trùng.

### LÝ DO THIẾT KẾ

Pipeline này được chạy trực tiếp trên collection `articles` chứ không dùng cache, vì cache (`laws_cache`) chỉ lưu thông tin tổng quan mỗi văn bản (1 document/law), không lưu danh sách điều. Khi xem chi tiết, người dùng cần đầy đủ danh sách điều nên phải truy vấn `articles`. Việc gộp keywords bằng `$setUnion` ở tầng database (thay vì lấy về app rồi gộp trong Python) giúp giảm dữ liệu truyền qua mạng và tận dụng engine của MongoDB.

## 6. Xem nội dung nguyên văn một điều luật

Khi người dùng nhấp vào một điều cụ thể, ứng dụng gọi:

```http
GET /api/v1/laws/detail?id=01/2009/tt-bnn_15
```

Đây là endpoint nhẹ nhất: chỉ tìm một document theo `_id`. Trong `LawRepository.get_by_id`:

```python
async def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
    """Get document by _id (full content)."""
    collection = await self._get_collection()

    doc = await collection.find_one({"_id": doc_id})

    if not doc:
        return None

    return {
        "id": doc.get("_id"),
        "law_id": doc.get("law_id"),
        "article_id": doc.get("article_id"),
        "title": doc.get("title"),
        "text": doc.get("text"),
        "topics": doc.get("metadata", {}).get("topics", []),
        "keywords": doc.get("metadata", {}).get("keywords", []),
        "summary": doc.get("metadata", {}).get("summary"),
        "year": doc.get("metadata", {}).get("year"),
    }
```

Khác với endpoint danh sách (chỉ trả tóm tắt), endpoint chi tiết trả thêm trường `text` — chính là nội dung nguyên văn của điều luật. Nếu không tìm thấy, route trả về lỗi `ARTICLE_NOT_FOUND` với HTTP 404.

Bên cạnh đó còn có endpoint `/laws/by-law` để lấy tất cả điều của một văn bản theo dạng phân trang (khác với `/info` ở chỗ `/by-law` phân trang danh sách điều, còn `/info` gộp tất cả vào một bản ghi).

### LÝ DO THIẾT KẾ

Vì `_id` được ghép từ `law_id_article_id` nên tra cứu một điều là thao tác `find_one` theo khóa chính — nhanh nhất có thể, không cần index phụ. Đây là lý do hệ thống chọn ghép `_id` thủ công thay vì để MongoDB tự sinh `ObjectId`: nó cho phép tham chiếu trực tiếp tới một điều luật mà không cần truy vấn trung gian.

## 7. Tìm kiếm toàn văn (full-text search)

Người dùng có thể tìm theo nội dung bằng GET hoặc POST:

```http
GET  /api/v1/laws/search?q=hợp đồng lao động&year=2019
POST /api/v1/laws/search
```

Cả hai route đều gọi chung `LawService.search`, rồi xuống `LawRepository.search`. Đây là phần phức tạp nhất của tầng repository, vì nó vừa hỗ trợ full-text search vừa hỗ trợ lọc theo nhiều trường.

Trước hết, repository dựng `filter_query` từ các tham số:

```python
filter_query = {}

# Full-text search hoặc search theo law_id
if query:
    # Tìm kiếm cả trong nội dung và law_id
    filter_query["$or"] = [
        {"$text": {"$search": query}},
        {"law_id": {"$regex": re.escape(query), "$options": "i"}},
    ]

# Filter by law_id (exact/partial match) - ưu tiên nếu có
if law_id:
    filter_query["law_id"] = {"$regex": re.escape(law_id), "$options": "i"}

# Filter by title (partial match)
if title:
    filter_query["title"] = {"$regex": re.escape(title), "$options": "i"}

# Filter by article_id
if article_id:
    filter_query["article_id"] = article_id

# Filter by topics
if topics:
    filter_query["metadata.topics"] = {"$in": topics}

# Filter by keywords
if keywords:
    filter_query["metadata.keywords"] = {"$in": keywords}

# Filter by year
if year:
    filter_query["metadata.year"] = year
```

Điểm quan trọng nhất là cách xử lý `query`. Hệ thống dùng `$or` gồm hai nhánh:

- `{"$text": {"$search": query}}`: full-text search dựa trên text index (`idx_title_text` trên `full_content_search`). MongoDB sẽ token hóa nội dung và khớp theo từ.
- `{"law_id": {"$regex": re.escape(query), ...}}`: tìm theo mã văn bản bằng regex (không phân biệt hoa thường). Điều này cho phép người dùng gõ một phần mã văn bản (ví dụ `2019/QH14`) để tìm.

Lưu ý `re.escape(query)` được dùng để escape các ký tự đặc biệt của regex, tránh việc người dùng vô tình (hoặc cố tình) chèn pattern regex gây lỗi hoặc tốn tài nguyên.

Phần truy vấn và sắp xếp xử lý riêng cho trường hợp có full-text search:

```python
if query and "$or" in filter_query:
    # Khi có full-text search, thử lấy score
    try:
        # Chỉ lấy score khi có $text
        text_filter = {"$text": {"$search": query}}
        projection["score"] = {"$meta": "textScore"}
        cursor = collection.find(text_filter, projection).sort([
            ("score", {"$meta": "textScore"})
        ]).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)

        # Nếu không có kết quả từ text search, thử search theo law_id
        if not documents:
            projection.pop("score", None)
            law_id_filter = {"law_id": {"$regex": re.escape(query), "$options": "i"}}
            cursor = collection.find(law_id_filter, projection).sort([
                ("metadata.year", DESCENDING),
                ("law_id", ASCENDING),
            ]).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            total = await collection.count_documents(law_id_filter)
    except Exception:
        # Fallback nếu có lỗi
        ...
```

Ý nghĩa:

- Khi có `query`, hệ thống ưu tiên chạy text search và lấy `textScore` (điểm liên quan do MongoDB tính) qua `{"$meta": "textScore"}`, đồng thời sắp xếp kết quả theo điểm này.
- Nếu text search không ra kết quả nào (ví dụ người dùng gõ một mã văn bản không phải từ tự nhiên), hệ thống tự động fallback sang tìm theo `law_id` bằng regex, sắp xếp theo năm giảm dần.
- Nếu có lỗi bất kỳ (ví dụ chưa có text index), khối `except` fallback về truy vấn `filter_query` thông thường.

Trường hợp không có `query` (chỉ lọc theo topic/year/...), kết quả được sắp xếp theo năm giảm dần, rồi `law_id`, rồi `article_id`.

### LÝ DO THIẾT KẾ

Việc bọc full-text search trong `$or` cùng với regex `law_id` xuất phát từ thực tế người dùng tra cứu pháp luật thường gõ một trong hai dạng: hoặc một cụm từ ngữ nghĩa (ví dụ "hợp đồng lao động"), hoặc một mã văn bản (ví dụ "100/2019"). Text index xử lý tốt dạng đầu nhưng không hợp với mã văn bản (vì mã không phải từ tự nhiên), nên cần thêm nhánh regex. Cơ chế fallback nhiều tầng (text → law_id regex → filter thường) đảm bảo người dùng luôn nhận được kết quả hợp lý thay vì màn hình rỗng.

Cần nhấn mạnh: đây là tìm kiếm theo **từ khóa / chuỗi ký tự**, không phải tìm theo ý nghĩa. Nếu người dùng gõ "uống rượu lái xe bị phạt bao nhiêu" thì text search có thể không khớp tốt với điều luật dùng thuật ngữ "nồng độ cồn". Đó là lý do hệ thống cần thêm tìm kiếm ngữ nghĩa bằng AI ở mục 9.

## 8. Cache `laws_cache` cho danh sách và bộ lọc

Hệ thống có một collection riêng tên `laws_cache` đóng vai trò **materialized view**: mỗi document tương ứng với một văn bản (1 doc/law), thay vì một điều. Cache này được dùng cho các truy vấn cần tốc độ cao và không cần dữ liệu chi tiết tới từng điều: danh sách văn bản, danh sách chủ đề, và thống kê dashboard.

Cache được dựng bằng `_build_laws_cache` trong `mongodb.py`:

```python
pipeline = [
    {"$sort": {"law_id": 1, "article_id": 1}},
    {
        "$group": {
            "_id": "$law_id",
            "year": {"$first": "$metadata.year"},
            "article_count": {"$sum": 1},
            "summary": {"$first": "$metadata.summary"},
            "first_title": {"$first": "$title"},
            "topics": {"$first": "$metadata.topics"},
        }
    },
    {
        "$project": {
            "_id": 1,
            "law_id": "$_id",
            "year": 1,
            "article_count": 1,
            "summary": {"$ifNull": ["$summary", "$first_title"]},
            "topics": {"$ifNull": ["$topics", []]},
        }
    },
]

cursor = col.aggregate(pipeline, allowDiskUse=True)
docs = await cursor.to_list(length=None)

if docs:
    await cache_col.drop()
    await cache_col.insert_many(docs)
    # Indexes on cache
    await cache_col.create_index([("year", -1), ("law_id", 1)], name="idx_year_law")
    await cache_col.create_index([("topics", 1)], name="idx_topics")
    await cache_col.create_index(
        [("law_id", 1), ("summary", 1)],
        name="idx_search",
    )
```

Nhờ có cache, `LawRepository.get_laws` truy vấn trên `laws_cache` (nhỏ hơn `articles` rất nhiều) thay vì phải `$group` toàn bộ điều mỗi lần:

```python
async def get_laws(self, ...):
    cache = await self._get_cache_collection()

    filter_query = {}
    if search:
        filter_query["$or"] = [
            {"law_id": {"$regex": re.escape(search), "$options": "i"}},
            {"summary": {"$regex": re.escape(search), "$options": "i"}},
        ]
    if year:
        filter_query["year"] = year
    if topics:
        filter_query["topics"] = {"$in": topics}

    total = await cache.count_documents(filter_query)

    cursor = cache.find(
        filter_query,
        {"_id": 0, "law_id": 1, "year": 1, "article_count": 1, "summary": 1, "topics": 1},
    ).sort([("year", DESCENDING), ("law_id", ASCENDING)]).skip(skip).limit(limit)

    laws = await cursor.to_list(length=limit)
    return laws, total
```

Tương tự, `get_all_topics` cũng chạy `$unwind` + `$group` trên `laws_cache` thay vì `articles`:

```python
cache = await self._get_cache_collection()
pipeline = [
    {"$unwind": "$topics"},
    {"$group": {"_id": "$topics"}},
]
```

Cache có hai mức cập nhật:

- `update_law_cache(law_id)`: chạy lại pipeline cho **một** `law_id` và `replace_one(..., upsert=True)`. Dùng sau khi ingest một văn bản mới — chỉ cập nhật đúng văn bản đó, rất nhanh.
- `delete_law_cache(law_id)`: xóa document khỏi cache khi xóa văn bản.
- `_build_laws_cache()`: dựng lại toàn bộ cache (dùng cho rebuild thủ công). Endpoint `POST /laws/rebuild-cache` (chỉ admin) gọi tới đây qua `LawService.rebuild_cache`.

### LÝ DO THIẾT KẾ

Một bộ luật lớn có thể có hàng trăm điều, và toàn hệ thống có thể có hàng chục nghìn document trong `articles`. Nếu mỗi lần mở thư viện đều phải `$group` toàn bộ `articles` theo `law_id`, truy vấn sẽ chậm và tốn tài nguyên. `laws_cache` chuyển công việc nặng này sang một lần dựng sẵn (precompute), đổi lại các truy vấn danh sách/lọc/topic chỉ còn quét trên một bảng nhỏ đã có index. Đây là sự đánh đổi điển hình: tốn thêm chỗ lưu và phải invalidate khi dữ liệu đổi, nhưng đọc nhanh hơn nhiều lần.

Lưu ý quan trọng về sự nhất quán: vì topics/summary trong cache được lấy bằng `$first` (giá trị của điều đầu tiên sau khi sort), nên cache phản ánh thông tin của Điều 1, không phải gộp toàn văn bản. Đây là lựa chọn có chủ đích để giữ cache nhỏ và dựng nhanh.

## 9. Tìm kiếm ngữ nghĩa bằng AI (semantic search)

Đây là điểm khác biệt lớn nhất của luồng tra cứu. Khi người dùng nhập một câu hỏi tự nhiên trong ô "AI Search" trên màn hình thư viện, ứng dụng gọi:

```http
POST /api/v1/laws/ai-search
```

với body:

```json
{
  "query": "uống rượu lái xe máy bị phạt bao nhiêu",
  "page": 1,
  "page_size": 10
}
```

Route `ai_search` trong `laws.py` không tự xử lý AI. Nó ủy thác sang RAG Service qua `rag_client.semantic_search`:

```python
@router.post("/ai-search")
async def ai_search(
    request: AISearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # Fetch all results from RAG service (up to 50)
    result = await rag_client.semantic_search(
        query=request.query,
        top_k=50,
    )

    if not result.get("success", True):
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=result.get("error", "Lỗi tìm kiếm AI"),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Transform RAG sources → AISearchResult
    sources = result.get("sources", [])
    all_items = []
    for src in sources:
        meta = src.get("metadata", {})
        all_items.append(AISearchResult(
            id=src.get("id", ""),
            law_id=meta.get("law_id"),
            article_id=meta.get("article_id"),
            title=meta.get("title"),
            content=src.get("content", ""),
            score=src.get("score", 0.0),
            topics=meta.get("topics", []),
            keywords=meta.get("keywords", []),
        ))

    # Pagination
    total = len(all_items)
    start = (request.page - 1) * request.page_size
    end = start + request.page_size
    page_items = all_items[start:end]
    ...
```

Cách hoạt động:

- Main Service gọi rag-service lấy tối đa 50 kết quả (`top_k=50`) trong một lần.
- Sau đó transform mỗi `source` từ rag-service thành `AISearchResult` (chuẩn hóa field cho client).
- **Phân trang được thực hiện ở phía Main Service**, trên danh sách đã lấy về, không gọi lại rag-service cho mỗi trang.

`AISearchRequest` ràng buộc `query` tối thiểu 3 ký tự và `page_size` tối đa 20:

```python
class AISearchRequest(BaseModel):
    """AI-powered semantic search request."""
    query: str = Field(..., min_length=3, max_length=500, description="Câu hỏi bằng ngôn ngữ tự nhiên")
    page: int = Field(default=1, ge=1, description="Trang hiện tại")
    page_size: int = Field(default=10, ge=1, le=20, description="Số kết quả mỗi trang")
```

### LÝ DO THIẾT KẾ

Tại sao lấy 50 kết quả một lần rồi phân trang ở Main Service, thay vì để rag-service phân trang? Vì semantic search cần chạy vector search + cross-encoder rerank — đây là các thao tác tốn tài nguyên. Nếu mỗi lần lật trang đều gọi lại rag-service, hệ thống sẽ phải rerank lại từ đầu một cách lãng phí. Lấy một lần đủ rộng (50 kết quả) rồi phân trang trong bộ nhớ giúp các lần lật trang gần như tức thời, đồng thời thứ tự xếp hạng ổn định giữa các trang.

## 10. RAGClient gọi RAG Service bằng kết nối nội bộ

`rag_client.semantic_search` (trong `main-service/app/services/rag_client.py`) gọi rag-service bằng API key nội bộ:

```python
async def semantic_search(
    self,
    query: str,
    top_k: int = 50,
) -> Dict[str, Any]:
    """Call RAG Service /semantic-search endpoint for AI-powered search."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{self.base_url}/api/v1/rag/semantic-search",
                json={
                    "query": query,
                    "top_k": top_k,
                    "include_sources": True,
                },
                headers={
                    "X-API-Key": settings.rag_service_api_key,
                    "X-Internal-Service": "main-service",
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {
                "success": False,
                "sources": [],
                "error": f"Không thể kết nối đến RAG Service: {str(e)}",
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "sources": [],
                "error": f"RAG Service error: {e.response.status_code}",
            }
```

Điểm cần hiểu:

- Header `X-API-Key` và `X-Internal-Service` chính là cơ chế xác thực giữa hai service. Client (mobile/web) không bao giờ gọi trực tiếp rag-service.
- Timeout 60s — đủ cho semantic search (thường chỉ 1-3s) nhưng ngắn hơn nhiều so với timeout 600s của luồng agentic chat, vì semantic search không gọi LLM nên không bị chậm do model fallback.
- Nếu rag-service không phản hồi, hàm trả về `success: False` kèm `error`, để route `ai-search` chuyển thành lỗi 500 thay vì để treo.

### LÝ DO THIẾT KẾ

Việc tách rag-service ra một service nội bộ riêng có lý do kỹ thuật: chỉ rag-service mới nạp model embedding (bi-encoder, cross-encoder) và giữ kết nối ChromaDB. Main Service không cần (và không nên) gánh các model nặng này. Mọi nhu cầu tìm kiếm ngữ nghĩa — dù là chat hay tra cứu thư viện — đều đi qua rag-service. Header API key đảm bảo chỉ backend tin cậy mới gọi được.

## 11. RAG Service xử lý semantic search

Endpoint `/semantic-search` của rag-service (trong `rag-service/app/api/v1/rag.py`) khác hẳn endpoint chat: nó **không gọi LLM** để sinh câu trả lời:

```python
@router.post("/semantic-search", response_model=SearchResponse)
async def semantic_search(
        request: SearchRequest,
        _: InternalAuth,
):
    """
    Semantic search — vector search + cross-encoder rerank only.

    Không dùng LLM answer generation → nhanh hơn (1-3s).
    Dùng cho AI-Powered Search trên Library screen.
    """
    try:
        start_time = time.time()
        rag_service = get_rag_service()

        # Dedicated semantic search pipeline (larger candidate pool, không ảnh hưởng chat)
        candidates = rag_service._vector_search_semantic(request.query)
        ranked = rag_service._rerank_semantic(request.query, candidates)

        # Filter by threshold
        threshold = request.score_threshold or 0.3
        filtered = [d for d in ranked if d.get("score", 0) >= threshold]

        # Deduplicate: multiple chunks of same article → keep highest score
        seen_articles = {}
        for d in filtered:
            meta = d.get("metadata", {})
            law_id = meta.get("law_id", "")
            article_id = meta.get("article_id", "")
            mongo_id = f"{law_id}_{article_id}" if law_id and article_id else d.get("id", "?")

            if mongo_id not in seen_articles or d.get("score", 0) > seen_articles[mongo_id].get("score", 0):
                seen_articles[mongo_id] = {**d, "_mongo_id": mongo_id}

        all_sorted = sorted(seen_articles.values(), key=lambda x: x.get("score", 0), reverse=True)
        docs = all_sorted[:request.top_k]
        ...
```

Các bước:

1. `_vector_search_semantic`: tìm các chunk gần nghĩa nhất trong ChromaDB.
2. `_rerank_semantic`: chấm lại bằng cross-encoder.
3. Lọc theo ngưỡng (`threshold` mặc định `0.3` — thấp hơn ngưỡng của chat).
4. **Khử trùng lặp theo điều luật**: vì một điều luật có thể bị chia thành nhiều chunk trong ChromaDB, hệ thống ghép lại `mongo_id = f"{law_id}_{article_id}"` và chỉ giữ chunk có điểm cao nhất cho mỗi điều.
5. Sắp xếp theo điểm giảm dần và cắt `top_k`.

Sau đó định dạng thành `SourceDocument`, dùng `_mongo_id` (ID của điều luật trong MongoDB) thay cho ID chunk:

```python
sources = []
for d in docs:
    sources.append(SourceDocument(
        id=d.get("_mongo_id", d.get("id", "?")),
        content=d.get("document", "")[:500],
        metadata=_parse_metadata(d.get("metadata", {})),
        score=d.get("score", 0),
    ))
```

### LÝ DO THIẾT KẾ

Bước khử trùng lặp theo `mongo_id` rất quan trọng. Nếu không khử, một điều luật dài bị chia 3 chunk có thể chiếm 3 vị trí trong kết quả, đẩy các điều khác xuống dưới và làm danh sách kết quả kém đa dạng. Bằng cách gom về cấp điều luật và lấy chunk điểm cao nhất, mỗi điều chỉ xuất hiện một lần. Việc trả về `_mongo_id` thay vì chunk ID cũng giúp client có thể gọi tiếp `GET /laws/detail?id=...` để xem nguyên văn điều đó — ChromaDB chunk ID không dùng trực tiếp với MongoDB được.

## 12. Vector search và cross-encoder rerank trong rag-service

Hai hàm cốt lõi của semantic search là `_vector_search_semantic` và `_rerank_semantic` trong `rag-service/app/services/rag_service.py`.

Vector search:

```python
def _vector_search_semantic(self, query: str) -> List[Dict[str, Any]]:
    """Vector search with larger candidate pool for semantic search (Library AI Search)."""
    query_embedding = self._embedding.encode_query(query).tolist()
    results = self._chroma.query_by_embedding(
        query_embedding=query_embedding,
        n_results=settings.semantic_search_top_k
    )
    valid = []
    if not results or not results.get("ids") or len(results["ids"][0]) == 0:
        return valid
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        # ChromaDB cosine distance = 1 - cosine_similarity
        score = max(0.0, 1.0 - distance)
        valid.append({
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": score,
        })
    return valid
```

Ý nghĩa:

- Câu truy vấn được biến thành vector bằng bi-encoder (`encode_query`).
- ChromaDB trả về các chunk gần nhất theo khoảng cách cosine. Hệ thống chuyển khoảng cách thành điểm tương đồng bằng `score = 1.0 - distance`.
- Số ứng viên lấy về là `semantic_search_top_k` (mặc định `100` theo config), lớn hơn pool của chat — vì semantic search cần độ phủ rộng để rerank chọn lọc.

Cross-encoder rerank:

```python
def _rerank_semantic(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Cross-encoder reranking with larger pool for semantic search."""
    if not candidates:
        return []
    top = candidates[:settings.semantic_search_rerank_candidates]
    documents = [c["document"][:1000] for c in top]
    raw_scores = self._embedding.rerank(query, documents)

    ce_min = min(raw_scores)
    ce_max = max(raw_scores)
    ce_range = ce_max - ce_min if ce_max != ce_min else 1.0

    current_year = datetime.now().year
    for i, c in enumerate(top):
        ce_norm = (raw_scores[i] - ce_min) / ce_range
        blended = (c["score"] * 0.3) + (ce_norm * 0.7)

        year = c.get("metadata", {}).get("year")
        if year:
            try:
                years_old = current_year - int(year)
                if years_old <= 2:
                    blended += 0.05
                elif years_old <= 5:
                    blended += 0.02
                elif years_old > 10:
                    blended -= 0.03
            except (ValueError, TypeError):
                pass

        c["score"] = max(0.0, min(1.0, float(blended)))
    top.sort(key=lambda x: x["score"], reverse=True)
    return top
```

Ý nghĩa:

- Chỉ rerank `semantic_search_rerank_candidates` ứng viên đầu (mặc định `60` theo config).
- `raw_scores` là điểm cross-encoder thô, được chuẩn hóa min-max về khoảng 0-1 (`ce_norm`).
- Điểm cuối cùng `blended` kết hợp `30%` điểm vector + `70%` điểm cross-encoder — ưu tiên cross-encoder vì nó đánh giá cặp (query, document) chính xác hơn.
- Year boost: cộng/trừ nhẹ theo độ mới của văn bản (mới hơn được ưu tiên nhẹ).

### LÝ DO THIẾT KẾ

Đây là kiến trúc retrieve-then-rerank điển hình: bi-encoder nhanh nhưng kém chính xác (chỉ encode query và document riêng rồi đo khoảng cách), trong khi cross-encoder chậm hơn nhưng chính xác hơn (xét đồng thời cặp query-document). Hệ thống dùng bi-encoder để lấy nhanh ~100 ứng viên, rồi dùng cross-encoder rerank ~60 ứng viên đầu. Công thức blend giống hệt phần dùng cho chat (cùng trọng số 0.3/0.7 và cùng year boost), giữ tính nhất quán giữa hai luồng. Điểm khác biệt nằm ở pool size (`semantic_search_top_k=100`, `semantic_search_rerank_candidates=60`) lớn hơn để phù hợp với mục tiêu duyệt danh sách (cần nhiều kết quả) thay vì sinh một câu trả lời (cần ít nhưng chính xác).

So sánh với full-text search (mục 7): full-text khớp theo từ nên không bắt được câu hỏi diễn đạt khác từ vựng điều luật; semantic search khớp theo ý nghĩa nên xử lý tốt câu hỏi tự nhiên, đổi lại tốn tài nguyên hơn và phải qua rag-service.

## 13. Các endpoint metadata phục vụ bộ lọc

Màn hình thư viện cần các danh sách để dựng bộ lọc: danh sách chủ đề, năm, mã văn bản, từ khóa. Các endpoint tương ứng:

```http
GET /api/v1/laws/topics
GET /api/v1/laws/years
GET /api/v1/laws/law-ids
GET /api/v1/laws/keywords
```

Mỗi endpoint đều có phân trang và một số có tìm kiếm (`q`). Cách lấy dữ liệu khác nhau tùy nguồn:

- `get_all_topics`: `$unwind` + `$group` trên **`laws_cache`** (nhỏ, nhanh).
- `get_all_keywords`: `$unwind` + `$group` trên `metadata.keywords` của **`articles`** (vì cache không lưu keywords đầy đủ).
- `get_all_years`: dùng `collection.distinct("metadata.year")` rồi sort giảm dần.
- `get_all_law_ids`: nếu có `search` thì dùng aggregation `$group` + `$match` regex; nếu không thì dùng `distinct("law_id")`.

Ví dụ `get_all_years`:

```python
async def get_all_years(self, skip: int = 0, limit: int = 100) -> Tuple[List[str], int]:
    """Get all unique years with pagination."""
    collection = await self._get_collection()

    # Get all distinct years first
    all_years = await collection.distinct("metadata.year")
    all_years = sorted([y for y in all_years if y], reverse=True)

    total = len(all_years)
    paginated_years = all_years[skip:skip + limit]

    return paginated_years, total
```

### LÝ DO THIẾT KẾ

Số lượng năm và mã văn bản thường không quá lớn, nên `distinct` là cách đơn giản và đủ nhanh; phân trang được làm trong bộ nhớ. Ngược lại, topics có thể trùng lặp nhiều giữa các điều nên phải `$unwind` + `$group` để loại trùng, và việc chạy trên `laws_cache` thay vì `articles` giúp tránh quét hàng chục nghìn điều. Keywords vẫn phải quét `articles` vì cache chỉ giữ topics của điều đầu tiên, không giữ keywords gộp.

## 14. Quản trị viên xóa một văn bản

Quản trị viên có thể xóa toàn bộ dữ liệu của một văn bản:

```http
DELETE /api/v1/laws/{law_id}
```

Đây là thao tác ghi duy nhất trong luồng tra cứu và liên quan tới cả ba kho dữ liệu. Route `delete_law` trong `laws.py` thực hiện theo thứ tự an toàn:

```python
# 1. ChromaDB — xoá trước vì nếu fail còn có thể rollback bằng cách giữ nguyên Mongo
try:
    await rag_client.delete_by_law_id(law_id)
except Exception as e:
    logger.error(f"❌ ChromaDB delete failed for {law_id}: {e}")
    errors.append(f"ChromaDB: {e}")

# 2. MongoDB articles
deleted_articles = 0
try:
    deleted_articles = await law_repo.delete_by_law_id(law_id)
except Exception as e:
    logger.error(f"❌ MongoDB articles delete failed for {law_id}: {e}")
    errors.append(f"MongoDB articles: {e}")

# 3. MongoDB laws_cache
try:
    mongodb = await get_mongodb()
    await mongodb.delete_law_cache(law_id)
except Exception as e:
    logger.error(f"❌ laws_cache delete failed for {law_id}: {e}")
    errors.append(f"laws_cache: {e}")

invalidate_dashboard_cache()
```

Các bước:

1. Kiểm tra quyền admin (`role == "admin"`), nếu không thì trả 403.
2. Kiểm tra văn bản tồn tại bằng `exists_by_law_id`, nếu không thì trả 404.
3. Xóa khỏi ChromaDB (qua rag-service) trước.
4. Xóa các điều khỏi MongoDB `articles`.
5. Xóa khỏi `laws_cache`.
6. Invalidate dashboard cache.

Mỗi bước được bọc `try/except` riêng và gom lỗi vào `errors`. Nếu có lỗi từng phần, route vẫn trả về 500 kèm mô tả lỗi nhưng các bước khác đã chạy xong — đây là xóa best-effort, không phải transaction nguyên tử.

### LÝ DO THIẾT KẾ

Thứ tự xóa ChromaDB trước được giải thích ngay trong comment code: nếu xóa ChromaDB thất bại, dữ liệu MongoDB vẫn còn nguyên, nên người dùng vẫn duyệt được văn bản và có thể thử xóa lại. Nếu làm ngược lại (xóa Mongo trước, Chroma fail), hệ thống sẽ rơi vào trạng thái lệch: điều luật biến mất khỏi thư viện nhưng vector vẫn còn trong ChromaDB, gây nhiễu cho cả chat lẫn semantic search. Vì hệ thống dùng ba kho dữ liệu khác nhau (không thể có transaction chung), cách an toàn nhất là chọn thứ tự sao cho trạng thái lỗi vẫn còn khắc phục được.

## 15. Cache dashboard và cơ chế invalidate

Bên cạnh `laws_cache` (cache dữ liệu trong MongoDB), hệ thống còn có một **in-memory TTL cache** cho thống kê dashboard, nằm trong `main-service/app/api/v1/dashboard.py`:

```python
_CACHE_TTL_SECONDS = 60.0
_cache_lock = asyncio.Lock()
_cache_data: Optional[Dict[str, Any]] = None
_cache_expires_at: float = 0.0


def invalidate_dashboard_cache() -> None:
    """Gọi sau khi upload/delete/rebuild-cache thành công để stats refresh ngay."""
    global _cache_data, _cache_expires_at
    _cache_data = None
    _cache_expires_at = 0.0
```

Dashboard hiển thị các số liệu: tổng số văn bản, tổng số điều, số task thành công/thất bại/đang xử lý, top chủ đề, và các task gần nhất. Các số liệu Mongo được lấy từ `laws_cache` bằng `$facet` (gộp nhiều thống kê trong một round-trip):

```python
facet_pipeline = [
    {"$facet": {
        "totals": [
            {"$group": {
                "_id": None,
                "total_laws": {"$sum": 1},
                "total_articles": {"$sum": "$article_count"},
            }}
        ],
        "top_topics": [
            {"$unwind": "$topics"},
            {"$group": {"_id": "$topics", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
    }}
]
```

Endpoint `/dashboard/stats` đọc cache với double-check locking để tránh nhiều request cùng miss cache rồi cùng đi query:

```python
now = time.monotonic()
if _cache_data is not None and now < _cache_expires_at:
    return success_response(data=_cache_data)

async with _cache_lock:
    # Double-check sau khi lấy lock — tránh race khi nhiều request cùng miss cache
    now = time.monotonic()
    if _cache_data is not None and now < _cache_expires_at:
        return success_response(data=_cache_data)

    payload = await _build_stats_payload(db)
    _cache_data = payload
    _cache_expires_at = time.monotonic() + _CACHE_TTL_SECONDS
```

Cache này được invalidate ở các thời điểm dữ liệu thay đổi. Trong luồng tra cứu, có hai chỗ gọi `invalidate_dashboard_cache()`:

- Sau khi xóa một văn bản (`DELETE /laws/{law_id}`).
- Sau khi rebuild cache (`POST /laws/rebuild-cache`).

Ngoài ra luồng upload/ingest văn bản (ngoài phạm vi tài liệu này) cũng gọi invalidate sau khi nạp xong.

### LÝ DO THIẾT KẾ

Có hai loại cache với mục đích khác nhau, đừng nhầm:

- `laws_cache` là một collection MongoDB (materialized view) — bền vững, dùng để tăng tốc các truy vấn danh sách/lọc/topic.
- Dashboard cache là biến trong RAM của tiến trình main-service, có TTL 60 giây — dùng để tránh query lại số liệu thống kê quá thường xuyên khi nhiều admin cùng mở dashboard.

Thống kê dashboard không cần realtime tuyệt đối (đúng như comment trong code: "chỉ đổi khi có upload/delete"), nên TTL 60s là chấp nhận được. Tuy nhiên khi có thao tác làm thay đổi dữ liệu (xóa/rebuild/ingest), hệ thống chủ động invalidate để admin thấy số liệu mới ngay lập tức thay vì chờ hết TTL. Double-check locking ngăn hiện tượng "cache stampede" — nhiều request cùng lúc thấy cache rỗng và cùng chạy aggregation nặng.

## 16. Tóm tắt luồng tra cứu

Toàn bộ luồng tra cứu văn bản luật có thể tóm tắt như sau:

```text
DUYỆT DANH SÁCH
Người dùng mở thư viện
-> GET /laws (có thể kèm q/year/topics)
-> LawRepository.get_laws truy vấn laws_cache
-> trả danh sách văn bản (group by law_id) + phân trang

XEM CHI TIẾT
Chọn một văn bản
-> GET /laws/info -> aggregation get_law_detail trên articles
-> trả thông tin văn bản + danh sách điều
Chọn một điều
-> GET /laws/detail -> find_one theo _id
-> trả nguyên văn điều luật (text)

FULL-TEXT SEARCH
Gõ từ khóa
-> GET/POST /laws/search
-> $or { $text trên full_content_search, regex law_id }
-> fallback law_id regex nếu text rỗng
-> trả danh sách điều khớp + textScore

AI SEMANTIC SEARCH
Gõ câu hỏi tự nhiên
-> POST /laws/ai-search
-> RAGClient.semantic_search (X-API-Key)
-> rag-service /semantic-search
   -> _vector_search_semantic (bi-encoder + ChromaDB)
   -> _rerank_semantic (cross-encoder 0.3/0.7 + year boost)
   -> dedup theo law_id_article_id
-> Main Service phân trang trong bộ nhớ
-> trả danh sách điều liên quan + score

QUẢN TRỊ
Admin xóa văn bản
-> DELETE /laws/{law_id}
-> xóa ChromaDB -> articles -> laws_cache
-> invalidate dashboard cache
Admin rebuild cache
-> POST /laws/rebuild-cache -> _build_laws_cache -> invalidate dashboard cache
```

Thiết kế này đạt ba mục tiêu. Thứ nhất, tách bạch rõ ràng giữa tìm kiếm từ khóa (MongoDB) và tìm kiếm ngữ nghĩa (rag-service), mỗi loại phục vụ một nhu cầu khác nhau. Thứ hai, tối ưu hiệu năng đọc bằng hai lớp cache (materialized view `laws_cache` và in-memory TTL cache dashboard). Thứ ba, đảm bảo nhất quán dữ liệu khi xóa qua ba kho bằng thứ tự xóa an toàn và invalidate cache chủ động.

## 17. Các file code chính liên quan

Các file quan trọng của luồng tra cứu văn bản luật gồm:

- `vietnam-law-service/main-service/app/api/v1/laws.py`: định nghĩa toàn bộ API tra cứu — list, info, search (GET/POST), ai-search, topics, years, law-ids, keywords, by-law, detail, rebuild-cache, và DELETE văn bản.
- `vietnam-law-service/main-service/app/services/law_service.py`: tầng service, chuyển đổi page/limit thành skip và gọi xuống repository.
- `vietnam-law-service/main-service/app/repositories/law_repository.py`: tầng truy cập MongoDB, chứa các aggregation pipeline cho `get_laws`, `get_law_detail`, `get_all_topics`, `search`...
- `vietnam-law-service/main-service/app/schemas/law.py`: các schema request/response, gồm `LawSearchRequest`, `AISearchRequest`, `AISearchResult`.
- `vietnam-law-service/main-service/app/db/mongodb.py`: kết nối MongoDB, tạo index, dựng và cập nhật `laws_cache`.
- `vietnam-law-service/main-service/app/api/v1/dashboard.py`: dashboard cache TTL và hàm `invalidate_dashboard_cache`.
- `vietnam-law-service/main-service/app/services/rag_client.py`: client nội bộ gọi rag-service, chứa method `semantic_search`.
- `vietnam-law-service/rag-service/app/api/v1/rag.py`: endpoint `/semantic-search` của rag-service.
- `vietnam-law-service/rag-service/app/services/rag_service.py`: chứa `_vector_search_semantic` và `_rerank_semantic`.

## 18. Các câu hỏi phản biện có thể gặp về luồng tra cứu

### Phân biệt full-text search và AI semantic search như thế nào?

Full-text search chạy hoàn toàn trong MongoDB, dùng text index trên `full_content_search` (kết hợp regex trên `law_id`), khớp theo từ/chuỗi ký tự. Nó nhanh, không cần GPU, nhưng không hiểu được câu hỏi diễn đạt khác từ vựng điều luật. AI semantic search chạy ở rag-service, biến câu hỏi thành vector bằng bi-encoder, tìm chunk gần nghĩa trong ChromaDB, rồi rerank bằng cross-encoder. Nó hiểu được ý nghĩa câu hỏi tự nhiên nhưng tốn tài nguyên hơn và phải qua một service riêng.

### Vì sao cần `laws_cache` mà không query thẳng `articles`?

Vì danh sách văn bản cần nhóm theo `law_id`, và một văn bản có thể có hàng trăm điều. `$group` toàn bộ `articles` mỗi lần mở thư viện sẽ chậm. `laws_cache` precompute sẵn một document cho mỗi văn bản, nên các truy vấn danh sách/lọc/topic chỉ quét một bảng nhỏ đã có index.

### Cache được invalidate khi nào?

Có hai loại cache. `laws_cache` (collection MongoDB) được cập nhật theo từng văn bản qua `update_law_cache` khi ingest, xóa qua `delete_law_cache` khi xóa văn bản, và dựng lại toàn bộ qua `_build_laws_cache` khi rebuild. Dashboard cache (in-memory TTL 60s) được invalidate bằng `invalidate_dashboard_cache()` ngay sau khi xóa văn bản, rebuild cache, hoặc ingest văn bản mới — để admin thấy số liệu mới mà không phải chờ hết TTL.

### Text index nằm trên trường nào và vì sao?

Text index `idx_title_text` đặt trên `title` và `full_content_search`. Trường `full_content_search` được dựng sẵn bằng cách ghép `title` và `text` khi lưu điều luật. Gom nội dung tìm kiếm vào một trường giúp kiểm soát những gì lọt vào index và tối ưu cho `$text` search. MongoDB chỉ cho phép một text index trên mỗi collection, nên code có kiểm tra để không tạo trùng.

### Vì sao semantic search lấy 50 kết quả rồi phân trang ở Main Service?

Vì vector search + cross-encoder rerank tốn tài nguyên. Nếu mỗi lần lật trang đều gọi lại rag-service, hệ thống phải rerank lại từ đầu. Lấy một lần đủ rộng (50 kết quả) rồi phân trang trong bộ nhớ giúp lật trang gần như tức thời và giữ thứ tự xếp hạng ổn định.

### Vì sao phải khử trùng lặp theo `law_id_article_id` trong semantic search?

Vì một điều luật dài bị chia thành nhiều chunk trong ChromaDB. Nếu không khử, nhiều chunk của cùng một điều có thể chiếm nhiều vị trí trong kết quả, làm danh sách kém đa dạng. Hệ thống gom về cấp điều luật, giữ chunk điểm cao nhất, và trả về `_mongo_id` để client có thể tra cứu tiếp nguyên văn điều đó trong MongoDB.

### Vì sao xóa ChromaDB trước MongoDB?

Vì nếu xóa ChromaDB thất bại, dữ liệu MongoDB vẫn còn nguyên, người dùng vẫn duyệt được và có thể thử xóa lại. Nếu xóa MongoDB trước mà ChromaDB fail, điều luật biến mất khỏi thư viện nhưng vector vẫn còn trong ChromaDB, gây nhiễu cho chat và semantic search. Vì ba kho dữ liệu không thể dùng chung một transaction, thứ tự này giữ cho trạng thái lỗi vẫn còn khắc phục được.

### Endpoint tra cứu có yêu cầu xác thực không?

Có. Mọi route trong nhóm `/laws` đều phụ thuộc `get_current_user`, nên đều cần access token hợp lệ. Riêng `rebuild-cache` và `DELETE /laws/{law_id}` còn yêu cầu `role == "admin"`, nếu không sẽ trả về 403.

### Semantic search có gọi LLM không?

Không. Endpoint `/semantic-search` chỉ chạy vector search + cross-encoder rerank, không sinh câu trả lời bằng LLM (khác hẳn luồng chat agentic). Nhờ vậy nó nhanh hơn nhiều (1-3s) và timeout chỉ 60s thay vì 600s như luồng chat.
