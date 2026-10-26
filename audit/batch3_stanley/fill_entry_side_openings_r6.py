"""Close the two unsupported blank holes beside Stanley's east main entrance."""
import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend';AUDIT=ROOT/'audit/batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_stanley_coulter_hall']
band=bpy.data.objects['SC_R6_East_Glazing_Band_Entry']
pts=[band.matrix_world@v.co for v in band.data.vertices]
y0=min(p.y for p in pts);y1=max(p.y for p in pts)
ends=[]
for y in (y0,y1):ends.append((y,max(p.x for p in pts if abs(p.y-y)<1e-6)))
def xfront(y):return ends[0][1]+(ends[1][1]-ends[0][1])*(y-ends[0][0])/(ends[1][0]-ends[0][0])

brick=bpy.data.materials.get('Purdue_Red_Brick_Procedural')
if not brick:raise RuntimeError('Missing Purdue procedural brick material')
def panel(name,a,b,z0,z1):
    # Fill the space between the nearest first-floor window and the portal frame.
    xa,xb=xfront(a),xfront(b);d=.22
    verts=[(xa,a,z0),(xb,b,z0),(xb,b,z1),(xa,a,z1),(xa-d,a,z0),(xb-d,b,z0),(xb-d,b,z1),(xa-d,a,z1)]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    m=bpy.data.meshes.new(name+'_Mesh');m.from_pydata(verts,[],faces);m.materials.append(brick);m.update()
    o=bpy.data.objects.new(name,m);asset.objects.link(o)
    o['R6_evidence']='Brick infill closes unmodeled view-through gaps visible beside the documented main entry; photo shows brick piers flanking the stone portal. Dimensions are fitted to adjacent modeled openings.'
    return o

left=panel('SC_R6_Entry_Brick_Infill_Left',-7.84,-5.56,1.82,5.42)
right=panel('SC_R6_Entry_Brick_Infill_Right',-2.44,.15,1.82,5.42)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'asset':str(ASSET),'sha256':sha,'objects':[left.name,right.name],'bounds':{o.name:[[min((o.matrix_world@Vector(c))[i] for c in o.bound_box) for i in range(3)],[max((o.matrix_world@Vector(c))[i] for c in o.bound_box) for i in range(3)]] for o in (left,right)},'source':'https://www.cla.purdue.edu/academic/english/images/stanleycoulterhall.jpg','note':'The facade photograph shows red brick at both sides of the stone portal. The previous blank rectangles were view-through gaps in the exported wall geometry.'}
(AUDIT/'entry_infill_r6.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
