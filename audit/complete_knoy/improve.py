import bpy,math,json
from mathutils import Vector
c=bpy.data.collections['Asset_knoy_hall'];root=bpy.data.objects['AssetRoot_knoy_hall']
m=bpy.data.materials.new('KNOY_Ground_Painted_Partitions');m.diffuse_color=(.73,.72,.66,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.78
# Manual trace of Purdue-hosted dissertation Fig3.19(d), PDFpage77; local fit ~0.5-1.5m uncertainty.
def pt(p):return Vector(((p[1]-100)*.126-15,(p[0]-64)*.13-46,0))
segments=[((100,158),(100,298)),((118,143),(485,143)),((118,321),(228,321)),((246,294),(302,294)),((320,278),(373,225)),((406,230),(505,327)),((524,313),(627,211)),((645,228),(708,290)),((143,165),(143,290)),((203,165),(203,290)),((294,165),(294,211)),((203,225),(283,225)),((203,260),(283,260)),((225,246),(225,282)),((341,165),(341,210)),((378,165),(378,208)),((414,165),(414,180))]
# North office wing trace: visible module grid without guessed room numbering.
for a,b in [((420,243),(503,326)),((443,221),(526,304)),((468,198),(552,281)),((491,175),(575,258)),((518,152),(600,235))]:segments.append((a,b))
for a,b in [((438,262),(539,161)),((460,285),(560,185)),((483,309),(584,208)),((547,285),(624,208)),((571,308),(647,231))]:segments.append((a,b))
for i,(a,b) in enumerate(segments):
 p,q=pt(a),pt(b);mid=(p+q)/2;mid.z=1.55
 bpy.ops.mesh.primitive_cube_add(size=1,location=mid);o=bpy.context.object;o.name='KNOY_Ground_TracePartition_%02d'%i;o.dimensions=((q-p).length,.13,2.8);o.rotation_euler.z=math.atan2(q.y-p.y,q.x-p.x);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m);o['evidence']='Liu dissertation Fig3.19d manual raster trace';o['uncertainty_m']=1.5
# Preserve exact local frame. New partitions are local matrix positions, root identity.
bpy.context.scene['interior_status']='Partial ground partition trace from published research floorplan; locations approximate ±1.5m; upper floors and furnishings unverified'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('added',len(segments))
