from mathutils import Euler,Vector
for loc,rot in [((114.02,-127.55,77.3),(1.168,0,.729)),((86.04,-96.25,58.33),(1.179,0,.729))]:
 d=Euler(rot).to_matrix()@Vector((0,0,-1)); print('dir',d,'target if 150',Vector(loc)+d*150)
