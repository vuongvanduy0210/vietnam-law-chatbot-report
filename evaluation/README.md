# Hướng dẫn chạy Evaluation — Vietnam Law Chatbot

> **Lưu ý**: Script này chạy trên **máy Windows** có source code backend.
> Máy Mac chỉ dùng để viết báo cáo — không cần cài gì thêm ở đó.

---

## Tổng quan

| Mục | Chi tiết |
|---|---|
| Số câu hỏi | 60 (30 factual N1 + 30 open N2) |
| Thời gian chạy | ~2–3 tiếng (tự động, không cần ngồi chờ) |
| Máy chạy | **Windows — máy có source code backend** |
| Kết quả | File CSV lưu trong `results/` |

---

## Bước 0 — Chuyển file sang máy Windows

Copy toàn bộ thư mục `Bao_Cao/evaluation/` từ Mac sang máy Windows.

**Cách nhanh nhất — dùng USB hoặc Google Drive:**
```
Copy thư mục:  Bao_Cao/evaluation/
Sang Windows:  C:\BaoCao\evaluation\   (hoặc bất kỳ đường dẫn nào)
```

**Hoặc dùng Git** (nếu project đã có remote repo):
```bash
# Mac: commit và push
git add Bao_Cao/evaluation/
git commit -m "add evaluation scripts"
git push

# Windows: pull về
git pull
```

---

## Bước 1 — Chuẩn bị môi trường trên máy Windows

### 1.1 Cài Python dependencies

Mở **Command Prompt** hoặc **PowerShell**, chạy:

```bat
pip install requests pandas tqdm python-dotenv
```

### 1.2 Tạo file .env

Trong thư mục `evaluation\`, tạo file tên `.env` (không có tên trước dấu chấm):

```bat
cd C:\BaoCao\evaluation
copy .env.example .env
```

Mở `.env` bằng Notepad và điền thông tin:

```
EVAL_BASE_URL=http://localhost:8000
EVAL_EMAIL=duyconbn7@gnailm.com
EVAL_PASSWORD=Vuongvanduy@0210
EVAL_DELAY=15
```

> **EVAL_DELAY**: số giây chờ giữa mỗi câu để tránh rate limit Gemini API.
> Giữ nguyên 15 là an toàn. Không nên đặt dưới 8.

---

## Bước 2 — Khởi động hệ thống backend

Trước khi chạy script, đảm bảo tất cả service đang hoạt động trên máy Windows.

### 2.1 Khởi động databases (Docker)

```bat
REM Từ thư mục chứa docker-compose.yml của project
docker compose up -d postgres chromadb mongo
```

Kiểm tra:
```bat
docker ps
REM Phải thấy 3 container: postgres, chromadb, mongo đều status "Up"
```

### 2.2 Khởi động Main Service

Mở **Command Prompt 1**:
```bat
cd C:\path\to\main-service
python -m uvicorn main:app --reload --port 8000
```

### 2.3 Khởi động RAG Service

Mở **Command Prompt 2**:
```bat
cd C:\path\to\rag-service
python -m uvicorn main:app --reload --port 8001
```

### 2.4 Kiểm tra nhanh

```bat
curl http://localhost:8000/health
REM Phải trả về {"status": "ok"} hoặc tương tự
```

---

## Bước 3 — Chạy thực nghiệm

Mở **Command Prompt 3** (riêng cho script evaluation):

```bat
cd C:\BaoCao\evaluation
python run_evaluation.py --mode agentic
```

### Nếu muốn chạy nền (đóng cửa sổ vẫn tiếp tục)

```bat
cd C:\BaoCao\evaluation
start /B python run_evaluation.py --mode agentic > eval_log.txt 2>&1
```

Xem tiến độ:
```bat
REM Xem log realtime (nhấn Ctrl+C để thoát xem, script vẫn chạy)
powershell -command "Get-Content eval_log.txt -Wait"

REM Hoặc mở file eval_log.txt bằng Notepad++ và bật auto-reload
```

### Output trong terminal khi đang chạy

```
============================================================
  Chạy evaluation mode=AGENTIC
  Tổng 60 câu hỏi
  Delay mỗi câu: 15s
  Ước tính thời gian: 135 phút
============================================================

  [AUTH] Đăng nhập thành công qua /api/v1/auth/login

Running:   5%|███▌              | 3/60 [06:12<1:57:43]

[03/60] N1-001 — Theo quy định hiện hành, lái xe ô tô...
  Latency: TTFT=4.2s, Total=11.8s
  Sources: 3
```

### Xử lý token hết hạn (tự động)

Script tự xử lý, không cần can thiệp:

```
Lần đầu chạy   →  đăng nhập bằng email/password
Gặp lỗi 401    →  tự gọi /auth/refresh để lấy token mới
Refresh hết hạn →  tự đăng nhập lại bằng email/password
```

---

## Bước 4 — Kết quả sau khi chạy

Kết quả tự lưu tại:
```
evaluation\results\results_agentic_YYYYMMDD_HHMM.csv
```

Mở bằng **Excel**. Các cột script tự điền:

| Cột | Nội dung |
|---|---|
| `id` | N1-001, N2-015... |
| `question` | Nội dung câu hỏi |
| `answer` | Câu trả lời của chatbot |
| `sources_count` | Số nguồn trích dẫn |
| `latency_ttft` | Giây đến token đầu tiên |
| `latency_total` | Giây đến khi xong hoàn toàn |
| `error` | Lỗi nếu có |

Các cột **bạn cần điền tay** sau:
`score_accuracy`, `score_quality`, `score_citation`, `score_conflict_ok`

---

## Bước 5 — Chấm điểm

### 5.1 Chấm N1 — Factual (mở Excel, lọc type = N1)

Đọc cột `answer`, tra đáp án trong file [N1_factual_questions.md](N1_factual_questions.md) cột `Expected ref`:

- **score_accuracy**: `1` nếu answer chứa đúng số liệu/điều khoản, `0` nếu sai
- **score_citation**: `1` nếu `sources_list` chứa đúng tên văn bản, `0` nếu không có
- **score_conflict_ok** (chỉ 3 câu `is_conflict = True`): `1` nếu hệ thống xác định đúng NĐ 168/2024 còn hiệu lực, không nhầm với NĐ 100/2019

### 5.2 Chấm N2 — Open (dùng LLM-judge, lọc type = N2)

Dán vào ChatGPT hoặc Gemini (có thể gộp 5–10 câu một lúc):

```
Bạn là chuyên gia đánh giá câu trả lời pháp lý Việt Nam.
Đánh giá các câu trả lời theo thang 1–5:
  5 = Đầy đủ, chính xác, có trích dẫn điều khoản cụ thể
  4 = Đúng hướng, có trích dẫn, thiếu vài điểm phụ
  3 = Đúng phần lớn nhưng thiếu thông tin quan trọng
  2 = Lẫn thông tin đúng và sai
  1 = Sai hoàn toàn hoặc từ chối không có lý

[CÂU 1]
Câu hỏi: {paste cột question}
Câu trả lời: {paste cột answer}

[CÂU 2] ...

Trả lời: [{"id":1,"score":X,"reason":"..."},{"id":2,...}]
```

Điền kết quả vào cột `score_quality`.

### 5.3 Tạo báo cáo tổng hợp

```bat
cd C:\BaoCao\evaluation
python run_evaluation.py --mode report --agentic-csv results\results_agentic_YYYYMMDD_HHMM.csv
```

Output mẫu:
```
Latency P50 = 11.4s  |  P95 = 18.7s
Accuracy@1 (N1) = 84.3%
Citation Accuracy   = 77.6%
Temporal Conflict   = 2/3
Answer Quality (N2) = 3.87 / 5.0
```

**Copy các con số này vào Bảng 4.6 trong** `04_Chuong_4.md`.

---

## Xử lý sự cố

### Script bị dừng giữa chừng

Không mất dữ liệu — script ghi CSV sau mỗi câu. Để chạy tiếp:

1. Mở CSV, đếm có bao nhiêu dòng kết quả (không tính header)
2. Mở `run_evaluation.py`, tìm hàm `run_evaluation`, thêm dòng:
   ```python
   questions = questions[23:]  # bỏ 23 câu đã chạy, thay số tương ứng
   ```
3. Chạy lại — kết quả ghi vào file CSV mới, ghép tay 2 file sau

### Lỗi 401 liên tục dù đã điền credentials đúng

Kiểm tra endpoint login của backend:
```bat
curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"your@email.com\",\"password\":\"yourpass\"}"
```

Nếu path khác (VD `/auth/login`), mở `run_evaluation.py`, tìm class
`AuthManager`, sửa list đường dẫn trong method `login()`.

### Lỗi TIMEOUT

Tăng timeout trong `run_evaluation.py`:
```python
REQUEST_TIMEOUT = 300  # dòng gần đầu file, tăng lên 300 giây
```

### Rate limit Gemini (lỗi 429 trong log RAG Service)

Tăng delay trong `.env`:
```
EVAL_DELAY=30
```

---

## Checklist trước khi bấm chạy

```
[ ] File .env đã tạo và điền đúng email/password
[ ] docker compose up -d → 3 container đang Up
[ ] Main Service chạy tại localhost:8000
[ ] RAG Service chạy tại localhost:8001
[ ] pip install requests pandas tqdm python-dotenv  đã chạy
[ ] Thử đăng nhập tay vào app được (xác nhận account đúng)
[ ] Tắt chế độ Sleep của Windows trong lúc chạy:
    Settings → System → Power & sleep → Sleep → Never
```

---

## Sau khi có kết quả — việc cần làm trên máy Mac

1. Copy file `results\results_agentic_XXX.csv` về Mac
2. Mở `Bao_Cao/04_Chuong_4.md`, điền số liệu vào **Bảng 4.6**
3. Thay các dòng `| % | % | +Δ% |` bằng số thực từ report
4. Build DOCX (chạy script convert MD → DOCX trên Mac)
