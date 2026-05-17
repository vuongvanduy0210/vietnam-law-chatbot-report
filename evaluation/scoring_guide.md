# Hướng dẫn chấm điểm sau khi chạy script

## Bước 1 — Chạy script

```bash
cd Bao_Cao/evaluation

# Cài dependencies
pip install requests pandas tqdm

# Lấy JWT token: đăng nhập vào app → F12 → Network → copy Authorization header
# Paste vào run_evaluation.py dòng ACCESS_TOKEN = "..."

# Chạy Agentic RAG (ước tính 30–60 phút, để qua đêm)
python run_evaluation.py --mode agentic

# Kết quả lưu tại: results/results_agentic_YYYYMMDD_HHMM.csv
```

## Bước 2 — Chấm điểm N1 (Factual) — tự động + thủ công

Mở file CSV bằng Excel/LibreOffice Calc. Với mỗi dòng **type=N1**:

### Cột `score_accuracy` (1/0)
- Đọc cột `answer`
- So sánh với `expected_ref` trong file N1_factual_questions.md
- Điền **1** nếu câu trả lời chứa đúng số liệu/điều khoản
- Điền **0** nếu sai hoặc không tìm được thông tin

**Ví dụ N1-001**: Expected = "30–40 triệu, tước 22–24 tháng"
- Answer có "30-40 triệu" và "22-24 tháng" → **1**
- Answer chỉ nói "bị phạt nặng" → **0**

### Cột `score_citation` (1/0)
- Kiểm tra cột `sources_list`
- Điền **1** nếu sources chứa đúng văn bản (NĐ 168/2024, BLLĐ 2019, v.v.)
- Điền **0** nếu không có sources hoặc sources sai văn bản

### Cột `score_conflict_ok` (1/0) — chỉ cho 3 câu có flag ★ conflict
- N1-001, N1-007, N1-022: câu hỏi về temporal conflict
- Điền **1** nếu hệ thống: (a) nhận diện đúng văn bản mới (NĐ 168/2024), (b) không trả lời dựa trên NĐ 100/2019 đã hết hiệu lực
- Điền **0** nếu trả lời sai văn bản hoặc không phân biệt được

## Bước 3 — Chấm điểm N2 (Open) — dùng LLM-judge

Với mỗi dòng **type=N2**, dùng prompt sau để hỏi Gemini/ChatGPT:

```
Bạn là chuyên gia đánh giá chất lượng câu trả lời pháp lý.
Hãy đánh giá câu trả lời sau theo thang 1-5:

Câu hỏi: [paste nội dung cột question]

Câu trả lời: [paste nội dung cột answer]

Tiêu chí:
- 5: Đầy đủ, chính xác, có trích dẫn điều khoản cụ thể
- 4: Đúng hướng, có trích dẫn nhưng thiếu vài điểm
- 3: Đúng phần lớn nhưng thiếu thông tin quan trọng
- 2: Có thông tin đúng nhưng lẫn thông tin sai
- 1: Sai hoàn toàn hoặc từ chối không có lý

Chỉ trả lời: {"score": X, "reason": "..."}
```

Điền kết quả vào cột `score_quality`.

**Lưu ý tốc độ**: Có thể chấm 5 câu N2 một lúc bằng cách dùng batch prompt.

## Bước 4 — Chạy báo cáo tự động

Sau khi điền đủ điểm:

```bash
# Tạo báo cáo summary
python run_evaluation.py --mode report \
  --agentic-csv results/results_agentic_YYYYMMDD_HHMM.csv

# Nếu có cả Naive RAG
python run_evaluation.py --mode report \
  --agentic-csv results/results_agentic_XXX.csv \
  --naive-csv results/results_naive_XXX.csv
```

## Bảng điền vào báo cáo (Bảng 4.6)

Sau khi chạy report, copy kết quả vào đây:

| Chỉ số | Naive RAG | Agentic RAG | Cải thiện |
|---|---|---|---|
| Accuracy@1 (N1, 30 câu) | __%  | __% | +Δ% |
| Citation Accuracy (N1) | __% | __% | +Δ% |
| Answer Quality /5 (N2) | __.__ | __.__ | +Δ |
| Temporal Conflict (3 câu) | /3 | /3 | — |
| Latency P50 (full) | __s | __s | — |
| Latency P95 (full) | __s | __s | — |

## Giải pháp Naive RAG để so sánh

Nếu chưa có endpoint Naive RAG riêng, có 2 cách:

**Cách 1 (nhanh nhất)**: Gọi thẳng Gemini API với prompt đơn giản:
```python
import google.generativeai as genai
# Với mỗi câu hỏi: retrieve top-5 từ ChromaDB → ghép vào prompt → gọi Gemini Flash
# Không Guardrail, không Verifier, không Query Analysis
```

**Cách 2 (dùng endpoint có sẵn)**: Kiểm tra xem backend có query param
`?mode=naive` hoặc tương tự không. Nếu không, có thể tắt tạm Guardrail
và Verifier trong config và chạy lại.

**Cách 3 (đơn giản nhất cho báo cáo)**: Chỉ chạy Agentic RAG thực tế.
Với Naive RAG, dùng con số ước tính từ kết quả ablation study
(có thể ghi rõ trong báo cáo: "kết quả Naive RAG được đánh giá qua
ablation study với bộ 15 câu đại diện").
```
