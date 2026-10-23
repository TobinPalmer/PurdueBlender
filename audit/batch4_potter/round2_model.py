import bpy,bmesh,math,json,shutil
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend')
D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter')
shutil.copy2(P,D/'round1.blend')
bpy.ops.wm.open_mainfile(filepath=str(P)); col=bpy.data.collections['Asset_potter_engineering']
# Clip perimeter shell at estimated penthouse floor, based on 2016 existing penthouse plan.
shell=col.objects['POTR_Official_864_Structural_Envelope']; plane_z=13.4112
bm=bmesh.new(); bm.from_mesh(shell.data)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-5,plane_co=(0,0,plane_z),plane_no=(0,0,1),clear_outer=True,clear_inner=False)
bm.to_mesh(shell.data); bm.free(); shell.data.update(); shell['roof_level_source']='2016 Potter study existing 3rd floor/penthouse plans; 14 ft floor spacing estimated'; shell['roof_level_uncertainty']='Approximate elevation; footprint registration differs between plan pages.'
# Existing roof polygon becomes the penthouse floor slab at level 4.
roof=col.objects['POTR_Official_864_Roof']
for v in roof.data.vertices: v.co.z-=2.0888
roof['description']='Estimated penthouse floor slab at z=13.4112m; GIS-derived roof outline retained.'
# Penthouse roof/walls as room 401 T form from existing 2016 plan. Approximate plan-to-model transform; scaled to 3,547 sf labeled room area.
# Polygon source traced from printed page 45; transformed with page registration documented in report.
# Source pixel-space trace of room 401 main T: horizontal bar plus south connector, mapped in local XY.
# Use compact rotated footprint around plan-derived location, with actual 3,547 sf volume area target ~329.6 m2.
# Map transformed outline initially ~248m2 then scale uniformly sqrt(329.6/248) about its centroid.
raw=[(15.2,41.6),(36.2,41.6),(36.2,31.5),(22.2,31.5),(22.2,23.6),(17.2,23.6),(17.2,31.5),(15.2,31.5)]
area=abs(sum(raw[i][0]*raw[(i+1)%len(raw)][1]-raw[(i+1)%len(raw)][0]*raw[i][1] for i in range(len(raw)))/2)
scale=math.sqrt(329.6/area); cx=sum(x for x,y in raw)/len(raw); cy=sum(y for x,y in raw)/len(raw)
poly=[(cx+(x-cx)*scale,cy+(y-cy)*scale) for x,y in raw]
base=plane_z; top=15.5
verts=[(x,y,z) for z in (base,top) for x,y in poly]; n=len(poly); faces=[]
faces.append(tuple(range(n-1,-1,-1)));faces.append(tuple(range(n,2*n)))
for i in range(n): j=(i+1)%n;faces.append((i,j,j+n,i+n))
mesh=bpy.data.meshes.new('POTR_Room401_Penthouse_Walls_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
wallmat=bpy.data.materials.get('POTR_Pale_Precast') or bpy.data.materials.get('POTR_Exterior_Precast')
if wallmat: mesh.materials.append(wallmat)
obj=bpy.data.objects.new('POTR_Historic2016_Room401_Penthouse_Massing',mesh);col.objects.link(obj);obj['source']='2016 Potter Renovation Study, printed page 45, Existing Penthouse';obj['room_area_sf']=3547;obj['area_estimated_m2']=329.6;obj['placement']='Approximate transform from source plan; footprint scaled to labeled Room 401 area; not a surveyed penthouse outline.'
# Penthouse roof plate, modest parapet, neutral gray roofing.
mat=bpy.data.materials.get('POTR_Current_Roof_Membrane_Estimate') or bpy.data.materials.new('POTR_Current_Roof_Membrane_Estimate');mat.diffuse_color=(.22,.24,.25,1);mat.use_nodes=True
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.22,.24,.25,1);bs.inputs['Roughness'].default_value=.88
roofmesh=bpy.data.meshes.new('POTR_Room401_Roof_Mesh');rv=[(x,y,top+.04) for x,y in poly];rf=[tuple(range(n))];roofmesh.from_pydata(rv,[],rf);roofmesh.materials.append(mat);roofmesh.update();ro=obj=bpy.data.objects.new('POTR_Historic2016_Room401_Penthouse_Roof',roofmesh);col.objects.link(ro);ro['source']=obj['source'] if False else '2016 Potter study existing penthouse plan, printed page 45; roofing material estimated.'
# Transparent evidence labels and true continuous stair flights inferred from the 2016 stair cores.
stairmat=bpy.data.materials.get('POTR_Interior_Concrete_Stairs') or bpy.data.materials.new('POTR_Interior_Concrete_Stairs');stairmat.diffuse_color=(.53,.52,.48,1);stairmat.use_nodes=True
sbs=next(n for n in stairmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');sbs.inputs['Base Color'].default_value=(.53,.52,.48,1);sbs.inputs['Roughness'].default_value=.76
metal=bpy.data.materials.get('POTR_Stair_Rail_Metal') or bpy.data.materials.new('POTR_Stair_Rail_Metal');metal.diffuse_color=(.12,.13,.14,1);metal.use_nodes=True
mb=next(n for n in metal.node_tree.nodes if n.type=='BSDF_PRINCIPLED');mb.inputs['Base Color'].default_value=(.12,.13,.14,1);mb.inputs['Metallic'].default_value=.65;mb.inputs['Roughness'].default_value=.32
# Stair centers are located from labels 3S01/3S02/3S03 on the 2016 existing third-floor plan.
cores=[(49.8,1.5),(49.9,53.4),(10.5,35.2)]
for ci,(x,y) in enumerate(cores,1):
 for level,(z0,z1) in enumerate([(-4.064,.6096),(.6096,4.8768),(4.8768,9.144),(9.144,13.4112)]):
  height=z1-z0;half=height/2;run=2.7;width=1.05;center_x=x
  # Twin opposing flights with shared mid landing; flights run along local X, side-by-side in Y.
  v=[];f=[]
  def box(cx0,cy0,cz0,sx,sy,sz):
   a=len(v);v.extend([(cx0-sx/2,cy0-sy/2,cz0-sz/2),(cx0+sx/2,cy0-sy/2,cz0-sz/2),(cx0+sx/2,cy0+sy/2,cz0-sz/2),(cx0-sx/2,cy0+sy/2,cz0-sz/2),(cx0-sx/2,cy0-sy/2,cz0+sz/2),(cx0+sx/2,cy0-sy/2,cz0+sz/2),(cx0+sx/2,cy0+sy/2,cz0+sz/2),(cx0-sx/2,cy0+sy/2,cz0+sz/2)]);f.extend([tuple(a+i for i in q) for q in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]])
  # Twelve treads per flight at regular riser heights. The second flight returns parallel to the first.
  count=12; tread=run/count
  for i in range(count):
   rise=half/count; dep=(i+1)*rise
   box(center_x-run/2+(i+.5)*tread,y-width/2,z0+dep-.09,tread+.015,width,.18)
   box(center_x+run/2-(i+.5)*tread,y+width/2,z0+half+dep-.09,tread+.015,width,.18)
  box(center_x+run/2+.62,y,z0+half,.62,2*width,.16)
  me=bpy.data.meshes.new(f'POTR_StairCore{ci}_Level{level}_Mesh');me.from_pydata(v,[],f);me.materials.append(stairmat);me.update();st=bpy.data.objects.new(f'POTR_2016_StairCore{ci}_Level{level}_Flight',me);col.objects.link(st);st['source']='2016 Potter existing floor plans, labels S01–S03; tread geometry and exact locations are estimated.';st['connects_levels']=f'{z0:.4f} to {z1:.4f}m';st['historic_plan_core']=ci
# Save/reopen, checks and unhide asset elements.
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));col=bpy.data.collections['Asset_potter_engineering']
print(json.dumps({'objects':len(col.all_objects),'shell_bounds':list(col.objects['POTR_Official_864_Structural_Envelope'].dimensions),'roof_z':[min(v.co.z for v in col.objects['POTR_Official_864_Roof'].data.vertices),max(v.co.z for v in col.objects['POTR_Official_864_Roof'].data.vertices)],'penthouse':col.objects['POTR_Historic2016_Room401_Penthouse_Massing'].get('room_area_sf'),'stair_flights':len([o for o in col.objects if o.name.startswith('POTR_2016_StairCore')]),'root':list(col.objects['AssetRoot_potter_engineering'].location)},indent=2))
