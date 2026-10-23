import bpy, json, math
from pathlib import Path
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall']
# Replace any prior pass of this detail group.
for n in ['HAAS_R6_Estimated_Interior_Door_Leaves','HAAS_R6_Estimated_Interior_Door_Frames']:
    o=bpy.data.objects.get(n)
    if o:bpy.data.objects.remove(o,do_unlink=True)
rooms=json.loads(Path('audit/batch3_haas/changes.json').read_text(encoding='utf-8'))['rooms']
leaves_v=[];leaves_f=[];frames_v=[];frames_f=[]
def add_box(vs,fs,center,dims,angle=0,hinge=None):
    cx,cy,cz=center;dx,dy,dz=[d/2 for d in dims]
    coords=[(-dx,-dy,-dz),(dx,-dy,-dz),(dx,dy,-dz),(-dx,dy,-dz),(-dx,-dy,dz),(dx,-dy,dz),(dx,dy,dz),(-dx,dy,dz)]
    ca,sa=math.cos(angle),math.sin(angle);base=len(vs)
    for x,y,z in coords:
        x+=cx;y+=cy
        if hinge is not None:
            x,y=hinge[0]+ca*x-sa*y,hinge[1]+sa*x+ca*y
        vs.append((x,y,z if hinge is None else z+hinge[2]))
    fs.extend([tuple(base+i for i in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
def xy(u,v):return (-26+(v-97)*28.1/713,26.5-(u-48)*52.5/1417)
width=.82;height=2.12;floor_z=.42;angle=math.radians(-45)
for room in rooms:
    rid,(u0,v0,u1,v1),kind=room;mid=(u0+u1)/2;gap=14
    xwall=xy(mid,v1)[0];hingey=xy(mid-gap,v1)[1]
    # One open, inward-swinging door per plan room. Position/swing and dimensions are estimates.
    add_box(leaves_v,leaves_f,(0,-width/2,height/2),(0.045,width,height),angle,(xwall,hingey,floor_z))
    jamb_y=(hingey,hingey-width)
    for yy in jamb_y:
        add_box(frames_v,frames_f,(xwall,yy,floor_z+height/2),(0.14,.075,height+.04))
    add_box(frames_v,frames_f,(xwall,hingey-width/2,floor_z+height+.03),(0.14,width+.12,.09))
def mesh_obj(name,verts,faces,material,prop):
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(material);mesh.update()
    o=bpy.data.objects.new(name,mesh);c.objects.link(o);o["geometry_basis"]=prop;return o
wood=bpy.data.materials.new('HAAS_R6_Interior_Door_Wood_estimated');wood.diffuse_color=(.34,.19,.09,1);wood.use_nodes=True
pbs=wood.node_tree.nodes.get('Principled BSDF');pbs.inputs['Base Color'].default_value=(.34,.19,.09,1);pbs.inputs['Roughness'].default_value=.7
plaster=bpy.data.materials.get('HAAS_Plan_Painted_Plaster_estimated')
prop='Estimated 0.82 m x 2.12 m leaf and centered swing opening at plan room lower edge; published plan has no metric scale or door-swing dimensions.'
leaf=mesh_obj('HAAS_R6_Estimated_Interior_Door_Leaves',leaves_v,leaves_f,wood,prop)
frame=mesh_obj('HAAS_R6_Estimated_Interior_Door_Frames',frames_v,frames_f,plaster,'Estimated jamb/head trim around plan-derived room entries; metric dimensions inferred.')
leaf['door_count']=len(rooms);frame['door_count']=len(rooms)
# Save a concise, explicit trace of the added plan-derived vs inferred detail.
Path('audit/batch3_haas/round6_interior.json').write_text(json.dumps({'door_leaves':len(rooms),'frames':len(rooms),'basis':'Room identities/adjacencies from the Purdue first-floor plan; door locations, widths, heights, and swing directions are estimated.','objects':2},indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('R6_INTERIOR_ADDED',len(rooms),len(leaves_f)//6,len(frames_f)//6,len(c.objects))
