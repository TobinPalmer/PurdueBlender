import bpy,numpy as np
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\ground_plan.png')
im=bpy.data.images.load(str(p),check_existing=False);w,h=im.size;print('size',w,h)
a=np.asarray(im.pixels[:],dtype=np.float32).reshape((h,w,4))[::-1].copy()
# Save the source raster region corresponding approximately to door leaves 11 and 12.
x0,y0,x1,y1=165,155,325,330
crop=a[y0:y1,x0:x1]
out=bpy.data.images.new('Knoy ground source region doors11-12',width=crop.shape[1]*4,height=crop.shape[0]*4,alpha=True)
out.pixels[:]=np.repeat(np.repeat(crop,4,0),4,1)[::-1].astype(np.float32).reshape(-1).tolist();out.filepath_raw=str(p.parent/'ground_door11_12_source_crop.png');out.file_format='PNG';out.save()
