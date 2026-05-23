from copy import deepcopy
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "Vương Văn Duy_Báo cáo.docx"
CHAPTER4 = ROOT / "Bao_Cao" / "04_Chuong_4.docx"
BACKUP = ROOT / "Vương Văn Duy_Báo cáo_backup_truoc_thay_chuong4.docx"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}
W = NS["w"]
R = NS["r"]
REL_NS = NS["rel"]

IMAGE_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"

STYLE_ID_REMAP = {
    "Tênhìnhvẽ": "Tnhnhv",
    "Tênbảng": "Tnbng",
}


def unzip_docx(path: Path, dest: Path):
    with ZipFile(path, "r") as z:
        z.extractall(dest)


def zip_dir(src_dir: Path, out_path: Path):
    with ZipFile(out_path, "w", ZIP_DEFLATED) as z:
        for path in sorted(src_dir.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(src_dir).as_posix())


def parse_xml(path: Path):
    parser = etree.XMLParser(remove_blank_text=False)
    return etree.parse(str(path), parser)


def paragraph_text(el) -> str:
    return "".join(el.xpath(".//w:t/text()", namespaces=NS)).strip()


def paragraph_style(el) -> str:
    style = el.find(".//w:pPr/w:pStyle", namespaces=NS)
    return style.get(f"{{{W}}}val") if style is not None else ""


def find_chapter_bounds(body):
    start = end = None
    for i, el in enumerate(body):
        if el.tag != f"{{{W}}}p":
            continue
        text = paragraph_text(el)
        style = paragraph_style(el)
        if style == "Heading1" and text.startswith("CHƯƠNG 4"):
            start = i
        elif start is not None and style == "Heading1":
            end = i
            break

    if start is None:
        raise RuntimeError("Không xác định được điểm bắt đầu Chương 4 trong file chính")

    if end is None:
        # Chapter 4 is the last chapter — end at sectPr or end of body
        end = len(body)
        for i in range(len(body) - 1, start, -1):
            if body[i].tag == f"{{{W}}}sectPr":
                end = i
                break

    if end <= start:
        raise RuntimeError("Không xác định được ranh giới Chương 4 trong file chính")
    return start, end


def next_rel_id(rels_root):
    max_id = 0
    for rel in rels_root.findall("rel:Relationship", namespaces=NS):
        rid = rel.get("Id", "")
        if rid.startswith("rId") and rid[3:].isdigit():
            max_id = max(max_id, int(rid[3:]))
    while True:
        max_id += 1
        candidate = f"rId{max_id}"
        if rels_root.find(f"rel:Relationship[@Id='{candidate}']", namespaces=NS) is None:
            return candidate


def relationship_map(rels_root):
    return {rel.get("Id"): rel for rel in rels_root.findall("rel:Relationship", namespaces=NS)}


def add_content_type_if_needed(content_types_root, extension: str, content_type: str):
    extension = extension.lstrip(".")
    existing = content_types_root.find(
        f"{{http://schemas.openxmlformats.org/package/2006/content-types}}Default[@Extension='{extension}']"
    )
    if existing is None:
        node = etree.Element(
            "{http://schemas.openxmlformats.org/package/2006/content-types}Default",
            Extension=extension,
            ContentType=content_type,
        )
        content_types_root.append(node)


def ensure_unique_media_name(media_dir: Path, original_name: str) -> str:
    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    idx = 1
    while True:
        candidate = f"chapter4_{stem}_{idx}{suffix}"
        if not (media_dir / candidate).exists():
            return candidate
        idx += 1


def max_docpr_id(root) -> int:
    max_id = 0
    for node in root.xpath(".//wp:docPr", namespaces=NS):
        val = node.get("id")
        if val and val.isdigit():
            max_id = max(max_id, int(val))
    return max_id


def remap_styles(element):
    for style_node in element.xpath(".//w:pStyle|.//w:tblStyle|.//w:rStyle", namespaces=NS):
        val = style_node.get(f"{{{W}}}val")
        if val in STYLE_ID_REMAP:
            style_node.set(f"{{{W}}}val", STYLE_ID_REMAP[val])


def copy_relationships_for_element(
    element,
    src_dir: Path,
    dst_dir: Path,
    src_rels_by_id: dict,
    dst_rels_root,
    content_types_root,
    rel_cache: dict,
):
    for attr_name in [f"{{{R}}}embed", f"{{{R}}}link", f"{{{R}}}id"]:
        for node in element.xpath(f".//*[@r:{attr_name.split('}')[-1]}]", namespaces=NS):
            old_rid = node.get(attr_name)
            if not old_rid or old_rid not in src_rels_by_id:
                continue

            if old_rid in rel_cache:
                node.set(attr_name, rel_cache[old_rid])
                continue

            src_rel = src_rels_by_id[old_rid]
            rel_type = src_rel.get("Type")
            target = src_rel.get("Target")
            target_mode = src_rel.get("TargetMode")
            new_rid = next_rel_id(dst_rels_root)

            new_rel = etree.Element(f"{{{REL_NS}}}Relationship")
            new_rel.set("Id", new_rid)
            new_rel.set("Type", rel_type)

            if rel_type == IMAGE_REL_TYPE and target and not target.startswith("http"):
                src_target_path = (src_dir / "word" / target).resolve()
                dst_media = dst_dir / "word" / "media"
                dst_media.mkdir(parents=True, exist_ok=True)
                new_name = ensure_unique_media_name(dst_media, Path(target).name)
                copy2(src_target_path, dst_media / new_name)
                new_rel.set("Target", f"media/{new_name}")

                suffix = Path(new_name).suffix.lower().lstrip(".")
                if suffix == "png":
                    add_content_type_if_needed(content_types_root, "png", "image/png")
                elif suffix in {"jpg", "jpeg"}:
                    add_content_type_if_needed(content_types_root, suffix, "image/jpeg")
                elif suffix == "webp":
                    add_content_type_if_needed(content_types_root, "webp", "image/webp")
            else:
                new_rel.set("Target", target)
                if target_mode:
                    new_rel.set("TargetMode", target_mode)

            dst_rels_root.append(new_rel)
            rel_cache[old_rid] = new_rid
            node.set(attr_name, new_rid)


def main():
    if not MAIN.exists():
        raise FileNotFoundError(MAIN)
    if not CHAPTER4.exists():
        raise FileNotFoundError(CHAPTER4)

    if not BACKUP.exists():
        copy2(MAIN, BACKUP)
        print(f"Backup: {BACKUP}")

    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        main_dir = tmp / "main"
        src_dir = tmp / "chapter4"
        unzip_docx(MAIN, main_dir)
        unzip_docx(CHAPTER4, src_dir)

        main_doc_tree = parse_xml(main_dir / "word" / "document.xml")
        src_doc_tree = parse_xml(src_dir / "word" / "document.xml")
        main_rels_tree = parse_xml(main_dir / "word" / "_rels" / "document.xml.rels")
        src_rels_tree = parse_xml(src_dir / "word" / "_rels" / "document.xml.rels")
        content_types_tree = parse_xml(main_dir / "[Content_Types].xml")

        main_body = main_doc_tree.getroot().find("w:body", namespaces=NS)
        src_body = src_doc_tree.getroot().find("w:body", namespaces=NS)
        start, end = find_chapter_bounds(main_body)
        print(f"Chapter 4 spans paragraphs [{start}, {end}) in main document")

        source_elements = [
            deepcopy(el)
            for el in src_body
            if el.tag != f"{{{W}}}sectPr"
        ]

        src_rels_by_id = relationship_map(src_rels_tree.getroot())
        rel_cache = {}
        next_docpr = max_docpr_id(main_doc_tree.getroot())

        for el in source_elements:
            remap_styles(el)
            copy_relationships_for_element(
                el,
                src_dir=src_dir,
                dst_dir=main_dir,
                src_rels_by_id=src_rels_by_id,
                dst_rels_root=main_rels_tree.getroot(),
                content_types_root=content_types_tree.getroot(),
                rel_cache=rel_cache,
            )
            for docpr in el.xpath(".//wp:docPr", namespaces=NS):
                next_docpr += 1
                docpr.set("id", str(next_docpr))

        for el in list(main_body)[start:end]:
            main_body.remove(el)

        for offset, el in enumerate(source_elements):
            main_body.insert(start + offset, el)

        main_doc_tree.write(
            str(main_dir / "word" / "document.xml"),
            xml_declaration=True,
            encoding="UTF-8",
            standalone="yes",
        )
        main_rels_tree.write(
            str(main_dir / "word" / "_rels" / "document.xml.rels"),
            xml_declaration=True,
            encoding="UTF-8",
            standalone="yes",
        )
        content_types_tree.write(
            str(main_dir / "[Content_Types].xml"),
            xml_declaration=True,
            encoding="UTF-8",
            standalone="yes",
        )

        zip_dir(main_dir, MAIN)

    print(f"Updated: {MAIN}")


if __name__ == "__main__":
    main()
