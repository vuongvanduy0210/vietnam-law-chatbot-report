#!/usr/bin/env python3
"""Redraw Chapter 3 data design diagrams as editable draw.io files."""

from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring


OUT_DIR = Path(__file__).parent

TITLE = (
    "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
    "whiteSpace=wrap;fontFamily=Arial;fontSize=28;fontStyle=1;"
)
TABLE_BODY = (
    "rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
    "strokeColor=#111111;strokeWidth=2.4;fillColor=#ffffff;"
)
TABLE_HEADER = (
    "rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
    "fontFamily=Arial;fontSize=18;fontStyle=1;fontColor=#ffffff;"
    "strokeColor=#111111;strokeWidth=2.4;fillColor=#111111;"
)
TABLE_TEXT = (
    "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
    "whiteSpace=wrap;fontFamily=Arial;fontSize=15;fontStyle=0;spacing=6;"
)
UML_TABLE = (
    "shape=table;startSize=36;container=1;collapsible=0;childLayout=tableLayout;"
    "fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;"
    "html=1;whiteSpace=wrap;strokeColor=#111111;strokeWidth=2.2;fillColor=#ffffff;"
    "fontFamily=Arial;fontSize=18;"
)
UML_ROW = (
    "shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;"
    "top=0;left=0;bottom=0;right=0;collapsible=0;dropTarget=0;fillColor=#ffffff;"
    "strokeColor=#111111;strokeWidth=1;html=1;"
)
UML_CELL = (
    "shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;"
    "fontFamily=Arial;fontSize=15;align=left;verticalAlign=middle;spacingLeft=8;"
    "html=1;whiteSpace=wrap;strokeColor=none;"
)
PANEL = (
    "rounded=1;arcSize=6;whiteSpace=wrap;html=1;align=center;verticalAlign=top;"
    "fontFamily=Arial;fontSize=17;fontStyle=1;spacing=12;spacingTop=12;"
    "strokeColor=#111111;strokeWidth=2.4;fillColor=#ffffff;"
)
PANEL_HEADER = (
    "rounded=1;arcSize=6;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
    "fontFamily=Arial;fontSize=18;fontStyle=1;fontColor=#ffffff;"
    "strokeColor=#111111;strokeWidth=2.4;fillColor=#111111;"
)
PANEL_TEXT = (
    "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
    "whiteSpace=wrap;fontFamily=Arial;fontSize=16;fontStyle=0;spacing=8;"
)
NOTE = (
    "rounded=1;arcSize=8;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
    "fontFamily=Arial;fontSize=16;fontStyle=1;spacing=10;"
    "strokeColor=#444444;strokeWidth=2;fillColor=#f7f7f7;"
)
DATABASE = (
    "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=20;"
    "align=center;verticalAlign=middle;fontFamily=Arial;fontSize=18;fontStyle=1;"
    "strokeColor=#111111;strokeWidth=2.6;fillColor=#ffffff;spacing=10;"
)
EDGE = (
    "endArrow=block;endFill=1;html=1;rounded=0;strokeColor=#111111;strokeWidth=2.2;"
    "fontFamily=Arial;fontSize=15;fontStyle=1;labelBackgroundColor=#ffffff;"
)
DASHED = EDGE + "dashed=1;"
ASSOC = (
    "endArrow=none;html=1;rounded=0;strokeColor=#111111;strokeWidth=2.1;"
    "fontFamily=Arial;fontSize=15;fontStyle=1;labelBackgroundColor=#ffffff;"
)
ER_ONE_MANY = (
    "startArrow=ERone;endArrow=ERmany;html=1;rounded=0;strokeColor=#111111;"
    "strokeWidth=2.2;fontFamily=Arial;fontSize=15;fontStyle=1;labelBackgroundColor=#ffffff;"
)
ER_ZERO_MANY = (
    "startArrow=ERzeroToOne;endArrow=ERmany;html=1;rounded=0;strokeColor=#111111;"
    "strokeWidth=2.2;fontFamily=Arial;fontSize=15;fontStyle=1;dashed=1;labelBackgroundColor=#ffffff;"
)
LOGICAL_REF = (
    "endArrow=open;endFill=0;html=1;rounded=0;strokeColor=#111111;strokeWidth=2.1;"
    "fontFamily=Arial;fontSize=15;fontStyle=1;dashed=1;labelBackgroundColor=#ffffff;"
)


class Diagram:
    def __init__(self, filename: str, width: int, height: int, title: str) -> None:
        self.filename = filename
        self.width = width
        self.height = height
        self.boxes: dict[str, tuple[int, int, int, int]] = {}
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
        self.node("title", title, 120, 24, width - 240, 56, TITLE)

    def node(self, node_id: str, value: str, x: int, y: int, w: int, h: int, style: str) -> None:
        self.boxes[node_id] = (x, y, w, h)
        cell = SubElement(
            self.root,
            "mxCell",
            {"id": node_id, "value": value, "style": style, "vertex": "1", "parent": "1"},
        )
        SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})

    def table(self, table_id: str, title: str, fields: list[str], x: int, y: int, w: int, h: int) -> None:
        self.node(table_id, "", x, y, w, h, TABLE_BODY)
        self.node(f"{table_id}_header", title, x, y, w, 42, TABLE_HEADER)
        self.node(f"{table_id}_fields", "<br>".join(fields), x + 14, y + 52, w - 28, h - 62, TABLE_TEXT)

    def uml_table(self, table_id: str, title: str, fields: list[str], x: int, y: int, w: int, row_h: int = 30) -> None:
        h = 36 + row_h * len(fields)
        self.node(table_id, title, x, y, w, h, UML_TABLE)
        self.boxes[table_id] = (x, y, w, h)
        for idx, field in enumerate(fields):
            row_id = f"{table_id}_row_{idx}"
            row = SubElement(
                self.root,
                "mxCell",
                {"id": row_id, "value": "", "style": UML_ROW, "vertex": "1", "parent": table_id},
            )
            SubElement(row, "mxGeometry", {"y": str(36 + idx * row_h), "width": str(w), "height": str(row_h), "as": "geometry"})
            cell = SubElement(
                self.root,
                "mxCell",
                {"id": f"{row_id}_cell", "value": field, "style": UML_CELL, "vertex": "1", "parent": row_id},
            )
            SubElement(cell, "mxGeometry", {"width": str(w), "height": str(row_h), "as": "geometry"})

    def panel(self, panel_id: str, title: str, fields: list[str], x: int, y: int, w: int, h: int) -> None:
        self.node(panel_id, "", x, y, w, h, PANEL)
        self.node(f"{panel_id}_header", title, x, y, w, 54, PANEL_HEADER)
        self.node(f"{panel_id}_fields", "<br>".join(fields), x + 18, y + 72, w - 36, h - 84, PANEL_TEXT)

    def center(self, node_id: str) -> tuple[int, int]:
        x, y, w, h = self.boxes[node_id]
        return x + w // 2, y + h // 2

    def side(self, node_id: str, where: str) -> tuple[int, int]:
        x, y, w, h = self.boxes[node_id]
        if where == "left":
            return x, y + h // 2
        if where == "right":
            return x + w, y + h // 2
        if where == "top":
            return x + w // 2, y
        if where == "bottom":
            return x + w // 2, y + h
        raise ValueError(where)

    def edge_points(
        self,
        edge_id: str,
        p1: tuple[int, int],
        p2: tuple[int, int],
        label: str = "",
        style: str = EDGE,
        points: list[tuple[int, int]] | None = None,
    ) -> None:
        cell = SubElement(
            self.root,
            "mxCell",
            {"id": edge_id, "value": label, "style": style, "edge": "1", "parent": "1"},
        )
        geo = SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        if points:
            arr = SubElement(geo, "Array", {"as": "points"})
            for x, y in points:
                SubElement(arr, "mxPoint", {"x": str(x), "y": str(y)})
        SubElement(geo, "mxPoint", {"x": str(p1[0]), "y": str(p1[1]), "as": "sourcePoint"})
        SubElement(geo, "mxPoint", {"x": str(p2[0]), "y": str(p2[1]), "as": "targetPoint"})

    def edge(self, edge_id: str, source: str, source_side: str, target: str, target_side: str, label: str, style: str = EDGE) -> None:
        self.edge_points(edge_id, self.side(source, source_side), self.side(target, target_side), label, style)

    def write(self) -> None:
        (OUT_DIR / self.filename).write_text(
            tostring(self.mxfile, encoding="unicode", short_empty_elements=False),
            encoding="utf-8",
        )


def draw_postgresql_erd() -> None:
    d = Diagram("hinh_3_14.drawio", 1580, 940, "Sơ đồ quan hệ dữ liệu trong PostgreSQL")

    d.uml_table(
        "users",
        "users",
        [
            "<b>PK</b> id : UUID",
            "<b>UQ</b> email : varchar",
            "hashed_password : varchar",
            "full_name : varchar",
            "phone_number : varchar",
            "role : varchar",
            "is_active : boolean",
            "last_login_at : timestamptz",
            "created_at, updated_at",
        ],
        80,
        130,
        340,
        30,
    )
    d.uml_table(
        "conversations",
        "conversations",
        [
            "<b>PK</b> id : UUID",
            "<b>FK</b> user_id → users.id",
            "title : varchar",
            "is_pinned : boolean",
            "is_archived : boolean",
            "message_count : integer",
            "last_message_at : timestamptz",
            "created_at, updated_at",
        ],
        620,
        130,
        360,
        30,
    )
    d.uml_table(
        "messages",
        "messages",
        [
            "<b>PK</b> id : UUID",
            "<b>FK</b> conversation_id → conversations.id",
            "<b>FK</b> question_id → messages.id",
            "role : varchar",
            "content : text",
            "sources : JSONB",
            "metadata : JSONB",
            "created_at : timestamptz",
        ],
        1160,
        130,
        360,
        30,
    )
    d.uml_table(
        "tokens",
        "refresh_tokens",
        [
            "<b>PK</b> id : UUID",
            "<b>FK</b> user_id → users.id",
            "<b>UQ</b> token : varchar",
            "expires_at : timestamptz",
            "is_revoked : boolean",
            "created_at : timestamptz",
        ],
        80,
        590,
        340,
        30,
    )
    d.uml_table(
        "tasks",
        "document_tasks",
        [
            "<b>PK</b> id : UUID",
            "<b>FK</b> user_id → users.id",
            "filename : varchar",
            "file_size_bytes : bigint",
            "status : enum",
            "progress : integer",
            "current_step : varchar",
            "law_id : varchar",
            "article_count : integer",
            "error_message : text",
            "created_at, completed_at",
        ],
        620,
        560,
        390,
        30,
    )
    d.node(
        "legend",
        "Ký hiệu: <b>PK</b> - khóa chính, <b>FK</b> - khóa ngoại, <b>UQ</b> - ràng buộc duy nhất. "
        "Quan hệ sử dụng ký pháp một - nhiều của ERD; quan hệ nét đứt là liên kết tự tham chiếu.",
        1080,
        630,
        410,
        115,
        NOTE,
    )

    d.edge("e_user_conv", "users", "right", "conversations", "left", "owns", ER_ONE_MANY)
    d.edge("e_conv_msg", "conversations", "right", "messages", "left", "contains", ER_ONE_MANY)
    d.edge("e_user_token", "users", "bottom", "tokens", "top", "has", ER_ONE_MANY)
    d.edge("e_user_task", "users", "bottom", "tasks", "left", "creates", ER_ONE_MANY)
    d.edge_points(
        "e_msg_self",
        d.side("messages", "bottom"),
        d.side("messages", "right"),
        "answers question_id",
        ER_ZERO_MANY,
        points=[(1340, 505), (1535, 505), (1535, 245)],
    )
    d.write()


def draw_data_stores() -> None:
    d = Diagram("hinh_3_15.drawio", 1600, 1000, "Sơ đồ liên kết dữ liệu giữa PostgreSQL, MongoDB và ChromaDB")

    d.node("pg_db", "PostgreSQL", 110, 115, 220, 95, DATABASE)
    d.node("mongo_db", "MongoDB", 680, 115, 220, 95, DATABASE)
    d.node("chroma_db", "ChromaDB", 1265, 115, 220, 95, DATABASE)

    d.table(
        "pg_tables",
        "PostgreSQL tables",
        [
            "<b>users</b>: tài khoản, vai trò",
            "<b>conversations</b>: phiên hội thoại",
            "<b>messages</b>: câu hỏi, trả lời, sources",
            "<b>document_tasks</b>: tiến trình upload",
            "<b>refresh_tokens</b>: phiên đăng nhập",
        ],
        55,
        275,
        330,
        230,
    )
    d.table(
        "mongo_articles",
        "articles",
        [
            "<b>PK</b> _id = law_id + article_id",
            "law_id",
            "article_id",
            "title, text",
            "metadata.topics",
            "metadata.keywords",
            "metadata.summary",
            "metadata.year",
            "full_content_search, source_url",
        ],
        610,
        275,
        360,
        305,
    )
    d.table(
        "mongo_cache",
        "laws_cache",
        [
            "<b>PK</b> _id = law_id",
            "law_id",
            "year",
            "article_count",
            "summary",
            "topics",
            "file_hash",
        ],
        610,
        655,
        360,
        205,
    )
    d.table(
        "chroma_collection",
        "vietnamese_law",
        [
            "<b>PK</b> id = law_id_article_id_chunkN",
            "document = title + chunk text",
            "embedding vector",
            "metadata.law_id",
            "metadata.article_id",
            "metadata.chunk_index",
            "metadata.total_chunks",
            "metadata.year",
            "metadata.topics, keywords, summary",
        ],
        1195,
        275,
        360,
        305,
    )
    d.node(
        "legend",
        "Đường liền: liên kết định danh chính giữa các kho dữ liệu. "
        "Đường nét đứt: tham chiếu logic phục vụ truy vấn, hiển thị nguồn và cache danh sách văn bản.",
        1060,
        690,
        405,
        105,
        NOTE,
    )

    d.edge("e_task_article", "pg_tables", "right", "mongo_articles", "left", "law_id", LOGICAL_REF)
    d.edge("e_article_vector", "mongo_articles", "right", "chroma_collection", "left", "law_id + article_id", ER_ONE_MANY)
    d.edge("e_cache_article", "mongo_articles", "bottom", "mongo_cache", "top", "materialized view", LOGICAL_REF)
    d.edge_points(
        "e_sources_vector",
        d.side("pg_tables", "bottom"),
        d.side("chroma_collection", "right"),
        "messages.sources → vector/source",
        LOGICAL_REF,
        points=[(220, 930), (1580, 930), (1580, 430)],
    )
    d.write()


if __name__ == "__main__":
    draw_postgresql_erd()
