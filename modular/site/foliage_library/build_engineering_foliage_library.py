"""Build a packed, project-local library of reusable foliage and site materials."""
import bpy, json
from uuid import uuid5, NAMESPACE_URL
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
LIB=Path(__file__).resolve().parent/'engineering_foliage_library.blend'
SITE=ROOT/'modular'/'site'
SOURCES=Path(__file__).resolve().parent/'source'

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene

def append_objects(blend_path, names):
    with bpy.data.libraries.load(str(blend_path),link=False) as (src,dst):
        missing=[n for n in names if n not in src.objects]
        if missing: raise RuntimeError(f'Missing objects in {blend_path}: {missing}')
        dst.objects=list(names)
    return [bpy.data.objects[n] for n in names]

def append_materials(blend_path,names):
    with bpy.data.libraries.load(str(blend_path),link=False) as (src,dst):
        missing=[n for n in names if n not in src.materials]
        if missing: raise RuntimeError(f'Missing materials in {blend_path}: {missing}')
        dst.materials=list(names)
    return [bpy.data.materials[n] for n in names]

def make_asset_collection(name, objects, source, lod, variant=None):
    col=bpy.data.collections.new(name); scene.collection.children.link(col)
    for obj in objects: col.objects.link(obj)
    bpy.context.view_layer.update()
    corners=[]
    for obj in objects:
        if obj.type!='MESH': continue
        corners.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
    if corners:
        lo=[min(p[i] for p in corners) for i in range(3)]
        hi=[max(p[i] for p in corners) for i in range(3)]
        dims=[hi[i]-lo[i] for i in range(3)]
        shift=Vector((-(lo[0]+hi[0])*.5,-(lo[1]+hi[1])*.5,-lo[2]))
        for obj in objects: obj.location += shift
        col['asset_bounds_xyz_m']=json.dumps([round(v,6) for v in dims])
        col['asset_origin']='XY centered, Z at source mesh minimum after normalization'
    col['source']=source; col['lod']=lod
    if variant: col['variant']=variant
    col['license']='CC0 1.0 Universal, Poly Haven asset' if source.startswith('Poly Haven') else 'PurdueMap project asset; see source provenance'
    return col

# Use the full source LOD1 canopy, then bake a conservative decimation while preserving material
# boundaries and UVs. The tiny loose leaf-cluster objects are Geometry Nodes inputs, not trees alone.
tree_path=SOURCES/'tree_small_02'/'tree_small_02.blend'
tree_obj=append_objects(tree_path,['tree_small_02_LOD1'])[0]
tree_temp=bpy.data.collections.new('_TEMP_TREE_LOD1'); scene.collection.children.link(tree_temp); tree_temp.objects.link(tree_obj)
tree_mod=tree_obj.modifiers.new('Baked leaf-preserving LOD2 reduction','DECIMATE'); tree_mod.ratio=1.0
tree_mod.delimit={'MATERIAL'}
bpy.context.view_layer.update()
tree_eval=tree_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
tree_reduced=tree_eval.to_mesh().copy(); tree_eval.to_mesh_clear()
tree_obj.modifiers.clear(); tree_obj.data=tree_reduced
tree_temp.objects.unlink(tree_obj); bpy.data.collections.remove(tree_temp)
tree_col=make_asset_collection('PH_Tree_Small_02_LOD2', [tree_obj],
    'Poly Haven tree_small_02 native LOD1 with full leaf coverage; shared collection retains stable LOD2 identifier','LOD2 decimated composite')

# Supplement the open source crown with a rotated leaf-only layer.
import bmesh, math
leaf_mesh=tree_obj.data.copy()
bm=bmesh.new(); bm.from_mesh(leaf_mesh)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index != 1], context='FACES')
bm.to_mesh(leaf_mesh); bm.free()
leaf_layer=bpy.data.objects.new('Broadleaf_fuller_crown_leaf_layer',leaf_mesh)
leaf_layer.location=tree_obj.location.copy()
leaf_layer.rotation_euler.z=math.radians(47)
leaf_layer['adaptation']='Rotated source leaf cards to provide fuller summer coverage; trunk unchanged'
tree_col.objects.link(leaf_layer)
# Low-cost texture-card shrubs in four distinct silhouettes.
shrub_cols=[]
for asset in ('shrub_02','shrub_04'):
    src=SOURCES/asset/f'{asset}.blend'
    for variant in 'abcd':
        obj_name=f'{asset}_{variant}_LOD2'
        obj=append_objects(src,[obj_name])[0]
        shrub_cols.append(make_asset_collection(f'PH_{asset.title()}_{variant.upper()}_LOD2',[obj],
            f'Poly Haven {asset}, variant {variant}','LOD2',variant))

# Fern variants are useful for planted beds, but no Arboretum fern points are inferred here.
fern_path=SOURCES/'fern_02'/'fern_02.blend'
with bpy.data.libraries.load(str(fern_path),link=False) as (src,dst):
    if 'fern_02' not in src.collections: raise RuntimeError('fern_02 collection missing')
    dst.collections=['fern_02']
fern_src=dst.collections[0]
fern_objs=list(fern_src.all_objects)
fern_col=make_asset_collection('PH_Fern_02_Variants',[o for o in fern_objs if o.type=='MESH'],
    'Poly Haven fern_02, variants a–d','source collection')

# Select compact LOD2 specimens for a reusable small-clump asset; lawn area remains a surface.
grass_path=SOURCES/'grass_medium_01'/'grass_medium_01.blend'
grass_names=['grass_medium_01_small_a_LOD2','grass_medium_01_small_b_LOD2',
             'grass_medium_01_mid_a_LOD2','grass_medium_01_tall_a_LOD2']
grass_objs=append_objects(grass_path,grass_names)
grass_col=make_asset_collection('PH_Grass_Medium_01_Selective_LOD2',grass_objs,
    'Poly Haven grass_medium_01, selected small/mid/tall LOD2 tufts','LOD2 selective variants')
grass_col['placement_guidance']='Selective planting only; not a blanket lawn scatter.'

# Three real fir sapling variants cover mapped evergreen planting. A baked 0.24 decimation keeps
# alpha-card detail while reducing each reusable mesh to a campus-friendly LOD2 budget.
fir_path=SOURCES/'fir_sapling'/'fir_sapling.blend'
fir_objects=append_objects(fir_path,['fir_sapling_a','fir_sapling_b','fir_sapling_c'])
fir_cols=[]
for variant,obj in zip('ABC',fir_objects):
    mesh=obj.data.copy(); obj.data=mesh
    temp=bpy.data.collections.new(f'_TEMP_FIR_{variant}'); scene.collection.children.link(temp); temp.objects.link(obj)
    dec=obj.modifiers.new('Baked LOD2 polygon reduction','DECIMATE'); dec.ratio=.40
    bpy.context.view_layer.update()
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    reduced=evaluated.to_mesh().copy(); evaluated.to_mesh_clear()
    obj.modifiers.clear(); obj.data=reduced
    temp.objects.unlink(obj); bpy.data.collections.remove(temp)
    fir_cols.append(make_asset_collection(f'PH_Fir_Sapling_{variant}_LOD2',[obj],
        f'Poly Haven fir_sapling, variant {variant}; source mesh decimated to 24% for campus instancing','LOD2',variant))

# Reuse project hardscape materials authored in the site collection.
site=SITE/'campus_site.blend'
reuse_names=['Campus_Walkway_Concrete','Manicured_Campus_Lawn','Purdue_Landscape_Green',
             'Plaza_Architectural_Concrete','Plaza_Purdue_Red_Brick_Pavers',
             'Street_Asphalt_Dark','Street_Curb_Concrete']
materials=append_materials(site,reuse_names)
for material in materials:
    material['source']='PurdueMap modular/site/campus_site.blend'
    material['reuse_status']='reused existing campus hardscape material'
    material.use_fake_user=True
grass_pbr=append_materials(SOURCES/'grass_ground'/'grass_ground.blend',['grass_ground'])[0]
asphalt_pbr=append_materials(SOURCES/'asphalt_01'/'asphalt_01.blend',['asphalt_01'])[0]
for material,provider in ((grass_pbr,'Poly Haven grass_ground 1K PBR'),(asphalt_pbr,'Poly Haven asphalt_01 1K PBR')):
    material['source']=provider; material['license']='CC0 1.0 Universal, Poly Haven'
    material['reuse_status']='packed tileable PBR material'
    material.use_fake_user=True

# Reusable site props are catalogued without adding any new placements to the patch.
prop_names=['Fountain_Perimeter_Bench_90','LoebFountain_Granite_Bollard_0','LoebFountain_Bollard_Nozzle_Cap_0',
            'FoundersPark_Campus_LampPost_Shaft_0','FoundersPark_Campus_LampPost_Base_0']
prop_objects=append_objects(site,prop_names)
project_props=[]
for prop in prop_objects[:3]:
    project_props.append(make_asset_collection(f'PurdueMap_{prop.name}_Asset',[prop],
        f'Existing campus_site.blend object {prop.name}; extracted for project reuse','source object'))
project_props.append(make_asset_collection('PurdueMap_Campus_LampPost_Asset',prop_objects[3:],
    'Existing campus_site.blend lamp post shaft and base; assembled as reusable source prop','source object family'))

# Explicit top-level library index for asset browsers and other patch builders.
index=bpy.data.collections.new('Engineering_Foliage_Library_Index'); scene.collection.children.link(index)
for collection in [tree_col,*shrub_cols,fern_col,grass_col,*fir_cols,*project_props]: index.children.link(collection)
index['asset_provenance']='Poly Haven downloadable source assets; all source files are included under source/.'
index['asset_license']='Mixed: Poly Haven assets/materials are CC0 1.0; extracted PurdueMap assets/materials retain project provenance. See each item properties and README.'
index['material_catalog']=json.dumps(reuse_names)

catalogs={
    'Foliage/Trees':'f79c4b61-ec18-4b12-9fc7-5aaaf227d4d1',
    'Foliage/Shrubs':'ca79e5c6-2349-4bc9-807b-a83ea9e9d4a8',
    'Foliage/Groundcover':'43aa74c2-a84e-4ee3-b2f5-1ad640f9444f',
    'Campus/Props':'98cbb166-0b28-42e4-8974-685f08f80355',
    'Campus/Materials':'8eb99b09-9d36-4bd5-b15b-032e120be30a',
}
def mark_asset(id_block,catalog,description,tags):
    id_block.asset_mark()
    id_block.asset_data.description=description
    id_block.asset_data.catalog_id=catalogs[catalog]
    for tag in tags: id_block.asset_data.tags.new(tag)
mark_asset(tree_col,'Foliage/Trees','Reusable Poly Haven tree_small_02 textured broadleaf tree; material-delimited decimated LOD2.', ['foliage','tree','lod2','cc0'])
for asset_col in shrub_cols:
    category='Foliage/Groundcover' if 'shrub_04' in asset_col.name else 'Foliage/Shrubs'
    mark_asset(asset_col,category,f'Reusable source {asset_col.name}; packed textures; LOD2.', ['foliage','shrub','lod2','cc0'])
mark_asset(fern_col,'Foliage/Groundcover','Four reusable fern_02 variants from Poly Haven; no unsupported placements in the Engineering Mall patch.', ['foliage','fern','cc0'])
mark_asset(grass_col,'Foliage/Groundcover','Selected small, mid and tall grass_medium_01 LOD2 tufts for selective planting only.', ['foliage','grass','lod2','cc0'])
for asset_col in fir_cols: mark_asset(asset_col,'Foliage/Trees',f'Poly Haven fir_sapling variant {asset_col.get("variant")}, decimated LOD2 for mapped evergreen tree placement.', ['foliage','evergreen','fir','lod2','cc0'])
for asset_col in project_props:
    mark_asset(asset_col,'Campus/Props',asset_col.get('source','PurdueMap site prop'),['campus','prop','purdue-map'])
for material in materials:
    mark_asset(material,'Campus/Materials',f'Reused from modular/site/campus_site.blend: {material.name}.',['campus','material','purdue-map'])
mark_asset(grass_pbr,'Campus/Materials','Poly Haven grass_ground 1K tileable PBR material; used on OSM turf areas only.',['grass','pbr','cc0'])
mark_asset(asphalt_pbr,'Campus/Materials','Poly Haven asphalt_01 1K tileable PBR material; used on OSM asphalt/service roads only.',['asphalt','pbr','cc0'])

# Pack every referenced image so the library opens independent of source paths.
bpy.ops.file.pack_all()
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:
        raise RuntimeError(f'Unpacked image remains: {image.name} at {image.filepath}')
bpy.ops.wm.save_as_mainfile(filepath=str(LIB),compress=True)
(LIB.parent/'blender_assets.cats.txt').write_text('VERSION 1\n'+''.join(f'{uid}:{catalog}:{catalog.split("/")[-1]}:Reusable project assets\n' for catalog,uid in catalogs.items()),encoding='utf-8')
print('LIBRARY_SAVED',LIB)
print('COLLECTIONS',[(c.name,c.get('asset_bounds_xyz_m'),len(c.all_objects)) for c in [tree_col,*shrub_cols,fern_col,grass_col]])
print('MATERIALS',[(m.name,len(m.node_tree.nodes) if m.node_tree else 0) for m in [*materials,grass_pbr,asphalt_pbr]])
print('PACKED_IMAGES',sum(bool(i.packed_file) for i in bpy.data.images),'TOTAL_IMAGES',len(bpy.data.images))
print('ASSETS_MARKED',sum(bool(idb.asset_data) for idb in [*bpy.data.collections,*bpy.data.materials]))


