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
    band_h = max(190, int(height * 0.085))
    margin = max(36, int(width * 0.035))
    out = Image.new("RGB", (width, height + band_h), "white")
    out.paste(image, (0, 0))
    draw = ImageDraw.Draw(out)

    y0 = height + int(band_h * 0.18)
    arrow_x = margin + 34
    draw.line((arrow_x, y0 + 82, arrow_x, y0 + 22), fill="black", width=max(4, width // 500))
    draw.polygon(
        [(arrow_x, y0), (arrow_x - 16, y0 + 30), (arrow_x + 16, y0 + 30)],
        fill="black",
    )
    draw.text((arrow_x - 8, y0 + 88), "N", fill="black", font=font(28, True))
    draw.text((arrow_x + 42, y0 + 21), "Bearing: true north (0 deg)", fill="#222222", font=font(24, True))

    bar_x = int(width * 0.46)
    bar_y = y0 + 42
    seg = max(100, int(width * 0.11))
    bar_h = 16
    draw.rectangle((bar_x, bar_y, bar_x + seg, bar_y + bar_h), fill="black", outline="black")
    draw.rectangle((bar_x + seg, bar_y, bar_x + 2 * seg, bar_y + bar_h), fill="white", outline="black")
    draw.line((bar_x, bar_y, bar_x + 2 * seg, bar_y), fill="black", width=2)
    draw.text((bar_x - 8, bar_y + 24), "0", fill="#222222", font=font(20))
    draw.text((bar_x + seg - 28, bar_y + 24), "100", fill="#222222", font=font(20))
    draw.text((bar_x + 2 * seg - 38, bar_y + 24), "200 km", fill="#222222", font=font(20))
    draw.text((bar_x, bar_y - 31), "Approximate scale", fill="#222222", font=font(22, True))

    note = (
        "Cartographic note: white background; regional/district display geometry; "
        "map orientation and scale are for manuscript interpretation."
    )
    draw.text((margin, height + band_h - 44), note, fill="#444444", font=font(20))
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
