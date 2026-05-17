#!/usr/bin/env python3
"""
Tự động chấm điểm N1 và xuất batch prompt N2 cho LLM-judge.

Usage:
    python score_n1_auto.py --csv results/results_agentic_YYYYMMDD_HHMM.csv
"""

import argparse
import re
import csv
from pathlib import Path

HERE = Path(__file__).parent

# ─── Expected answers cho 30 N1 questions trong CSV ───────────────────────────
# Format: { "N1-XXX": { "accuracy_kws": [...], "citation_kws": [...], "is_conflict": bool } }
# accuracy_kws: ít nhất 1 từ khóa phải có trong answer → score_accuracy = 1
# citation_kws: ít nhất 1 từ khóa phải có trong sources_list → score_citation = 1

N1_EXPECTED = {
    "N1-001": {
        "accuracy_kws": ["22-24", "22 đến 24", "22–24", "22 - 24", "30-40", "30–40 triệu",
                         "22 tháng đến 24", "30.000.000 đồng đến 40.000.000",
                         "30 triệu đến 40", "30 triệu đồng đến 40"],
        "citation_kws": ["168/2024", "NĐ 168", "Nghị định 168"],
        "conflict_kws_ok": ["168/2024", "NĐ 168"],   # phải trích NĐ 168 là đang có hiệu lực
        "conflict_kws_bad": [],                        # answer vẫn ok dù đề cập NĐ 100/2019 để so sánh
        "is_conflict": True,
    },
    "N1-003": {
        "accuracy_kws": ["18-20", "18–20", "18 triệu", "20 triệu", "18.000.000", "20.000.000"],
        "citation_kws": ["168/2024", "NĐ 168", "Nghị định 168"],
        "is_conflict": False,
    },
    "N1-007": {
        "accuracy_kws": ["400.000", "600.000", "400 000", "600 000", "400–600", "400-600"],
        "citation_kws": ["168/2024", "NĐ 168", "Nghị định 168"],
        "conflict_kws_ok": ["168/2024", "NĐ 168"],
        "conflict_kws_bad": [],
        "is_conflict": True,
    },
    "N1-011": {
        "accuracy_kws": ["0 mg", "0mg", "bằng 0", "cấm hoàn toàn", "không được uống", "0 miligam"],
        "citation_kws": ["168/2024", "NĐ 168"],
        "is_conflict": False,
    },
    "N1-013": {
        "accuracy_kws": ["10-12", "10–12", "10 triệu", "12 triệu", "10.000.000", "12.000.000"],
        "citation_kws": ["168/2024", "NĐ 168"],
        "is_conflict": False,
    },
    "N1-022": {
        "accuracy_kws": ["168/2024", "NĐ 168", "01/01/2025", "1/1/2025", "thay thế"],
        "citation_kws": ["168/2024", "NĐ 168"],
        "conflict_kws_ok": ["168/2024", "NĐ 168", "01/01/2025", "thay thế"],
        "conflict_kws_bad": [],
        "is_conflict": True,
    },
    "N1-026": {
        "accuracy_kws": ["62 tuổi", "62 tuoi", "năm 2028", "62"],
        "citation_kws": ["Bộ luật Lao động", "BLLĐ", "2019", "113", "169"],
        "is_conflict": False,
    },
    "N1-028": {
        "accuracy_kws": ["12 ngày", "12 ngay", "12 ngày/năm"],
        "citation_kws": ["Bộ luật Lao động", "BLLĐ", "Điều 113"],
        "is_conflict": False,
    },
    "N1-030": {
        "accuracy_kws": ["60 ngày", "60 ngay", "60 ngày làm việc"],
        "citation_kws": ["Bộ luật Lao động", "BLLĐ", "Điều 25"],
        "is_conflict": False,
    },
    "N1-031": {
        "accuracy_kws": ["150%", "150 %", "ít nhất 150", "1,5 lần"],
        "citation_kws": ["Bộ luật Lao động", "BLLĐ", "Điều 98"],
        "is_conflict": False,
    },
    "N1-033": {
        "accuracy_kws": ["40 giờ", "40 gio", "40 giờ/tháng", "40h/tháng"],
        "citation_kws": ["Bộ luật Lao động", "BLLĐ", "Điều 107"],
        "is_conflict": False,
    },
    "N1-035": {
        "accuracy_kws": ["30 ngày", "30 ngay", "ít nhất 30"],
        "citation_kws": ["Bộ luật Lao động", "BLLĐ", "Điều 35"],
        "is_conflict": False,
    },
    "N1-043": {
        "accuracy_kws": ["8%", "8 %", "tỷ lệ 8", "mức 8"],
        "citation_kws": ["Bảo hiểm xã hội", "BHXH", "Luật BHXH"],
        "is_conflict": False,
    },
    "N1-045": {
        "accuracy_kws": ["6 tháng", "6 thang", "6 tháng thai sản"],
        "citation_kws": ["Bộ luật Lao động", "BLLĐ", "Điều 139"],
        "is_conflict": False,
    },
    "N1-046": {
        "accuracy_kws": ["50 thành viên", "không quá 50", "tối đa 50"],
        "citation_kws": ["Luật Doanh nghiệp", "Doanh nghiệp 2020", "Điều 46"],
        "is_conflict": False,
    },
    "N1-047": {
        "accuracy_kws": ["3 cổ đông", "ít nhất 3", "tối thiểu 3 cổ đông"],
        "citation_kws": ["Luật Doanh nghiệp", "Doanh nghiệp 2020", "Điều 111"],
        "is_conflict": False,
    },
    "N1-050": {
        "accuracy_kws": ["3 ngày", "ba ngày làm việc", "3 ngày làm việc"],
        "citation_kws": ["Luật Doanh nghiệp", "Doanh nghiệp 2020", "Điều 26"],
        "is_conflict": False,
    },
    "N1-053": {
        "accuracy_kws": ["3 năm", "ba năm", "trong 3 năm"],
        "citation_kws": ["Luật Doanh nghiệp", "Doanh nghiệp 2020", "Điều 120"],
        "is_conflict": False,
    },
    "N1-060": {
        "accuracy_kws": ["20%", "20 %", "mức 20", "thuế suất 20"],
        "citation_kws": ["Thuế thu nhập doanh nghiệp", "Thuế TNDN", "Luật thuế"],
        "is_conflict": False,
    },
    "N1-064": {
        "accuracy_kws": ["51%", "51 %", "ít nhất 51", "tối thiểu 51"],
        "citation_kws": ["Luật Doanh nghiệp", "Doanh nghiệp 2020", "Điều 145"],
        "is_conflict": False,
    },
    "N1-066": {
        "accuracy_kws": ["lâu dài", "không thời hạn", "ổn định lâu dài"],
        "citation_kws": ["Luật Đất đai", "Đất đai 2024", "Điều 170"],
        "is_conflict": False,
    },
    "N1-067": {
        "accuracy_kws": ["50 năm", "năm mươi năm"],
        "citation_kws": ["Luật Đất đai", "Đất đai 2024", "Điều 172"],
        "is_conflict": False,
    },
    "N1-070": {
        "accuracy_kws": ["50 năm", "50 năm, có thể gia hạn", "năm mươi năm"],
        "citation_kws": ["Luật Nhà ở", "Nhà ở 2023", "Điều 17"],
        "is_conflict": False,
    },
    "N1-076": {
        "accuracy_kws": ["2%", "2 %", "2% trên", "mức 2"],
        "citation_kws": ["Thu nhập cá nhân", "Thuế TNCN", "TNCN"],
        "is_conflict": False,
    },
    "N1-080": {
        "accuracy_kws": ["5 năm", "sau 5 năm", "ít nhất 5"],
        "citation_kws": ["Luật Nhà ở", "Nhà ở 2023"],
        "is_conflict": False,
    },
    "N1-086": {
        "accuracy_kws": ["16 tuổi", "đủ 16", "từ 16"],
        "citation_kws": ["Bộ luật Hình sự", "BLHS", "Điều 12"],
        "is_conflict": False,
    },
    "N1-087": {
        "accuracy_kws": ["2 triệu", "2.000.000", "từ 2 triệu"],
        "citation_kws": ["Bộ luật Hình sự", "BLHS", "Điều 173"],
        "is_conflict": False,
    },
    "N1-088": {
        "accuracy_kws": ["15 năm", "đến 15 năm", "tối đa 15", "7 năm đến 15",
                         "trên 7 năm đến 15", "7 đến 15"],
        "citation_kws": ["Bộ luật Hình sự", "BLHS", "Điều 9", "135/vbhn", "100/2015"],
        "is_conflict": False,
    },
    "N1-091": {
        "accuracy_kws": ["3 năm", "ba năm"],
        "citation_kws": ["Bộ luật Dân sự", "BLDS", "Điều 429"],
        "is_conflict": False,
    },
    "N1-093": {
        "accuracy_kws": ["20%/năm", "20 %/năm", "20%", "20 phần trăm"],
        "citation_kws": ["Bộ luật Dân sự", "BLDS", "Điều 468"],
        "is_conflict": False,
    },
}


def contains_any(text: str, keywords: list) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def score_n1_row(row: dict) -> dict:
    qid = row["id"]
    expected = N1_EXPECTED.get(qid)
    if not expected:
        return {"score_accuracy": "", "score_citation": "", "score_conflict_ok": ""}

    answer = str(row.get("answer", ""))
    sources = str(row.get("sources_list", ""))

    # score_accuracy
    acc = 1 if contains_any(answer, expected["accuracy_kws"]) else 0

    # score_citation
    cite = 1 if contains_any(sources, expected["citation_kws"]) else 0

    # score_conflict_ok (chỉ cho conflict questions)
    conflict_ok = ""
    if expected.get("is_conflict"):
        ok_kws = expected.get("conflict_kws_ok", [])
        bad_kws = expected.get("conflict_kws_bad", [])
        has_ok = contains_any(answer, ok_kws)
        has_bad = bad_kws and not contains_any(answer, bad_kws)
        conflict_ok = 1 if (has_ok and (not bad_kws or has_bad)) else 0

    return {
        "score_accuracy": acc,
        "score_citation": cite,
        "score_conflict_ok": conflict_ok,
    }


def generate_n2_prompt(n2_rows: list) -> str:
    lines = [
        "Bạn là chuyên gia đánh giá câu trả lời pháp lý Việt Nam.",
        "Đánh giá từng câu trả lời theo thang 1–5:",
        "  5 = Đầy đủ, chính xác, có trích dẫn điều khoản cụ thể",
        "  4 = Đúng hướng, có trích dẫn, thiếu vài điểm phụ",
        "  3 = Đúng phần lớn nhưng thiếu thông tin quan trọng",
        "  2 = Lẫn thông tin đúng và sai",
        "  1 = Sai hoàn toàn hoặc từ chối không có lý",
        "",
    ]
    for i, row in enumerate(n2_rows, 1):
        lines.append(f"[CÂU {i}] ID: {row['id']}")
        lines.append(f"Câu hỏi: {row['question']}")
        lines.append(f"Câu trả lời: {str(row['answer'])[:1500]}")
        lines.append("")

    lines.append('Trả lời JSON: [{"id":"N2-xxx","score":X,"reason":"..."},...]')
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to results CSV")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = HERE / args.csv

    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))

    # Auto-score N1
    n1_rows = [r for r in rows if r["type"] == "N1"]
    n2_rows = [r for r in rows if r["type"] == "N2"]

    print("=" * 60)
    print(f"  Auto-scoring {len(n1_rows)} câu N1")
    print("=" * 60)

    n1_scored = {"accuracy": [], "citation": [], "conflict": []}
    for row in rows:
        if row["type"] == "N1":
            scores = score_n1_row(row)
            row["score_accuracy"] = scores["score_accuracy"]
            row["score_citation"] = scores["score_citation"]
            row["score_conflict_ok"] = scores["score_conflict_ok"]

            n1_scored["accuracy"].append(int(scores["score_accuracy"]))
            n1_scored["citation"].append(int(scores["score_citation"]))
            if scores["score_conflict_ok"] != "":
                n1_scored["conflict"].append(int(scores["score_conflict_ok"]))

            flag = "✓" if scores["score_accuracy"] == 1 else "✗"
            cite_flag = "✓" if scores["score_citation"] == 1 else "✗"
            conflict_str = f"  conflict={scores['score_conflict_ok']}" if scores["score_conflict_ok"] != "" else ""
            print(f"  {row['id']}  acc={flag}  cite={cite_flag}{conflict_str}")

    # Summary N1
    acc_total = sum(n1_scored["accuracy"])
    cite_total = sum(n1_scored["citation"])
    conflict_total = sum(n1_scored["conflict"]) if n1_scored["conflict"] else 0
    conflict_count = len(n1_scored["conflict"])

    print()
    print(f"  Accuracy@1  : {acc_total}/{len(n1_rows)}  = {acc_total/len(n1_rows)*100:.1f}%")
    print(f"  Citation    : {cite_total}/{len(n1_rows)}  = {cite_total/len(n1_rows)*100:.1f}%")
    if conflict_count:
        print(f"  Temporal OK : {conflict_total}/{conflict_count}")
    print()

    # Latency stats
    latencies = []
    for row in rows:
        try:
            latencies.append(float(row["latency_total"]))
        except Exception:
            pass
    if latencies:
        latencies.sort()
        n = len(latencies)
        p50 = latencies[int(n * 0.50)]
        p95 = latencies[int(n * 0.95)]
        print(f"  Latency P50 : {p50:.1f}s   P95 : {p95:.1f}s")
        print()

    # Write scored CSV
    out_path = csv_path.parent / (csv_path.stem + "_scored.csv")
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Đã lưu CSV có điểm N1 → {out_path.name}")
    print()

    # Generate N2 prompts (chia thành batch 10)
    print("=" * 60)
    print(f"  Batch prompt cho {len(n2_rows)} câu N2 (chia 3 batch)")
    print("=" * 60)

    batch_size = 10
    for bi, start in enumerate(range(0, len(n2_rows), batch_size), 1):
        batch = n2_rows[start:start + batch_size]
        prompt = generate_n2_prompt(batch)
        prompt_file = HERE / f"n2_batch_{bi}_prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        ids = [r["id"] for r in batch]
        print(f"  Batch {bi}: {ids[0]}–{ids[-1]}  → {prompt_file.name}")

    print()
    print("  ✅ Xong! Việc cần làm tiếp theo:")
    print("  1. Mở từng file n2_batch_X_prompt.txt → paste vào ChatGPT/Gemini")
    print("  2. Copy JSON kết quả → điền cột score_quality vào CSV _scored")
    print("  3. Chạy: python run_evaluation.py --mode report \\")
    print(f"           --agentic-csv {out_path.name}")


if __name__ == "__main__":
    main()
