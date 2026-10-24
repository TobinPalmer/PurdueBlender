import bpy, json, os
from mathutils import Vector
p=bpy.data.filepath
assert p.lower().endswith('krach_leadership_center.blend')
asset=bpy.data.collections.get('Asset_krach_leadership_center'); assert asset
members=set()
def walk(c):
 for o in c.objects: members.add(o)
 for ch in c.children: walk(ch)
walk(asset)
assert len(members)>=30,len(members)
shell=bpy.data.objects['KRCH structural shell | GIS outline']; assert shell in members
assert bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard'] in members
assert bpy.data.objects['KRCH | transparent Main Street ground-floor storefront'] in members
assert bpy.data.objects['KRCH | paired transparent lobby entrance leaves'] in members
assert bpy.data.objects['KRCH | photo-backed pale limestone roof-edge fascia'] in members
assert bpy.data.objects['KRCH | schematic mechanical penthouse (location estimated)'] in members
rails=bpy.data.objects['KRCH | continuous stair handrails over glass gallery guards']; assert rails in members and len(rails.data.splines)==32
# Geometry bounding and local frame checks
pts=[shell.matrix_world@v.co for v in shell.data.vertices]
bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
assert abs(bounds[0][0]+35.19456)<0.02 and abs(bounds[0][1]-35.2)<0.02
assert abs(bounds[1][0]+14.14485)<0.02 and abs(bounds[1][1]-14.15313)<0.02
st=bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard']
stvals=[tuple(v.co) for v in st.data.vertices]
st_bounds=[[min(v[i] for v in stvals),max(v[i] for v in stvals)] for i in range(3)]
assert st_bounds[2][0]>=-1.1 and st_bounds[2][1]<16.0,st_bounds
slabs=sorted([o for o in members if o.name.startswith('KRCH | schematic level slab')],key=lambda o:o['level_top_m'])
assert len(slabs)==5
void_checks=[]
for slab in slabs:
 z=slab['level_top_m']; inv=slab.matrix_world.inverted()
 hole=slab.ray_cast(inv@Vector((-30.7965,-9.3,z+0.5)),inv.to_3x3()@Vector((0,0,-1)))[0]
 field=slab.ray_cast(inv@Vector((0,0,z+0.5)),inv.to_3x3()@Vector((0,0,-1)))[0]
 assert not hole and field,(slab.name,hole,field)
 void_checks.append({'level_m':z,'atrium_point_clear':not hole,'floor_point_present':field,'mesh_faces':len(slab.data.polygons)})
# Verify all material dependencies are internal and procedural/packed.
unpacked=[]
for m in bpy.data.materials:
 if not m.use_nodes: continue
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE' and not n.image.packed_file:
   if not os.path.exists(bpy.path.abspath(n.image.filepath)): unpacked.append((m.name,n.image.filepath))
assert not unpacked,unpacked
end_windows=bpy.data.objects['KRCH | west end facade windows']
assert len(end_windows.data.polygons)==12*6, len(end_windows.data.polygons)
front_windows=bpy.data.objects['KRCH | repeated punched window glass']
assert len(front_windows.data.polygons)==36*6, len(front_windows.data.polygons)
storefront=bpy.data.objects['KRCH | transparent Main Street ground-floor storefront']
assert len(storefront.data.polygons)==16*6, len(storefront.data.polygons)
window_ray_checks=[]
front_x=[-23.1,-18.6,-14.1,-9.6,-5.1,-.6,4.0,9.3,14.6,19.9,25.2,30.0]
def facade_y(x):
    xa,ya=-16.32078934,-14.05729580; xb,yb=.99312007,-13.16014194
    return ya+(yb-ya)*(x-xa)/(xb-xa) if xa<=x<=xb else -13.90
for x in front_x:
    for z in [4.88,8.78,12.68]:
        inv=shell.matrix_world.inverted()
        hit,loc,_,_=shell.ray_cast(inv@Vector((x,-16.0,z)),inv.to_3x3()@Vector((0,1,0)))
        clear=not hit or loc.y>-12.5
        assert clear,('south elevation pane is blocked by shell',x,z,tuple(loc))
        window_ray_checks.append(('south',x,z,clear))
for y in [-12.70,-11.0,-9.2,-7.5]:
    for z in [4.88,8.78,12.68]:
        inv=shell.matrix_world.inverted()
        hit,loc,_,_=shell.ray_cast(inv@Vector((-37.0,y,z)),inv.to_3x3()@Vector((1,0,0)))
        clear=not hit or loc.x>-34.7
        assert clear,('west end pane is blocked by shell',y,z,tuple(loc))
        window_ray_checks.append(('west_end',y,z,clear))
print(json.dumps({'file':p,'collection':asset.name,'asset_object_count':len(members),'shell_bounds_m':bounds,'stair_bounds_m':st_bounds,'three_upper_rows_on_end_facade':12,'three_upper_rows_on_long_facades':36,'continuous_public_storefront_panes':16,'verified_open_window_rays':len(window_ray_checks),'five_floor_void_tests':void_checks,'continuous_handrail_splines':len(rails.data.splines),'roof_fascia':bpy.data.objects['KRCH | photo-backed pale limestone roof-edge fascia'].name,'mechanical_penthouse_dimensions_m':list(bpy.data.objects['KRCH | schematic mechanical penthouse (location estimated)'].dimensions),'no_missing_external_images':True,'preview_expected_files':['audit/krach_leadership_center/source_preview.png','audit/krach_leadership_center/lobby_stair_preview.png']},indent=2))


