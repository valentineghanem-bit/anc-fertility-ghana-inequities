"""Standardize Article 1 manuscript figures for journal upload.

Applies a white RGB background to every manuscript figure, sets PNG metadata to
300 dpi, adds cartographic furniture to map figures in a reserved bottom band,
and regenerates PLOS-ready TIFF uploads from the corrected PNG sources.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
FIG_DIR = ROOT / "outputs" / "figures"
PLOS_FIG_DIRS = [
    PROJECT / "submission_package" / "Q1_FINAL_2026-07-12" / "figures",
    PROJECT / "submission_package" / "SPLUS_2026-07-12" / "figures",
]

MAP_SOURCES = {
    "06_figure_06_lisa_map_2022.png",
    "06_figure_C1_anc_choropleth_2022.png",
    "06_figure_C2_tfr_choropleth_2022.png",
    "06_figure_C3_cei_choropleth.png",
    "06_figure_C4_risk_zone_choropleth.png",
    "06_figure_C5_anc_temporal_choropleth.png",
}

MAP_BASE_HEIGHTS = {
    "06_figure_06_lisa_map_2022.png": 1974,
    "06_figure_C1_anc_choropleth_2022.png": 1972,
    "06_figure_C2_tfr_choropleth_2022.png": 1972,
    "06_figure_C3_cei_choropleth.png": 1972,
    "06_figure_C4_risk_zone_choropleth.png": 1979,
    "06_figure_C5_anc_temporal_choropleth.png": 4745,
}

FIGURE_UPLOADS = [
    ("Fig1.tif", "06_figure_01_anc_heatmap.png"),
    ("Fig2.tif", "06_figure_02_anc_trajectories.png"),
    ("Fig3.tif", "06_figure_03_tfr_vs_anc_scatter.png"),
    ("Fig4.tif", "06_figure_09_north_south_gap.png"),
    ("Fig5.tif", "06_figure_11_gini_inequality.png"),
    ("Fig6.tif", "06_figure_04_decision_tree.png"),
    ("Fig7.tif", "06_figure_05_feature_importance_multi.png"),
    ("Fig8.tif", "06_figure_12_partial_dependence_tfr.png"),
    ("Fig9.tif", "06_figure_08_risk_stratification_dashboard.png"),
    ("Fig10.tif", "06_figure_10_adolescent_fertility_trends.png"),
    ("Fig11.tif", "06_figure_07_morans_temporal.png"),
    ("Fig12.tif", "06_figure_06_lisa_map_2022.png"),
    ("Fig13.tif", "06_figure_C4_risk_zone_choropleth.png"),
    ("Fig14.tif", "06_figure_C1_anc_choropleth_2022.png"),
    ("Fig15.tif", "06_figure_C2_tfr_choropleth_2022.png"),
    ("Fig16.tif", "06_figure_C3_cei_choropleth.png"),
    ("Fig17.tif", "06_figure_C5_anc_temporal_choropleth.png"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def flatten_white(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA"):
        background = Image.new("RGB", image.size, "white")
        alpha = image.getchannel("A")
        background.paste(image.convert("RGBA"), mask=alpha)
        return background
    return image.convert("RGB")


def force_near_white_background(image: Image.Image) -> Image.Image:
    """Convert faint off-white/grey plotting backgrounds to pure white."""
    image = image.convert("RGB")
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if r >= 238 and g >= 238 and b >= 238:
                pixels[x, y] = (255, 255, 255)
    return image


def add_cartographic_band(image: Image.Image) -> Image.Image:
    width, height = image.size
    band_h = max(230, int(height * 0.12))
    margin = max(36, int(width * 0.035))
    out = Image.new("RGB", (width, height + band_h), "white")
    out.paste(image, (0, 0))
    draw = ImageDraw.Draw(out)

    body_size = max(22, width // 58)
    bold_size = max(25, width // 50)
    label_size = max(30, width // 48)
    note_size = max(20, width // 70)
    body_font = font(body_size, False)
    body_bold = font(bold_size, True)
    label_font = font(label_size, True)
    note_font = font(note_size, False)
    arrow_h = max(90, width // 28)
    arrow_w = max(18, width // 120)
    arrow_x = margin + max(38, width // 80)
    y0 = height + int(band_h * 0.16)
    draw.line(
        (arrow_x, y0 + arrow_h, arrow_x, y0 + int(arrow_h * 0.28)),
        fill="black",
        width=max(5, width // 420),
    )
    draw.polygon(
        [
            (arrow_x, y0),
            (arrow_x - arrow_w, y0 + int(arrow_h * 0.33)),
            (arrow_x + arrow_w, y0 + int(arrow_h * 0.33)),
        ],
        fill="black",
    )
    draw.text((arrow_x - arrow_w // 2, y0 + arrow_h + 8), "N", fill="black", font=label_font)
    draw.text(
        (arrow_x + max(48, width // 70), y0 + int(arrow_h * 0.25)),
        "Bearing: true north (0 deg)",
        fill="#222222",
        font=body_bold,
    )

    bar_x = int(width * 0.42)
    bar_y = y0 + int(arrow_h * 0.44)
    seg = max(125, int(width * 0.115))
    bar_h = max(18, width // 150)
    draw.rectangle((bar_x, bar_y, bar_x + seg, bar_y + bar_h), fill="black", outline="black")
    draw.rectangle((bar_x + seg, bar_y, bar_x + 2 * seg, bar_y + bar_h), fill="white", outline="black")
    draw.line((bar_x, bar_y, bar_x + 2 * seg, bar_y), fill="black", width=max(2, width // 1200))
    label_y = bar_y + bar_h + max(10, width // 260)
    draw.text((bar_x - 8, label_y), "0", fill="#222222", font=body_font)
    draw.text((bar_x + seg - max(30, width // 115), label_y), "100", fill="#222222", font=body_font)
    draw.text((bar_x + 2 * seg - max(50, width // 82), label_y), "200 km", fill="#222222", font=body_font)
    title_y = max(height + 6, bar_y - bold_size - max(18, width // 170))
    draw.text((bar_x, title_y), "Approximate scale", fill="#222222", font=body_bold)

    note = (
        "Cartographic note: white background; regional/district display geometry; "
        "map orientation and scale are for manuscript interpretation."
    )
    draw.text((margin, height + band_h - max(60, width // 70)), note, fill="#444444", font=note_font)
    return out


def constrain_for_upload(image: Image.Image, max_width: int = 2250) -> Image.Image:
    if image.width <= max_width:
        return image
    ratio = max_width / image.width
    new_size = (max_width, max(1, round(image.height * ratio)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def standardize_pngs() -> None:
    for path in sorted(FIG_DIR.glob("*.png")):
        image = force_near_white_background(flatten_white(Image.open(path)))
        if path.name in MAP_SOURCES:
            base_h = MAP_BASE_HEIGHTS[path.name]
            if image.height > base_h:
                image = image.crop((0, 0, image.width, base_h))
            image = add_cartographic_band(image)
        image.save(path, dpi=(300, 300))
        print(f"PNG standardized: {path.name} {image.size}")


def write_tiff_uploads() -> None:
    for out_dir in PLOS_FIG_DIRS:
        if not out_dir.exists():
            continue
        for tif_name, src_name in FIGURE_UPLOADS:
            src = FIG_DIR / src_name
            if not src.exists():
                raise FileNotFoundError(src)
            image = constrain_for_upload(flatten_white(Image.open(src)))
            image.save(out_dir / tif_name, dpi=(300, 300), compression="tiff_lzw")
            print(f"TIFF written: {out_dir.name}/{tif_name} {image.size}")


def write_manifest() -> None:
    for out_dir in PLOS_FIG_DIRS:
        if not out_dir.exists():
            continue
        rows = []
        for tif_name, src_name in FIGURE_UPLOADS:
            tif = out_dir / tif_name
            if not tif.exists():
                continue
            with Image.open(tif) as image:
                mb = tif.stat().st_size / (1024 * 1024)
                rows.append((tif_name, src_name, f"{image.width} x {image.height}", f"{mb:.2f}"))

        lines = [
            "# PLOS Figure Upload Manifest",
            "",
            "Final figure files are TIFF, RGB, 300 dpi, LZW-compressed, no alpha channel, and use a white background.",
            "Map figures include north arrow/bearing and an approximate 200 km scale bar in a reserved bottom band.",
            "",
            "| File | Source PNG | Pixels | Size MB |",
            "|---|---|---:|---:|",
        ]
        lines.extend(f"| {a} | outputs/figures/{b} | {c} | {d} |" for a, b, c, d in rows)
        (out_dir / "FIGURE_UPLOAD_MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    standardize_pngs()
    write_tiff_uploads()
    write_manifest()


if __name__ == "__main__":
    main()
