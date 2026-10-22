import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
asset=bpy.data.collections['Asset_bell_tower'];obs=list(asset.all_objects)
def bounds(objects):
 vs=[o.matrix_world@Vector(c) for o in objects if o.type in {'MESH','FONT'} for c in o.bound_box]
 return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
bb=bounds(obs);ref=json.loads((P/'official_BELL_reference.json').read_text());shaft=bpy.data.objects['Shaft_Structural_Envelope'];center=list(shaft.matrix_world.translation);rc=ref['official_polygon_center_xy_m'];report={'reopen':True,'export_collection':asset.name,'objects':len(obs),'bounds':bb,'shaft_center_xy':center[:2],'mapped_center_residual_m':math.dist(center[:2],rc),'roof_peak_height_m':bb[1][2],'published_height_m':48.768,'clock_dials':sum('Ivory_Dial' in o.name for o in obs),'roman_markings':sum('_Roman_' in o.name for o in obs),'bells':sum(o.name.startswith('Historic_Bell_') for o in obs),'preview_in_asset':any('Preview' in o.name for o in obs),'external_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file]}
assert report['clock_dials']==4 and report['roman_markings']==48 and report['bells']==4
assert report['mapped_center_residual_m']<1e-4
corners=[shaft.matrix_world@Vector(c) for c in shaft.bound_box]
poly=[]
for v in corners:
 if not any(math.dist(v[:2],p)<1e-5 for p in poly):poly.append(tuple(v[:2]))
poly.sort(key=lambda p:math.atan2(p[1]-center[1],p[0]-center[0]))
ring=ref['rings_xy_m'][0][:-1]
def ds(p,a,b):
 d=Vector(b)-Vector(a);t=max(0,min(1,(Vector(p)-Vector(a)).dot(d)/d.length_squared));return (Vector(p)-(Vector(a)+t*d)).length
def residual(a,b):
 return max(min(ds(p,b[i],b[(i+1)%len(b)]) for i in range(len(b))) for j in range(len(a)) for k in range(101) for p in [tuple(a[j][n]+(a[(j+1)%len(a)][n]-a[j][n])*k/100 for n in range(2))])
report['structural_square_vs_GIS_polygon_boundary_max_sampled_distance_m']=max(residual(poly,ring),residual(ring,poly))
def svgpoints(vs):return ' '.join(f'{300+(v[0]-center[0])*52:.2f},{300-(v[1]-center[1])*52:.2f}' for v in vs)
(P/'footprint_comparison.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="680" viewBox="0 0 600 680"><rect width="600" height="680" fill="#faf9f5"/><text x="30" y="35" font-family="sans-serif" font-size="21">Bell Tower: structural envelope</text><polygon points="'+svgpoints(ring)+'" fill="none" stroke="#008080" stroke-width="6"/><polygon points="'+svgpoints(poly)+'" fill="none" stroke="#dc4c36" stroke-width="2"/><text x="30" y="590" fill="#008080" font-family="sans-serif" font-size="18">Purdue GIS BELL / FID 290</text><text x="30" y="620" fill="#dc4c36" font-family="sans-serif" font-size="18">Reconstructed equivalent structural square</text><text x="30" y="653" font-family="sans-serif" font-size="14">Local meters; mapped envelope is not a certified survey.</text></svg>')
# Save an identical-angle original comparison using current preview stage.
scene=bpy.context.scene
for c in list(scene.collection.children):
 if c==asset:scene.collection.children.unlink(c)
with bpy.data.libraries.load(str(P/'original.blend'),link=False) as (s,d):d.collections=['Asset_bell_tower']
orig=d.collections[0];scene.collection.children.link(orig)
scene.render.filepath=str(P/'before_full.png');scene.cycles.samples=16;bpy.ops.render.render(write_still=True)
# Fresh scene library compatibility: exact exported name and identity instance.
bpy.ops.wm.read_factory_settings(use_empty=True)
path=P.parent/'buildings/bell_tower.blend'
with bpy.data.libraries.load(str(path),link=True) as (s,d):
 report['library_export_present']='Asset_bell_tower' in s.collections
 d.collections=['Asset_bell_tower']
inst=bpy.data.objects.new('BellTower_Link_Compatibility_Test',None);inst.instance_type='COLLECTION';inst.instance_collection=d.collections[0];bpy.context.scene.collection.objects.link(inst)
report['identity_instance']=inst.matrix_world==Matrix.Identity(4)
report['linked_object_count']=len(inst.instance_collection.all_objects)
(P/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
