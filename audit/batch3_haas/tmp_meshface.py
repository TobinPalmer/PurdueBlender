import bpy
for n in ['HAAS_R7_EastFacade_Inlaid_Brickwork','HAAS_R8_EastWing_Brick_Inlays_EST']:
 o=bpy.data.objects[n];m=o.data;print(n,len(m.vertices),len(m.polygons),tuple(m.bounds[0]) if False else '')
 for i,p in enumerate(m.polygons[:12]):print(i,len(p.vertices),[tuple(round(x,3) for x in m.vertices[v].co) for v in p.vertices])
