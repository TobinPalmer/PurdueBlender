"""Shared physically scaled material helpers. Import from a building worker in Blender."""
import bpy, math, re
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
TEXTURES=ROOT/'textures'/'brick_wall_001'
def metric_uv(obj,tile_m=1.1):
    if obj.type!='MESH':return
    if obj.data.users>1:obj.data=obj.data.copy()
    mesh=obj.data
    uv=mesh.uv_layers.get('PBR_MetricUV') or mesh.uv_layers.new(name='PBR_MetricUV')
    mat=obj.matrix_world
    norm=mat.to_3x3().inverted_safe().transposed()
    for p in mesh.polygons:
        n=(norm@p.normal).normalized()
        if abs(n.z)<.8:
            u=Vector((-n.y,n.x,0)).normalized();v=Vector((0,0,1))
        else:u=Vector((1,0,0));v=Vector((0,1,0))
        for li in p.loop_indices:
            co=mat@mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(co.dot(u)/tile_m,co.dot(v)/tile_m)
def shader(mat):
    mat.use_nodes=True;ns=mat.node_tree.nodes;ns.clear()
    out=ns.new('ShaderNodeOutputMaterial');out.location=(700,0)
    bs=ns.new('ShaderNodeBsdfPrincipled');bs.location=(420,0)
    mat.node_tree.links.new(bs.outputs[0],out.inputs['Surface'])
    return ns,mat.node_tree.links,bs
def image_node(ns,file,noncolor=False,texture_set='brick_wall_001'):
    p=ROOT/'textures'/texture_set/file
    if not p.exists():raise FileNotFoundError(p)
    im=bpy.data.images.load(str(p),check_existing=True)
    if noncolor:im.colorspace_settings.name='Non-Color'
    tex=ns.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT'
    im.filepath=bpy.path.relpath(str(p))
    return tex
def upgrade_brick(mat,tint=(1,1,1,1),tile_m=1.1,bump_m=.004,weathering=.18,texture_set='brick_wall_001'):
    ns,lk,bs=shader(mat)
    uv=ns.new('ShaderNodeUVMap');uv.uv_map='PBR_MetricUV';uv.location=(-900,0)
    texs={k:image_node(ns,f,nc,texture_set) for k,f,nc in [('color','diffuse.jpg',False),('normal','normal.jpg',True),('rough','rough.jpg',True),('height','height.jpg',True)]}
    for i,t in enumerate(texs.values()):t.location=(-680,260-i*260);lk.new(uv.outputs['UV'],t.inputs['Vector'])
    hsv=ns.new('ShaderNodeHueSaturation');hsv.inputs['Saturation'].default_value=.75;hsv.inputs['Value'].default_value=1.12
    lk.new(texs['color'].outputs['Color'],hsv.inputs['Color'])
    mix=ns.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=tint
    lk.new(hsv.outputs[0],mix.inputs[1])
    macro=ns.new('ShaderNodeTexNoise');macro.inputs['Scale'].default_value=.16;macro.inputs['Detail'].default_value=2
    lk.new(uv.outputs['UV'],macro.inputs['Vector'])
    variation=ns.new('ShaderNodeMapRange');variation.inputs['To Min'].default_value=.88;variation.inputs['To Max'].default_value=1.10
    lk.new(macro.outputs['Fac'],variation.inputs['Value'])
    breakup=ns.new('ShaderNodeMixRGB');breakup.blend_type='MULTIPLY';breakup.inputs[0].default_value=1
    lk.new(mix.outputs[0],breakup.inputs[1]);lk.new(variation.outputs['Result'],breakup.inputs[2]);lk.new(breakup.outputs[0],bs.inputs['Base Color'])
    lk.new(texs['rough'].outputs['Color'],bs.inputs['Roughness'])
    normal=ns.new('ShaderNodeNormalMap');normal.uv_map='PBR_MetricUV';normal.inputs['Strength'].default_value=.45
    lk.new(texs['normal'].outputs['Color'],normal.inputs['Color'])
    bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.55;bump.inputs['Distance'].default_value=bump_m
    lk.new(texs['height'].outputs['Color'],bump.inputs['Height']);lk.new(normal.outputs['Normal'],bump.inputs['Normal']);lk.new(bump.outputs['Normal'],bs.inputs['Normal'])
    mat['pbr_kind']='scanned brick';mat['pbr_source']='https://polyhaven.com/a/'+texture_set;mat['pbr_license']='CC0';mat['pbr_tile_m']=tile_m
    mat['pbr_note']='Texture is representative masonry, not a scan of this Purdue building; verify coursing and tint against photographs.'
    return mat
def upgrade_surface(mat,kind,color=None):
    old=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if mat.use_nodes else None
    base=tuple(old.inputs['Base Color'].default_value) if old else tuple(mat.diffuse_color)
    ns,lk,bs=shader(mat);bs.inputs['Base Color'].default_value=color or base
    if kind=='glass':
        bs.inputs['Base Color'].default_value=(.68,.81,.84,1);bs.inputs['Roughness'].default_value=.09
        bs.inputs['Transmission Weight'].default_value=.92;bs.inputs['IOR'].default_value=1.46
        mat['pbr_kind']=kind;return mat
    if kind=='metal':bs.inputs['Metallic'].default_value=.82;bs.inputs['Roughness'].default_value=.3
    else:bs.inputs['Roughness'].default_value=.72 if kind=='stone' else .8
    tc=ns.new('ShaderNodeTexCoord');noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=120;noise.inputs['Detail'].default_value=3
    lk.new(tc.outputs['Object'],noise.inputs['Vector'])
    bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.0008 if kind=='stone' else .0015
    lk.new(noise.outputs['Fac'],bump.inputs['Height']);lk.new(bump.outputs['Normal'],bs.inputs['Normal'])
    mat['pbr_kind']=kind;return mat
def classify(name):
    n=name.lower()
    if any(w in n for w in ('brick','masonry','red_clay')):return 'brick'
    if any(w in n for w in ('glass','glazing')):return 'glass'
    if any(w in n for w in ('limestone','bedford','stone','concrete','plaster','stucco')):return 'stone'
    if any(w in n for w in ('copper','bronze','steel','aluminum','aluminium','iron','metal')):return 'metal'
    return None
def upgrade_collection(collection,overrides=None,tint=(1,1,1,1),tile_m=1.1,texture_set='brick_wall_001'):
    overrides=overrides or {};changed={};uvobjects=[]
    for o in collection.all_objects:
        if o.type!='MESH':continue
        brick=False
        for slot in o.material_slots:
            m=slot.material
            if not m:continue
            k=overrides.get(m.name,classify(m.name))
            if k=='brick':brick=True
            if m.name not in changed and k:
                if k=='brick':upgrade_brick(m,tint=tint,tile_m=tile_m,texture_set=texture_set)
                else:upgrade_surface(m,k)
                changed[m.name]=k
        if brick:metric_uv(o,tile_m);uvobjects.append(o.name)
    return {'materials':changed,'brick_uv_objects':uvobjects}
def pack_textures():
    for im in bpy.data.images:
        if im.source=='FILE' and im.filepath and not im.packed_file:
            try:im.pack()
            except RuntimeError:pass
