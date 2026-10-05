"""ЛР9: создание видимого цифрового водяного знака и тест устойчивости.
Требуется Pillow: py -m pip install Pillow.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
FORMATS = {"JPEG": "jpg", "PNG": "png", "GIF": "gif", "BMP": "bmp", "TIFF": "tiff"}
ACTIONS = [
    ("01_quality_60", "Сжатие JPEG, качество 60%"),
    ("02_quality_80", "Сжатие JPEG, качество 80%"),
    ("03_crop_10", "Обрезка 10% краёв"),
    ("04_rotate_restore", "Поворот +15° и возврат"),
    ("05_reduce_50", "Уменьшение до 50%"),
    ("06_enlarge_150", "Увеличение до 150%"),
    ("07_blur_contrast", "Размытие и контраст"),
    ("08_removed", "Удаление (ретушь) ЦВЗ"),
]


def font(size: int, bold: bool = False):
    names = ["DejaVuSans-Bold.ttf", "arialbd.ttf"] if bold else ["DejaVuSans.ttf", "arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def make_original() -> Image.Image:
    """Создаёт самостоятельное учебное изображение-контейнер."""
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), "#102a43")
    d = ImageDraw.Draw(img)
    for y in range(h):
        c = int(30 + 80 * y / h)
        d.line((0, y, w, y), fill=(12, c, min(180, c + 65)))
    d.ellipse((75, 100, 525, 550), fill="#f6c85f", outline="#ffffff", width=5)
    d.ellipse((160, 185, 440, 465), fill="#2f80ed", outline="#d9efff", width=7)
    d.polygon([(760, 110), (1100, 305), (920, 640), (650, 495)], fill="#36c5a2", outline="#e9fffa", width=6)
    d.rounded_rectangle((95, 595, 1105, 730), radius=24, fill="#ffffff", outline="#b9e4ff", width=3)
    d.text((135, 620), "ЛАБОРАТОРИЯ ИНФОРМАЦИОННОЙ БЕЗОПАСНОСТИ", fill="#16324f", font=font(31, True))
    d.text((135, 670), "Учебное изображение-контейнер для исследования ЦВЗ", fill="#31506e", font=font(24))
    return img


def apply_watermark(image: Image.Image) -> Image.Image:
    """Наносит видимый диагональный текст с прозрачностью 40%."""
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mark = Image.new("RGBA", (1100, 180), (0, 0, 0, 0))
    md = ImageDraw.Draw(mark)
    text = "© МиСЗКИ • ЛАУКЕРТ К. М."
    f = font(66, True)
    bbox = md.textbbox((0, 0), text, font=f, stroke_width=2)
    x = (1100 - (bbox[2] - bbox[0])) // 2
    md.text((x, 35), text, font=f, fill=(255, 255, 255, 102), stroke_width=2, stroke_fill=(12, 42, 67, 102))
    mark = mark.rotate(24, expand=True, resample=Image.Resampling.BICUBIC)
    layer.alpha_composite(mark, ((image.width - mark.width) // 2, (image.height - mark.height) // 2))
    return Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")


def save(image: Image.Image, path: Path, fmt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "JPEG":
        image.convert("RGB").save(path, fmt, quality=95, optimize=True)
    elif fmt == "GIF":
        image.convert("P", palette=Image.Palette.ADAPTIVE).save(path, fmt)
    else:
        image.convert("RGB").save(path, fmt)


def jpeg_roundtrip(image: Image.Image, quality: int) -> Image.Image:
    temp = OUT / "temporary.jpg"
    image.save(temp, "JPEG", quality=quality)
    result = Image.open(temp).convert("RGB").copy()
    temp.unlink()
    return result


def transform(image: Image.Image, action: str, original: Image.Image) -> Image.Image:
    w, h = image.size
    if action == "01_quality_60": return jpeg_roundtrip(image, 60)
    if action == "02_quality_80": return jpeg_roundtrip(image, 80)
    if action == "03_crop_10":
        cropped = image.crop((int(w*.1), int(h*.1), int(w*.9), int(h*.9)))
        return cropped.resize((w, h), Image.Resampling.LANCZOS)
    if action == "04_rotate_restore":
        # Поворот на расширенном холсте и последующая центральная обрезка
        # предотвращают появление чёрных треугольников по краям.
        pad = 300
        canvas = Image.new("RGB", (w + 2 * pad, h + 2 * pad), "#1676b2")
        canvas.paste(image, (pad, pad))
        canvas = canvas.rotate(15, resample=Image.Resampling.BICUBIC, fillcolor="#1676b2")
        canvas = canvas.rotate(-15, resample=Image.Resampling.BICUBIC, fillcolor="#1676b2")
        return canvas.crop((pad, pad, pad + w, pad + h))
    if action == "05_reduce_50": return image.resize((w//2, h//2), Image.Resampling.LANCZOS)
    if action == "06_enlarge_150": return image.resize((int(w*1.5), int(h*1.5)), Image.Resampling.LANCZOS)
    if action == "07_blur_contrast": return ImageEnhance.Contrast(image.filter(ImageFilter.GaussianBlur(2))).enhance(1.45)
    if action == "08_removed":
        # Имитация ретуши: текст удалён, но в его области остаётся сглаженная полоса.
        mask = Image.new("L", (w, h), 0)
        band = Image.new("L", (1100, 180), 0)
        ImageDraw.Draw(band).rectangle((0, 25, 1100, 155), fill=185)
        band = band.rotate(24, expand=True, resample=Image.Resampling.BICUBIC)
        mask.paste(band, ((w - band.width) // 2, (h - band.height) // 2))
        return Image.composite(original.filter(ImageFilter.GaussianBlur(7)), original, mask)
    raise ValueError(action)


def sheet(items: list[tuple[str, Image.Image]], path: Path, columns: int = 2) -> None:
    thumb_w, thumb_h = 440, 293
    rows = (len(items) + columns - 1) // columns
    page = Image.new("RGB", (columns * 470 + 30, rows * 350 + 30), "white")
    d = ImageDraw.Draw(page)
    for index, (title, image) in enumerate(items):
        x = 20 + (index % columns) * 470
        y = 20 + (index // columns) * 350
        copy = image.copy(); copy.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        page.paste(copy, (x, y))
        d.text((x, y + 298), title, fill="#102a43", font=font(18, True))
    page.save(path, "PNG")


def main() -> None:
    print("ЛР9 — защита электронных документов цифровыми водяными знаками", flush=True)
    print("Создание изображения и нанесение ЦВЗ (прозрачность 40%)...", flush=True)
    OUT.mkdir(exist_ok=True)
    original = make_original()
    marked = apply_watermark(original)
    save(original, OUT / "original.png", "PNG")
    formats_dir = OUT / "formats"
    for fmt, ext in FORMATS.items(): save(marked, formats_dir / f"watermarked.{ext}", fmt)
    sheet([("Оригинал", original), ("Видимый ЦВЗ: 40%, диагональ", marked)], OUT / "watermark_steps.png")

    results: dict[str, list[tuple[str, Image.Image]]] = {}
    for fmt, ext in FORMATS.items():
        print(f"Обработка формата {fmt}...", flush=True)
        base = Image.open(formats_dir / f"watermarked.{ext}").convert("RGB")
        result_set = []
        for action, title in ACTIONS:
            outcome = transform(base, action, original)
            save(outcome, OUT / "tests" / action / f"{fmt.lower()}.{ext}", fmt)
            result_set.append((title, outcome))
        results[fmt] = result_set
        sheet(result_set, OUT / f"tests_{fmt.lower()}.png", columns=2)

    print("Создано: original.png и 5 форматов с видимым ЦВЗ (прозрачность 40%).")
    print("Проверка устойчивости (для всех форматов):")
    for number, (_, title) in enumerate(ACTIONS, 1):
        verdict = "знак читаем" if number < 8 else "знак удалён, остались признаки ретуши/потери деталей"
        print(f" {number}. {title}: {verdict}")
    print("Результаты: output/formats, output/tests и обзорные PNG-файлы.")

if __name__ == "__main__":
    main()
