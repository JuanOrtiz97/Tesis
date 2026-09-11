from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "figuras" / "mapa-san-cristobal-galapagos.png"
target = ROOT / "figuras" / "mapa-san-cristobal-galapagos-mejorado.png"

image = Image.open(source).convert("RGBA")
# Recorta el margen de océano sin eliminar el mapa de ubicación de Ecuador.
image = image.crop((90, 0, 950, 1060))
draw = ImageDraw.Draw(image, "RGBA")

font_candidates = [
    Path("C:/Windows/Fonts/SourceSansPro-Semibold.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
]
font_path = next((path for path in font_candidates if path.exists()), None)
font = ImageFont.truetype(str(font_path), 27) if font_path else ImageFont.load_default()
small_font = ImageFont.truetype(str(font_path), 21) if font_path else ImageFont.load_default()

# San Cristóbal queda resaltada en rojo en el mapa original; se añade un llamado
# limpio para que la ubicación no dependa únicamente del color.
target_point = (785, 822)
label_box = (445, 735, 735, 815)
draw.rounded_rectangle(label_box, radius=12, fill=(255, 255, 255, 235), outline=(32, 42, 51, 230), width=2)
draw.text((465, 748), "San Cristóbal", fill=(32, 42, 51, 255), font=font)
draw.text((465, 781), "cantón de estudio", fill=(96, 106, 115, 255), font=small_font)
draw.line((735, 775, target_point[0], target_point[1]), fill=(201, 119, 40, 255), width=4)
draw.ellipse((target_point[0] - 7, target_point[1] - 7, target_point[0] + 7, target_point[1] + 7), fill=(201, 119, 40, 255))

# Leyenda mínima para hacer explícita la codificación del mapa.
legend = (28, 965, 315, 1025)
draw.rounded_rectangle(legend, radius=10, fill=(255, 255, 255, 225), outline=(112, 128, 160, 220), width=2)
draw.rectangle((48, 987, 70, 1009), fill=(198, 35, 61, 255))
draw.text((84, 982), "Isla de estudio", fill=(32, 42, 51, 255), font=small_font)

image.save(target, optimize=True)
print(target)
