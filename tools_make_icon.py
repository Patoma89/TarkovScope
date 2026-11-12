# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os

repo_root = r'C:\Users\INFORMES1\Desktop\Python\TarkovScope'
ico_path = os.path.join(repo_root, 'ttc.ico')

def make_ttc_icon(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Outer circle (tactical dark matte with gold bezel)
    pad = int(size * 0.04)
    r = size - pad * 2
    
    # Outer gold ring
    d.ellipse([pad, pad, pad + r, pad + r], fill=(12, 16, 24, 255), outline=(212, 184, 134, 255), width=int(size * 0.035))
    
    # Inner dark circular scope lens
    lens_pad = pad + int(size * 0.04)
    lens_r = size - lens_pad * 2
    d.ellipse([lens_pad, lens_pad, lens_pad + lens_r, lens_pad + lens_r], fill=(16, 21, 31, 255), outline=(45, 55, 75, 255), width=int(size * 0.015))
    
    # Crosshairs reticle
    cx, cy = size // 2, size // 2
    accent_gold = (232, 108, 37, 220)  # Orange accent
    gold_soft = (212, 184, 134, 180)
    
    line_w = max(1, int(size * 0.018))
    # Horizontal line with gap in center
    gap = int(size * 0.18)
    d.line([(lens_pad, cy), (cx - gap, cy)], fill=gold_soft, width=line_w)
    d.line([(cx + gap, cy), (lens_pad + lens_r, cy)], fill=gold_soft, width=line_w)
    # Vertical line with gap in center
    d.line([(cx, lens_pad), (cx, cy - gap)], fill=gold_soft, width=line_w)
    d.line([(cx, cy + gap), (cx, lens_pad + lens_r)], fill=gold_soft, width=line_w)
    
    # Rangefinder ticks
    for tick in [-1, 1]:
        tx = cx + tick * int(size * 0.28)
        d.line([(tx, cy - int(size * 0.04)), (tx, cy + int(size * 0.04))], fill=gold_soft, width=line_w)
        ty = cy + tick * int(size * 0.28)
        d.line([(cx - int(size * 0.04), ty), (cx + int(size * 0.04), ty)], fill=gold_soft, width=line_w)

    # Text TTC in center
    try:
        font = ImageFont.truetype("segoeuib.ttf", int(size * 0.28))
    except Exception:
        font = ImageFont.load_default()
        
    text = "TTC"
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Text shadow
    d.text((cx - tw // 2 + 2, cy - th // 2 - int(size*0.03) + 2), text, fill=(5, 7, 10, 240), font=font)
    # Text fill
    d.text((cx - tw // 2, cy - th // 2 - int(size*0.03)), text, fill=(248, 250, 252, 255), font=font)
    
    return img

sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
images = [make_ttc_icon(s[0]) for s in sizes]

images[0].save(ico_path, format="ICO", sizes=sizes)
print(f"[OK] Generado {ico_path} con {len(sizes)} resoluciones.")
