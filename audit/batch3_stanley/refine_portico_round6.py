import bpy, math, json
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']
portico=bpy.data.collections['SC_Portico_and_Entrances']
def world_bounds(o):
 pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
 return Vector(tuple(min(v[i] for v in pts) for i in range(3))),Vector(tuple(max(v[i] for v in pts) for i in range(3)))
def transform_world(o,scale=(1,1,1),pivot=None):
 lo,hi=world_bounds(o); ctr=Vector(pivot) if pivot else (lo+hi)*.5; inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  q=o.matrix_world@v.co
  q=Vector(tuple(ctr[i]+(q[i]-ctr[i])*scale[i] for i in range(3)))
  v.co=inv@q
 o.data.update()
for o in list(portico.objects):
 if o.name.startswith('SC_Portico_Step_'):
  transform_world(o,scale=(0.62,0.54,1),pivot=(30.45,-3.95,0.90))
 elif o.name.startswith('SC_Portico_Balustrade_') or o.name.startswith('SC_Portico_Pedestal_'):
  # narrow the side wings about the staircase flanks without moving their run
  transform_world(o,scale=(0.62,0.54,1),pivot=(30.45,-3.95,0.90))
 elif o.name=='SC_Portico_Porch_Slab':
  transform_world(o,scale=(0.78,0.43,1),pivot=(29.815,-3.975,1.775))
# Slim down columns horizontally while maintaining their current verified alignment to the portal.
for n in ('SC_Portico_Column_Plinth_0','SC_Portico_Column_Shaft_0','SC_Portico_Column_Capital_0','SC_Portico_Column_Plinth_3','SC_Portico_Column_Shaft_3','SC_Portico_Column_Capital_3'):
 o=bpy.data.objects.get(n)
 if o: transform_world(o,scale=(0.72,0.72,1))
# Document evidence dates and model limits on scene.
scene=bpy.context.scene
scene['Google Maps verification']='Place card / satellite map observed 2026-10-23; Street View & 360 listing opened to interior panorama by Kaho Sakaue, capture Jun 2021. No street-facing panorama was exposed in this view.'
scene['Entry review note']='Current Google Maps photo shows a rectangular pale stone entry frame and glazed doors. Model entry is simplified; 2022 plans historical only; dimensions/details not measured.'
bpy.ops.wm.save_as_mainfile(filepath=p)
print('saved',p, 'asset',len(bpy.data.collections['Asset_stanley_coulter_hall'].all_objects),'root',list(root.location),list(root.scale))
