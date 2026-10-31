"""Build a new Haas exterior from research-derived geometry_input.json.

The old library is used solely to preserve its hidden schematic interior archive;
none of its exterior meshes, materials, openings, roofs or modifiers are reused.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'modular/manifest.json').exists())
REVISION='detail_color_r04'
OUT=ROOT/'audit/felix_haas_hall/second_pass'/REVISION
data=json.loads((OUT/'geometry_input.json').read_text())
OLD=ROOT/'audit/felix_haas_hall/second_pass/revision_r02/source_before_rebuild.blend'
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene;S.name='Building_felix_haas_hall';S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
C=bpy.data.collections.new('Asset_felix_haas_hall');S.collection.children.link(C)

def basic(name,color,rough=.8,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m
mats={
    'brick':basic('HAAS_New_Pressed_Red_Brick',(.23,.080,.052)),
    'stone':basic('HAAS_New_Bedford_Limestone',(.66,.64,.57)),
    'stone_shade':basic('HAAS_Detail_ShallowStoneIncisions',(.43,.42,.36)),
    'service_metal':basic('HAAS_Detail_Gray_ServiceDoor',(.18,.19,.18),.70,.12),
    'bronze':basic('HAAS_New_Dark_Window_Frames',(.050,.048,.038),.42,.25),
    'glass':basic('HAAS_New_Recessed_Glazing',(.045,.055,.048),.20,.30),
    'wood':basic('HAAS_New_Entry_Oak',(.28,.13,.047),.58),
    'wood_dark':basic('HAAS_New_Entry_Recessed_Panels',(.19,.070,.024),.64),
    'joint':basic('HAAS_New_Masonry_Joints',(.12,.11,.08),.9),
    'roof':basic('HAAS_New_Red_Clay_Tile',(.20,.058,.035),.78),
    'soffit':basic('HAAS_New_Dark_Timber_Eaves',(.055,.032,.015),.82),
    'metal':basic('HAAS_New_Drainage_Metal',(.038,.032,.023),.52,.4),
    'alarm':basic('HAAS_Detail_Red_Alarm',(.28,.018,.022),.5),
    'light_glass':basic('HAAS_Detail_Unlit_LanternGlass',(.24,.25,.21),.28,.05),
}

def masonry(mat,width,height,c1,c2,mortar,roof=False):
    nt=mat.node_tree;n=nt.nodes;links=nt.links;p=next(v for v in n if v.type=='BSDF_PRINCIPLED')
    geo=n.new('ShaderNodeNewGeometry');pos=n.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Position'],pos.inputs[0])
    comb=n.new('ShaderNodeCombineXYZ')
    if roof:
        links.new(pos.outputs['X'],comb.inputs['X']);links.new(pos.outputs['Y'],comb.inputs['Y'])
    else:
        normal=n.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Normal'],normal.inputs[0])
        absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE';links.new(normal.outputs['X'],absolute.inputs[0])
        test=n.new('ShaderNodeMath');test.operation='GREATER_THAN';test.inputs[1].default_value=.65;links.new(absolute.outputs[0],test.inputs[0])
        mix=n.new('ShaderNodeMixRGB');links.new(test.outputs[0],mix.inputs[0]);links.new(pos.outputs['X'],mix.inputs[1]);links.new(pos.outputs['Y'],mix.inputs[2])
        links.new(mix.outputs[0],comb.inputs['X']);links.new(pos.outputs['Z'],comb.inputs['Y'])
    tex=n.new('ShaderNodeTexBrick');tex.inputs['Scale'].default_value=1;tex.inputs['Brick Width'].default_value=width;tex.inputs['Row Height'].default_value=height
    tex.inputs['Mortar Size'].default_value=.005 if not roof else .009
    tex.inputs['Mortar Smooth'].default_value=.001
    tex.inputs['Color1'].default_value=(*c1,1);tex.inputs['Color2'].default_value=(*c2,1);tex.inputs['Mortar'].default_value=(*mortar,1)
    links.new(comb.outputs[0],tex.inputs['Vector']);links.new(tex.outputs['Color'],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.invert=True;bump.inputs['Strength'].default_value=.18 if mat==mats['stone'] else .30;bump.inputs['Distance'].default_value=.008 if not roof else .028
    links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
masonry(mats['brick'],.215,.072,(.19,.065,.044),(.28,.098,.068),(.21,.19,.155))
masonry(mats['stone'],1.2,.45,(.62,.60,.53),(.70,.68,.60),(.52,.51,.46))
masonry(mats['roof'],.33,.21,(.16,.045,.028),(.24,.071,.042),(.11,.035,.024),True)

def mesh(name,verts,faces,material):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000002)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    me.materials.append(material);o=bpy.data.objects.new(name,me);C.objects.link(o);return o
for part in data['parts']:mesh(part['name'],part['vertices'],part['faces'],mats[part['material']])

main_roof=bpy.data.objects['HAAS_Rebuild_Main_RoofSolid'];entry_roof=bpy.data.objects['HAAS_Rebuild_Entry_RoofSolid']
bpy.context.view_layer.objects.active=main_roof
mod=main_roof.modifiers.new('Unite_new_hipped_volumes','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=entry_roof
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(entry_roof,do_unlink=True);main_roof.name='HAAS_Rebuild_Unified_Hipped_Roof'

def box(name,loc,size,material):
    x,y,z=loc;a,b,c=[s/2 for s in size]
    v=[(x+dx*a,y+dy*b,z+dz*c) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)
def point(f,u,d,z):return(f['a'][0]+f['t'][0]*u+f['n'][0]*d,f['a'][1]+f['t'][1]*u+f['n'][1]*d,z)
def beam(f,name,u,d,z,w,depth,h,material):
    verts=[point(f,u+du*w/2,d+dd*depth/2,z+dz*h/2) for du,dd,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)

def side_profile(f,name,u,width,profile,material):
    verts=[point(f,u+du,d,z) for du in (-width/2,width/2) for d,z in profile];N=len(profile)
    return mesh(name,verts,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N) for k in range(N)],material)

def tube(f,name,coordinates,radius,material):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=radius;cu.bevel_resolution=3;cu.use_fill_caps=True
    sp=cu.splines.new('POLY');sp.points.add(len(coordinates)-1)
    for p,(u,d,z) in zip(sp.points,coordinates):p.co=(*point(f,u,d,z),1)
    o=bpy.data.objects.new(name,cu);C.objects.link(o);cu.materials.append(material);return o

for f in data['facades']:
    L=f['length'];i=f['id']
    beam(f,f'HAAS_Rebuild_Timber_Fascia_{i}',L/2,.23,11.60,L,.52,.22,mats['soffit'])
    if L<4:continue
    # Sculpted under-eave brackets, visible in the street-level photographs.
    for j in range(max(2,round(L/1.5))):
        u=L*(j+.5)/max(2,round(L/1.5))
        profile=[(-.01,10.99),(.07,10.99),(.13,11.11),(.25,11.25),(.47,11.36),(.57,11.42),(.57,11.57),(-.01,11.57)]
        verts=[point(f,u+offset,d,z) for offset in (-.075,.075) for d,z in profile];N=len(profile)
        faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N) for k in range(N)]
        mesh(f'HAAS_Rebuild_EaveBracket_{i}_{j}',verts,faces,mats['soffit'])
    # Subtle drainpipes at a small number of source-consistent divisions.
    if i in (4,9,10,11):
        stations=[L*.03,L*.97] if i!=10 else [L*.32,L*.65]
        for j,u in enumerate(stations):
            cu=bpy.data.curves.new(f'HAAS_New_Downpipe_{i}_{j}','CURVE');cu.dimensions='3D';cu.bevel_depth=.048;cu.bevel_resolution=3;cu.use_fill_caps=True
            sp=cu.splines.new('POLY');sp.points.add(2)
            for p,xyz in zip(sp.points,[point(f,u,.20,.35),point(f,u,.20,11.15),point(f,u,.48,11.56)]):p.co=(*xyz,1)
            o=bpy.data.objects.new(cu.name,cu);C.objects.link(o);cu.materials.append(mats['metal'])

# Main entry staircase: dedicated building-owned features, never a campus placement edit.
front=data['facades'][4];mid=front['length']/2
for j in range(17):
    rise=2.38*(j+1)/17;distance=(17-j)*.31
    beam(front,f'HAAS_Rebuild_MainEntry_Tread_{j+1}',mid,distance/2+.25,rise/2,4.60,distance,rise,mats['stone'])
beam(front,'HAAS_Rebuild_MainEntry_Landing',mid,.33,2.28,4.8,.80,.20,mats['stone'])
for sign in (-1,1):
    beam(front,f'HAAS_Rebuild_Stair_LowerPier_{sign}',mid+sign*2.54,5.35,.42,.62,.70,.84,mats['stone'])
    beam(front,f'HAAS_Rebuild_Stair_UpperPier_{sign}',mid+sign*2.54,.83,2.35,.62,.65,.90,mats['stone'])
    side_profile(front,f'HAAS_Detail_StairSolidCheek_{sign}',mid+sign*2.54,.48,[(.8,.05),(5.35,.05),(5.35,.72),(.8,2.66)],mats['stone'])
    side_profile(front,f'HAAS_Detail_StairCheekCap_{sign}',mid+sign*2.54,.58,[(.8,2.66),(5.35,.72),(5.35,.83),(.8,2.77)],mats['stone'])
    # Building entrance handrails follow the rise, with no unsupported campus site.
    cu=bpy.data.curves.new(f'HAAS_New_EntryRail_{sign}','CURVE');cu.dimensions='3D';cu.bevel_depth=.024;cu.bevel_resolution=3;cu.use_fill_caps=True
    coords=[point(front,mid+sign*2.24,5.30,1.0),point(front,mid+sign*2.24,.75,3.20)]
    sp=cu.splines.new('POLY');sp.points.add(1)
    for p,xyz in zip(sp.points,coords):p.co=(*xyz,1)
    o=bpy.data.objects.new(cu.name,cu);C.objects.link(o);cu.materials.append(mats['metal'])
    for k,d in enumerate([1,2.5,4.0,5.25]):beam(front,f'HAAS_Rebuild_RailPost_{sign}_{k}',mid+sign*2.24,d,(2.38*(1-d/5.5)+.45),.04,.04,.90,mats['metal'])

# Paired wall lanterns on the pale front fields, from the user's close photo.
for sign in (-1,1):
    u=mid+sign*3.90;z=5.70
    beam(front,f'HAAS_Detail_LanternWallPlate_{sign}',u,.19,z+.13,.13,.12,.52,mats['metal'])
    tube(front,f'HAAS_Detail_LanternScroll_{sign}',[(u,.23,z-.10),(u,.47,z-.08),(u,.62,z+.10),(u,.62,z+.37),(u,.52,z+.48)],.018,mats['metal'])
    beam(front,f'HAAS_Detail_LanternGlass_{sign}',u,.56,z+.63,.23,.23,.40,mats['light_glass'])
    for dx in (-.135,.135):
        for dd in (-.135,.135):beam(front,f'HAAS_Detail_LanternFrame_{sign}_{dx}_{dd}',u+dx,.56+dd,z+.63,.025,.025,.44,mats['metal'])
    for zz in (z+.40,z+.86):beam(front,f'HAAS_Detail_LanternRim_{sign}_{zz}',u,.56,zz,.32,.32,.045,mats['metal'])
    verts=[point(front,u+du,.56+dd,z+.885) for du,dd in [(-.18,-.18),(.18,-.18),(.18,.18),(-.18,.18)]]+[point(front,u,.56,z+1.08)]
    mesh(f'HAAS_Detail_LanternHippedCap_{sign}',verts,[(0,3,2,1),(0,1,4),(1,2,4),(2,3,4),(3,0,4)],mats['metal'])
    beam(front,f'HAAS_Detail_LanternFinial_{sign}',u,.56,z+1.12,.045,.045,.10,mats['metal'])

# Rear entry: photographed retaining cheeks and recessed pedestrian approach.
west=data['facades'][10];door=next(w for w in data['openings'] if w['label']=='WestDoor');u=door['u']
beam(west,'HAAS_Detail_WestApproach',u,2.50,.025,3.10,5.0,.10,mats['stone'])
for sign in (-1,1):
    side_profile(west,f'HAAS_Detail_WestRetainingCheek_{sign}',u+sign*1.76,.35,[(.12,.02),(5.1,.02),(5.1,.75),(.12,1.95)],mats['stone'])
    side_profile(west,f'HAAS_Detail_WestRetainingCap_{sign}',u+sign*1.76,.43,[(.12,1.95),(5.1,.75),(5.1,.84),(.12,2.04)],mats['stone'])
beam(west,'HAAS_Detail_WestEntryLight',u,.25,3.75,.55,.26,.22,mats['metal'])
beam(west,'HAAS_Detail_WestEntryLightLens',u,.39,3.75,.44,.025,.12,mats['light_glass'])
for sign in (-1,1):
    beam(west,f'HAAS_Detail_WestDoorKickPlate_{sign}',u+sign*.63,-.075,.34,1.03,.055,.25,mats['bronze'])
    beam(west,f'HAAS_Detail_WestDoorPull_{sign}',u+sign*.16,.00,1.20,.055,.09,.38,mats['bronze'])
beam(west,'HAAS_Detail_WestCameraMount',u+west['length']/9+.85,.20,6.40,.12,.15,.15,mats['service_metal'])
beam(west,'HAAS_Detail_WestSecurityCamera',u+west['length']/9+1.0,.37,6.40,.30,.24,.14,mats['stone'])
north=data['facades'][11]
beam(north,'HAAS_Detail_NorthAlarmBox',.90,.20,2.70,.23,.20,.38,mats['alarm'])

# Preserve only the old schematic interior as an explicit, hidden recovery archive.
if OLD.exists():
    with bpy.data.libraries.load(str(OLD),link=False) as (src,dst):dst.objects=[name for name in src.objects if name.startswith('HAAS_Plan_')]
    archive=bpy.data.collections.new('HAAS_PreRebuild_SchematicInterior_Archive');S.collection.children.link(archive)
    for o in dst.objects:
        if o:archive.objects.link(o)
    archive.hide_render=True;archive.hide_viewport=True

C['revision']=REVISION
C['basis']='New exterior geometry from official Purdue GIS FID 233 and recorded photographs. No inherited exterior geometry used.'
C['acceptance']='Independent visual review required; not complete.'
C['dimensional_uncertainty']='Heights, openings and facade detailing are photo-derived estimates; some return elevations remain incompletely observed.'

# Default user viewport; review cameras are temporary and generated separately.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.region_3d.view_location=Vector((-6,0,6));sp.region_3d.view_rotation=(Vector((-6,0,6))-Vector((65,-65,35))).to_track_quat('-Z','Y')
            sp.region_3d.view_distance=83;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False

checks=[]
for o in C.all_objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    checks.append({'name':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces)})
    bm.free()
bad=[r for r in checks if r['nonmanifold_edges'] or r['zero_area_faces']]
report={'revision':REVISION,'export_collection':C.name,'export_objects':len(C.all_objects),'openings':len(data['openings']),'legacy_exterior_objects':sum(o.name.startswith(('HAAS_Photo_','HAAS_R4_','HAAS_SP_West_','HAAS_Corrected_')) for o in C.all_objects),'nonmanifold_or_degenerate_meshes':bad,'meshes':checks,'old_exterior_used_as_reference':False,'saved_path':str(OUT/'candidate.blend'),'accepted':False}
(OUT/'mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
# Never replace the canonical library until the mesh checks have been inspected.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'candidate.blend'),compress=True)
report['sha256']=hashlib.sha256((OUT/'candidate.blend').read_bytes()).hexdigest()
(OUT/'mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('revision','export_objects','openings','legacy_exterior_objects','nonmanifold_or_degenerate_meshes','sha256')}))
