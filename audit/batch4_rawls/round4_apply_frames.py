import bpy,os,json
from mathutils import Vector
p=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=p)
g=bpy.data.objects['RAWL_North_Windows_Glass'];f=bpy.data.objects['RAWL_North_Windows_BronzeMullions'];inv=f.matrix_world.inverted();verts=[];faces=[]
def y_at(pts,x):
 xa,xb=pts[0].x,pts[1].x;ya,yb=pts[0].y,pts[1].y
 return ya+(x-xa)*(yb-ya)/(xb-xa)
def box(x0,x1,z0,z1,pts):
 # The thin frame sits just outside the pane and follows its measured facade slope.
 base=len(verts);front=.02;depth=.04
 for yoff in (front,front-depth):
  for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]:verts.append(tuple(inv@Vector((x,y_at(pts,x)+yoff,z))))
 faces.extend([(base+0,base+1,base+2,base+3),(base+7,base+6,base+5,base+4)])
 for i in range(4):faces.append((base+i,base+i+4,base+(i+1)%4+4,base+(i+1)%4))
for poly in g.data.polygons:
 pts=[g.matrix_world@g.data.vertices[i].co for i in poly.vertices]
 x0=min(v.x for v in pts);x1=max(v.x for v in pts);z0=min(v.z for v in pts);z1=max(v.z for v in pts);bw=.055
 box(x0,x0+bw,z0,z1,pts);box(x1-bw,x1,z0,z1,pts)
 box(x0+bw,x1-bw,z0,z0+bw,pts);box(x0+bw,x1-bw,z1-bw,z1,pts)
mesh=bpy.data.meshes.new('RAWL_North_Window_PerimeterFrames_R4');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(bpy.data.materials['RAWL_Dark_Bronze_Metal']);f.data=mesh
# Keep the previously measured 8 cm location, retain the evidence-derived perimeter frame width.
f.location.y=.08
bpy.ops.wm.save_as_mainfile(filepath=p)
with open('audit/batch4_rawls/round4_model_changes.json','w') as out:json.dump({'asset':p,'north_panes_and_frames_world_offset_y_m':.08,'north_masonry':'Rebuilt the continuous outer and inner north wall skins as masonry panels around the 60 measured existing glass quads. Added brick reveal returns at every opening. Preserved original outer shell bounds, adjacent wall faces, wall object and material assignment.','north_frames':'Replaced 60 full-area rectangular bronze blocker boxes with 4 narrow perimeter bronze bars per pane (55 mm width, 40 mm depth), using the measured glass quad bounds and facade slope.','glass_material':'Blue-gray, low-roughness reflective/transmissive appearance retained; opened wall apertures now expose actual panes and interior.','registration_uncertainty':'Existing 1–2m GIS registration uncertainty remains. Plan1086 boundary remains provisional; no new survey control point was found.','geometry_check':'Reopen and ray trace nine interior pane locations; confirm the exterior masonry no longer occludes pane centers.'},out,indent=2)
print('saved frame bars',len(faces),'old blocker faces 360')
