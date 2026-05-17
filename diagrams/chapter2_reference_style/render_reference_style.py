from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "sample_images" / "chapter2_reference_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BLACK = "#111111"
GRAY = "#666666"
LIGHT = "#f6f6f6"
WHITE = "#ffffff"


def font(size: int, bold: bool = False):
    paths = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in paths:
        if path and Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


F_TITLE = font(30, True)
F_H = font(22, True)
F = font(18)
F_S = font(15)
F_XS = font(13)


def canvas(title: str, w=1400, h=760):
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)
    d.text((w // 2, 34), title, anchor="mm", font=F_TITLE, fill=BLACK)
    d.line((70, 62, w - 70, 62), fill=BLACK, width=2)
    return img, d


def text_bbox(d, text, fnt):
    box = d.multiline_textbbox((0, 0), text, font=fnt, spacing=4)
    return box[2] - box[0], box[3] - box[1]


def wrap(d, text, fnt, max_w):
    lines: list[str] = []
    for raw in text.split("\n"):
        words = raw.split()
        cur = ""
        for word in words:
            trial = word if not cur else f"{cur} {word}"
            if text_bbox(d, trial, fnt)[0] <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return "\n".join(lines)


def label(d, x, y, text, fnt=F_S, anchor="mm"):
    d.multiline_text((x, y), text, anchor=anchor, font=fnt, fill=BLACK, align="center", spacing=4)


def pill(d, x, y, w, h, text, fill=WHITE, stroke=BLACK, fnt=F, width=2):
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=fill, outline=stroke, width=width)
    label(d, x + w / 2, y + h / 2, wrap(d, text, fnt, w - 28), fnt=fnt)
    return (x, y, w, h)


def rect(d, x, y, w, h, text, fill=WHITE, stroke=BLACK, fnt=F, width=2):
    d.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=fill, outline=stroke, width=width)
    label(d, x + w / 2, y + h / 2, wrap(d, text, fnt, w - 24), fnt=fnt)
    return (x, y, w, h)


def chip(d, x, y, w, h, text):
    r = rect(d, x, y, w, h, "", fill=WHITE, stroke=BLACK, width=2)
    cx, cy = x + 26, y + h / 2
    d.rounded_rectangle((cx - 14, cy - 14, cx + 14, cy + 14), radius=5, outline=BLACK, width=2)
    for dx in (-20, 20):
        d.line((cx + dx, cy - 8, cx + dx + (8 if dx < 0 else -8), cy - 8), fill=BLACK, width=1)
        d.line((cx + dx, cy + 8, cx + dx + (8 if dx < 0 else -8), cy + 8), fill=BLACK, width=1)
    label(d, x + 78, y + h / 2, text, fnt=F_S, anchor="lm")
    return r


def db(d, x, y, w, h, text):
    d.rectangle((x, y + 18, x + w, y + h - 18), fill=WHITE, outline=BLACK, width=2)
    d.ellipse((x, y, x + w, y + 36), fill=BLACK, outline=BLACK, width=2)
    d.ellipse((x, y + h - 36, x + w, y + h), fill=WHITE, outline=BLACK, width=2)
    d.arc((x, y + h - 36, x + w, y + h), 0, 180, fill=BLACK, width=2)
    label(d, x + w / 2, y + h + 22, text, fnt=F_XS)
    return (x, y, w, h)


def person(d, x, y, scale=1.0, caption=""):
    r = 16 * scale
    d.ellipse((x - r, y - r, x + r, y + r), outline=BLACK, width=2)
    d.line((x, y + r, x, y + 70 * scale), fill=BLACK, width=2)
    d.line((x, y + 36 * scale, x - 34 * scale, y + 54 * scale), fill=BLACK, width=2)
    d.line((x, y + 36 * scale, x + 34 * scale, y + 54 * scale), fill=BLACK, width=2)
    d.line((x, y + 70 * scale, x - 28 * scale, y + 108 * scale), fill=BLACK, width=2)
    d.line((x, y + 70 * scale, x + 28 * scale, y + 108 * scale), fill=BLACK, width=2)
    if caption:
        label(d, x, y + 132 * scale, caption, fnt=F_XS)


def tool_icon(d, x, y, caption="Các tool"):
    d.line((x - 20, y + 20, x + 20, y - 20), fill=BLACK, width=3)
    d.line((x - 12, y - 22, x - 22, y - 12), fill=BLACK, width=3)
    d.line((x + 14, y + 22, x + 24, y + 12), fill=BLACK, width=3)
    d.ellipse((x - 8, y - 8, x + 8, y + 8), outline=BLACK, width=2)
    label(d, x, y + 48, caption, fnt=F_XS)


def mid(r, side):
    x, y, w, h = r
    return {
        "l": (x, y + h / 2),
        "r": (x + w, y + h / 2),
        "t": (x + w / 2, y),
        "b": (x + w / 2, y + h),
        "c": (x + w / 2, y + h / 2),
    }[side]


def arrow_head(d, x1, y1, x2, y2):
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 11
    p1 = (x2 - size * math.cos(ang - math.pi / 7), y2 - size * math.sin(ang - math.pi / 7))
    p2 = (x2 - size * math.cos(ang + math.pi / 7), y2 - size * math.sin(ang + math.pi / 7))
    d.polygon([(x2, y2), p1, p2], fill=BLACK)


def arrow(d, a, b, text=None, curved=False, width=2):
    x1, y1 = a
    x2, y2 = b
    if curved:
        mx = (x1 + x2) / 2
        d.line((x1, y1, mx, y1, mx, y2, x2, y2), fill=BLACK, width=width, joint="curve")
    else:
        d.line((x1, y1, x2, y2), fill=BLACK, width=width)
    arrow_head(d, x1, y1, x2, y2)
    if text:
        lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 12
        label(d, lx, ly, text, fnt=F_XS)


def hinh_2_1():
    img, d = canvas("Hình 2.1. Kiến trúc tổng thể hệ thống", 1500, 760)
    user = person(d, 110, 270, 0.75, "Người dùng")
    mobile = pill(d, 220, 180, 180, 52, "Mobile App")
    admin = pill(d, 220, 330, 180, 52, "Admin Web")
    main = pill(d, 510, 250, 250, 70, "Main Service\nAPI + nghiệp vụ")
    rag = pill(d, 880, 250, 250, 70, "RAG Service\nAgent + Retrieval")
    llm = chip(d, 910, 120, 170, 58, "LLMs")
    pg = db(d, 1180, 105, 70, 70, "PostgreSQL")
    mongo = db(d, 1290, 105, 70, 70, "MongoDB")
    chroma = db(d, 1235, 275, 70, 70, "ChromaDB")
    cloud = rect(d, 1190, 470, 160, 54, "Cloudinary", fill=LIGHT, fnt=F_S)
    web = rect(d, 1190, 585, 160, 54, "Web Search", fill=LIGHT, fnt=F_S)
    arrow(d, (145, 282), mid(mobile, "l"))
    arrow(d, mid(mobile, "r"), mid(main, "l"), "SSE")
    arrow(d, mid(admin, "r"), mid(main, "l"), "WebSocket")
    arrow(d, mid(main, "r"), mid(rag, "l"), "Internal API")
    arrow(d, mid(rag, "t"), mid(llm, "b"))
    arrow(d, mid(main, "t"), (1215, 175), curved=True)
    arrow(d, mid(main, "t"), (1325, 175), curved=True)
    arrow(d, mid(rag, "r"), (1235, 310))
    arrow(d, mid(main, "b"), mid(cloud, "l"), curved=True)
    arrow(d, mid(rag, "b"), mid(web, "l"), curved=True)
    save(img, "hinh_2_1")


def hinh_2_4():
    img, d = canvas("Hình 2.4. Agent graph xử lý câu hỏi", 1500, 820)
    start = pill(d, 670, 90, 150, 38, "__START__", fnt=F_XS)
    summary = pill(d, 600, 165, 290, 44, "__Summary_Chat_History__", fnt=F_XS)
    thinking = pill(d, 615, 240, 260, 44, "__Initial_Thinking__", fnt=F_XS)
    validator = pill(d, 605, 345, 260, 48, "__Plan_Validator__", fnt=F_XS)
    end = pill(d, 1070, 345, 180, 48, "__END__", fnt=F_XS)
    replan = pill(d, 210, 345, 210, 48, "__Re_Planning__", fnt=F_XS)
    rag = pill(d, 235, 470, 205, 48, "__RAG_Agentic__", fnt=F_XS)
    task = pill(d, 620, 470, 230, 48, "__Do_Task__", fnt=F_XS)
    exec_tools = pill(d, 620, 585, 245, 48, "__Execute_tools__", fnt=F_XS)
    tools = [
        pill(d, 1040, 515, 220, 44, "Tool_retrieve_law", fnt=F_XS),
        pill(d, 1040, 585, 220, 44, "Tool_search_web", fnt=F_XS),
        pill(d, 1040, 655, 220, 44, "Tool_check_effective_date", fnt=F_XS),
        pill(d, 1040, 725, 220, 44, "Tool_rank_citation", fnt=F_XS),
    ]
    arrow(d, mid(start, "b"), mid(summary, "t"))
    arrow(d, mid(summary, "b"), mid(thinking, "t"))
    arrow(d, mid(thinking, "b"), mid(validator, "t"))
    arrow(d, mid(replan, "r"), mid(validator, "l"), "Re-Plan")
    arrow(d, mid(validator, "r"), mid(end, "l"), "End")
    arrow(d, mid(rag, "r"), mid(task, "l"), "Do-Task")
    arrow(d, mid(validator, "b"), mid(task, "t"))
    arrow(d, mid(task, "b"), mid(exec_tools, "t"))
    for idx, t in enumerate(tools):
        arrow(d, mid(exec_tools, "r"), mid(t, "l"))
    save(img, "hinh_2_4")


def hinh_2_6():
    img, d = canvas("Hình 2.6. Two-stage Retrieval", 1500, 720)
    q = pill(d, 90, 310, 155, 52, "Query")
    enc = pill(d, 310, 220, 190, 56, "Bi-Encoder\nvector hóa")
    chroma = db(d, 575, 105, 78, 78, "ChromaDB\nTop 60")
    candidate = pill(d, 730, 220, 190, 56, "Candidate\nTop 40")
    cross = pill(d, 310, 430, 190, 56, "Cross-Encoder\nrerank")
    boost = pill(d, 560, 430, 170, 56, "Year Boost")
    conflict = pill(d, 790, 430, 210, 56, "Conflict Check")
    top = pill(d, 1060, 430, 155, 56, "Top 10")
    score = pill(d, 1240, 320, 140, 58, "Score\n>= 0.60?")
    context = pill(d, 1240, 210, 150, 48, "Context")
    fallback = pill(d, 1240, 515, 150, 48, "Fallback")
    label(d, 430, 160, "Giai đoạn 1: tìm kiếm vector", fnt=F_H)
    label(d, 690, 560, "Giai đoạn 2: rerank và chuẩn hóa", fnt=F_H)
    arrow(d, mid(q, "r"), mid(enc, "l"))
    arrow(d, mid(enc, "r"), (575, 145))
    arrow(d, (653, 145), mid(candidate, "l"))
    arrow(d, mid(candidate, "b"), mid(cross, "t"), curved=True)
    arrow(d, mid(cross, "r"), mid(boost, "l"))
    arrow(d, mid(boost, "r"), mid(conflict, "l"))
    arrow(d, mid(conflict, "r"), mid(top, "l"))
    arrow(d, mid(top, "r"), mid(score, "l"))
    arrow(d, mid(score, "t"), mid(context, "b"), "Có")
    arrow(d, mid(score, "b"), mid(fallback, "t"), "Không")
    save(img, "hinh_2_6")


def hinh_2_9():
    img, d = canvas("Hình 2.9. Quy trình nạp văn bản pháp luật", 1500, 760)
    person(d, 90, 245, 0.7, "Admin")
    upload = pill(d, 210, 250, 210, 58, "Upload PDF")
    task = pill(d, 520, 250, 230, 58, "Tạo DocumentTask")
    cloud = db(d, 590, 95, 70, 70, "Cloudinary")
    parse = chip(d, 850, 225, 180, 58, "LLMs")
    mongo = db(d, 910, 95, 70, 70, "MongoDB")
    ingest = pill(d, 850, 390, 210, 58, "/ingest/articles")
    chunk = pill(d, 1130, 330, 180, 54, "Chunk")
    embed = pill(d, 1130, 425, 180, 54, "Embed")
    chroma = db(d, 1220, 555, 70, 70, "ChromaDB")
    status = pill(d, 520, 580, 260, 56, "WebSocket status")
    arrow(d, (128, 295), mid(upload, "l"))
    arrow(d, mid(upload, "r"), mid(task, "l"))
    arrow(d, mid(task, "t"), (625, 165), "Lưu PDF")
    arrow(d, mid(task, "r"), mid(parse, "l"), "Parse")
    arrow(d, mid(parse, "t"), (945, 165), "Articles")
    arrow(d, mid(parse, "b"), mid(ingest, "t"))
    arrow(d, mid(ingest, "r"), mid(chunk, "l"))
    arrow(d, mid(chunk, "b"), mid(embed, "t"))
    arrow(d, mid(embed, "b"), (1255, 555), "Upsert")
    arrow(d, (1220, 590), mid(status, "r"), "Hoàn tất", curved=True)
    arrow(d, mid(status, "l"), (128, 330), "Progress", curved=True)
    save(img, "hinh_2_9")


def save(img, name):
    img.save(OUT_DIR / f"{name}.png", optimize=True)


def main():
    hinh_2_1()
    hinh_2_4()
    hinh_2_6()
    hinh_2_9()
    print(f"Rendered reference-style previews to {OUT_DIR}")


if __name__ == "__main__":
    main()
