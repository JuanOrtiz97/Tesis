from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "figuras" / "mapa-san-cristobal-galapagos-mejorado.png"
target = ROOT / "figuras" / "mapa-san-cristobal-galapagos-isometrico.png"

W, H = 1600, 1100
canvas = Image.new("RGBA", (W, H), (243, 245, 247, 255))
draw = ImageDraw.Draw(canvas, "RGBA")

# Retícula isométrica ligera, inspirada en la referencia, sin competir con el mapa.
for start in range(-800, W + 800, 80):
    draw.line((start, H, start + 900, 0), fill=(176, 192, 208, 55), width=2)
    draw.line((start, 0, start + 900, H), fill=(176, 192, 208, 42), width=2)

font_candidates = [
    Path("C:/Windows/Fonts/SourceSansPro-Semibold.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
]
font_path = next((path for path in font_candidates if path.exists()), None)
title_font = ImageFont.truetype(str(font_path), 46) if font_path else ImageFont.load_default()
label_font = ImageFont.truetype(str(font_path), 27) if font_path else ImageFont.load_default()
small_font = ImageFont.truetype(str(font_path), 22) if font_path else ImageFont.load_default()

draw.text((110, 78), "Contexto territorial", fill=(32, 42, 51, 255), font=title_font)
draw.text((114, 132), "GALÁPAGOS · ECUADOR", fill=(45, 127, 157, 255), font=small_font)

# Tarjeta principal con sombra y volumen, manteniendo el mapa original sin deformarlo.
map_image = Image.open(source).convert("RGBA")
map_image.thumbnail((850, 850), Image.Resampling.LANCZOS)
map_card = Image.new("RGBA", (map_image.width + 42, map_image.height + 42), (255, 255, 255, 255))
map_card.paste(map_image, (21, 21), map_image)
map_card = map_card.rotate(4, resample=Image.Resampling.BICUBIC, expand=True)

shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
shadow_card = Image.new("RGBA", map_card.size, (25, 43, 58, 95))
shadow_card.putalpha(shadow_card.getchannel("A").filter(ImageFilter.GaussianBlur(16)))
shadow_card = shadow_card.rotate(4, resample=Image.Resampling.BICUBIC, expand=True)
shadow.alpha_composite(shadow_card, (285, 193))
canvas.alpha_composite(shadow, (0, 0))
canvas.alpha_composite(map_card, (260, 160))

# Marcador exterior para reforzar la lectura del sitio de estudio.
marker_box = (1120, 755, 1505, 895)
draw.rounded_rectangle(marker_box, radius=18, fill=(255, 255, 255, 245), outline=(112, 128, 160, 255), width=3)
draw.rectangle((1155, 790, 1185, 820), fill=(198, 35, 61, 255))
draw.text((1210, 770), "San Cristóbal", fill=(32, 42, 51, 255), font=label_font)
draw.text((1210, 812), "cantón de estudio", fill=(96, 106, 115, 255), font=small_font)
draw.line((1120, 825, 965, 842), fill=(201, 119, 40, 255), width=4)
draw.ellipse((954, 831, 976, 853), fill=(201, 119, 40, 255))

canvas.convert("RGB").save(target, optimize=True)
print(target)
