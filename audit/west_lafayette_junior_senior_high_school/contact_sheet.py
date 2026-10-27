from PIL import Image,ImageDraw
import glob,os
fs=glob.glob('audit/west_lafayette_junior_senior_high_school/sources/kjg_images/*.jpg')
out=Image.new('RGB',(1200,((len(fs)+3)//4)*230),'white')
d=ImageDraw.Draw(out)
for i,f in enumerate(fs):
 im=Image.open(f); im.thumbnail((280,195)); x=(i%4)*300; y=(i//4)*230; out.paste(im,(x,y)); d.text((x,y+198),os.path.basename(f)[:10],fill='black')
out.save('audit/west_lafayette_junior_senior_high_school/sources/kjg_contact_sheet.jpg')
