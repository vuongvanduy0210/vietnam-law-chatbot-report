from __future__ import annotations

import argparse
import copy
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

ET.register_namespace("p", P_NS)
ET.register_namespace("a", A_NS)
ET.register_namespace("r", R_NS)

NS = {"p": P_NS, "a": A_NS, "r": R_NS}

SLIDE_W = 13_333_332
SLIDE_H = 7_500_000


@dataclass
class ShapeInfo:
    spid: str
    name: str
    text: str
    x: int
    y: int
    w: int
    h: int
    tag: str
    element: ET.Element


def q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def norm_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def text_of(el: ET.Element) -> str:
    return norm_text(" ".join(t.text or "" for t in el.findall(".//a:t", NS)))


def c_nv_pr(el: ET.Element) -> ET.Element | None:
    for path in (
        ".//p:cNvPr",
    ):
        node = el.find(path, NS)
        if node is not None:
            return node
    return None


def bounds_of(el: ET.Element) -> tuple[int, int, int, int]:
    xfrm = el.find(".//a:xfrm", NS)
    if xfrm is None:
        return (0, 0, 0, 0)
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    x = int(off.get("x", "0")) if off is not None else 0
    y = int(off.get("y", "0")) if off is not None else 0
    w = int(ext.get("cx", "0")) if ext is not None else 0
    h = int(ext.get("cy", "0")) if ext is not None else 0
    return (x, y, w, h)


def collect_shapes(root: ET.Element) -> list[ShapeInfo]:
    sp_tree = root.find(".//p:spTree", NS)
    if sp_tree is None:
        return []
    shapes: list[ShapeInfo] = []
    for child in list(sp_tree):
        if child.tag in {q(P_NS, "nvGrpSpPr"), q(P_NS, "grpSpPr")}:
            continue
        c = c_nv_pr(child)
        if c is None:
            continue
        spid = c.get("id")
        if not spid:
            continue
        x, y, w, h = bounds_of(child)
        shapes.append(
            ShapeInfo(
                spid=spid,
                name=c.get("name", ""),
                text=text_of(child),
                x=x,
                y=y,
                w=w,
                h=h,
                tag=child.tag,
                element=child,
            )
        )
    return shapes


def is_background_or_brand(
    shape: ShapeInfo,
    repeated_texts: set[str],
    previous_texts: set[str],
) -> bool:
    text = shape.text
    area = shape.w * shape.h
    slide_area = SLIDE_W * SLIDE_H

    # Full-slide backgrounds, decorative corner marks, and logo/header chrome.
    if not text and area > slide_area * 0.55 and shape.x < 300_000 and shape.y < 300_000:
        return True
    if not text and shape.x < 900_000 and shape.y > SLIDE_H - 900_000:
        return True
    if not text and shape.x > SLIDE_W - 1_000_000 and shape.y < 900_000:
        return True
    if shape.y < 780_000 and (shape.x < 1_500_000 or not text):
        return True
    if text == "HỌC VIỆN KỸ THUẬT MẬT MÃ":
        return True

    # Keep repeated top-level titles stable only after their first appearance.
    # Example: title 2.2 is animated on slide 8, then held static on slides 9-10.
    if (
        text in repeated_texts
        and text in previous_texts
        and len(text) > 8
        and shape.y < 1_350_000
        and re.match(r"^\d+(\.\d+)*\s*\.?", text)
    ):
        return True

    # Tiny page markers or standalone section numbers are treated as chrome.
    if re.fullmatch(r"\d+", text or "") and shape.y < 1_800_000:
        return True
    if text.strip().upper() in {"MAJOR: INTERIOR DESIGN"}:
        return True

    return False


def all_repeated_adjacent_texts(slide_shapes: dict[int, list[ShapeInfo]]) -> set[str]:
    repeated: set[str] = set()
    for idx in sorted(slide_shapes):
        current = {s.text for s in slide_shapes[idx] if s.text}
        nxt = {s.text for s in slide_shapes.get(idx + 1, []) if s.text}
        repeated |= current & nxt
    return repeated


def force_animate(shape: ShapeInfo, slide_num: int) -> bool:
    if slide_num in {1, 2} and shape.text == "HỌC VIỆN KỸ THUẬT MẬT MÃ":
        return True

    # Slide 2 uses a top-left freeform as the academy logo.
    if (
        slide_num == 2
        and not shape.text
        and shape.tag == q(P_NS, "sp")
        and shape.name.startswith("Freeform")
        and shape.x < 1_500_000
        and shape.y < 800_000
    ):
        return True

    return False


def ctn(tid: int, **attrs: str) -> ET.Element:
    node = ET.Element(q(P_NS, "cTn"), {"id": str(tid), **attrs})
    return node


def cond(delay: str = "0", evt: str | None = None) -> ET.Element:
    attrs = {"delay": delay}
    if evt:
        attrs["evt"] = evt
    return ET.Element(q(P_NS, "cond"), attrs)


def st_cond(delay: str = "0") -> ET.Element:
    st = ET.Element(q(P_NS, "stCondLst"))
    st.append(cond(delay))
    return st


def target(spid: str) -> ET.Element:
    tgt = ET.Element(q(P_NS, "tgtEl"))
    ET.SubElement(tgt, q(P_NS, "spTgt"), {"spid": spid})
    return tgt


def visibility_set(spid: str, value: str, tid: int) -> ET.Element:
    set_el = ET.Element(q(P_NS, "set"))
    cb = ET.SubElement(set_el, q(P_NS, "cBhvr"))
    ctn_el = ctn(tid, dur="1", fill="hold")
    ctn_el.append(st_cond("0"))
    cb.append(ctn_el)
    cb.append(target(spid))
    attrs = ET.SubElement(cb, q(P_NS, "attrNameLst"))
    ET.SubElement(attrs, q(P_NS, "attrName")).text = "style.visibility"
    to = ET.SubElement(set_el, q(P_NS, "to"))
    ET.SubElement(to, q(P_NS, "strVal"), {"val": value})
    return set_el


def slide_left_effect(spid: str, tid: int, dur: int = 980) -> ET.Element:
    anim = ET.Element(
        q(P_NS, "animMotion"),
        {
            "origin": "layout",
            "path": "M 0.08 0 L 0 0 E",
            "pathEditMode": "relative",
        },
    )
    cb = ET.SubElement(anim, q(P_NS, "cBhvr"), {"additive": "base"})
    cb.append(ctn(tid, dur=str(dur)))
    cb.append(target(spid))
    attrs = ET.SubElement(cb, q(P_NS, "attrNameLst"))
    ET.SubElement(attrs, q(P_NS, "attrName")).text = "ppt_x"
    ET.SubElement(attrs, q(P_NS, "attrName")).text = "ppt_y"
    return anim


def wipe_effect(spid: str, tid: int, dur: int = 860) -> ET.Element:
    anim = ET.Element(q(P_NS, "animEffect"), {"transition": "in", "filter": "wipe(left)"})
    cb = ET.SubElement(anim, q(P_NS, "cBhvr"))
    cb.append(ctn(tid, dur=str(dur)))
    cb.append(target(spid))
    return anim


def fade_effect(spid: str, transition: str, tid: int, dur: int = 760) -> ET.Element:
    anim = ET.Element(q(P_NS, "animEffect"), {"transition": transition, "filter": "fade"})
    cb = ET.SubElement(anim, q(P_NS, "cBhvr"))
    cb.append(ctn(tid, dur=str(dur)))
    cb.append(target(spid))
    return anim


def effect_par(
    spid: str,
    transition: str,
    delay: int,
    ids: list[int],
    automatic: bool,
    effect: str,
) -> ET.Element:
    par = ET.Element(q(P_NS, "par"))
    node_type = "withEffect" if automatic else "clickEffect"
    preset_class = "entr" if transition == "in" else "exit"
    outer = ctn(
        ids.pop(0),
        presetID="10",
        presetClass=preset_class,
        presetSubtype="0",
        fill="hold",
        grpId="0",
        nodeType=node_type,
    )
    outer.append(st_cond(str(delay)))
    child_tn = ET.SubElement(outer, q(P_NS, "childTnLst"))
    if transition == "in":
        child_tn.append(visibility_set(spid, "visible", ids.pop(0)))
        if effect == "slide-left":
            child_tn.append(slide_left_effect(spid, ids.pop(0)))
        elif effect == "wipe":
            child_tn.append(wipe_effect(spid, ids.pop(0)))
        else:
            child_tn.append(fade_effect(spid, "in", ids.pop(0)))
    else:
        child_tn.append(fade_effect(spid, "out", ids.pop(0)))
        child_tn.append(visibility_set(spid, "hidden", ids.pop(0)))
    par.append(outer)
    return par


def build_timing(
    spids: list[str],
    *,
    automatic: bool = True,
    include_exit: bool = False,
    effect: str = "wipe",
) -> ET.Element:
    timing = ET.Element(q(P_NS, "timing"))
    tn_lst = ET.SubElement(timing, q(P_NS, "tnLst"))
    root_par = ET.SubElement(tn_lst, q(P_NS, "par"))
    root_ctn = ctn(1, dur="indefinite", restart="never", nodeType="tmRoot")
    root_par.append(root_ctn)
    root_child = ET.SubElement(root_ctn, q(P_NS, "childTnLst"))
    seq = ET.SubElement(root_child, q(P_NS, "seq"), {"concurrent": "1", "nextAc": "seek"})
    main = ctn(2, dur="indefinite", nodeType="mainSeq")
    seq.append(main)
    main_child = ET.SubElement(main, q(P_NS, "childTnLst"))

    wrapper = ET.SubElement(main_child, q(P_NS, "par"))
    wrapper_ctn = ctn(3, fill="hold")
    wrapper_ctn.append(st_cond("0" if automatic else "indefinite"))
    wrapper_child = ET.SubElement(wrapper_ctn, q(P_NS, "childTnLst"))
    wrapper.append(wrapper_ctn)

    next_id = 4
    ids = list(range(next_id, next_id + len(spids) * 6 + 20))

    # In automatic mode the content fades in slowly after the slide appears.
    # This keeps Back/Previous navigation focused on slides instead of rewinding
    # through every animation step.
    for idx, spid in enumerate(spids):
        wrapper_child.append(effect_par(spid, "in", 180 + idx * 170, ids, automatic, effect))

    if include_exit:
        for idx, spid in enumerate(spids):
            wrapper_child.append(effect_par(spid, "out", 900 + idx * 70, ids, automatic, effect))

    if not automatic:
        prev = ET.SubElement(seq, q(P_NS, "prevCondLst"))
        prev_cond = cond("0", "onPrev")
        prev_tgt = ET.SubElement(prev_cond, q(P_NS, "tgtEl"))
        ET.SubElement(prev_tgt, q(P_NS, "sldTgt"))
        prev.append(prev_cond)

        nxt = ET.SubElement(seq, q(P_NS, "nextCondLst"))
        nxt_cond = cond("0", "onNext")
        nxt_tgt = ET.SubElement(nxt_cond, q(P_NS, "tgtEl"))
        ET.SubElement(nxt_tgt, q(P_NS, "sldTgt"))
        nxt.append(nxt_cond)

    bld = ET.SubElement(timing, q(P_NS, "bldLst"))
    for spid in spids:
        ET.SubElement(bld, q(P_NS, "bldP"), {"spid": spid, "grpId": "0"})
    return timing


def slide_index(path: str) -> int:
    m = re.search(r"slide(\d+)\.xml$", path)
    return int(m.group(1)) if m else 0


def patch_slide(
    xml: bytes,
    repeated_texts: set[str],
    previous_texts: set[str],
    slide_num: int,
    *,
    automatic: bool,
    include_exit: bool,
    effect: str,
) -> tuple[bytes, int]:
    root = ET.fromstring(xml)
    for node in list(root):
        if node.tag in {q(P_NS, "timing"), q(P_NS, "transition")}:
            root.remove(node)

    shapes = collect_shapes(root)
    candidates = [
        s
        for s in shapes
        if force_animate(s, slide_num)
        or not is_background_or_brand(s, repeated_texts, previous_texts)
    ]
    candidates.sort(key=lambda s: (s.y // 150_000, s.x))
    spids = [s.spid for s in candidates]
    if spids:
        root.append(build_timing(spids, automatic=automatic, include_exit=include_exit, effect=effect))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), len(spids)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--manual-click",
        action="store_true",
        help="Use click-controlled animation. Default uses automatic fade-in so Back goes to previous slide.",
    )
    parser.add_argument(
        "--include-exit",
        action="store_true",
        help="Also add fade-out effects. Disabled by default to keep slide navigation clean.",
    )
    parser.add_argument(
        "--effect",
        choices=("wipe", "fade", "slide-left"),
        default="wipe",
        help="Entrance animation style. Default is wipe because it is cleaner for technical diagrams.",
    )
    args = parser.parse_args()

    if args.input.resolve() == args.output.resolve():
        raise SystemExit("Refusing to overwrite input file.")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.input) as zin:
        slide_names = sorted(
            [n for n in zin.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
            key=slide_index,
        )
        slide_shapes = {
            slide_index(n): collect_shapes(ET.fromstring(zin.read(n))) for n in slide_names
        }
        repeated_texts = all_repeated_adjacent_texts(slide_shapes)

        report_lines: list[str] = []
        tmp_output = args.output.with_suffix(args.output.suffix + ".tmp")
        with zipfile.ZipFile(tmp_output, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename in slide_names:
                    idx = slide_index(item.filename)
                    previous_texts = {s.text for s in slide_shapes.get(idx - 1, []) if s.text}
                    data, count = patch_slide(
                        data,
                        repeated_texts,
                        previous_texts,
                        idx,
                        automatic=not args.manual_click,
                        include_exit=args.include_exit,
                        effect=args.effect,
                    )
                    report_lines.append(f"{Path(item.filename).stem}: {count} animated shapes")
                zout.writestr(copy.copy(item), data)
        shutil.move(tmp_output, args.output)

    if args.report:
        args.report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
