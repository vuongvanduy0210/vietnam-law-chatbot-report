from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "sample_images" / "chapter2_bw_preview"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BLACK = "#111111"
MID = "#555555"
LIGHT = "#f4f4f4"
PANEL = "#f8f8f8"
WHITE = "#ffffff"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if path and Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


FONT_TITLE = font(42, True)
FONT_H = font(30, True)
FONT = font(25)
FONT_S = font(22)
FONT_XS = font(19)


def new_canvas(title: str, w: int = 1800, h: int = 1100):
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)
    d.text((w // 2, 48), title, anchor="mm", font=FONT_TITLE, fill=BLACK)
    d.line((80, 90, w - 80, 90), fill=BLACK, width=3)
    return img, d


def text_size(d: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont):
    box = d.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap(d: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_w: int):
    lines: list[str] = []
    for raw in text.split("\n"):
        words = raw.split(" ")
        current = ""
        for word in words:
            trial = word if not current else f"{current} {word}"
            if text_size(d, trial, fnt)[0] <= max_w:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def center_text(d, rect, text, fnt=FONT, title_first=True, fill=BLACK):
    x, y, w, h = rect
    lines = wrap(d, text, fnt, w - 34)
    line_h = fnt.size + 8
    total_h = len(lines) * line_h
    cy = y + (h - total_h) / 2 + line_h / 2 - 4
    for idx, line in enumerate(lines):
        use_font = FONT_H if title_first and idx == 0 and len(lines) > 1 else fnt
        d.text((x + w / 2, cy + idx * line_h), line, anchor="mm", font=use_font, fill=fill)


def box(d, x, y, w, h, text, fill=WHITE, outline=BLACK, width=4, radius=22, fnt=FONT):
    d.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=outline, width=width)
    center_text(d, (x, y, w, h), text, fnt=fnt)
    return (x, y, w, h)


def panel(d, x, y, w, h, title):
    d.rounded_rectangle((x, y, x + w, y + h), radius=26, fill=PANEL, outline="#9a9a9a", width=3)
    d.text((x + w / 2, y + 38), title, anchor="mm", font=FONT_H, fill=BLACK)
    return (x, y, w, h)


def diamond(d, cx, cy, w, h, text):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    d.polygon(pts, fill=LIGHT, outline=BLACK)
    d.line(pts + [pts[0]], fill=BLACK, width=4, joint="curve")
    center_text(d, (cx - w / 2 + 20, cy - h / 2 + 20, w - 40, h - 40), text, fnt=FONT_S, title_first=False)
    return (cx - w / 2, cy - h / 2, w, h)


def midpoint(rect, side):
    x, y, w, h = rect
    return {
        "left": (x, y + h / 2),
        "right": (x + w, y + h / 2),
        "top": (x + w / 2, y),
        "bottom": (x + w / 2, y + h),
        "center": (x + w / 2, y + h / 2),
    }[side]


def arrow(d, start, end, label: str | None = None, width=3):
    x1, y1 = start
    x2, y2 = end
    d.line((x1, y1, x2, y2), fill=BLACK, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 17
    p1 = (x2 - size * math.cos(ang - math.pi / 7), y2 - size * math.sin(ang - math.pi / 7))
    p2 = (x2 - size * math.cos(ang + math.pi / 7), y2 - size * math.sin(ang + math.pi / 7))
    d.polygon([(x2, y2), p1, p2], fill=BLACK)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        tw, th = text_size(d, label, FONT_XS)
        d.rounded_rectangle((mx - tw / 2 - 10, my - th / 2 - 8, mx + tw / 2 + 10, my + th / 2 + 8), radius=8, fill=WHITE)
        d.text((mx, my), label, anchor="mm", font=FONT_XS, fill=BLACK)


def poly_arrow(d, pts, label: str | None = None):
    for a, b in zip(pts, pts[1:]):
        d.line((*a, *b), fill=BLACK, width=3)
    arrow(d, pts[-2], pts[-1], label=label)


def save(img, name):
    img.save(OUT_DIR / f"{name}.png", optimize=True)


def hinh_2_1():
    img, d = new_canvas("Hình 2.1. Kiến trúc tổng thể hệ thống")
    panel(d, 80, 140, 390, 720, "Giao diện")
    panel(d, 560, 140, 520, 720, "Dịch vụ")
    panel(d, 1170, 140, 550, 410, "Dữ liệu")
    panel(d, 1170, 610, 550, 310, "Dịch vụ ngoài")

    mobile = box(d, 140, 260, 270, 120, "Mobile App\nKotlin Multiplatform", fnt=FONT_S)
    admin = box(d, 140, 560, 270, 120, "Admin Web\nNext.js", fnt=FONT_S)
    main = box(d, 650, 260, 340, 130, "Main Service :8000\nAuth | Chat | Laws | Upload", fnt=FONT_S)
    rag = box(d, 650, 560, 340, 130, "RAG Service :8001\nAgentic RAG | Ingestion", fnt=FONT_S)

    pg = box(d, 1230, 235, 220, 86, "PostgreSQL", LIGHT, MID, 3, 18, FONT_S)
    mongo = box(d, 1230, 350, 220, 86, "MongoDB", LIGHT, MID, 3, 18, FONT_S)
    chroma = box(d, 1230, 465, 220, 86, "ChromaDB", LIGHT, MID, 3, 18, FONT_S)
    gem = box(d, 1230, 680, 220, 86, "Gemini API", LIGHT, MID, 3, 18, FONT_S)
    search = box(d, 1230, 805, 220, 86, "Tavily\nGoogle", LIGHT, MID, 3, 18, FONT_S)
    cloud = box(d, 1480, 745, 190, 86, "Cloudinary", LIGHT, MID, 3, 18, FONT_S)

    arrow(d, midpoint(mobile, "right"), midpoint(main, "left"), "HTTPS + SSE")
    arrow(d, midpoint(admin, "right"), midpoint(main, "left"), "HTTPS + WebSocket")
    arrow(d, midpoint(main, "bottom"), midpoint(rag, "top"), "Internal API")
    for idx, target in enumerate((pg, mongo, cloud)):
        sx, sy = midpoint(main, "right")
        tx, ty = midpoint(target, "left")
        route_x = 1115 + idx * 12
        poly_arrow(d, [(sx, sy), (route_x, sy), (route_x, ty), (tx, ty)])
    for idx, target in enumerate((chroma, gem, search)):
        sx, sy = midpoint(rag, "right")
        tx, ty = midpoint(target, "left")
        route_x = 1100 + idx * 12
        poly_arrow(d, [(sx, sy), (route_x, sy), (route_x, ty), (tx, ty)])
    save(img, "hinh_2_1")


def hinh_2_2():
    img, d = new_canvas("Hình 2.2. Cấu trúc Main Service")
    headers = ["API Routes", "Business Services", "Repositories", "Databases"]
    xs = [100, 500, 900, 1300]
    for x, h in zip(xs, headers):
        panel(d, x, 150, 330, 760, h)
    routes = [box(d, 155, 250 + i * 115, 220, 72, t, fnt=FONT_S) for i, t in enumerate(["Auth", "Chat", "Documents", "Laws", "Guided"])]
    services = [box(d, 545, 230 + i * 120, 240, 82, t, fnt=FONT_S) for i, t in enumerate(["Auth Service", "Chat Service", "Document Processor", "Law Service", "RAG Client"])]
    repos = [box(d, 945, 260 + i * 135, 240, 84, t, LIGHT, MID, 3, 18, FONT_S) for i, t in enumerate(["User Repo", "Conversation Repo", "Document Task Repo", "Law Repo"])]
    dbs = [box(d, 1360, 340, 210, 95, "PostgreSQL", LIGHT, MID, 3, 18, FONT_S), box(d, 1360, 570, 210, 95, "MongoDB", LIGHT, MID, 3, 18, FONT_S)]
    arrow(d, (430, 530), (500, 530))
    arrow(d, (830, 530), (900, 530))
    arrow(d, (1230, 425), (1360, 390))
    arrow(d, (1230, 650), (1360, 620))
    arrow(d, midpoint(services[1], "right"), midpoint(services[4], "left"), "SSE proxy")
    save(img, "hinh_2_2")


def hinh_2_3():
    img, d = new_canvas("Hình 2.3. Cấu trúc RAG Service")
    panel(d, 90, 170, 360, 700, "API")
    panel(d, 520, 170, 520, 700, "Agent Graph")
    panel(d, 1110, 170, 300, 700, "Tools")
    panel(d, 1480, 170, 240, 700, "Hạ tầng")

    api = [box(d, 150, 270 + i * 120, 240, 76, t, fnt=FONT_S) for i, t in enumerate(["/rag/agent-search", "/rag/search", "/guided/*", "/ingest/articles"])]
    graph = [box(d, 625, 245 + i * 115, 310, 78, t, fnt=FONT_S) for i, t in enumerate(["Guardrail", "Query Analysis", "Agent + Tools", "Verifier"])]
    tools = [box(d, 1150, 360, 220, 90, "Internal Law\nRetrieval", fnt=FONT_S), box(d, 1150, 565, 220, 90, "Web Law\nSearch", fnt=FONT_S)]
    infra = [box(d, 1510, 280 + i * 150, 180, 80, t, LIGHT, MID, 3, 18, FONT_XS) for i, t in enumerate(["Gemini", "Embeddings", "ChromaDB"])]

    arrow(d, (450, 520), (520, 520))
    for a, b in zip(graph, graph[1:]):
        arrow(d, midpoint(a, "bottom"), midpoint(b, "top"))
    arrow(d, midpoint(graph[2], "right"), midpoint(tools[0], "left"))
    arrow(d, midpoint(graph[2], "right"), midpoint(tools[1], "left"))
    arrow(d, midpoint(graph[0], "right"), midpoint(infra[0], "left"))
    arrow(d, midpoint(tools[0], "right"), midpoint(infra[1], "left"))
    arrow(d, midpoint(tools[0], "right"), midpoint(infra[2], "left"))
    save(img, "hinh_2_3")


def hinh_2_4():
    img, d = new_canvas("Hình 2.4. Luồng Agentic RAG")
    start = box(d, 90, 470, 210, 90, "User Query", fnt=FONT_S)
    guard = diamond(d, 430, 515, 210, 150, "Guardrail\nhợp lệ?")
    reject = box(d, 360, 720, 210, 80, "Từ chối", LIGHT, MID, 3, 18, FONT_S)
    qa = box(d, 620, 455, 245, 120, "Query Analysis\nrewrite + context", fnt=FONT_S)
    agent = diamond(d, 1010, 515, 240, 165, "Agent ReAct\ncần tool?")
    internal = box(d, 890, 720, 230, 80, "Internal Law", LIGHT, MID, 3, 18, FONT_S)
    web = box(d, 1150, 720, 210, 80, "Web Search", LIGHT, MID, 3, 18, FONT_S)
    verify = box(d, 1300, 455, 230, 120, "Verifier\nkiểm chứng", fnt=FONT_S)
    end = box(d, 1580, 470, 150, 90, "Answer\n+ citation", fnt=FONT_S)
    arrow(d, midpoint(start, "right"), midpoint(guard, "left"))
    arrow(d, midpoint(guard, "right"), midpoint(qa, "left"), "Có")
    arrow(d, midpoint(guard, "bottom"), midpoint(reject, "top"), "Không")
    arrow(d, midpoint(qa, "right"), midpoint(agent, "left"))
    arrow(d, midpoint(agent, "bottom"), midpoint(internal, "top"), "Nội bộ")
    arrow(d, midpoint(agent, "bottom"), midpoint(web, "top"), "Cập nhật")
    arrow(d, midpoint(internal, "top"), midpoint(agent, "bottom"))
    arrow(d, midpoint(web, "top"), midpoint(agent, "bottom"))
    arrow(d, midpoint(agent, "right"), midpoint(verify, "left"), "Đủ")
    arrow(d, midpoint(verify, "right"), midpoint(end, "left"))
    poly_arrow(d, [midpoint(reject, "right"), (1500, 760), midpoint(end, "bottom")])
    save(img, "hinh_2_4")


def hinh_2_5():
    img, d = new_canvas("Hình 2.5. Vòng lặp ReAct")
    center = box(d, 745, 450, 310, 130, "Agent\nđiều phối vòng lặp", LIGHT, BLACK, 4, 24, FONT_S)
    thought = box(d, 745, 190, 310, 110, "Thought\nlập kế hoạch", fnt=FONT_S)
    action = box(d, 1180, 450, 280, 110, "Action\ngọi tool", fnt=FONT_S)
    observe = box(d, 745, 710, 310, 110, "Observation\nnhận bằng chứng", fnt=FONT_S)
    check = diamond(d, 430, 515, 250, 160, "Đủ bằng chứng?")
    out = box(d, 220, 820, 280, 100, "Generate\nanswer + sources", fnt=FONT_S)
    inp = box(d, 220, 190, 280, 100, "Input\nquery analysis", fnt=FONT_S)
    arrow(d, midpoint(inp, "right"), midpoint(thought, "left"))
    arrow(d, midpoint(thought, "bottom"), midpoint(center, "top"))
    arrow(d, midpoint(center, "right"), midpoint(action, "left"))
    arrow(d, midpoint(action, "bottom"), midpoint(observe, "right"))
    arrow(d, midpoint(observe, "left"), midpoint(check, "bottom"))
    arrow(d, midpoint(check, "top"), midpoint(thought, "left"), "Chưa")
    arrow(d, midpoint(check, "bottom"), midpoint(out, "top"), "Rồi")
    save(img, "hinh_2_5")


def hinh_2_6():
    img, d = new_canvas("Hình 2.6. Two-stage Retrieval")
    panel(d, 90, 160, 1620, 320, "Giai đoạn 1: tìm kiếm vector")
    panel(d, 90, 560, 1620, 320, "Giai đoạn 2: rerank và chọn kết quả")
    row1 = [
        box(d, 160, 285, 250, 100, "Query\nđã viết lại", fnt=FONT_S),
        box(d, 485, 285, 250, 100, "Bi-Encoder\n768 chiều", fnt=FONT_S),
        box(d, 810, 285, 250, 100, "ChromaDB\nTop 60", fnt=FONT_S),
        box(d, 1135, 285, 250, 100, "Candidate\nTop 40", fnt=FONT_S),
    ]
    row2 = [
        box(d, 160, 685, 250, 100, "Cross-Encoder\nrerank", fnt=FONT_S),
        box(d, 485, 685, 250, 100, "Year Boost\nưu tiên mới", fnt=FONT_S),
        box(d, 810, 685, 250, 100, "Conflict Check\nđánh dấu cũ", fnt=FONT_S),
        box(d, 1135, 685, 250, 100, "Top 10\ncho Agent", fnt=FONT_S),
    ]
    decision = diamond(d, 1545, 735, 220, 150, "Score\n>= 0.60?")
    ok = box(d, 1425, 310, 230, 90, "Trả context", LIGHT, MID, 3, 18, FONT_S)
    fallback = box(d, 1425, 905, 230, 90, "Fallback\nweb search", LIGHT, MID, 3, 18, FONT_S)
    for a, b in zip(row1, row1[1:]):
        arrow(d, midpoint(a, "right"), midpoint(b, "left"))
    poly_arrow(d, [midpoint(row1[-1], "bottom"), (1260, 520), (285, 520), midpoint(row2[0], "top")])
    for a, b in zip(row2, row2[1:]):
        arrow(d, midpoint(a, "right"), midpoint(b, "left"))
    arrow(d, midpoint(row2[-1], "right"), midpoint(decision, "left"))
    arrow(d, midpoint(decision, "top"), midpoint(ok, "bottom"), "Có")
    arrow(d, midpoint(decision, "bottom"), midpoint(fallback, "top"), "Không")
    save(img, "hinh_2_6")


def hinh_2_7():
    img, d = new_canvas("Hình 2.7. Xử lý xung đột thời gian")
    a = box(d, 100, 470, 230, 100, "Kết quả\nsau rerank", fnt=FONT_S)
    b = box(d, 420, 470, 260, 100, "Nhóm theo\nloại văn bản + chủ đề", fnt=FONT_S)
    c = diamond(d, 840, 520, 260, 170, "Có nhiều năm\ntrong nhóm?")
    pass_box = box(d, 760, 730, 210, 85, "Giữ nguyên", LIGHT, MID, 3, 18, FONT_S)
    cmp = box(d, 1070, 470, 250, 100, "So sánh\nnăm ban hành", fnt=FONT_S)
    new = box(d, 1400, 350, 250, 90, "Văn bản mới nhất", LIGHT, MID, 3, 18, FONT_S)
    old = box(d, 1400, 600, 250, 90, "Cảnh báo văn bản cũ", LIGHT, MID, 3, 18, FONT_S)
    out = box(d, 1400, 810, 250, 90, "Context\ncho Agent", fnt=FONT_S)
    arrow(d, midpoint(a, "right"), midpoint(b, "left"))
    arrow(d, midpoint(b, "right"), midpoint(c, "left"))
    arrow(d, midpoint(c, "right"), midpoint(cmp, "left"), "Có")
    arrow(d, midpoint(c, "bottom"), midpoint(pass_box, "top"), "Không")
    arrow(d, midpoint(cmp, "right"), midpoint(new, "left"))
    arrow(d, midpoint(cmp, "right"), midpoint(old, "left"))
    arrow(d, midpoint(new, "bottom"), midpoint(out, "top"))
    arrow(d, midpoint(old, "bottom"), midpoint(out, "top"))
    arrow(d, midpoint(pass_box, "right"), midpoint(out, "left"))
    save(img, "hinh_2_7")


def hinh_2_8():
    img, d = new_canvas("Hình 2.8. Luồng tư vấn có hướng dẫn")
    xs = [180, 520, 860, 1200, 1540]
    names = ["Người dùng", "Mobile", "Main Service", "RAG Service", "Gemini"]
    for x, name in zip(xs, names):
        box(d, x - 115, 160, 230, 70, name, LIGHT, BLACK, 3, 18, FONT_S)
        d.line((x, 240, x, 930), fill="#999999", width=3)
    steps = [
        (0, 1, 300, "Nhập câu hỏi"),
        (1, 2, 380, "POST /guided/clarify"),
        (2, 3, 460, "Chuyển tiếp clarify"),
        (3, 4, 540, "Phân tích ngữ cảnh thiếu"),
        (4, 3, 620, "Câu hỏi làm rõ"),
        (3, 2, 700, "Clarify response"),
        (2, 1, 780, "SSE thinking + answer"),
        (1, 0, 860, "Hiển thị đáp án"),
    ]
    for i, j, y, label in steps:
        arrow(d, (xs[i], y), (xs[j], y), label)
    save(img, "hinh_2_8")


def hinh_2_9():
    img, d = new_canvas("Hình 2.9. Quy trình nạp văn bản pháp luật")
    admin = box(d, 90, 490, 230, 110, "Admin Web\nupload PDF", fnt=FONT_S)
    task = box(d, 400, 260, 250, 100, "Tạo\nDocumentTask", fnt=FONT_S)
    cloud = box(d, 760, 180, 240, 90, "Upload\nCloudinary", LIGHT, MID, 3, 18, FONT_S)
    parse = box(d, 760, 380, 240, 100, "Parse &\nstructure", fnt=FONT_S)
    mongo = box(d, 1120, 380, 230, 100, "Lưu\nMongoDB", LIGHT, MID, 3, 18, FONT_S)
    chunk = box(d, 760, 650, 240, 100, "Chunk\narticles", fnt=FONT_S)
    embed = box(d, 1120, 650, 230, 100, "Embed\nbatch", fnt=FONT_S)
    chroma = box(d, 1470, 650, 230, 100, "Upsert\nChromaDB", LIGHT, MID, 3, 18, FONT_S)
    ws = box(d, 1470, 880, 230, 90, "WebSocket\nstatus", fnt=FONT_S)
    arrow(d, midpoint(admin, "right"), midpoint(task, "left"))
    arrow(d, midpoint(task, "right"), midpoint(cloud, "left"))
    arrow(d, midpoint(task, "right"), midpoint(parse, "left"))
    arrow(d, midpoint(parse, "right"), midpoint(mongo, "left"))
    arrow(d, midpoint(mongo, "bottom"), midpoint(chunk, "top"))
    arrow(d, midpoint(chunk, "right"), midpoint(embed, "left"))
    arrow(d, midpoint(embed, "right"), midpoint(chroma, "left"))
    arrow(d, midpoint(chroma, "bottom"), midpoint(ws, "top"))
    poly_arrow(d, [midpoint(ws, "left"), (1000, 925), (520, 925), midpoint(admin, "bottom")])
    save(img, "hinh_2_9")


def hinh_2_10():
    img, d = new_canvas("Hình 2.10. Cơ chế xoay vòng API key")
    req = box(d, 100, 490, 230, 100, "Yêu cầu\nGemini API", fnt=FONT_S)
    pick = box(d, 420, 490, 230, 100, "Chọn\nAPI key", fnt=FONT_S)
    call = box(d, 740, 490, 230, 100, "Gọi\nGemini", fnt=FONT_S)
    resp = diamond(d, 1100, 540, 230, 160, "HTTP\nresponse")
    ok = box(d, 1420, 310, 230, 90, "200\nTrả kết quả", LIGHT, MID, 3, 18, FONT_S)
    rotate = box(d, 1420, 500, 230, 90, "429 / 503\nđổi key", fnt=FONT_S)
    err = box(d, 1420, 700, 230, 90, "400 / 401\nbáo lỗi", LIGHT, MID, 3, 18, FONT_S)
    backoff = box(d, 760, 780, 230, 90, "Hết key\nbackoff", LIGHT, MID, 3, 18, FONT_S)
    arrow(d, midpoint(req, "right"), midpoint(pick, "left"))
    arrow(d, midpoint(pick, "right"), midpoint(call, "left"))
    arrow(d, midpoint(call, "right"), midpoint(resp, "left"))
    arrow(d, midpoint(resp, "right"), midpoint(ok, "left"), "OK")
    arrow(d, midpoint(resp, "right"), midpoint(rotate, "left"), "retry")
    arrow(d, midpoint(resp, "right"), midpoint(err, "left"), "fail")
    poly_arrow(d, [midpoint(rotate, "bottom"), (1535, 880), midpoint(backoff, "right")])
    arrow(d, midpoint(backoff, "top"), midpoint(call, "bottom"))
    arrow(d, midpoint(rotate, "left"), midpoint(call, "right"))
    save(img, "hinh_2_10")


def main():
    for fn in [hinh_2_1, hinh_2_2, hinh_2_3, hinh_2_4, hinh_2_5, hinh_2_6, hinh_2_7, hinh_2_8, hinh_2_9, hinh_2_10]:
        fn()
    print(f"Rendered modern previews to {OUT_DIR}")


if __name__ == "__main__":
    main()
