import bpy
for n in ['Purdue_Road_Asphalt_Surface','Purdue_Elevated_Sidewalks_Wide','Purdue_Dedicated_Green_Bike_Lanes','Purdue_Intersection_Crosswalk_Stripes','Purdue_Raised_Concrete_Curbs','Purdue_Road_Yellow_Striping','Purdue_Terrain_Ground']:
 o=bpy.data.objects[n]; pos=sum(p.normal.z>.95 for p in o.data.polygons); neg=sum(p.normal.z<-.95 for p in o.data.polygons); side=len(o.data.polygons)-pos-neg
 print(n,'faces',len(o.data.polygons),'positive',pos,'negative',neg,'side/angled',side,'uv_layers',len(o.data.uv_layers))
