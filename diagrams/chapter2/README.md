# Chapter 2 Diagrams

This folder contains Mermaid source files for Chapter 2 figures.

Expected PNG output names in `Bao_Cao/sample_images/`:

- `hinh_2_1.png`
- `hinh_2_2.png`
- `hinh_2_3.png`
- `hinh_2_4.png`
- `hinh_2_5.png`
- `hinh_2_6.png`
- `hinh_2_7.png`
- `hinh_2_8.png`
- `hinh_2_9.png`
- `hinh_2_10.png`

Render all diagrams with:

```bash
cd /Users/duy/Downloads/sourcecode
bash Bao_Cao/diagrams/chapter2/render_chapter2_diagrams.sh
```

The render script requires Mermaid CLI (`mmdc`). If it is missing, install it first:

```bash
npm install -g @mermaid-js/mermaid-cli
```

After rendering, `02_Chuong_2.md` can be converted to DOCX because it already contains `[IMG:hinh_2_X.png]` placeholders.
