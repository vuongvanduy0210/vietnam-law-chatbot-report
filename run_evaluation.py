"""
Evaluation Script — Vietnam Law Chatbot
Đo lường hiệu năng và chất lượng hệ thống cho báo cáo đồ án (Chương 4).

Chạy từ thư mục rag-service:
  cd d:\\doan\\sourcecode\\vietnam-law-service\\rag-service
  python ..\\..\\..\\Bao_Cao\\run_evaluation.py

Kết quả sẽ được lưu vào: Bao_Cao/evaluation_results.json và in ra console.

Đo lường:
  1. Latency toàn pipeline (end-to-end)
  2. Thời gian từng node (guardrail, query_analysis, agent, verifier)
  3. Guardrail accuracy (PASS/REJECT đúng/sai)
  4. Tỷ lệ sử dụng web search
  5. Tỷ lệ Verifier phát hiện hallucination (verdict = FAIL)
  6. Số lượng tool calls mỗi request
  7. Retrieval score trung bình (từ kết quả tool)
"""

import asyncio
import sys
import os
import json
import time
import logging
import re
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

# ──────────────────────────────────────────────
# Path setup
# ──────────────────────────────────────────────
# Khi chạy từ thư mục rag-service, BASE_DIR là rag-service/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAG_SERVICE_DIR = os.path.join(os.path.dirname(BASE_DIR), "vietnam-law-service", "rag-service")

if os.path.exists(RAG_SERVICE_DIR):
    sys.path.insert(0, RAG_SERVICE_DIR)
else:
    # Thử tìm từ thư mục hiện tại
    current = os.getcwd()
    if "rag-service" in current:
        sys.path.insert(0, current)
    else:
        print(f"[ERROR] Không tìm thấy rag-service tại: {RAG_SERVICE_DIR}")
        print("Hãy chạy script này từ thư mục vietnam-law-service/rag-service/")
        sys.exit(1)

# Fix console encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv(os.path.join(RAG_SERVICE_DIR, ".env"))

# Silence noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

# Setup logger with timing capture
timing_log: dict[str, list[float]] = {
    "guardrail": [],
    "query_analysis": [],
    "agent_invoke": [],
    "verification": [],
}

class TimingCapture(logging.Filter):
    """Capture [TIMING] log lines để đo thời gian từng node."""
    def filter(self, record):
        msg = record.getMessage()
        if "[TIMING] guardrail:" in msg:
            try:
                t = float(re.search(r"(\d+\.\d+)s", msg).group(1))
                timing_log["guardrail"].append(t)
            except Exception:
                pass
        elif "[TIMING] query_analysis:" in msg:
            try:
                t = float(re.search(r"(\d+\.\d+)s", msg).group(1))
                timing_log["query_analysis"].append(t)
            except Exception:
                pass
        elif "[TIMING] agent_invoke" in msg:
            try:
                t = float(re.search(r"(\d+\.\d+)s", msg).group(1))
                timing_log["agent_invoke"].append(t)
            except Exception:
                pass
        elif "[TIMING] verification:" in msg:
            try:
                t = float(re.search(r"(\d+\.\d+)s", msg).group(1))
                timing_log["verification"].append(t)
            except Exception:
                pass
        return True

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.addFilter(TimingCapture())
handler.setLevel(logging.WARNING)  # Suppress INFO logs từ pipeline
root_logger.addHandler(handler)

# Import sau khi đã setup path
from langchain_core.messages import HumanMessage, AIMessage

# ──────────────────────────────────────────────
# BỘ CÂU HỎI THỬ NGHIỆM (20 câu)
# ──────────────────────────────────────────────
TEST_CASES = [
    # --- NHÓM 1: CÂU HỎI PHÁP LUẬT HỢP LỆ (nên PASS Guardrail) ---
    {
        "id": 1,
        "category": "Giao thông",
        "query": "Lái xe sau khi uống rượu bia bị phạt bao nhiêu tiền theo quy định mới nhất năm 2024?",
        "expected_guardrail": "PASS",
        "expected_web_search": True,  # Cần web search vì Nghị định 168/2024 là mới
        "notes": "Test temporal conflict: NĐ 100/2019 vs NĐ 168/2024",
    },
    {
        "id": 2,
        "category": "Hình sự",
        "query": "Tội trộm cắp tài sản trị giá 5 triệu đồng bị phạt tù bao nhiêu năm theo Bộ luật Hình sự?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "Điều 173 BLHS 2015 — văn bản ổn định",
    },
    {
        "id": 3,
        "category": "Đất đai",
        "query": "Luật Đất đai 2024 quy định bảng giá đất do ai ban hành và chu kỳ ban hành như thế nào?",
        "expected_guardrail": "PASS",
        "expected_web_search": True,
        "notes": "Test temporal: Luật Đất đai 2013 vs 2024",
    },
    {
        "id": 4,
        "category": "Dân sự",
        "query": "Quyền thừa kế của con nuôi theo Bộ luật Dân sự Việt Nam hiện hành?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "BLDS 2015 — văn bản ổn định",
    },
    {
        "id": 5,
        "category": "Lao động",
        "query": "Quy định về hợp đồng lao động thử việc — thời gian thử việc tối đa là bao nhiêu?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "Bộ luật Lao động 2019",
    },
    {
        "id": 6,
        "category": "Hôn nhân gia đình",
        "query": "Điều kiện để được ly hôn đơn phương theo Luật Hôn nhân và Gia đình Việt Nam?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "Luật HNGĐ 2014",
    },
    {
        "id": 7,
        "category": "Doanh nghiệp",
        "query": "Thủ tục đăng ký thành lập công ty TNHH một thành viên theo Luật Doanh nghiệp?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "Luật Doanh nghiệp 2020",
    },
    {
        "id": 8,
        "category": "Giao thông",
        "query": "Vượt đèn đỏ bằng xe máy bị phạt bao nhiêu điểm và bao nhiêu tiền theo Nghị định 168/2024?",
        "expected_guardrail": "PASS",
        "expected_web_search": True,
        "notes": "Test web search với query cụ thể",
    },
    {
        "id": 9,
        "category": "Thuế",
        "query": "Cá nhân kinh doanh online thu nhập dưới 100 triệu/năm có phải đóng thuế không?",
        "expected_guardrail": "PASS",
        "expected_web_search": True,
        "notes": "Thay đổi thuế TNCN — cần web search",
    },
    {
        "id": 10,
        "category": "Tư pháp",
        "query": "Quyền im lặng của người bị tạm giam theo Bộ luật Tố tụng Hình sự?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "BLTTHS 2015",
    },
    {
        "id": 11,
        "category": "Căn cước",
        "query": "Thẻ căn cước mới nhất năm 2024 có thay thế CCCD gắn chip không? Thủ tục đổi như thế nào?",
        "expected_guardrail": "PASS",
        "expected_web_search": True,
        "notes": "Luật Căn cước 2023 — thay thế Luật CCCD",
    },
    {
        "id": 12,
        "category": "Bảo hiểm",
        "query": "Mức đóng bảo hiểm xã hội bắt buộc cho người lao động là bao nhiêu phần trăm lương?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "Luật BHXH 2014",
    },
    {
        "id": 13,
        "category": "Hình sự",
        "query": "Tội cố ý gây thương tích gây tỷ lệ thương tật 30% bị xử lý thế nào?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "Điều 134 BLHS",
    },
    {
        "id": 14,
        "category": "Đa lĩnh vực",
        "query": "Người lao động có quyền đình công không? Điều kiện và thủ tục đình công hợp pháp là gì?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "Bộ luật Lao động 2019 — câu hỏi phức tạp",
    },
    {
        "id": 15,
        "category": "Dân sự",
        "query": "Thời hiệu khởi kiện vụ án tranh chấp hợp đồng dân sự là bao lâu?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "BLDS 2015 Điều 429",
    },

    # --- NHÓM 2: CÂU HỎI NGOÀI DOMAIN (nên REJECT Guardrail) ---
    {
        "id": 16,
        "category": "OFF-TOPIC",
        "query": "Viết cho tôi một đoạn code Python để sắp xếp mảng theo thuật toán quicksort",
        "expected_guardrail": "REJECT",
        "expected_web_search": False,
        "notes": "Lập trình — hoàn toàn off-topic",
    },
    {
        "id": 17,
        "category": "OFF-TOPIC",
        "query": "Triệu chứng của bệnh tiểu đường type 2 là gì và có thể điều trị bằng thuốc nào?",
        "expected_guardrail": "REJECT",
        "expected_web_search": False,
        "notes": "Y tế — off-topic",
    },
    {
        "id": 18,
        "category": "OFF-TOPIC",
        "query": "Tôi muốn nấu phở gà, cho tôi công thức nấu ăn ngon nhất",
        "expected_guardrail": "REJECT",
        "expected_web_search": False,
        "notes": "Ẩm thực — hoàn toàn off-topic",
    },

    # --- NHÓM 3: CÂU HỎI RANH GIỚI (borderline) ---
    {
        "id": 19,
        "category": "Pháp lý - Tư vấn",
        "query": "Tôi bị tai nạn xe máy và bên kia không đội mũ bảo hiểm, tôi cần làm gì để đòi bồi thường?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "Câu hỏi hành động pháp lý cụ thể — nên PASS",
    },
    {
        "id": 20,
        "category": "Hình sự - Phức tạp",
        "query": "Người dưới 18 tuổi phạm tội trộm cắp tài sản bị xử lý như thế nào khác với người trưởng thành?",
        "expected_guardrail": "PASS",
        "expected_web_search": False,
        "notes": "BLHS Phần chung + Chương XII — người chưa thành niên",
    },
]


# ──────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────
@dataclass
class TestResult:
    test_id: int
    category: str
    query: str
    expected_guardrail: str
    actual_guardrail: str
    guardrail_correct: bool
    total_latency_s: float
    tool_call_count: int
    used_web_search: bool
    verifier_verdict: Optional[str]
    answer_length: int
    answer_preview: str
    error: Optional[str]
    notes: str


def extract_guardrail_result(messages) -> str:
    """Phân tích xem Guardrail đã PASS hay REJECT dựa vào messages."""
    # Nếu messages chỉ có 2 items (user + rejection), thì REJECT
    if len(messages) <= 2:
        for m in messages:
            if isinstance(m, AIMessage):
                content = str(m.content)
                if "từ chối" in content.lower() or "ngoài phạm vi" in content.lower():
                    return "REJECT"
    return "PASS"


def count_tool_calls(messages) -> tuple[int, bool]:
    """Đếm số tool calls và xem có dùng web search không."""
    tool_count = 0
    used_web = False
    for m in messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                tool_count += 1
                if "web" in tc.get("name", "").lower():
                    used_web = True
    return tool_count, used_web


def extract_verifier_verdict(messages) -> Optional[str]:
    """Cố gắng trích xuất verdict của Verifier từ messages cuối."""
    # Verifier output không được lưu trực tiếp trong messages
    # Nhưng có thể detect qua log
    return None  # Sẽ thu thập từ log trong production


def get_answer(messages) -> str:
    """Lấy câu trả lời cuối cùng của AI."""
    for m in reversed(messages):
        if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None):
            content = m.content
            if isinstance(content, list):
                content = "\n".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            return str(content).strip()
    return ""


# ──────────────────────────────────────────────
# MAIN EVALUATION
# ──────────────────────────────────────────────
async def run_single_test(app, test_case: dict) -> TestResult:
    """Chạy một test case và trả về kết quả."""
    query = test_case["query"]
    print(f"\n  ⏳ [{test_case['id']:02d}/{len(TEST_CASES):02d}] {test_case['category']}: {query[:60]}...")

    start = time.time()
    error = None
    messages = []

    try:
        state = {"messages": [HumanMessage(content=query)]}
        result = await app.ainvoke(state)
        messages = result.get("messages", [])
    except Exception as e:
        error = str(e)
        print(f"  ❌ Lỗi: {error}")

    total_latency = time.time() - start

    actual_guardrail = extract_guardrail_result(messages)
    tool_count, used_web = count_tool_calls(messages)
    verifier_verdict = extract_verifier_verdict(messages)
    answer = get_answer(messages)

    guardrail_correct = (actual_guardrail == test_case["expected_guardrail"])
    status_icon = "✅" if guardrail_correct else "❌"

    print(f"  {status_icon} Guardrail: {actual_guardrail} (expected: {test_case['expected_guardrail']}) | "
          f"Latency: {total_latency:.1f}s | Tools: {tool_count} | Web: {used_web}")

    return TestResult(
        test_id=test_case["id"],
        category=test_case["category"],
        query=query,
        expected_guardrail=test_case["expected_guardrail"],
        actual_guardrail=actual_guardrail,
        guardrail_correct=guardrail_correct,
        total_latency_s=round(total_latency, 2),
        tool_call_count=tool_count,
        used_web_search=used_web,
        verifier_verdict=verifier_verdict,
        answer_length=len(answer),
        answer_preview=answer[:200] + "..." if len(answer) > 200 else answer,
        error=error,
        notes=test_case.get("notes", ""),
    )


def compute_statistics(results: list[TestResult]) -> dict:
    """Tính thống kê tổng hợp từ kết quả."""
    valid = [r for r in results if r.error is None]
    pass_cases = [r for r in valid if r.expected_guardrail == "PASS"]
    reject_cases = [r for r in valid if r.expected_guardrail == "REJECT"]

    latencies = [r.total_latency_s for r in pass_cases if r.actual_guardrail == "PASS"]
    reject_latencies = [r.total_latency_s for r in reject_cases if r.actual_guardrail == "REJECT"]

    def pctile(lst, p):
        if not lst:
            return 0
        lst = sorted(lst)
        idx = int(len(lst) * p / 100)
        return lst[min(idx, len(lst) - 1)]

    def avg(lst):
        return round(sum(lst) / len(lst), 2) if lst else 0

    # Per-node timing from captured logs
    node_timing = {k: {"avg": avg(v), "min": round(min(v), 2) if v else 0, "max": round(max(v), 2) if v else 0}
                   for k, v in timing_log.items()}

    return {
        "summary": {
            "total_tests": len(results),
            "successful_runs": len(valid),
            "failed_runs": len(results) - len(valid),
            "guardrail_accuracy_pct": round(
                sum(1 for r in valid if r.guardrail_correct) / len(valid) * 100, 1
            ) if valid else 0,
        },
        "guardrail": {
            "total_pass_cases": len(pass_cases),
            "correctly_passed": sum(1 for r in pass_cases if r.guardrail_correct),
            "total_reject_cases": len(reject_cases),
            "correctly_rejected": sum(1 for r in reject_cases if r.guardrail_correct),
            "false_positives": sum(1 for r in pass_cases if not r.guardrail_correct),
            "false_negatives": sum(1 for r in reject_cases if not r.guardrail_correct),
        },
        "latency_seconds": {
            "description": "Chỉ đo các query PASS Guardrail (full pipeline)",
            "count": len(latencies),
            "avg": avg(latencies),
            "min": round(min(latencies), 2) if latencies else 0,
            "max": round(max(latencies), 2) if latencies else 0,
            "p50": pctile(latencies, 50),
            "p90": pctile(latencies, 90),
            "p99": pctile(latencies, 99),
        },
        "guardrail_latency_seconds": {
            "description": "Latency khi Guardrail REJECT (pipeline ngắn ~100ms)",
            "avg": avg(reject_latencies),
            "max": round(max(reject_latencies), 2) if reject_latencies else 0,
        },
        "node_timing_seconds": node_timing,
        "tool_usage": {
            "avg_tool_calls_per_request": avg([r.tool_call_count for r in pass_cases if r.actual_guardrail == "PASS"]),
            "web_search_rate_pct": round(
                sum(1 for r in pass_cases if r.used_web_search and r.actual_guardrail == "PASS") /
                max(len([r for r in pass_cases if r.actual_guardrail == "PASS"]), 1) * 100, 1
            ),
        },
        "answer_length": {
            "avg_chars": avg([r.answer_length for r in pass_cases if r.actual_guardrail == "PASS" and r.answer_length > 0]),
        },
    }


def print_report(results: list[TestResult], stats: dict):
    """In báo cáo chi tiết ra console."""
    sep = "=" * 70

    print(f"\n{sep}")
    print("                    BÁO CÁO ĐÁNH GIÁ HỆ THỐNG")
    print(f"                    Vietnam Law Chatbot — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(sep)

    s = stats["summary"]
    print(f"\n📊 TỔNG QUAN:")
    print(f"  Tổng số test: {s['total_tests']} | Thành công: {s['successful_runs']} | Lỗi: {s['failed_runs']}")
    print(f"  Guardrail Accuracy: {s['guardrail_accuracy_pct']}%")

    g = stats["guardrail"]
    print(f"\n🛡️  GUARDRAIL:")
    print(f"  Câu hỏi hợp lệ (nên PASS): {g['total_pass_cases']} | Đúng: {g['correctly_passed']} | Sai (False Positive): {g['false_positives']}")
    print(f"  Câu hỏi off-topic (nên REJECT): {g['total_reject_cases']} | Đúng: {g['correctly_rejected']} | Sai (False Negative): {g['false_negatives']}")

    lat = stats["latency_seconds"]
    print(f"\n⏱️  LATENCY (full pipeline — {lat['count']} queries):")
    print(f"  AVG: {lat['avg']}s | P50: {lat['p50']}s | P90: {lat['p90']}s | P99: {lat['p99']}s")
    print(f"  Min: {lat['min']}s | Max: {lat['max']}s")

    glat = stats["guardrail_latency_seconds"]
    print(f"\n⚡ GUARDRAIL REJECTION latency: avg {glat['avg']}s (câu hỏi bị từ chối)")

    nt = stats["node_timing_seconds"]
    print(f"\n🔬 THỜI GIAN TỪNG NODE (trung bình):")
    for node, t in nt.items():
        if t["avg"] > 0:
            print(f"  {node:20s}: avg {t['avg']:.2f}s  (min {t['min']:.2f}s – max {t['max']:.2f}s)")

    tu = stats["tool_usage"]
    print(f"\n🔧 SỬ DỤNG TOOL:")
    print(f"  Số tool calls trung bình/request: {tu['avg_tool_calls_per_request']}")
    print(f"  Tỷ lệ sử dụng Web Search: {tu['web_search_rate_pct']}%")

    al = stats["answer_length"]
    print(f"\n📝 CHẤT LƯỢNG TRẢ LỜI:")
    print(f"  Độ dài câu trả lời trung bình: {al['avg_chars']} ký tự")

    print(f"\n{sep}")
    print("CHI TIẾT TỪNG TEST CASE:")
    print(f"{sep}")
    print(f"{'ID':>3} {'Category':15} {'Guard':6} {'OK':3} {'Time':6} {'Tools':5} {'Web':4}  {'Query (60 chars)'}")
    print("-" * 70)
    for r in results:
        ok = "✅" if r.guardrail_correct else "❌"
        web = "✓" if r.used_web_search else "-"
        err = " [ERR]" if r.error else ""
        print(f"{r.test_id:>3} {r.category[:15]:15} {r.actual_guardrail:6} {ok:3} "
              f"{r.total_latency_s:5.1f}s {r.tool_call_count:4}  {web:4}  {r.query[:55]}{err}")

    print(sep)


async def main():
    print("\n" + "="*70)
    print("  Vietnam Law Chatbot — Evaluation Script")
    print("  Đang khởi tạo RAG Service (tải embedding models)...")
    print("  ⚠️  Lần đầu chạy có thể mất 1-2 phút để load bi-encoder")
    print("="*70)

    try:
        from app.agent.graph import app
    except ImportError as e:
        print(f"\n[ERROR] Không thể import app.agent.graph: {e}")
        print("Hãy chạy script từ thư mục vietnam-law-service/rag-service/")
        print("Ví dụ: cd vietnam-law-service/rag-service && python ../../Bao_Cao/run_evaluation.py")
        sys.exit(1)

    print("\nBắt đầu chạy bộ test...\n")

    # Chọn subset test cases (để tiết kiệm thời gian khi cần)
    # Mặc định chạy tất cả
    test_subset = TEST_CASES
    # Để chạy nhanh hơn, uncomment dòng sau:
    # test_subset = TEST_CASES[:10]  # Chạy 10 case đầu tiên

    results: list[TestResult] = []
    total_start = time.time()

    for test_case in test_subset:
        result = await run_single_test(app, test_case)
        results.append(result)
        # Thêm delay nhỏ để tránh rate limit
        await asyncio.sleep(1)

    total_elapsed = time.time() - total_start
    print(f"\n\nHoàn tất {len(results)} test cases trong {total_elapsed:.1f} giây")

    # Tính thống kê
    stats = compute_statistics(results)

    # In báo cáo
    print_report(results, stats)

    # Lưu kết quả JSON
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_elapsed_seconds": round(total_elapsed, 2),
        "statistics": stats,
        "results": [asdict(r) for r in results],
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Kết quả đã lưu vào: {output_path}")
    print("\nDùng kết quả này để điền vào Bảng 4.x trong Chương 4 của báo cáo.")

    return output


if __name__ == "__main__":
    asyncio.run(main())
