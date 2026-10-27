import bpy,json,math
p=r'modular/buildings/massing_house_1089876362_14ecd2c.blend'
bpy.ops.wm.open_mainfile(filepath=p)
o=bpy.data.objects['House_1089876362']
verts=[o.matrix_world @ v.co for v in o.data.vertices]
ring=[]
for v in verts:
 if abs(v.z-min(q.z for q in verts))<0.01: ring.append([round(v.x,6),round(v.y,6)])
# order is original mesh vertex index order
json.dump({'base_ring_xy':ring,'bounds':{'xmin':min(v.x for v in verts),'xmax':max(v.x for v in verts),'ymin':min(v.y for v in verts),'ymax':max(v.y for v in verts)}},open('audit/kappa_delta_rho/source_model_probe.json','w'),indent=2)
