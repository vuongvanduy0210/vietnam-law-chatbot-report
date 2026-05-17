#!/usr/bin/env python3
"""Generate editable draw.io sources for Chapter 2 conceptual diagrams."""

from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring


OUT_DIR = Path(__file__).parent

BASE = (
    "whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
    "fontFamily=Arial;fontSize=18;fontStyle=1;strokeColor=#111111;"
    "strokeWidth=2.4;fillColor=#ffffff;spacing=10;spacingTop=6;spacingBottom=6;"
)
RECT = "rounded=1;arcSize=10;" + BASE
MUTED = RECT.replace("fillColor=#ffffff", "fillColor=#f2f2f2").replace(
    "strokeColor=#111111", "strokeColor=#555555"
)
PILL = "rounded=1;arcSize=50;" + BASE
ELLIPSE = "ellipse;" + BASE
DIAMOND = (
    "rhombus;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
    "fontFamily=Arial;fontSize=17;fontStyle=1;strokeColor=#111111;"
    "strokeWidth=2.4;fillColor=#ffffff;spacing=8;"
)
DB = (
    "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;"
    "size=18;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=18;"
    "fontStyle=1;strokeColor=#333333;strokeWidth=2.4;fillColor=#f2f2f2;"
    "spacing=10;spacingTop=6;spacingBottom=6;"
)
LANE = (
    "rounded=1;arcSize=6;whiteSpace=wrap;html=1;align=center;verticalAlign=top;"
    "fontFamily=Arial;fontSize=20;fontStyle=1;strokeColor=#111111;"
    "strokeWidth=2.2;fillColor=#f7f7f7;spacingTop=14;"
)
TITLE = (
    "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
    "whiteSpace=wrap;fontFamily=Arial;fontSize=24;fontStyle=1;"
)
EDGE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
    "html=1;strokeColor=#111111;strokeWidth=2.2;endArrow=block;endFill=1;"
    "fontFamily=Arial;fontSize=15;fontStyle=1;"
)
DASHED = EDGE + "dashed=1;"


class Diagram:
    def __init__(self, filename: str, width: int, height: int) -> None:
        self.filename = filename
        self.mxfile = Element(
            "mxfile",
            {
                "host": "app.diagrams.net",
                "modified": "2026-05-14T00:00:00.000Z",
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

    def node(self, node_id: str, value: str, x: int, y: int, w: int, h: int, style: str = RECT) -> None:
        cell = SubElement(
            self.root,
            "mxCell",
            {"id": node_id, "value": value, "style": style, "vertex": "1", "parent": "1"},
        )
        SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})

    def edge(self, edge_id: str, source: str, target: str, value: str = "", dashed: bool = False) -> None:
        cell = SubElement(
            self.root,
            "mxCell",
            {
                "id": edge_id,
                "value": value,
                "style": DASHED if dashed else EDGE,
                "edge": "1",
                "parent": "1",
                "source": source,
                "target": target,
            },
        )
        SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    def write(self) -> None:
        xml = tostring(self.mxfile, encoding="unicode", short_empty_elements=False)
        (OUT_DIR / self.filename).write_text(xml, encoding="utf-8")


def hinh_2_1() -> Diagram:
    d = Diagram("hinh_2_1.drawio", 1500, 950)
    d.node("title", "Kiến trúc tổng quan theo lớp", 450, 35, 600, 45, TITLE)
    d.node("ui", "Giao diện sử dụng<br>Mobile App và Admin Web", 120, 130, 980, 90, LANE)
    d.node("main", "Lớp điều phối nghiệp vụ<br>tiếp nhận yêu cầu, xác thực, lưu lịch sử, điều phối xử lý", 120, 300, 980, 100, LANE)
    d.node("ai", "Lớp tri thức và suy luận<br>truy hồi văn bản, lập luận bằng LLMs, kiểm chứng câu trả lời", 120, 480, 980, 100, LANE)
    d.node("data", "Lớp dữ liệu nền<br>người dùng, hội thoại, văn bản pháp luật, vector tri thức", 120, 660, 980, 100, LANE)
    d.node("ext", "Nguồn hỗ trợ bên ngoài<br>LLMs, tìm kiếm pháp luật,<br>lưu trữ file", 1180, 470, 240, 130, MUTED)

    d.edge("e1", "ui", "main", "tương tác")
    d.edge("e2", "main", "ai", "yêu cầu xử lý")
    d.edge("e3", "ai", "data", "đọc/ghi tri thức")
    d.edge("e4", "ai", "ext", "", dashed=True)
    return d


def hinh_2_2() -> Diagram:
    d = Diagram("hinh_2_2.drawio", 1500, 950)
    d.node("title", "Main Service như trung tâm điều phối", 415, 35, 670, 45, TITLE)
    d.node("core", "Main Service<br>điều phối yêu cầu<br>và chuẩn hóa luồng nghiệp vụ", 555, 390, 390, 130, ELLIPSE)
    d.node("auth", "Xác thực<br>phân quyền user/admin", 120, 230, 300, 90)
    d.node("chat", "Hội thoại<br>lưu lịch sử và streaming", 120, 590, 300, 90)
    d.node("guided", "Tư vấn có hướng dẫn<br>làm rõ nhu cầu trước khi trả lời", 1080, 230, 300, 90)
    d.node("admin", "Quản trị văn bản<br>kiểm tra, xử lý,<br>cập nhật tri thức", 1080, 590, 300, 100)
    d.node("db", "Dữ liệu giao dịch<br>users, messages, tasks", 575, 720, 350, 90, MUTED)
    d.node("rag", "RAG Service<br>truy hồi và suy luận pháp luật", 575, 150, 350, 90, MUTED)

    d.edge("e1", "auth", "core")
    d.edge("e2", "chat", "core")
    d.edge("e3", "guided", "core")
    d.edge("e4", "admin", "core")
    d.edge("e5", "core", "rag")
    d.edge("e6", "core", "db")
    return d


def hinh_2_3() -> Diagram:
    d = Diagram("hinh_2_3.drawio", 1500, 950)
    d.node("title", "RAG Service như bộ máy trả lời có kiểm chứng", 355, 35, 790, 45, TITLE)
    d.node("query", "Câu hỏi pháp luật", 100, 420, 240, 90, PILL)
    d.node("understand", "Hiểu truy vấn<br>xác định ý định và phạm vi", 430, 390, 280, 110)
    d.node("retrieve", "Truy hồi tri thức<br>văn bản nội bộ + nguồn cập nhật", 820, 270, 300, 110)
    d.node("reason", "Suy luận<br>tổng hợp bằng chứng pháp lý", 820, 550, 300, 110)
    d.node("verify", "Kiểm chứng<br>loại bỏ nội dung thiếu căn cứ", 1230, 390, 230, 110)
    d.node("answer", "Câu trả lời<br>kèm nguồn tham chiếu", 1230, 720, 230, 90, MUTED)
    d.node("knowledge", "Kho tri thức<br>MongoDB + ChromaDB", 665, 740, 300, 90, MUTED)

    d.edge("e1", "query", "understand")
    d.edge("e2", "understand", "retrieve")
    d.edge("e3", "retrieve", "reason")
    d.edge("e4", "reason", "verify")
    d.edge("e5", "verify", "answer")
    d.edge("e6", "knowledge", "retrieve", "", dashed=True)
    d.edge("e7", "knowledge", "reason", "", dashed=True)
    return d


def hinh_2_4() -> Diagram:
    d = Diagram("hinh_2_4.drawio", 1450, 980)
    d.node("title", "Phương pháp Agentic RAG bốn bước", 390, 35, 670, 45, TITLE)
    d.node("q", "Input<br>câu hỏi và ngữ cảnh hội thoại", 80, 430, 260, 95, PILL)
    d.node("guard", "1. Guardrail<br>lọc câu hỏi ngoài phạm vi", 430, 390, 240, 130, DIAMOND)
    d.node("analysis", "2. Phân tích truy vấn<br>tách nhu cầu tìm kiếm nội bộ<br>và nguồn cập nhật", 760, 390, 300, 130)
    d.node("agent", "3. Agent hành động<br>lập kế hoạch, gọi công cụ,<br>thu thập bằng chứng", 1150, 280, 240, 150)
    d.node("verify", "4. Kiểm chứng<br>đối chiếu bằng chứng trước khi trả lời", 1150, 570, 240, 130)
    d.node("reject", "Từ chối phù hợp<br>khi không phải câu hỏi pháp luật", 430, 650, 260, 90, MUTED)
    d.node("out", "Output<br>câu trả lời có căn cứ", 760, 730, 300, 90, MUTED)

    d.edge("e1", "q", "guard")
    d.edge("e2", "guard", "analysis", "hợp lệ")
    d.edge("e3", "guard", "reject", "không hợp lệ")
    d.edge("e4", "analysis", "agent")
    d.edge("e5", "agent", "verify")
    d.edge("e6", "verify", "out")
    d.edge("e7", "reject", "out", dashed=True)
    return d


def hinh_2_5() -> Diagram:
    d = Diagram("hinh_2_5.drawio", 1400, 950)
    d.node("title", "Vòng lặp Re-Act trong quá trình suy luận", 360, 35, 680, 45, TITLE)
    d.node("task", "Nhiệm vụ trả lời<br>câu hỏi pháp luật", 545, 120, 310, 85, PILL)
    d.node("think", "Think<br>lập kế hoạch tìm kiếm", 545, 300, 310, 85)
    d.node("act", "Act<br>gọi công cụ truy hồi", 935, 430, 280, 85)
    d.node("observe", "Observe<br>nhận bằng chứng", 545, 600, 310, 85)
    d.node("decide", "Đủ căn cứ?", 205, 430, 250, 130, DIAMOND)
    d.node("answer", "Trả lời<br>tổng hợp và dẫn nguồn", 545, 790, 310, 85, MUTED)
    d.node("tools", "Công cụ<br>tri thức nội bộ + web pháp luật", 965, 650, 300, 95, MUTED)

    d.edge("e1", "task", "think")
    d.edge("e2", "think", "act")
    d.edge("e3", "act", "tools")
    d.edge("e4", "tools", "observe")
    d.edge("e5", "observe", "decide")
    d.edge("e6", "decide", "think", "", dashed=True)
    d.edge("e7", "decide", "answer")
    return d


def hinh_2_6() -> Diagram:
    d = Diagram("hinh_2_6.drawio", 1500, 900)
    d.node("title", "Phương pháp truy hồi tri thức theo tầng lọc", 360, 35, 780, 45, TITLE)
    d.node("q", "Truy vấn đã tối ưu", 80, 395, 240, 85, PILL)
    d.node("search", "Tìm kiếm ngữ nghĩa<br>lấy nhiều ứng viên", 410, 360, 270, 110)
    d.node("rerank", "Xếp hạng lại<br>theo mức phù hợp", 770, 360, 270, 110)
    d.node("time", "Kiểm tra thời điểm<br>ưu tiên văn bản hiện hành", 1130, 360, 290, 110)
    d.node("context", "Ngữ cảnh chọn lọc<br>đưa vào Agent", 610, 675, 300, 90, MUTED)
    d.node("fallback", "Nguồn yếu<br>kích hoạt tìm kiếm web", 1060, 675, 300, 90, MUTED)
    d.node("store", "Kho vector văn bản pháp luật", 500, 155, 500, 80, DB)

    d.edge("e1", "q", "search")
    d.edge("e2", "search", "rerank")
    d.edge("e3", "rerank", "time")
    d.edge("e4", "time", "context", "đạt ngưỡng")
    d.edge("e5", "time", "fallback", "chưa chắc chắn")
    d.edge("e6", "store", "search", "ứng viên", dashed=True)
    return d


def hinh_2_7() -> Diagram:
    d = Diagram("hinh_2_7.drawio", 1450, 900)
    d.node("title", "Xử lý xung đột thời gian của văn bản pháp luật", 325, 35, 800, 45, TITLE)
    d.node("old", "Văn bản cũ<br>có thể đã bị sửa đổi", 150, 260, 280, 100, MUTED)
    d.node("new", "Văn bản mới<br>được ưu tiên khi còn hiệu lực", 150, 560, 280, 100)
    d.node("compare", "Đối chiếu hiệu lực<br>năm ban hành, quan hệ sửa đổi,<br>nguồn pháp luật cập nhật", 560, 390, 330, 140, DIAMOND)
    d.node("current", "Nguồn hiện hành<br>dùng làm căn cứ chính", 1040, 250, 290, 100, MUTED)
    d.node("reference", "Nguồn cũ<br>chỉ dùng để giải thích thay đổi", 1040, 570, 290, 100, MUTED)
    d.node("agent", "Ngữ cảnh đã gắn trạng thái<br>chuyển cho Agent", 550, 725, 350, 85, PILL)

    d.edge("e1", "old", "compare")
    d.edge("e2", "new", "compare")
    d.edge("e3", "compare", "current")
    d.edge("e4", "compare", "reference")
    d.edge("e5", "current", "agent")
    d.edge("e6", "reference", "agent", dashed=True)
    return d


def hinh_2_8() -> Diagram:
    d = Diagram("hinh_2_8.drawio", 1500, 900)
    d.node("title", "Luồng trả lời câu hỏi có hướng dẫn", 405, 35, 690, 45, TITLE)
    d.node("vague", "Câu hỏi ban đầu<br>thiếu thông tin", 80, 390, 260, 95, PILL)
    d.node("clarify", "Bước 1<br>hỏi làm rõ<br>chủ đề, đối tượng, hoàn cảnh", 430, 340, 300, 145)
    d.node("answering", "Bước 2<br>trả lời theo dữ kiện đã chọn", 820, 340, 300, 145)
    d.node("result", "Kết quả<br>câu trả lời sát ngữ cảnh<br>kèm nguồn tham chiếu", 1210, 390, 240, 110, MUTED)
    d.node("user", "Người dùng chọn<br>các phương án làm rõ", 435, 650, 290, 90, MUTED)
    d.node("rag", "RAG có kiểm chứng<br>truy hồi, suy luận, verifier", 825, 650, 290, 90, MUTED)

    d.edge("e1", "vague", "clarify")
    d.edge("e2", "clarify", "user")
    d.edge("e3", "user", "answering")
    d.edge("e4", "answering", "rag")
    d.edge("e5", "rag", "result")
    d.edge("e6", "answering", "result")
    return d


def hinh_2_9() -> Diagram:
    d = Diagram("hinh_2_9.drawio", 1600, 980)
    d.node("title", "Luồng cập nhật tri thức pháp luật từ phía quản trị", 330, 35, 940, 45, TITLE)
    d.node("upload", "Admin tải văn bản mới", 80, 430, 250, 90, PILL)
    d.node("check", "Tiền kiểm<br>định dạng, trùng lặp,<br>nhận diện văn bản", 420, 380, 300, 135)
    d.node("extract", "Trích xuất cấu trúc<br>điều khoản, metadata,<br>nguồn PDF", 810, 380, 300, 135)
    d.node("store", "Lưu tri thức gốc<br>MongoDB articles<br>laws_cache", 1200, 270, 280, 110, DB)
    d.node("vector", "Tạo vector truy hồi<br>chunk + embedding<br>ChromaDB", 1200, 560, 280, 110, DB)
    d.node("publish", "Sẵn sàng phục vụ hỏi đáp", 655, 755, 290, 90, MUTED)
    d.node("rollback", "Cơ chế hoàn tác<br>giữ các kho dữ liệu đồng bộ", 655, 160, 290, 90, MUTED)

    d.edge("e1", "upload", "check")
    d.edge("e2", "check", "extract")
    d.edge("e3", "extract", "store")
    d.edge("e4", "extract", "vector")
    d.edge("e5", "store", "publish")
    d.edge("e6", "vector", "publish")
    d.edge("e7", "check", "rollback", "", dashed=True)
    d.edge("e8", "extract", "rollback", "", dashed=True)
    d.edge("e9", "store", "rollback", "", dashed=True)
    d.edge("e10", "vector", "rollback", "", dashed=True)
    return d


def hinh_2_10() -> Diagram:
    d = Diagram("hinh_2_10.drawio", 1500, 900)
    d.node("title", "Luồng trải nghiệm hỏi đáp theo thời gian thực", 360, 35, 780, 45, TITLE)
    d.node("ask", "Người dùng đặt câu hỏi", 80, 390, 260, 90, PILL)
    d.node("persist", "Ghi nhận hội thoại<br>lưu user message", 430, 350, 280, 110)
    d.node("stream", "Streaming xử lý<br>trả tiến trình từng bước", 810, 350, 280, 110)
    d.node("answer", "Câu trả lời cuối<br>answer + sources", 1190, 390, 240, 90, MUTED)
    d.node("history", "Lịch sử hội thoại<br>lưu user/assistant message", 435, 645, 270, 95, MUTED)
    d.node("suggest", "Câu hỏi gợi ý<br>sinh nền sau khi trả lời", 815, 650, 270, 90, MUTED)
    d.node("rag", "Agentic RAG<br>truy hồi và kiểm chứng", 815, 145, 270, 90, MUTED)

    d.edge("e1", "ask", "persist")
    d.edge("e2", "persist", "stream")
    d.edge("e3", "stream", "answer")
    d.edge("e4", "stream", "rag", "xử lý", dashed=True)
    d.edge("e5", "persist", "history")
    d.edge("e7", "stream", "suggest", "", dashed=True)
    return d


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for build in [
        hinh_2_1,
        hinh_2_2,
        hinh_2_3,
        hinh_2_4,
        hinh_2_5,
        hinh_2_6,
        hinh_2_7,
        hinh_2_8,
        hinh_2_9,
        hinh_2_10,
    ]:
        build().write()


if __name__ == "__main__":
    main()
