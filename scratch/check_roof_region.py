import bpy,os
for f,boxes in [('mccutcheon_hall_roof_close.png',[(400,200,1000,700)]),('niswonger_aviation_tech_roof_close.png',[(400,250,1000,700)])]:
 img=bpy.data.images.load(os.path.abspath('audit/texture_final_two/'+f),check_existing=False); w,h=img.size; p=list(img.pixels); print(f,w,h)
 for x0,y0,x1,y1 in boxes:
  vals=[]
  for y in range(y0,min(y1,h)):
   for x in range(x0,min(x1,w)):
    i=(y*w+x)*4; vals.append(p[i:i+3])
  print([(round(min(v[c] for v in vals),4),round(max(v[c] for v in vals),4),round(sum(v[c] for v in vals)/len(vals),4)) for c in range(3)])
