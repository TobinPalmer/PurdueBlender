import bpy, json, math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset=root/'modular'/'buildings'/'national_soil_erosion_laboratory.blend'
audit=root/'audit'/'batchC_national_soil_erosion'
slope=-0.040643
front_angle=math.atan(slope)
front_line=lambda x:-25.560637+slope*(x-20.253156)
events=[]
panels=['SOIL | R2 continuous blank brick elevation west wing','SOIL | R2 continuous blank brick elevation east left','SOIL | R2 continuous blank brick elevation east right','SOIL | R2 brick lintel above recessed entry']
for name in panels:
    obj=bpy.data.objects[name];obj.location.y=front_line(obj.location.x);obj.rotation_euler.z=front_angle
    events.append({'name':name,'new_y_m':obj.location.y,'rotation_z_rad':front_angle})
door=bpy.data.objects['Soil Lab | approximate recessed main entrance surround'];door.location.y=front_line(door.location.x)+.10;door.rotation_euler.z=front_angle
threshold=bpy.data.objects['SOIL | entrance threshold'];threshold.location.y=front_line(threshold.location.x)-.625;threshold.rotation_euler.z=front_angle
events.extend([{'name':door.name,'new_y_m':door.location.y},{'name':threshold.name,'new_y_m':threshold.location.y}])
for obj in list(bpy.data.objects):
    n=obj.name
    if n.startswith('SOIL | glazing sill') and obj.location.y<-24.0:
        events.append({'removed':n,'reason':'south-front sill remained after evidence-backed blank-facade correction'});bpy.data.objects.remove(obj,do_unlink=True);continue
    if n.startswith('Soil Lab | schematic visible research workbench') or n.startswith('Soil Lab | schematic sample tray'):
        if obj.location.y<-24.0:
            obj.location.y+=1.5;events.append({'name':n,'interior_y_shift_m':1.5})
    if n.startswith('SOIL | R2 entrance vertical metal stile'):
        obj.location.y=front_line(obj.location.x)-.18;obj.rotation_euler.z=front_angle
    elif n.startswith('SOIL | R2 glazed entry door leaf'):
        obj.location.y=front_line(obj.location.x)-.12;obj.rotation_euler.z=front_angle
    elif n in ('SOIL | R2 entrance head frame','SOIL | R2 entrance transom top rail'):
        obj.location.y=front_line(obj.location.x)-.18;obj.rotation_euler.z=front_angle
    elif n=='SOIL | R2 entrance transom glazing':
        obj.location.y=front_line(obj.location.x)-.12;obj.rotation_euler.z=front_angle
    elif n.startswith('SOIL | R2 entrance reveal return'):
        obj.location.y=front_line(obj.location.x);obj.rotation_euler.z=front_angle
    elif n.startswith('SOIL | R2 entrance sign') or n=='SOIL | R2 entrance address plaque':
        obj.location.y=front_line(obj.location.x)-.06;obj.rotation_euler=(math.pi/2,0,front_angle)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
(audit/'nsel_r2_facade_gis_alignment.json').write_text(json.dumps({'basis':'FID242 south edge from local endpoints [20.253156,-25.560637] to [-32.434018,-23.418094] m','slope':slope,'angle_radians':front_angle,'changes':events},indent=2)+'\n',encoding='utf-8')
print(json.dumps(events,indent=2))
