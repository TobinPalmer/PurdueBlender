from pathlib import Path
from PIL import Image, ImageDraw

folder = Path('audit/batch2_krannert')
pages = sorted(folder.glob('aia65page-*.jpg'))
cell_w, cell_h, cols = 140, 180, 8
sheet = Image.new('RGB', (cell_w * cols, cell_h * ((len(pages) + cols - 1) // cols)), 'white')
draw = ImageDraw.Draw(sheet)
for i, path in enumerate(pages):
    im = Image.open(path)
    im.thumbnail((130, 155))
    x = (i % cols) * cell_w + 5
    y = (i // cols) * cell_h + 18
    sheet.paste(im, (x, y))
    draw.text((x, y - 16), str(i + 1), fill='black')
out = folder / 'indiana_architect_1965_contact.jpg'
sheet.save(out, quality=88)
print(f'{len(pages)} pages -> {out}')
