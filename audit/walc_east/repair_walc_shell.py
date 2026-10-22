import bpy,json,shutil,math
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/walc_east'
# Reuse only helper definition, never the repair loop.
exec((D/'repair.py').read_text().split('for id,code,height,fids in ')[0])
a=next(x for x in M['assets'] if x['id']=='walc');p=R/'modular'/a['file'];shutil.copy2(p,D/'walc_before_shell.blend');bpy.ops.wm.open_mainfile(filepath=str(p));c=bpy.data.collections[a['collection']];ox,oy=a['placement_origin_xy_m'];r=next(x for x in ref['buildings'] if x['fid']==906);pts=[(x-ox,y-oy) for x,y in r['rings_xy_m'][0]][:-1]
archive=bpy.data.collections.new('WALC_Previous_Exterior_Reference');bpy.context.scene.collection.children.link(archive);archive.hide_render=True;archive.hide_viewport=True
explicit=['Masonry lower plinth','Brick horizontal spandrels','Clear insulated glazing','Window mullions','Window transoms','Limestone window jamb','Limestone sill lintel','Brick vertical piers','Stone stringcourse','Hipped wing roof','Eaves fascia','End brick spandrels','End brick piers','End stone bands','Entry limestone columns','Eave knee braces','Tall window bronze surround','Reading room upper transom','Glass entry canopy','Canopy ties','Door framing','Door pulls','Inscription limestone frieze','Reading room roof','Rear roof','Rear brick bands','Rear brick piers','Recessed roof','Upper limestone facade closure','Heavy bronze window surround','Tripartite tall window mullions','Tall window horizontal divisions','Upper-light vertical subdivision','Limestone front pier','Paired eave knee brackets','Broad dark front soffit','Wing dark front soffit','Limestone mortar seams','Flush inscription band','Corner limestone upper closure','Deep bronze projecting reveals','Wing tripartite mullions']
archived=[]
for o in list(c.all_objects):
 if o.name in explicit:
  archive.objects.link(o)
  for col in list(o.users_collection):
   if col!=archive:col.objects.unlink(o)
  archived.append(o.name)
brick=bpy.data.materials.new('WALC_Reference_Brick');brick.diffuse_color=(.33,.17,.1,1);stone=bpy.data.materials.new('WALC_Reference_Limestone');stone.diffuse_color=(.64,.59,.46,1);glass=bpy.data.materials.new('WALC_Reference_Glass');glass.diffuse_color=(.12,.22,.27,1);roof=bpy.data.materials.new('WALC_Reference_Roof');roof.diffuse_color=(.16,.17,.18,1)
# Signed area controls inward edge normal. Preserve official exterior vertices exactly.
area=sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)));sgn=1 if area>0 else -1
for i,(x,y) in enumerate(pts):
 X,Y=pts[(i+1)%len(pts)];dx,dy=X-x,Y-y;L=math.hypot(dx,dy)
 if L<.00001:continue
 nx,ny=-dy/L*.28*sgn,dx/L*.28*sgn;quad=[(x,y),(X,Y),(X+nx,Y+ny),(x+nx,y+ny)]
 for j,(lo,hi,mat) in enumerate([(0,1,stone),(1,1.35,brick),(1.35,4.5,glass),(4.5,6.2,brick),(6.2,9.4,glass),(9.4,11.5,brick),(11.5,14.8,glass),(14.8,16.7,stone)]):
  solid(f'WALC_Source906_Edge_{i}_Band{j}',quad,lo,hi,mat if L>.6 else brick,c)
 for j in range(max(1,math.ceil(L/5))):
  t=j/max(1,math.ceil(L/5));s=min(1,t+.25/L);A=(x+t*dx,y+t*dy);B=(x+s*dx,y+s*dy);solid(f'WALC_Source906_Edge_{i}_Pier{j}',[A,B,(B[0]+nx,B[1]+ny),(A[0]+nx,A[1]+ny)],1,16.7,brick,c)
roofobj=solid('WALC_Official_906_Roof',pts,16.7,17,roof,c);roofobj['source_fid']=906;c['review_note']='Official footprint perimeter and roof rebuilt; preserved compatible interior. Facade/window bands, roof elevation and all heights remain estimates.'
bpy.ops.wm.save_as_mainfile(filepath=str(p));bpy.ops.wm.open_mainfile(filepath=str(p));(D/'walc_shell_changes.json').write_text(json.dumps({'archived_exterior':archived,'source_fid':906,'placement_unchanged':[ox,oy],'wall_height_estimate_m':16.7,'roof_height_estimate_m':17,'retained_interiors':'Existing interior, furniture, basement, and landscape components remain estimates.'},indent=2))
# Inspect old Knoy counterpart without modifying it.
p=R/'modular/buildings/massing_knoy_hall_knoy_f598616.blend'
if p.exists():
 bpy.ops.wm.open_mainfile(filepath=str(p));(D/'knoy_old_massing.json').write_text(json.dumps({'file':str(p),'collections':[x.name for x in bpy.data.collections],'objects':[o.name for o in bpy.data.objects]},indent=2))
