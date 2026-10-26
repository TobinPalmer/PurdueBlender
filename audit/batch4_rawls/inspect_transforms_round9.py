import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];ASSET=ROOT/'modular/buildings/rawls_hall.blend';OUT=Path(__file__).with_name('round9_transform_inventory.json');bpy.ops.wm.open_mainfile(filepath=str(ASSET))
names=['AssetRoot_rawls_hall','RAWL_Masonry_Exterior_Walls','RAWL_SE_Diagonal_CurtainWall_Glass','RAWL_SE_Diagonal_CurtainWall_BronzeMullions','RAWL_South_Windows_South_Glass','RAWL_North_Windows_Glass']
items=[]
for n in names:
 o=bpy.data.objects[n]
 items.append({'name':n,'parent':o.parent.name if o.parent else None,'location':list(o.location),'matrix_parent_inverse':[list(row) for row in o.matrix_parent_inverse],'matrix_world':[list(row) for row in o.matrix_world],'verts':len(o.data.vertices) if o.type=='MESH' else None})
OUT.write_text(json.dumps(items,indent=2));print(json.dumps(items,indent=2))
