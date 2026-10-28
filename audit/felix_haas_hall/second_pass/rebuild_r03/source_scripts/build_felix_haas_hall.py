"""Build a new Haas exterior from research-derived geometry_input.json.

The old library is used solely to preserve its hidden schematic interior archive;
none of its exterior meshes, materials, openings, roofs or modifiers are reused.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'modular/manifest.json').exists())
OUT=ROOT/'audit/felix_haas_hall/second_pass/rebuild_r03'
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
    'brick':basic('HAAS_New_Pressed_Red_Brick',(.28,.075,.035)),
    'stone':basic('HAAS_New_Bedford_Limestone',(.57,.54,.45)),
    'bronze':basic('HAAS_New_Dark_Window_Frames',(.033,.030,.022),.35,.40),
    'glass':basic('HAAS_New_Recessed_Glazing',(.032,.052,.068),.20,.20),
    'wood':basic('HAAS_New_Entry_Oak',(.13,.055,.018),.58),
    'wood_dark':basic('HAAS_New_Entry_Recessed_Panels',(.075,.026,.008),.64),
    'joint':basic('HAAS_New_Masonry_Joints',(.12,.11,.08),.9),
    'roof':basic('HAAS_New_Red_Clay_Tile',(.33,.078,.030),.70),
    'soffit':basic('HAAS_New_Dark_Timber_Eaves',(.055,.032,.015),.82),
    'metal':basic('HAAS_New_Drainage_Metal',(.038,.032,.023),.52,.4),
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
    tex.inputs['Mortar Size'].default_value=.007 if not roof else .009
    tex.inputs['Mortar Smooth'].default_value=.001
    tex.inputs['Color1'].default_value=(*c1,1);tex.inputs['Color2'].default_value=(*c2,1);tex.inputs['Mortar'].default_value=(*mortar,1)
    links.new(comb.outputs[0],tex.inputs['Vector']);links.new(tex.outputs['Color'],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.invert=True;bump.inputs['Strength'].default_value=.38;bump.inputs['Distance'].default_value=.01 if not roof else .035
    links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
masonry(mats['brick'],.25,.078,(.24,.066,.030),(.36,.100,.047),(.16,.14,.11))
masonry(mats['stone'],1.0,.42,(.56,.535,.47),(.64,.61,.54),(.40,.38,.32))
masonry(mats['roof'],.33,.21,(.31,.073,.029),(.43,.118,.048),(.16,.046,.023),True)

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
    # Building entrance handrails follow the rise, with no unsupported campus site.
    cu=bpy.data.curves.new(f'HAAS_New_EntryRail_{sign}','CURVE');cu.dimensions='3D';cu.bevel_depth=.024;cu.bevel_resolution=3;cu.use_fill_caps=True
    coords=[point(front,mid+sign*2.24,5.30,1.0),point(front,mid+sign*2.24,.75,3.20)]
    sp=cu.splines.new('POLY');sp.points.add(1)
    for p,xyz in zip(sp.points,coords):p.co=(*xyz,1)
    o=bpy.data.objects.new(cu.name,cu);C.objects.link(o);cu.materials.append(mats['metal'])
    for k,d in enumerate([1,2.5,4.0,5.25]):beam(front,f'HAAS_Rebuild_RailPost_{sign}_{k}',mid+sign*2.24,d,(2.38*(1-d/5.5)+.45),.04,.04,.90,mats['metal'])

# Preserve only the old schematic interior as an explicit, hidden recovery archive.
if OLD.exists():
    with bpy.data.libraries.load(str(OLD),link=False) as (src,dst):dst.objects=[name for name in src.objects if name.startswith('HAAS_Plan_')]
    archive=bpy.data.collections.new('HAAS_PreRebuild_SchematicInterior_Archive');S.collection.children.link(archive)
    for o in dst.objects:
        if o:archive.objects.link(o)
    archive.hide_render=True;archive.hide_viewport=True

C['revision']='research_rebuild_r03'
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
report={'revision':'research_rebuild_r03','export_collection':C.name,'export_objects':len(C.all_objects),'openings':len(data['openings']),'legacy_exterior_objects':sum(o.name.startswith(('HAAS_Photo_','HAAS_R4_','HAAS_SP_West_','HAAS_Corrected_')) for o in C.all_objects),'nonmanifold_or_degenerate_meshes':bad,'meshes':checks,'old_exterior_used_as_reference':False,'saved_path':str(OUT/'candidate.blend'),'accepted':False}
(OUT/'mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
# Never replace the canonical library until the mesh checks have been inspected.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'candidate.blend'),compress=True)
report['sha256']=hashlib.sha256((OUT/'candidate.blend').read_bytes()).hexdigest()
(OUT/'mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('revision','export_objects','openings','legacy_exterior_objects','nonmanifold_or_degenerate_meshes','sha256')}))
