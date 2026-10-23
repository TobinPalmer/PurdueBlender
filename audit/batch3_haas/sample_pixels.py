from PIL import Image
im=Image.open('audit/batch3_haas/elevation_east.png').convert('RGB')
for pt in [(700,350),(500,380),(750,420),(250,320),(700,540),(350,500)]:print(pt,im.getpixel(pt))
