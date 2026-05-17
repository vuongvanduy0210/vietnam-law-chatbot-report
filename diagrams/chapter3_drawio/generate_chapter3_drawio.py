#!/usr/bin/env python3
"""Generate clean, editable draw.io sources for Chapter 3 diagrams."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring


OUT_DIR = Path(__file__).parent

TITLE = (
    "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
    "whiteSpace=wrap;fontFamily=Arial;fontSize=24;fontStyle=1;"
)
BASE_TEXT = (
    "whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
    "fontFamily=Arial;fontSize=18;fontStyle=1;spacing=10;spacingTop=6;spacingBottom=6;"
)
USECASE = "ellipse;" + BASE_TEXT + "strokeColor=#111111;strokeWidth=2.4;fillColor=#ffffff;"
RECT = "rounded=1;arcSize=10;" + BASE_TEXT + "strokeColor=#111111;strokeWidth=2.4;fillColor=#ffffff;"
MUTED = "rounded=1;arcSize=10;" + BASE_TEXT + "strokeColor=#555555;strokeWidth=2.4;fillColor=#f2f2f2;"
DB = (
    "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=18;"
    "align=center;verticalAlign=middle;fontFamily=Arial;fontSize=18;fontStyle=1;"
    "strokeColor=#333333;strokeWidth=2.4;fillColor=#f2f2f2;spacing=10;spacingTop=8;spacingBottom=8;"
)
ACTOR = (
    "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;"
    "fontFamily=Arial;fontSize=18;fontStyle=1;strokeColor=#111111;strokeWidth=2.4;fillColor=#ffffff;"
)
BOUNDARY = (
    "rounded=1;arcSize=4;whiteSpace=wrap;html=1;align=center;verticalAlign=top;"
    "fontFamily=Arial;fontSize=22;fontStyle=1;strokeColor=#111111;strokeWidth=2.2;"
    "fillColor=none;spacingTop=14;"
)
ENTITY = (
    "rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=top;fontFamily=Arial;"
    "fontSize=17;fontStyle=1;strokeColor=#111111;strokeWidth=2.4;fillColor=#f2f2f2;"
    "spacing=12;spacingTop=12;spacingBottom=12;"
)
ASSOC = (
    "endArrow=none;html=1;rounded=0;strokeColor=#111111;strokeWidth=2.0;"
    "fontFamily=Arial;fontSize=15;fontStyle=1;"
)
INCLUDE = (
    "endArrow=open;endFill=0;html=1;rounded=0;strokeColor=#111111;strokeWidth=1.8;"
    "dashed=1;fontFamily=Arial;fontSize=15;fontStyle=1;"
)
ARROW = (
    "endArrow=block;endFill=1;html=1;rounded=0;strokeColor=#111111;strokeWidth=2.1;"
    "fontFamily=Arial;fontSize=14;fontStyle=1;"
)
RETURN = ARROW.replace("strokeWidth=2.1", "strokeWidth=1.8") + "dashed=1;"
LIFELINE = "endArrow=none;html=1;rounded=0;strokeColor=#555555;strokeWidth=1.5;dashed=1;"


@dataclass
class Box:
    x: int
    y: int
    w: int
    h: int

    @property
    def cx(self) -> int:
        return self.x + self.w // 2

    @property
    def cy(self) -> int:
        return self.y + self.h // 2

    @property
    def left(self) -> tuple[int, int]:
        return self.x, self.cy

    @property
    def right(self) -> tuple[int, int]:
        return self.x + self.w, self.cy

    @property
    def top(self) -> tuple[int, int]:
        return self.cx, self.y

    @property
    def bottom(self) -> tuple[int, int]:
        return self.cx, self.y + self.h


class Diagram:
    def __init__(self, filename: str, width: int, height: int, title: str) -> None:
        self.filename = filename
        self.boxes: dict[str, Box] = {}
        self.mxfile = Element(
            "mxfile",
            {
                "host": "app.diagrams.net",
                "modified": "2026-05-17T00:00:00.000Z",
                "agent": "Codex",
                "version": "30.0.1",
                "type": "device",
            },
        )
        name = filename.replace(".drawio", "")
        diagram = SubElement(self.mxfile, "diagram", {"id": name, "name": name})
        model = SubElement(
            diagram,
            "mxGraphModel",
            {
                "dx": "1500",
                "dy": "1100",
                "grid": "1",
                "gridSize": "10",
                "guides": "1",
                "tooltips": "1",
                "connect": "1",
                "arrows": "1",
                "fold": "1",
                "page": "1",
                "pageScale": "1",
                "pageWidth": str(width),
                "pageHeight": str(height),
                "math": "0",
                "shadow": "0",
            },
        )
        self.root = SubElement(model, "root")
        SubElement(self.root, "mxCell", {"id": "0"})
        SubElement(self.root, "mxCell", {"id": "1", "parent": "0"})
        self.node("title", title, 220, 30, width - 440, 48, TITLE)

    def node(self, node_id: str, value: str, x: int, y: int, w: int, h: int, style: str) -> Box:
        self.boxes[node_id] = Box(x, y, w, h)
        cell = SubElement(
            self.root,
            "mxCell",
            {"id": node_id, "value": value, "style": style, "vertex": "1", "parent": "1"},
        )
        SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})
        return self.boxes[node_id]

    def edge_points(self, edge_id: str, p1: tuple[int, int], p2: tuple[int, int], value: str = "", style: str = ASSOC) -> None:
        cell = Element("mxCell", {"id": edge_id, "value": value, "style": style, "edge": "1", "parent": "1"})
        self.root.insert(2, cell)
        geo = SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        SubElement(geo, "mxPoint", {"x": str(p1[0]), "y": str(p1[1]), "as": "sourcePoint"})
        SubElement(geo, "mxPoint", {"x": str(p2[0]), "y": str(p2[1]), "as": "targetPoint"})

    def edge(self, edge_id: str, source: str, target: str, value: str = "", style: str = INCLUDE) -> None:
        cell = Element(
            "mxCell",
            {"id": edge_id, "value": value, "style": style, "edge": "1", "parent": "1", "source": source, "target": target},
        )
        self.root.insert(2, cell)
        SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    def assoc_from_actor(self, edge_id: str, actor_id: str, usecase_id: str, side: str = "left") -> None:
        actor = self.boxes[actor_id]
        usecase = self.boxes[usecase_id]
        start = actor.right if side == "left" else actor.left
        end = usecase.left if side == "left" else usecase.right
        self.edge_points(edge_id, start, end, "", ASSOC)

    def write(self) -> None:
        (OUT_DIR / self.filename).write_text(tostring(self.mxfile, encoding="unicode", short_empty_elements=False), encoding="utf-8")


def actor(d: Diagram, node_id: str, label: str, x: int, y: int) -> None:
    d.node(node_id, label, x, y, 95, 135, ACTOR)


def usecase(d: Diagram, node_id: str, label: str, x: int, y: int, w: int = 260, h: int = 100) -> None:
    d.node(node_id, label, x, y, w, h, USECASE)


def participant(d: Diagram, node_id: str, label: str, x: int, y: int = 125, w: int = 175, h: int = 60, bottom: int = 850) -> int:
    b = d.node(node_id, label, x, y, w, h, RECT)
    d.edge_points(f"life_{node_id}", b.bottom, (b.cx, bottom), "", LIFELINE)
    return b.cx


def message(d: Diagram, edge_id: str, xs: dict[str, int], source: str, target: str, y: int, label: str, style: str = ARROW) -> None:
    d.edge_points(edge_id, (xs[source], y), (xs[target], y), label, style)


def usecase_shell(filename: str, title: str, system: str, width: int = 1600, height: int = 940) -> Diagram:
    d = Diagram(filename, width, height, title)
    d.node("system", system, 270, 115, width - 540, height - 210, BOUNDARY)
    return d


def hinh_3_1() -> Diagram:
    d = usecase_shell("hinh_3_1.drawio", "Usecase tổng quát của hệ thống Vietnam Law Chatbot", "Vietnam Law Chatbot", 1800, 1040)
    actor(d, "user", "Người dùng", 80, 460)
    actor(d, "admin", "Quản trị viên", 1625, 460)
    items = [
        ("auth", "Đăng ký,<br>đăng nhập", 360, 190),
        ("conv", "Quản lý<br>hội thoại", 360, 390),
        ("chat", "Gửi câu hỏi<br>pháp luật", 360, 590),
        ("guided", "Tư vấn<br>có hướng dẫn", 710, 260),
        ("law", "Tra cứu thư viện<br>pháp luật", 710, 460),
        ("ai", "Tìm kiếm AI<br>ngữ nghĩa", 710, 660),
        ("doc", "Quản trị<br>văn bản", 1080, 190),
        ("upload", "Cập nhật văn bản<br>pháp luật", 1080, 390),
        ("track", "Theo dõi tiến trình<br>xử lý tài liệu", 1080, 590),
        ("dash", "Xem dashboard<br>thống kê", 1080, 790),
    ]
    for node_id, label, x, y in items:
        usecase(d, node_id, label, x, y)
    for i, target in enumerate(["auth", "conv", "chat", "guided", "law", "ai"], 1):
        d.assoc_from_actor(f"u{i}", "user", target, "left")
    for i, target in enumerate(["doc", "upload", "track", "dash"], 1):
        d.assoc_from_actor(f"a{i}", "admin", target, "right")
    return d


def hinh_3_2() -> Diagram:
    d = usecase_shell("hinh_3_2.drawio", "Usecase đăng ký, đăng nhập và quản lý tài khoản", "Nhóm xác thực và tài khoản")
    actor(d, "user", "Người dùng", 80, 400)
    for node_id, label, x, y in [
        ("signup", "Đăng ký<br>tài khoản", 420, 210),
        ("login", "Đăng nhập", 770, 210),
        ("refresh", "Làm mới<br>token", 1040, 390),
        ("logout", "Đăng xuất", 420, 570),
        ("profile", "Xem/cập nhật<br>thông tin cá nhân", 770, 570),
        ("password", "Đổi<br>mật khẩu", 600, 390),
    ]:
        usecase(d, node_id, label, x, y)
    for i, target in enumerate(["signup", "login", "logout", "profile", "password"], 1):
        d.assoc_from_actor(f"e{i}", "user", target, "left")
    d.edge("inc1", "login", "refresh", "&lt;&lt;include&gt;&gt;")
    return d


def hinh_3_3() -> Diagram:
    d = usecase_shell("hinh_3_3.drawio", "Usecase quản lý danh sách cuộc trò chuyện", "Quản lý hội thoại")
    actor(d, "user", "Người dùng", 80, 400)
    for node_id, label, x, y in [
        ("new", "Tạo<br>hội thoại", 430, 220),
        ("list", "Xem danh sách<br>hội thoại", 800, 220),
        ("update", "Cập nhật hội thoại<br>đổi tên, ghim, lưu trữ", 430, 440),
        ("delete", "Xóa<br>hội thoại", 800, 440),
        ("search", "Tìm kiếm<br>lịch sử chat", 615, 650),
    ]:
        usecase(d, node_id, label, x, y)
    for i, target in enumerate(["new", "list", "update", "delete", "search"], 1):
        d.assoc_from_actor(f"e{i}", "user", target, "left")
    return d


def hinh_3_4() -> Diagram:
    d = usecase_shell("hinh_3_4.drawio", "Usecase gửi câu hỏi pháp luật", "Hỏi đáp pháp luật")
    actor(d, "user", "Người dùng", 80, 400)
    for node_id, label, x, y in [
        ("input", "Nhập câu hỏi<br>pháp luật", 400, 220),
        ("send", "Gửi tin nhắn<br>qua chat", 720, 220),
        ("ready", "Nhận event<br>ready", 1040, 220),
        ("progress", "Theo dõi tiến trình<br>SSE", 400, 560),
        ("done", "Nhận câu trả lời<br>và nguồn dẫn", 720, 560),
        ("suggest", "Xem câu hỏi<br>gợi ý", 1040, 560),
    ]:
        usecase(d, node_id, label, x, y)
    d.assoc_from_actor("e1", "user", "input", "left")
    for i, (source, target, label) in enumerate([
        ("input", "send", "&lt;&lt;include&gt;&gt;"),
        ("send", "ready", "&lt;&lt;include&gt;&gt;"),
        ("send", "progress", "&lt;&lt;include&gt;&gt;"),
        ("send", "done", "&lt;&lt;include&gt;&gt;"),
        ("done", "suggest", "&lt;&lt;extend&gt;&gt;"),
    ], 1):
        d.edge(f"i{i}", source, target, label)
    return d


def hinh_3_5() -> Diagram:
    d = usecase_shell("hinh_3_5.drawio", "Usecase tư vấn có hướng dẫn", "Tư vấn có hướng dẫn")
    actor(d, "user", "Người dùng", 80, 400)
    for node_id, label, x, y in [
        ("input", "Nhập câu hỏi<br>ban đầu", 420, 220),
        ("clarify", "Nhận câu hỏi<br>làm rõ", 820, 220),
        ("select", "Chọn đáp án<br>ngữ cảnh", 420, 570),
        ("answer", "Nhận câu trả lời<br>có nguồn dẫn", 820, 570),
        ("stream", "Theo dõi tiến trình<br>qua SSE", 620, 395),
    ]:
        usecase(d, node_id, label, x, y)
    d.assoc_from_actor("e1", "user", "input", "left")
    d.assoc_from_actor("e2", "user", "select", "left")
    d.edge("i1", "input", "clarify", "&lt;&lt;include&gt;&gt;")
    d.edge("i2", "select", "answer", "&lt;&lt;include&gt;&gt;")
    d.edge("i3", "answer", "stream", "&lt;&lt;include&gt;&gt;")
    return d


def hinh_3_6() -> Diagram:
    d = usecase_shell("hinh_3_6.drawio", "Usecase tra cứu thư viện pháp luật", "Tra cứu thư viện pháp luật")
    actor(d, "user", "Người dùng", 80, 400)
    for node_id, label, x, y in [
        ("list_laws", "Xem danh sách<br>văn bản", 420, 220),
        ("filter_laws", "Lọc theo năm,<br>chủ đề", 820, 220),
        ("search_laws", "Tìm kiếm theo<br>nội dung", 420, 570),
        ("detail_laws", "Xem chi tiết<br>điều luật", 820, 570),
        ("meta_laws", "Xem topic,<br>năm, keyword", 620, 395),
    ]:
        usecase(d, node_id, label, x, y)
    for i, target in enumerate(["list_laws", "filter_laws", "search_laws", "detail_laws"], 1):
        d.assoc_from_actor(f"e{i}", "user", target, "left")
    d.edge("i1", "list_laws", "meta_laws", "&lt;&lt;include&gt;&gt;")
    return d


def hinh_3_7() -> Diagram:
    d = usecase_shell("hinh_3_7.drawio", "Usecase tìm kiếm AI ngữ nghĩa", "Tìm kiếm AI ngữ nghĩa")
    actor(d, "user", "Người dùng", 80, 400)
    for node_id, label, x, y in [
        ("query", "Nhập truy vấn<br>ngôn ngữ tự nhiên", 380, 220),
        ("search", "Thực hiện<br>tìm kiếm AI", 720, 220),
        ("result", "Xem danh sách<br>điều luật liên quan", 1060, 220),
        ("refine_query", "Điều chỉnh<br>từ khóa tìm kiếm", 380, 570),
        ("view_sources", "Xem nguồn dẫn<br>được hệ thống gợi ý", 720, 570),
        ("detail", "Mở chi tiết<br>điều luật", 1060, 570),
    ]:
        usecase(d, node_id, label, x, y)
    d.assoc_from_actor("e1", "user", "query", "left")
    d.assoc_from_actor("e2", "user", "refine_query", "left")
    for i, (source, target, label) in enumerate([
        ("query", "search", "&lt;&lt;include&gt;&gt;"),
        ("search", "result", "&lt;&lt;include&gt;&gt;"),
        ("refine_query", "search", "&lt;&lt;extend&gt;&gt;"),
        ("result", "view_sources", "&lt;&lt;extend&gt;&gt;"),
        ("result", "detail", "&lt;&lt;extend&gt;&gt;"),
    ], 1):
        d.edge(f"i{i}", source, target, label)
    return d


def hinh_3_8() -> Diagram:
    d = usecase_shell("hinh_3_8.drawio", "Usecase cập nhật văn bản pháp luật", "Cập nhật văn bản pháp luật")
    actor(d, "admin", "Quản trị viên", 80, 400)
    for node_id, label, x, y in [
        ("upload", "Upload PDF<br>văn bản pháp luật", 380, 220),
        ("preview", "Xem trước kết quả<br>trích xuất", 720, 220),
        ("confirm", "Xác nhận<br>cập nhật văn bản", 1060, 220),
        ("edit_meta", "Bổ sung/chỉnh sửa<br>thông tin văn bản", 380, 570),
        ("track", "Theo dõi kết quả<br>xử lý", 720, 570),
        ("cancel", "Hủy yêu cầu<br>cập nhật", 1060, 570),
    ]:
        usecase(d, node_id, label, x, y)
    d.assoc_from_actor("e1", "admin", "upload", "left")
    d.assoc_from_actor("e2", "admin", "edit_meta", "left")
    d.assoc_from_actor("e3", "admin", "cancel", "left")
    d.edge("i1", "upload", "preview", "&lt;&lt;include&gt;&gt;")
    d.edge("i2", "preview", "confirm", "&lt;&lt;include&gt;&gt;")
    d.edge("i3", "edit_meta", "preview", "&lt;&lt;extend&gt;&gt;")
    d.edge("i4", "confirm", "track", "&lt;&lt;include&gt;&gt;")
    return d


def hinh_3_9() -> Diagram:
    d = usecase_shell("hinh_3_9.drawio", "Usecase theo dõi tiến trình xử lý tài liệu", "Theo dõi xử lý tài liệu", height=1060)
    actor(d, "admin", "Quản trị viên", 80, 400)
    for node_id, label, x, y in [
        ("list", "Xem danh sách<br>task xử lý", 380, 210),
        ("progress", "Theo dõi<br>tiến trình task", 720, 210),
        ("status", "Xem trạng thái<br>hoàn tất/thất bại", 1060, 210),
        ("cancel", "Hủy task<br>đang chạy", 380, 530),
        ("error", "Xem chi tiết<br>lỗi xử lý", 720, 530),
        ("dash", "Xem dashboard<br>thống kê", 1060, 530),
        ("delete", "Xóa log<br>task", 720, 745),
    ]:
        usecase(d, node_id, label, x, y)
    for i, target in enumerate(["list", "cancel", "delete", "dash"], 1):
        d.assoc_from_actor(f"e{i}", "admin", target, "left")
    d.edge("i1", "list", "progress", "&lt;&lt;include&gt;&gt;")
    d.edge("i2", "progress", "status", "&lt;&lt;include&gt;&gt;")
    d.edge("i3", "status", "error", "&lt;&lt;extend&gt;&gt;")
    return d


def hinh_3_10() -> Diagram:
    d = Diagram("hinh_3_10.drawio", 1850, 950, "Biểu đồ tuần tự luồng gửi câu hỏi pháp luật")
    xs = {
        "mobile": participant(d, "mobile", "Mobile App", 80, bottom=890),
        "main": participant(d, "main", "Main Service", 380, bottom=890),
        "pg": participant(d, "pg", "PostgreSQL", 680, bottom=890),
        "rag": participant(d, "rag", "RAG Service", 980, bottom=890),
        "chroma": participant(d, "chroma", "ChromaDB", 1280, bottom=890),
        "mongo": participant(d, "mongo", "MongoDB", 1580, bottom=890),
    }
    steps = [
        ("s1", "mobile", "main", 235, "POST /chat/messages/stream", ARROW),
        ("s2", "main", "pg", 290, "tạo/lấy conversation", ARROW),
        ("s3", "main", "pg", 345, "lưu user message", ARROW),
        ("s4", "main", "mobile", 400, "event ready", RETURN),
        ("s5", "main", "rag", 455, "POST /rag/agent-search/stream", ARROW),
        ("s6", "rag", "main", 510, "event progress(validate/analyze)", RETURN),
        ("s7", "main", "mobile", 565, "event progress", RETURN),
        ("s8", "rag", "chroma", 620, "truy hồi vector chunks", ARROW),
        ("s9", "rag", "mongo", 675, "đối chiếu metadata/nội dung nguồn", ARROW),
        ("s10", "rag", "main", 745, "event done(answer, sources)", RETURN),
        ("s11", "main", "pg", 800, "lưu assistant message", ARROW),
        ("s12", "main", "mobile", 855, "event done", RETURN),
    ]
    for edge_id, source, target, y, label, style in steps:
        message(d, edge_id, xs, source, target, y, label, style)
    return d


def hinh_3_11() -> Diagram:
    d = Diagram("hinh_3_11.drawio", 1500, 900, "Biểu đồ tuần tự luồng tư vấn có hướng dẫn")
    xs = {
        "mobile": participant(d, "mobile", "Mobile App", 100),
        "main": participant(d, "main", "Main Service", 430),
        "rag": participant(d, "rag", "RAG Service", 760),
        "chroma": participant(d, "chroma", "ChromaDB", 1090),
    }
    steps = [
        ("s1", "mobile", "main", 240, "POST /guided/clarify", ARROW),
        ("s2", "main", "rag", 310, "POST /rag/guided-clarify", ARROW),
        ("s3", "rag", "main", 380, "status, topic, questions", RETURN),
        ("s4", "main", "mobile", 450, "câu hỏi làm rõ", RETURN),
        ("s5", "mobile", "main", 540, "POST /guided/answer/stream", ARROW),
        ("s6", "main", "rag", 610, "POST /rag/guided-answer/stream", ARROW),
        ("s7", "rag", "chroma", 680, "truy hồi nguồn phù hợp", ARROW),
        ("s8", "rag", "main", 750, "event done(answer, sources)", RETURN),
        ("s9", "main", "mobile", 820, "event done", RETURN),
    ]
    for edge_id, source, target, y, label, style in steps:
        message(d, edge_id, xs, source, target, y, label, style)
    return d


def hinh_3_12() -> Diagram:
    d = Diagram("hinh_3_12.drawio", 1650, 900, "Biểu đồ tuần tự luồng tra cứu văn bản pháp luật")
    xs = {
        "mobile": participant(d, "mobile", "Mobile App", 90),
        "main": participant(d, "main", "Main Service", 390),
        "mongo": participant(d, "mongo", "MongoDB", 690),
        "rag": participant(d, "rag", "RAG Service", 990),
        "chroma": participant(d, "chroma", "ChromaDB", 1290),
    }
    steps = [
        ("s1", "mobile", "main", 240, "GET /laws?q/year/topics", ARROW),
        ("s2", "main", "mongo", 310, "aggregation group by law_id", ARROW),
        ("s3", "mongo", "main", 380, "danh sách văn bản", RETURN),
        ("s4", "main", "mobile", 450, "items, total, page", RETURN),
        ("s5", "mobile", "main", 540, "POST /laws/ai-search", ARROW),
        ("s6", "main", "rag", 610, "POST /rag/semantic-search", ARROW),
        ("s7", "rag", "chroma", 680, "vector search + rerank", ARROW),
        ("s8", "chroma", "rag", 750, "sources", RETURN),
        ("s9", "rag", "main", 820, "semantic search results", RETURN),
    ]
    for edge_id, source, target, y, label, style in steps:
        message(d, edge_id, xs, source, target, y, label, style)
    return d


def hinh_3_13() -> Diagram:
    d = Diagram("hinh_3_13.drawio", 1900, 1080, "Biểu đồ tuần tự luồng cập nhật văn bản pháp luật")
    xs = {
        "admin": participant(d, "admin", "Admin Web", 80, bottom=990),
        "main": participant(d, "main", "Main Service", 370, bottom=990),
        "pg": participant(d, "pg", "PostgreSQL", 660, bottom=990),
        "mongo": participant(d, "mongo", "MongoDB", 950, bottom=990),
        "rag": participant(d, "rag", "RAG Service", 1240, bottom=990),
        "chroma": participant(d, "chroma", "ChromaDB", 1530, bottom=990),
    }
    steps = [
        ("s1", "admin", "main", 235, "POST /documents/upload-v2", ARROW),
        ("s2", "main", "pg", 290, "tạo document_tasks", ARROW),
        ("s3", "main", "admin", 345, "WebSocket UPLOAD_PROGRESS", RETURN),
        ("s4", "main", "main", 400, "kiểm tra file, hash, law_id", ARROW),
        ("s5", "main", "main", 455, "OCR + parse + validate", ARROW),
        ("s6", "main", "mongo", 510, "lưu articles + laws_cache", ARROW),
        ("s7", "main", "rag", 565, "POST /ingest/articles", ARROW),
        ("s8", "rag", "chroma", 620, "chunk, embedding, insert", ARROW),
        ("s9", "chroma", "rag", 675, "success", RETURN),
        ("s10", "rag", "main", 730, "ingest result", RETURN),
        ("s11", "main", "pg", 785, "status=completed, progress=100", ARROW),
        ("s12", "main", "admin", 840, "UPLOAD_STATUS completed", RETURN),
    ]
    for edge_id, source, target, y, label, style in steps:
        message(d, edge_id, xs, source, target, y, label, style)
    d.node("alt", "Nhánh lỗi: rollback MongoDB, xóa vector theo law_id và cập nhật task failed", 470, 925, 960, 65, MUTED)
    return d


def hinh_3_14() -> Diagram:
    d = Diagram("hinh_3_14.drawio", 1750, 1050, "Sơ đồ quan hệ dữ liệu trong PostgreSQL")
    d.node("users", "users<br><br>* id : UUID<br>email : varchar<br>hashed_password : varchar<br>full_name : varchar<br>role : varchar<br>is_active : boolean", 90, 150, 320, 250, ENTITY)
    d.node("conversations", "conversations<br><br>* id : UUID<br>user_id : UUID<br>title : varchar<br>is_pinned : boolean<br>is_archived : boolean<br>message_count : integer", 535, 150, 350, 260, ENTITY)
    d.node("messages", "messages<br><br>* id : UUID<br>conversation_id : UUID<br>question_id : UUID<br>role : varchar<br>content : text<br>sources : JSONB<br>metadata : JSONB", 1010, 150, 360, 310, ENTITY)
    d.node("tokens", "refresh_tokens<br><br>* id : UUID<br>user_id : UUID<br>token : varchar<br>expires_at : timestamptz<br>is_revoked : boolean", 150, 660, 330, 230, ENTITY)
    d.node("tasks", "document_tasks<br><br>* id : UUID<br>user_id : UUID<br>filename : varchar<br>status : enum<br>progress : integer<br>law_id : varchar<br>article_count : integer", 620, 660, 360, 290, ENTITY)
    d.node("self_ref", "question_id<br>tham chiếu message gốc", 1190, 615, 250, 80, MUTED)
    d.edge("e1", "users", "conversations", "1 - N", ARROW)
    d.edge("e2", "conversations", "messages", "1 - N", ARROW)
    d.edge("e3", "users", "tokens", "1 - N", ARROW)
    d.edge("e4", "users", "tasks", "1 - N", ARROW)
    d.edge("e5", "messages", "self_ref", "question_id", INCLUDE)
    return d


def hinh_3_15() -> Diagram:
    d = Diagram("hinh_3_15.drawio", 1650, 980, "Liên kết logic giữa PostgreSQL, MongoDB và ChromaDB")
    d.node("pg", "PostgreSQL<br>dữ liệu nghiệp vụ", 120, 160, 360, 90, MUTED)
    d.node("pg_items", "users<br>conversations<br>messages.sources<br>document_tasks.law_id", 150, 330, 300, 175, MUTED)
    d.node("mongo", "MongoDB<br>kho văn bản gốc", 645, 160, 360, 90, MUTED)
    d.node("mongo_items", "VietnamLawDB.articles<br>laws_cache<br>metadata điều luật<br>nội dung đã chuẩn hóa", 675, 330, 300, 175, MUTED)
    d.node("chroma", "ChromaDB<br>kho vector truy hồi", 1170, 160, 360, 90, MUTED)
    d.node("chroma_items", "vietnamese_law<br>chunk_id<br>law_id + article_id<br>embedding vector", 1200, 330, 300, 175, MUTED)
    d.node("chat", "Luồng hỏi đáp<br>đọc lịch sử từ PostgreSQL<br>truy nguồn MongoDB/ChromaDB", 400, 680, 370, 130, RECT)
    d.node("upload", "Luồng cập nhật văn bản<br>ghi văn bản gốc vào MongoDB<br>ghi chunk embedding vào ChromaDB", 900, 670, 420, 150, RECT)
    d.edge("e1", "pg", "pg_items", "", ARROW)
    d.edge("e2", "mongo", "mongo_items", "", ARROW)
    d.edge("e3", "chroma", "chroma_items", "", ARROW)
    d.edge("e4", "pg_items", "mongo_items", "law_id", ARROW)
    d.edge("e5", "mongo_items", "chroma_items", "law_id + article_id", ARROW)
    d.edge("e6", "pg_items", "chat", "", INCLUDE)
    d.edge("e7", "mongo_items", "chat", "", INCLUDE)
    d.edge("e8", "chroma_items", "chat", "", INCLUDE)
    d.edge("e9", "upload", "mongo_items", "", ARROW)
    d.edge("e10", "upload", "chroma_items", "", ARROW)
    return d


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    builders = [
        hinh_3_1,
        hinh_3_2,
        hinh_3_3,
        hinh_3_4,
        hinh_3_5,
        hinh_3_6,
        hinh_3_7,
        hinh_3_8,
        hinh_3_9,
        hinh_3_10,
        hinh_3_11,
        hinh_3_12,
        hinh_3_13,
        hinh_3_14,
        hinh_3_15,
    ]
    diagrams = [build() for build in builders]
    for diagram in diagrams:
        diagram.write()

    bundle = Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": "2026-05-17T00:00:00.000Z",
            "agent": "Codex",
            "version": "30.0.1",
            "type": "device",
        },
    )
    for diagram in diagrams:
        bundle.append(list(diagram.mxfile)[0])
    (OUT_DIR / "chapter3_all.drawio").write_text(tostring(bundle, encoding="unicode", short_empty_elements=False), encoding="utf-8")


if __name__ == "__main__":
    main()
