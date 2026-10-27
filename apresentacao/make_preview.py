from PIL import Image, ImageDraw
import os, glob
base = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(base, 'out', 'slide-*.png')))
cols, rows = 4, 6
thumb_w, thumb_h = 380, 214
gap = 24
label_h = 22
W = cols * thumb_w + (cols + 1) * gap
H = rows * (thumb_h + label_h) + (rows + 1) * gap
canvas = Image.new('RGB', (W, H), '#F4F1EA')
d = ImageDraw.Draw(canvas)
for i, f in enumerate(files):
    r, c = divmod(i, cols)
    x = gap + c * (thumb_w + gap)
    y = gap + r * (thumb_h + label_h + gap)
    im = Image.open(f).convert('RGB').resize((thumb_w, thumb_h), Image.LANCZOS)
    canvas.paste(im, (x, y))
    d.text((x, y + thumb_h + 5), f'{i+1:02d}', fill='#6E6960')
out = os.path.join(base, 'preview.png')
canvas.save(out)
print(out, canvas.size)
