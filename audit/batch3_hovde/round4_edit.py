import bpy, math
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); F=P/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(F)); c=bpy.data.collections['Asset_hovde_hall']; root=bpy.data.objects['HOVD_Root']
# Pull the stone portico forward from the glazing plane and tighten the stone mass around the column line.
for name in ['HOVD_Portico_Entablature','HOVD_Portico_Cornice','HOVD_Portico_Pediment_Base','HOVD_Portico_Pediment_Crown']:
 o=bpy.data.objects[name]; o.location.x += .75
ent=bpy.data.objects['HOVD_Portico_Entablature']; ent.scale.z*=.72; ent.location.z=11.22
corn=bpy.data.objects['HOVD_Portico_Cornice']; corn.scale.z*=.78; corn.location.z=12.08
ped=bpy.data.objects['HOVD_Portico_Pediment_Base']; ped.scale.z*=.72; ped.location.z=13.45
crown=bpy.data.objects['HOVD_Portico_Pediment_Crown']; crown.scale.z*=.85; crown.location.z=14.80
# Replace simple round column cylinders with subtly tapered, fluted shafts. Their original transforms, spacing, and bases stay fixed.
for i in range(1,7):
 o=bpy.data.objects[f'HOVD_Classical_Column_{i}']; old=o.data
 coords=[v.co.copy() for v in old.vertices]
 zmin=min(v.z for v in coords); zmax=max(v.z for v in coords); rmax=max(max(abs(v.x),abs(v.y)) for v in coords)
 # Interpret original cylinder bounds, not the object's world placement.
 rings=[(zmin,.80),(zmin+.10,.88),(zmin+.28,.88),(zmin+.43,.91),(zmin+.75,.94),(zmin+1.05,.98),(zmax-1.15,.93),(zmax-.75,.90),(zmax-.40,.88),(zmax-.18,.96),(zmax,.96)]
 verts=[];faces=[];n=96
 for z,rf in rings:
  for j in range(n):
   a=2*math.pi*j/n; groove=max(0.0,math.cos(12*a))**12
   rr=rmax*rf-.018*groove
   verts.append((rr*math.cos(a),rr*math.sin(a),z))
 for k in range(len(rings)-1):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n;c1=(k+1)*n+(j+1)%n;d=(k+1)*n+j;faces.append((a,b,c1,d))
 me=bpy.data.meshes.new(f'HOVD_Fluted_Column_{i}_Mesh');me.from_pydata(verts,[],faces);me.materials.clear()
 for m in old.materials:me.materials.append(m)
 me.update();o.data=me
 for poly in me.polygons:poly.use_smooth=True
# Give each shaft a low-profile round molding at both transitions for readable depth.
limestone=bpy.data.materials['Bedford_Indiana_Limestone']
def make_ring(name,cx,cy,cz,major,minor):
 vs=[];fs=[];nu=64;nv=12
 for u in range(nu):
  a=2*math.pi*u/nu
  for v in range(nv):
   b=2*math.pi*v/nv;r=major+minor*math.cos(b);z=minor*math.sin(b)
   vs.append((r*math.cos(a),r*math.sin(a),z))
 for u in range(nu):
  for v in range(nv):
   fs.append((u*nv+v,u*nv+(v+1)%nv,((u+1)%nu)*nv+(v+1)%nv,((u+1)%nu)*nv+v))
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(vs,[],fs);me.materials.append(limestone);me.update();ob=bpy.data.objects.new(name,me);c.objects.link(ob);ob.parent=root;ob.matrix_parent_inverse.identity();ob.location=(cx,cy,cz);return ob
for i in range(1,7):
 col=bpy.data.objects[f'HOVD_Classical_Column_{i}'];x,y,_=col.location
 make_ring(f'HOVD_Column_FluteCollar_Base_{i}',x,y,1.16,.57,.065)
 make_ring(f'HOVD_Column_FluteCollar_Capital_{i}',x,y,9.97,.57,.065)
# Resize the board table and seats along the long room axis to restore perimeter circulation.
for o in list(c.all_objects):
 if not o: continue
 group=o.name.startswith('HOVD_Board_Table_') or o.name.startswith('HOVD_Chair_')
 if group:
  o.location.y=25+(o.location.y-25)*.82
  if o.type=='MESH':o.scale.y*=.82
# Add restrained administration-office storage and boardroom credenza; room arrangements remain interpretive.
wood=bpy.data.materials.get('Hovde_Executive_Walnut'); navy=bpy.data.materials.get('Hovde_Boardroom_Mahogany'); gold=bpy.data.materials.get('Purdue_Old_Gold')
def box(name,loc,dims,mat,bevel=0.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0));o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.parent=root;o.matrix_parent_inverse.identity();o.location=loc
 if mat:o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('Soft furniture edges','BEVEL');mod.width=bevel;mod.segments=2
  o.modifiers.new('Weighted furniture normals','WEIGHTED_NORMAL')
 c.objects.link(o)
 for coll in list(o.users_collection):
  if coll!=c:coll.objects.unlink(o)
 return o
# Office bookcase along east side with five shelf rails and varied book spines.
box('HOVD_Pres_Interpretive_Bookcase_Carcass',(4.00,-25.0,5.45),(.34,3.45,2.10),wood,.055)
for j,z in enumerate([4.65,5.18,5.71,6.24]):
 box(f'HOVD_Pres_Bookcase_Shelf_{j+1}',(3.79,-25.0,z),(.14,3.30,.07),wood,.015)
for k in range(20):
 y=-26.48+k*.155; h=[.34,.39,.43,.32,.37][k%5]
 mat=[navy,gold,limestone][k%3]
 box(f'HOVD_Pres_Book_Spine_{k+1}',(3.77,y,4.70+h/2),(.11,.105,h),mat,.008)
# Low credenza / records storage at the south side, leaving the doorway clear.
box('HOVD_Pres_Interpretive_Records_Credenza',(-2.15,-29.00,4.91),(3.2,.42,.96),wood,.05)
for j,x in enumerate([-3.12,-2.15,-1.18]):
 box(f'HOVD_Pres_Credenza_Drawer_{j+1}',(x,-28.77,4.93),(.84,.025,.28),limestone,.01)
# Boardroom side credenza and bound-volume accents on the west side.
box('HOVD_Board_Interpretive_Credenza',(-4.05,25.0,4.92),(.42,3.5,.92),navy,.05)
for k in range(12):
 y=23.55+k*.25;h=.28+(k%3)*.04
 box(f'HOVD_Board_Minutes_Volume_{k+1}',(-3.78,y,5.42+h/2),(.12,.16,h),[gold,limestone,wood][k%3],.008)
# Add a subtle wall marker panel over the boardroom credenza without representing a specific historic seal.
box('HOVD_Board_Interpretive_Wayfinding_Panel',(-4.02,25.0,6.50),(.10,1.25,.62),limestone,.025)
# Save only the assigned source asset.
bpy.ops.wm.save_as_mainfile(filepath=str(F));print('saved round4; portico stepped outward and shortened; 6 fluted shafts; board seating compressed to fit room; interpretive storage added')
