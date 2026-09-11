from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "figuras" / "mapa-san-cristobal-galapagos-mejorado.png"
target = ROOT / "figuras" / "mapa-san-cristobal-galapagos-isometrico.png"

W, H = 1600, 1100
canvas = Image.new("RGBA", (W, H), (248, 249, 250, 255))
draw = ImageDraw.Draw(canvas, "RGBA")

# Retícula axonométrica muy ligera: solo estructura el plano de fondo.
for start in range(-900, W + 900, 90):
    draw.line((start, H, start + 720, 0), fill=(155, 177, 194, 36), width=2)
    draw.line((start, 0, start + 720, H), fill=(155, 177, 194, 28), width=2)

font_candidates = [
    Path("C:/Windows/Fonts/SourceSansPro-Semibold.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
]
font_path = next((path for path in font_candidates if path.exists()), None)
title_font = ImageFont.truetype(str(font_path), 46) if font_path else ImageFont.load_default()
label_font = ImageFont.truetype(str(font_path), 27) if font_path else ImageFont.load_default()
small_font = ImageFont.truetype(str(font_path), 22) if font_path else ImageFont.load_default()

# Encabezado sobrio, como en un gráfico axonométrico editorial.
draw.text((110, 78), "Contexto territorial", fill=(32, 42, 51, 255), font=title_font)
draw.text((114, 132), "GALÁPAGOS · ECUADOR", fill=(45, 127, 157, 255), font=small_font)

def shear(im, k=-0.16):
    """Inclina una tarjeta rectangular para construir una axonometría sencilla."""
    w, h = im.size
    shift = int(abs(k) * h) + 8
    out = im.transform((w + shift, h), Image.Transform.AFFINE,
                       (1, -k, -shift if k < 0 else 0, 0, 1, 0),
                       resample=Image.Resampling.BICUBIC)
    bbox = out.getbbox()
    return out.crop(bbox) if bbox else out

# Plano principal: mapa plano, sin perspectiva fotográfica, con una pequeña
# extrusión inferior que hace explícita la axonometría.
map_image = Image.open(source).convert("RGBA")
map_image.thumbnail((650, 740), Image.Resampling.LANCZOS)
card = Image.new("RGBA", (map_image.width + 36, map_image.height + 36), (255, 255, 255, 255))
card.paste(map_image, (18, 18), map_image)
top = shear(card)

# Sombra y canto lateral discretos.
shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
shadow_shape = Image.new("RGBA", top.size, (37, 55, 67, 75))
shadow_shape.putalpha(shadow_shape.getchannel("A").filter(ImageFilter.GaussianBlur(18)))
shadow.alpha_composite(shadow_shape, (300, 210))
canvas.alpha_composite(shadow)

map_x, map_y = 280, 175
edge = Image.new("RGBA", top.size, (67, 87, 101, 255))
edge.putalpha(top.getchannel("A"))
canvas.alpha_composite(edge, (map_x + 12, map_y + 28))
canvas.alpha_composite(top, (map_x, map_y))

# Único llamado exterior, reducido para no competir con la información del mapa.
marker_box = (1085, 735, 1495, 860)
draw.rounded_rectangle(marker_box, radius=14, fill=(255, 255, 255, 250), outline=(112, 128, 160, 255), width=3)
draw.rectangle((1120, 775, 1150, 805), fill=(198, 35, 61, 255))
draw.text((1175, 750), "San Cristóbal", fill=(32, 42, 51, 255), font=label_font)
draw.text((1175, 794), "cantón de estudio", fill=(96, 106, 115, 255), font=small_font)
draw.line((1085, 795, 921, 803), fill=(201, 119, 40, 255), width=3)
draw.ellipse((910, 792, 932, 814), fill=(201, 119, 40, 255))

canvas.convert("RGB").save(target, optimize=True)
print(target)
