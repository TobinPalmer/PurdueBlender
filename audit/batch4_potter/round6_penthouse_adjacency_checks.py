import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend')
D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter')
bpy.ops.wm.open_mainfile(filepath=str(P)); bpy.ops.wm.open_mainfile(filepath=str(P))
c=bpy.data.collections['Asset_potter_engineering']
def hit_obj(o,origin,direction,distance):
 inv=o.matrix_world.inverted(); org=inv@Vector(origin); direct=(inv.to_3x3()@Vector(direction)).normalized(); hit,loc,norm,idx=o.ray_cast(org,direct,distance=distance)
 return {'hit':bool(hit),'face':idx if hit else None}
checks=[]
for label,objname,x0,x1,y,z,side_y in [
 ('401 to 401A','POTR_Historic2016_Room401_Penthouse_Massing',16.3,16.9,35.2,14.3,35.7),
 ('4S04 west entry','POTR_4S04_Enclosure_Walls_183sf_Estimate',9.0,9.6,35.2,14.3,35.9),
 ('4S04 to 401A','POTR_4S04_Enclosure_Walls_183sf_Estimate',12.7,13.3,35.2,14.3,35.7)]:
 o=bpy.data.objects[objname];checks.append({'interface':label,'center':hit_obj(o,(x0,y,z),(1,0,0),x1-x0),'side_control':hit_obj(o,(x0,side_y,z),(1,0,0),x1-x0)})
# Segment area and bounds summary, using room labels from printed penthouse plan.
room401=3547*.09290304; roomA=100*.09290304; room4=183*.09290304
# T polygon's modeled wall centerline points are reconstructible from projected extrema and vertices.
mass=bpy.data.objects['POTR_Historic2016_Room401_Penthouse_Massing']; xs=[v.co.x for v in mass.data.vertices];ys=[v.co.y for v in mass.data.vertices]
# Top stair terminal tread, landing contact, roof opening, root/GIS integrity.
stair=bpy.data.objects['POTR_2016_StairCore3_Level3_Flight'];topfaces=[]
for f in stair.data.polygons:
 if f.normal.z>.99 and f.area>.08:
  vs=[stair.data.vertices[i].co for i in f.vertices]; topfaces.append({'z':sum(v.z for v in vs)/len(vs),'xmin':min(v.x for v in vs),'xmax':max(v.x for v in vs),'ymin':min(v.y for v in vs),'ymax':max(v.y for v in vs)})
top=max(topfaces,key=lambda r:r['z']);land=bpy.data.objects['POTR_2016_StairCore3_Penthouse_Landing_4S04_Estimate'];lb=[land.matrix_world@Vector(v) for v in land.bound_box]
landing={'top_tread_z':top['z'],'landing_top_z':max(v.z for v in lb),'tread_landing_riser_m':max(v.z for v in lb)-top['z'],'top_tread_xy_bounds':[top['xmin'],top['ymin'],top['xmax'],top['ymax']],'landing_xy_bounds':[min(v.x for v in lb),min(v.y for v in lb),max(v.x for v in lb),max(v.y for v in lb)],'xy_overlap':not (top['xmax']<min(v.x for v in lb) or top['xmin']>max(v.x for v in lb) or top['ymax']<min(v.y for v in lb) or top['ymin']>max(v.y for v in lb))}
roof=bpy.data.objects['POTR_Official_864_Roof'];dg=bpy.context.evaluated_depsgraph_get();eo=roof.evaluated_get(dg);me=eo.to_mesh();opening_hits=[]
for pt in [(10.5,35.2,13.2),(8.7,35.2,13.2),(12.3,35.2,13.2)]:
 origin=eo.matrix_world.inverted()@Vector(pt); direction=eo.matrix_world.to_3x3().inverted()@Vector((0,0,1));h,*_=eo.ray_cast(origin,direction,distance=2);opening_hits.append({'xy':pt[:2],'upward_ray_hits_roof':bool(h)})
eo.to_mesh_clear()
res={'reopened_twice':True,'root_origin':list(bpy.data.objects['AssetRoot_potter_engineering'].location),'gis_shell_xy':list(bpy.data.objects['POTR_Official_864_Structural_Envelope'].dimensions[:2]),'room_label_areas_sf':{'401':3547,'401A':100,'4S04':183},'room_label_areas_m2':{'401':room401,'401A':roomA,'4S04':room4},'room401_wall_bounds_xy':[min(xs),min(ys),max(xs),max(ys)],'affine':'Printed p.45 mapped through registered p.44 affine and uniform scale to room401 area; approximate, not surveyed.','doorway_raycast_checks':checks,'stair_to_landing':landing,'roof_rays':opening_hits,'missing_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]}
(D/'round6_penthouse_adjacency_checks.json').write_text(json.dumps(res,indent=2)); print(json.dumps(res,indent=2))

