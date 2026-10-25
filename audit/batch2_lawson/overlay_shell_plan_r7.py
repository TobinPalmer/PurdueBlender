import json
from PIL import Image,ImageDraw
root=r'C:/Users/Tobin/Documents/Blender/PurdueMap/'
im=Image.open(root+'audit/batch2_lawson/plan.png').convert('RGBA');d=ImageDraw.Draw(im,'RGBA')
marker=(-282.5,44.0)
# plan trace frame carried by existing Lawson interior geometry
def px(x):return 327+(x+15.55)/.0944
def py(y):return 88+(42.27-y)/.0944
geo=json.load(open(root+'audit/batch2_lawson/r7_shell_edges.json'))
G=json.load(open(root+'modular/buildings/target_buildings_gis.json'))['LWSN']['world_polygon']
pts=[(px(x-marker[0]),py(y-marker[1])) for x,y in G]
d.line(pts+[pts[0]],fill=(240,20,25,255),width=3)
for key,col in [('LWSN_Exterior_Brick',(20,50,255,255)),('LWSN_Rotunda_Curtain_Glass',(0,180,70,255))]:
 for seg in geo[key]['edges']:
  d.line([(px(x),py(y)) for x,y in seg],fill=col,width=3)
im.save(root+'audit/batch2_lawson/gis_shell_plan_overlay_r7.png')
