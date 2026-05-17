"""
Evaluation script — Vietnam Law Chatbot
Chạy batch 60 câu hỏi tự động, lưu kết quả ra CSV.
Tự động đăng nhập và refresh token khi hết hạn.

Cách dùng:
  # 1. Copy .env.example → .env, điền email/password
  # 2. Cài dependencies:
  pip install requests pandas tqdm python-dotenv

  python run_evaluation.py --mode agentic   # chạy Agentic RAG
  python run_evaluation.py --mode naive     # chạy Naive RAG
  python run_evaluation.py --mode both      # chạy cả hai
  python run_evaluation.py --mode report --agentic-csv results/xxx.csv
"""

import csv
import json
import time
import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
import requests
from tqdm import tqdm

# ─── LOAD CONFIG FROM .env ─────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
_env_file = SCRIPT_DIR / ".env"
if _env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_file)

BASE_URL          = os.getenv("EVAL_BASE_URL", "http://localhost:8000")
EVAL_EMAIL        = os.getenv("EVAL_EMAIL", "")
EVAL_PASSWORD     = os.getenv("EVAL_PASSWORD", "")
DELAY_BETWEEN_QUESTIONS = int(os.getenv("EVAL_DELAY", "15"))
REQUEST_TIMEOUT   = 180  # giây — Agentic RAG có thể mất tới 3 phút

QUESTIONS_FILE = SCRIPT_DIR / "selected_60_questions.md"
RESULTS_DIR    = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)
# ───────────────────────────────────────────────────────────────────────────────


# ─── AUTH MANAGER ──────────────────────────────────────────────────────────────
class AuthManager:
    """Quản lý JWT: tự đăng nhập, tự refresh khi nhận 401."""

    def __init__(self, base_url: str, email: str, password: str):
        self.base_url      = base_url
        self.email         = email
        self.password      = password
        self.access_token  = ""
        self.refresh_token = ""

    # ── public ──────────────────────────────────────────────────────────────
    def login(self) -> bool:
        """Đăng nhập bằng email/password, lưu access + refresh token."""
        # Thử các endpoint phổ biến của FastAPI auth
        for path in ("/api/v1/auth/login", "/api/v1/auth/token", "/auth/login"):
            try:
                resp = requests.post(
                    f"{self.base_url}{path}",
                    # FastAPI OAuth2PasswordRequestForm dùng form data
                    data={"username": self.email, "password": self.password},
                    timeout=30,
                )
                if resp.status_code == 200:
                    return self._save_tokens(resp.json(), path)
                # Thử JSON body nếu form data không được chấp nhận
                resp2 = requests.post(
                    f"{self.base_url}{path}",
                    json={"email": self.email, "password": self.password},
                    timeout=30,
                )
                if resp2.status_code == 200:
                    return self._save_tokens(resp2.json(), path)
            except requests.RequestException:
                continue
        print("❌ Không đăng nhập được. Kiểm tra BASE_URL, email, password trong .env")
        return False

    def refresh(self) -> bool:
        """Dùng refresh_token để lấy access_token mới."""
        if not self.refresh_token:
            return self.login()
        for path in ("/api/v1/auth/refresh", "/api/v1/auth/token/refresh"):
            try:
                resp = requests.post(
                    f"{self.base_url}{path}",
                    json={"refresh_token": self.refresh_token},
                    timeout=30,
                )
                if resp.status_code == 200:
                    return self._save_tokens(resp.json(), path)
            except requests.RequestException:
                continue
        # refresh thất bại → đăng nhập lại
        print("  [AUTH] Refresh token hết hạn — đăng nhập lại...")
        return self.login()

    def apply(self, session: requests.Session):
        """Cập nhật Authorization header cho session."""
        session.headers.update({"Authorization": f"Bearer {self.access_token}"})

    # ── private ─────────────────────────────────────────────────────────────
    def _save_tokens(self, data: dict, path: str) -> bool:
        token = (
            data.get("access_token")
            or data.get("token")
            or data.get("accessToken")
            or ""
        )
        if not token:
            return False
        self.access_token  = token
        self.refresh_token = (
            data.get("refresh_token")
            or data.get("refreshToken")
            or self.refresh_token
        )
        print(f"  [AUTH] ✅ Đăng nhập thành công qua {path}")
        return True


def load_questions() -> list[dict]:
    """Parse câu hỏi từ file selected_60_questions.md"""
    questions = []
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        content = f.read()

    # Tìm tất cả dòng trong bảng markdown có format: | ID | Nhóm | Câu hỏi |
    pattern = r"\|\s*(N[12]-\d{3})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
    for match in re.finditer(pattern, content):
        qid = match.group(1).strip()
        group = match.group(2).strip()
        question = match.group(3).strip()
        if question and question != "Câu hỏi":  # bỏ header
            questions.append({
                "id": qid,
                "group": group,
                "type": "N1" if qid.startswith("N1") else "N2",
                "is_conflict": "★ conflict" in group,
                "question": question,
            })
    return questions


def create_conversation(session: requests.Session, auth: AuthManager) -> str | None:
    """Tạo một conversation mới, trả về conversation_id. Tự refresh nếu 401."""
    for attempt in range(2):
        resp = session.post(
            f"{BASE_URL}/api/v1/conversations",
            json={"title": f"Eval-{datetime.now().strftime('%H%M%S')}"},
            timeout=30,
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            return data.get("id") or data.get("conversation_id")
        if resp.status_code == 401 and attempt == 0:
            print("  [AUTH] 401 khi tạo conversation — refresh token...")
            auth.refresh()
            auth.apply(session)
            continue
        print(f"  [WARN] Không tạo được conversation: {resp.status_code} {resp.text[:200]}")
        return None


def ask_question_stream(session: requests.Session, conv_id: str, question: str,
                        auth: AuthManager | None = None) -> dict:
    """
    Gửi câu hỏi, thu nhận SSE stream, trả về dict chứa:
      answer, sources, latency_ttft, latency_total, raw_events
    """
    url = f"{BASE_URL}/api/v1/conversations/{conv_id}/messages"
    payload = {"content": question, "role": "user"}

    t_start = time.time()
    t_first_token = None
    answer_chunks = []
    sources = []
    raw_events = []

    for attempt in range(2):
      try:
        with session.post(
            url,
            json=payload,
            headers={"Accept": "text/event-stream"},
            stream=True,
            timeout=REQUEST_TIMEOUT,
        ) as resp:
            if resp.status_code == 401 and attempt == 0 and auth:
                print("  [AUTH] 401 khi stream — refresh token...")
                auth.refresh()
                auth.apply(session)
                t_start = time.time()  # reset timer
                t_first_token = None
                answer_chunks.clear()
                sources.clear()
                raw_events.clear()
                continue
            if resp.status_code not in (200, 201):
                return {
                    "answer": "",
                    "sources": [],
                    "latency_ttft": -1,
                    "latency_total": -1,
                    "error": f"HTTP {resp.status_code}: {resp.text[:300]}",
                }

            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                raw_events.append(line)

                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str in ("[DONE]", ""):
                        break
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    event_type = data.get("type", "")

                    if event_type == "answer" or event_type == "token":
                        token = data.get("content", data.get("token", ""))
                        if token:
                            if t_first_token is None:
                                t_first_token = time.time()
                            answer_chunks.append(token)

                    elif event_type == "sources":
                        sources = data.get("sources", [])

                    elif event_type == "done":
                        sources = data.get("sources", sources)
                        break

      except requests.Timeout:
          return {
              "answer": "".join(answer_chunks),
              "sources": sources,
              "latency_ttft": round(t_first_token - t_start, 2) if t_first_token else -1,
              "latency_total": -1,
              "error": "TIMEOUT",
          }
      except Exception as e:
          return {
              "answer": "".join(answer_chunks),
              "sources": sources,
              "latency_ttft": -1,
              "latency_total": -1,
              "error": str(e),
          }
      break  # thành công, thoát vòng retry

    t_end = time.time()
    return {
        "answer": "".join(answer_chunks),
        "sources": sources,
        "latency_ttft": round((t_first_token - t_start), 2) if t_first_token else -1,
        "latency_total": round(t_end - t_start, 2),
        "error": "",
    }


def ask_question_sync(session: requests.Session, conv_id: str, question: str) -> dict:
    """Fallback: gọi non-streaming endpoint nếu stream không hoạt động"""
    url = f"{BASE_URL}/api/v1/conversations/{conv_id}/messages"
    payload = {"content": question, "role": "user"}
    t_start = time.time()

    try:
        resp = session.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        t_end = time.time()
        if resp.status_code in (200, 201):
            data = resp.json()
            return {
                "answer": data.get("content", data.get("answer", "")),
                "sources": data.get("sources", []),
                "latency_ttft": -1,
                "latency_total": round(t_end - t_start, 2),
                "error": "",
            }
        return {
            "answer": "",
            "sources": [],
            "latency_ttft": -1,
            "latency_total": -1,
            "error": f"HTTP {resp.status_code}",
        }
    except Exception as e:
        return {"answer": "", "sources": [], "latency_ttft": -1, "latency_total": -1, "error": str(e)}


def run_evaluation(mode: str) -> Path:
    """Chạy toàn bộ 60 câu, lưu kết quả ra CSV"""
    questions = load_questions()
    print(f"\n{'='*60}")
    print(f"  Chạy evaluation mode={mode.upper()}")
    print(f"  Tổng {len(questions)} câu hỏi")
    print(f"  Delay mỗi câu: {DELAY_BETWEEN_QUESTIONS}s")
    estimated = len(questions) * (120 + DELAY_BETWEEN_QUESTIONS) / 60
    print(f"  Ước tính thời gian: {estimated:.0f} phút")
    print(f"{'='*60}\n")

    # Kiểm tra credentials
    if not EVAL_EMAIL or not EVAL_PASSWORD:
        print("❌ Chưa có credentials. Tạo file .env từ .env.example và điền email/password.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = RESULTS_DIR / f"results_{mode}_{timestamp}.csv"

    fieldnames = [
        "id", "type", "group", "is_conflict", "question",
        "answer", "sources_count", "sources_list",
        "latency_ttft", "latency_total", "error",
        # Cột chấm điểm — điền tay sau khi chạy xong
        "score_accuracy",     # N1: 1/0 (đúng/sai factual)
        "score_quality",      # N2: 1-5 (LLM-judge hoặc human)
        "score_citation",     # 1/0 (citation có khớp nguồn không)
        "score_conflict_ok",  # N1 conflict: 1/0 (phát hiện đúng cặp xung đột không)
        "notes",              # Ghi chú thêm
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Khởi tạo auth và đăng nhập lần đầu
        auth = AuthManager(BASE_URL, EVAL_EMAIL, EVAL_PASSWORD)
        if not auth.login():
            sys.exit(1)

        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        auth.apply(session)

        for i, q in enumerate(tqdm(questions, desc="Running")):
            tqdm.write(f"\n[{i+1:02d}/{len(questions)}] {q['id']} — {q['question'][:80]}...")

            # Tạo conversation mới cho mỗi câu để tránh ngữ cảnh chồng chéo
            conv_id = create_conversation(session, auth)
            if not conv_id:
                tqdm.write("  [SKIP] Không tạo được conversation")
                result = {"answer": "", "sources": [], "latency_ttft": -1,
                          "latency_total": -1, "error": "NO_CONV_ID"}
            else:
                result = ask_question_stream(session, conv_id, q["question"], auth)
                if result.get("error") == "TIMEOUT" or (
                    not result["answer"] and result["error"]
                ):
                    tqdm.write(f"  [RETRY sync] {result['error']}")
                    result = ask_question_sync(session, conv_id, q["question"])

            sources_list = result.get("sources", [])
            tqdm.write(f"  Latency: TTFT={result['latency_ttft']}s, Total={result['latency_total']}s")
            tqdm.write(f"  Sources: {len(sources_list)}")
            if result.get("error"):
                tqdm.write(f"  [ERROR] {result['error']}")

            row = {
                "id": q["id"],
                "type": q["type"],
                "group": q["group"],
                "is_conflict": q["is_conflict"],
                "question": q["question"],
                "answer": result["answer"][:2000],  # cắt để CSV không quá lớn
                "sources_count": len(sources_list),
                "sources_list": json.dumps(sources_list, ensure_ascii=False)[:500],
                "latency_ttft": result["latency_ttft"],
                "latency_total": result["latency_total"],
                "error": result.get("error", ""),
                "score_accuracy": "",
                "score_quality": "",
                "score_citation": "",
                "score_conflict_ok": "",
                "notes": "",
            }
            writer.writerow(row)
            f.flush()  # ghi ngay lập tức, không mất dữ liệu nếu bị gián đoạn

            # Delay trước câu tiếp theo
            if i < len(questions) - 1:
                time.sleep(DELAY_BETWEEN_QUESTIONS)

    print(f"\n✅ Xong! Kết quả lưu tại: {output_path}")
    return output_path


def generate_report(agentic_path: Path, naive_path: Path | None = None):
    """Tạo báo cáo tổng hợp từ CSV kết quả (sau khi đã điền điểm thủ công)"""
    import pandas as pd

    df_a = pd.read_csv(agentic_path)
    print("\n" + "="*60)
    print("  BÁO CÁO ĐÁNH GIÁ — AGENTIC RAG")
    print("="*60)

    # Latency
    valid_lat = df_a[df_a["latency_total"] > 0]["latency_total"]
    if len(valid_lat):
        print(f"\nLatency (full response):")
        print(f"  P50 = {valid_lat.median():.1f}s")
        print(f"  P95 = {valid_lat.quantile(0.95):.1f}s")
        print(f"  Mean = {valid_lat.mean():.1f}s")

    valid_ttft = df_a[df_a["latency_ttft"] > 0]["latency_ttft"]
    if len(valid_ttft):
        print(f"Latency (TTFT):")
        print(f"  P50 = {valid_ttft.median():.1f}s")
        print(f"  P95 = {valid_ttft.quantile(0.95):.1f}s")

    # Accuracy (N1)
    n1 = df_a[df_a["type"] == "N1"]
    if n1["score_accuracy"].notna().any():
        acc = n1["score_accuracy"].dropna().astype(float)
        print(f"\nAccuracy@1 (N1, {len(acc)} câu): {acc.mean()*100:.1f}%")

    # Citation accuracy
    if n1["score_citation"].notna().any():
        cit = n1["score_citation"].dropna().astype(float)
        print(f"Citation Accuracy (N1): {cit.mean()*100:.1f}%")

    # Conflict detection
    conflict = df_a[df_a["is_conflict"] == True]
    if conflict["score_conflict_ok"].notna().any():
        cf = conflict["score_conflict_ok"].dropna().astype(float)
        print(f"Temporal Conflict Detection: {cf.sum():.0f}/{len(cf)}")

    # Answer quality (N2)
    n2 = df_a[df_a["type"] == "N2"]
    if n2["score_quality"].notna().any():
        qual = n2["score_quality"].dropna().astype(float)
        print(f"\nAnswer Quality (N2, {len(qual)} câu): {qual.mean():.2f}/5.0")

    # Error rate
    errors = df_a[df_a["error"].notna() & (df_a["error"] != "")]
    print(f"\nError rate: {len(errors)}/{len(df_a)} ({len(errors)/len(df_a)*100:.1f}%)")

    if naive_path:
        df_n = pd.read_csv(naive_path)
        print("\n" + "="*60)
        print("  SO SÁNH: NAIVE vs AGENTIC")
        print("="*60)

        rows = []
        for col, label in [
            ("score_accuracy", "Accuracy@1 (N1)"),
            ("score_citation", "Citation Accuracy (N1)"),
            ("score_quality", "Answer Quality (N2, /5)"),
        ]:
            a_val = df_a[col].dropna().astype(float).mean()
            n_val = df_n[col].dropna().astype(float).mean()
            if col == "score_quality":
                rows.append(f"  {label:<30} Naive={n_val:.2f}  Agentic={a_val:.2f}  Δ={a_val-n_val:+.2f}")
            else:
                rows.append(f"  {label:<30} Naive={n_val*100:.1f}%  Agentic={a_val*100:.1f}%  Δ={+(a_val-n_val)*100:.1f}%")

        for r in rows:
            print(r)

        lat_a = df_a[df_a["latency_total"] > 0]["latency_total"].median()
        lat_n = df_n[df_n["latency_total"] > 0]["latency_total"].median()
        print(f"  {'Latency P50 (full response)':<30} Naive={lat_n:.1f}s  Agentic={lat_a:.1f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vietnam Law Chatbot Evaluation")
    parser.add_argument("--mode", choices=["agentic", "naive", "both", "report"],
                        default="agentic")
    parser.add_argument("--agentic-csv", help="Path đến CSV kết quả Agentic (dùng với --mode report)")
    parser.add_argument("--naive-csv", help="Path đến CSV kết quả Naive (dùng với --mode report)")
    args = parser.parse_args()

    if args.mode in ("agentic", "both"):
        agentic_result = run_evaluation("agentic")
        print(f"\n→ Mở {agentic_result} và điền cột score_accuracy, score_citation, score_conflict_ok (N1)")
        print(f"→ Điền score_quality (N2) bằng LLM-judge hoặc human review")

    if args.mode in ("naive", "both"):
        # Nếu có endpoint naive mode riêng, điền vào đây
        # Có thể cần điều chỉnh URL hoặc payload
        run_evaluation("naive")

    if args.mode == "report":
        try:
            import pandas
        except ImportError:
            print("❌ Cần cài pandas: pip install pandas")
            sys.exit(1)
        if not args.agentic_csv:
            print("❌ Cần chỉ định --agentic-csv")
            sys.exit(1)
        naive = Path(args.naive_csv) if args.naive_csv else None
        generate_report(Path(args.agentic_csv), naive)
