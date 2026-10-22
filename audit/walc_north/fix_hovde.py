import bpy,pathlib,shutil,json
from mathutils import Matrix
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=P/'audit/walc_north';path=P/'modular/buildings/hovde_hall.blend';shutil.copy2(path,D/'hovde_before.blend');bpy.ops.wm.open_mainfile(filepath=str(path));col=bpy.data.collections['Asset_hovde_hall'];root=bpy.data.objects['HOVD_Root'];changed=[]
# Register the entrance assembly only to official east-side projection: depth3.58m,width14.63m.
sy=14.63/18.8;sx=3.58/7.2
T=Matrix(((0,-sx,0,10.8-35.5*sx),(sy,0,0,-.255),(0,0,1,0),(0,0,0,1)))
site=Matrix(((0,-1,0,-24.7),(1,0,0,0),(0,0,1,0),(0,0,0,1)))
for o in list(col.all_objects):
 n=o.name
 if n.startswith(('HOVD_Portico_','HOVD_Col_','HOVD_Sign_','HOVD_Door_','HOVD_Grand_Step_')):
  assert o.parent==root,n;o.matrix_basis=T@o.matrix_basis;changed.append(n)
 elif n.startswith(('HOVD_Plaza_','HOVD_Planter_','HOVD_Bench_','HOVD_Bike_','HOVD_Lantern_')):
  assert o.parent==root,n;o.matrix_basis=site@o.matrix_basis;changed.append(n)
# Close the inherited door opening at the incorrect south end; preserve four walls and add backing at moved door site.
bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name='HOVD_South_End_Former_Entrance_Infill';o.parent=root;o.location=(0,-35.15,5.25);o.scale=(3.6,.35,5.25)
for c in list(o.users_collection):c.objects.unlink(o)
col.objects.link(o);mat=bpy.data.objects['HOVD_Wall_South_Center_Upper'].data.materials
if mat:o.data.materials.append(mat[0])
col['horizontal_review']='Core retained; entrance and site moved from incorrect south end to official east-side projection. Portico plan14.63x3.58m from official polygon. Facade height/details remain estimates.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert bpy.data.objects.get('HOVD_South_End_Former_Entrance_Infill')
(D/'hovde_correction.json').write_text(json.dumps({'id':'hovde_hall','source':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','provider':'Purdue GIS','fid':618,'retrieved':'2026-10-22','source_crs':'EPSG4326','transform':'Project origin40.4274,-86.9137;X84810.6041654m/degree;Y111040m/degree;local HOVD root(-62.85,93) rotated39.52deg','raw_source_snapshot':'../official_purdue_buildings_wgs84.json','change':'Portico, columns, entrance doors and steps transferred to east long-side entrance. Portico only plan scaled to official14.63m width and3.58m projection; core unscaled. Site furniture rigidly rotated and relocated with entrance. Former incorrect south door gap infilled.','source_date':'not provided','main_core_approximate_plan':'Source21.6x71m; official approx21.5x70.4m excludes portico. Core offset submeter retained pending finer wall correspondence.','height':'Unverified existing estimates retained','site':'Dimensions/layout remain estimates; moved away from false south entrance','changed_objects':changed,'reopened':True},indent=2))
