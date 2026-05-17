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
        try:
            resp = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": self.email, "password": self.password},
                timeout=30,
            )
            if resp.status_code == 200:
                return self._save_tokens(resp.json(), "/api/v1/auth/login")
            print(f"❌ Đăng nhập thất bại: HTTP {resp.status_code} — {resp.text[:200]}")
        except requests.RequestException as e:
            print(f"❌ Không kết nối được server: {e}")
        return False

    def refresh(self) -> bool:
        """Dùng refresh_token để lấy access_token mới."""
        if not self.refresh_token:
            return self.login()
        try:
            resp = requests.post(
                f"{self.base_url}/api/v1/auth/refresh",
                json={"refresh_token": self.refresh_token},
                timeout=30,
            )
            if resp.status_code == 200:
                return self._save_tokens(resp.json(), "/api/v1/auth/refresh")
        except requests.RequestException:
            pass
        print("  [AUTH] Refresh token hết hạn — đăng nhập lại...")
        return self.login()

    def apply(self, session: requests.Session):
        """Cập nhật Authorization header cho session."""
        session.headers.update({"Authorization": f"Bearer {self.access_token}"})

    # ── private ─────────────────────────────────────────────────────────────
    def _save_tokens(self, resp_body: dict, path: str) -> bool:
        # Server wrap response: {"success": true, "data": {"access_token": ...}}
        payload = resp_body.get("data") or resp_body
        token = payload.get("access_token") or payload.get("token") or ""
        if not token:
            print(f"  [AUTH] ❌ Không tìm thấy access_token trong response: {resp_body}")
            return False
        self.access_token  = token
        self.refresh_token = payload.get("refresh_token") or self.refresh_token
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


def refresh_if_401(resp, session: requests.Session, auth: AuthManager, attempt: int) -> bool:
    """Trả về True nếu đã refresh và cần retry."""
    if resp.status_code == 401 and attempt == 0:
        print("  [AUTH] 401 — refresh token...")
        auth.refresh()
        auth.apply(session)
        return True
    return False


def ask_question_stream(session: requests.Session, conv_id: str | None, question: str,
                        auth: AuthManager | None = None) -> dict:
    """
    Gửi câu hỏi, thu nhận SSE stream, trả về dict chứa:
      answer, sources, latency_ttft, latency_total, raw_events
    conv_id=None → server tự tạo conversation mới (mỗi câu hỏi 1 conversation riêng)
    """
    url = f"{BASE_URL}/api/v1/chat/messages/stream"
    payload = {"message": question, "conversation_id": conv_id}

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
                auth.refresh()
                auth.apply(session)
                t_start = time.time()
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

            current_event = ""
            for line in resp.iter_lines(decode_unicode=True):
                raw_events.append(line)
                if not line:
                    continue

                if line.startswith("event:"):
                    current_event = line[6:].strip()
                    continue

                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str in ("[DONE]", ""):
                        break
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    if current_event == "done":
                        if t_first_token is None:
                            t_first_token = time.time()
                        msg = data.get("assistant_message", {})
                        answer_chunks.append(msg.get("content", ""))
                        sources = msg.get("sources") or []
                        break

                    elif current_event == "error":
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


def ask_question_sync(session: requests.Session, conv_id: str | None, question: str) -> dict:
    """Fallback: gọi non-streaming endpoint nếu stream không hoạt động"""
    url = f"{BASE_URL}/api/v1/chat/messages"
    payload = {"message": question, "conversation_id": conv_id}
    t_start = time.time()

    try:
        resp = session.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        t_end = time.time()
        if resp.status_code in (200, 201):
            body = resp.json()
            assistant_msg = body.get("data", {}).get("assistant_message", {})
            return {
                "answer": assistant_msg.get("content", ""),
                "sources": assistant_msg.get("sources") or [],
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


def run_evaluation(mode: str, resume_path: Path | None = None) -> Path:
    """Chạy toàn bộ 60 câu, lưu kết quả ra CSV.
    Nếu resume_path được chỉ định, bỏ qua các câu đã có answer và append vào file đó.
    """
    questions = load_questions()

    fieldnames = [
        "id", "type", "group", "is_conflict", "question",
        "answer", "sources_count", "sources_list",
        "latency_ttft", "latency_total", "error",
        "score_accuracy", "score_quality", "score_citation", "score_conflict_ok", "notes",
    ]

    # ── Resume mode: đọc file cũ, lọc câu chưa chạy ─────────────────────────
    done_ids: set[str] = set()
    if resume_path and resume_path.exists():
        with open(resume_path, encoding="utf-8-sig") as rf:
            for row in csv.DictReader(rf):
                if row.get("answer", "").strip():  # chỉ skip nếu có answer
                    done_ids.add(row["id"])
        output_path = resume_path
        print(f"\n{'='*60}")
        print(f"  RESUME mode={mode.upper()} — file: {resume_path.name}")
        print(f"  Đã xong: {len(done_ids)} câu — Còn lại: {len(questions) - len(done_ids)} câu")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = RESULTS_DIR / f"results_{mode}_{timestamp}.csv"
        print(f"\n{'='*60}")
        print(f"  Chạy evaluation mode={mode.upper()}")
        print(f"  Tổng {len(questions)} câu hỏi")

    remaining = [q for q in questions if q["id"] not in done_ids]
    estimated = len(remaining) * (120 + DELAY_BETWEEN_QUESTIONS) / 60
    print(f"  Sẽ chạy: {len(remaining)} câu — Delay: {DELAY_BETWEEN_QUESTIONS}s/câu")
    print(f"  Ước tính thời gian: {estimated:.0f} phút")
    print(f"{'='*60}\n")

    if not remaining:
        print("✅ Tất cả câu đã chạy xong!")
        return output_path

    # Kiểm tra credentials
    if not EVAL_EMAIL or not EVAL_PASSWORD:
        print("❌ Chưa có credentials. Tạo file .env từ .env.example và điền email/password.")
        sys.exit(1)

    # Mở file: append nếu resume, ghi mới nếu fresh run
    open_mode = "a" if done_ids else "w"
    with open(output_path, open_mode, newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not done_ids:
            writer.writeheader()

        # Khởi tạo auth và đăng nhập lần đầu
        auth = AuthManager(BASE_URL, EVAL_EMAIL, EVAL_PASSWORD)
        if not auth.login():
            sys.exit(1)

        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        auth.apply(session)

        for i, q in enumerate(tqdm(remaining, desc="Running", file=sys.stdout)):
            print(f"\n[{i+1:02d}/{len(questions)}] {q['id']} — {q['question'][:80]}...", flush=True)

            # Tạo conversation mới cho mỗi câu để tránh ngữ cảnh chồng chéo
            # conversation_id=None → server tự tạo mới, mỗi câu hỏi 1 context riêng
            print(f"  → Gửi câu hỏi (conversation mới)...", flush=True)
            result = ask_question_stream(session, None, q["question"], auth)
            if result.get("error") == "TIMEOUT" or (
                not result["answer"] and result["error"]
            ):
                print(f"  [RETRY sync] {result['error']}", flush=True)
                result = ask_question_sync(session, None, q["question"])

            sources_list = result.get("sources", [])
            print(f"  Latency: TTFT={result['latency_ttft']}s, Total={result['latency_total']}s", flush=True)
            print(f"  Sources: {len(sources_list)}", flush=True)
            if result.get("error"):
                print(f"  [ERROR] {result['error']}", flush=True)

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
            if i < len(remaining) - 1:
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
    parser.add_argument("--resume", metavar="CSV_PATH",
                        help="Resume từ file CSV cũ, bỏ qua các câu đã có answer")
    parser.add_argument("--agentic-csv", help="Path đến CSV kết quả Agentic (dùng với --mode report)")
    parser.add_argument("--naive-csv", help="Path đến CSV kết quả Naive (dùng với --mode report)")
    args = parser.parse_args()

    if args.mode in ("agentic", "both"):
        resume = Path(args.resume) if args.resume else None
        agentic_result = run_evaluation("agentic", resume_path=resume)
        print(f"\n→ Mở {agentic_result} và điền cột score_accuracy, score_citation, score_conflict_ok (N1)")
        print(f"→ Điền score_quality (N2) bằng LLM-judge hoặc human review")

    if args.mode in ("naive", "both"):
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
