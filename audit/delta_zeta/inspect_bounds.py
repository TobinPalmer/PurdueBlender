import bpy,json,math
bpy.ops.wm.open_mainfile(filepath='modular/buildings/massing_house_301841601_7ae6159.blend');o=bpy.data.objects['House_301841601'];p=json.load(open('audit/delta_zeta/sources/purdue_gis_fid752_raw.json'))['features'][0]['geometry']['rings'][0][:-1]
lat0=40.4274;lon0=-86.9137;xy=[((x-lon0)*111412.84*math.cos(math.radians(lat0)),(y-lat0)*111040) for x,y in p];p0,p1=xy[:2];dx=p1[0]-p0[0];dy=p1[1]-p0[1];L=math.hypot(dx,dy);u=(dx/L,dy/L);n=(dy/L,-dx/L)
coords=[o.matrix_world@v.co for v in o.data.vertices];v=max(coords,key=lambda v:v.y);print('maxY',tuple(v));ds=v.x-p0[0];dt=v.y-p0[1];print('local approx',ds*u[0]+dt*u[1],ds*n[0]+dt*n[1]);print('upper ten',sorted([(round(v.y,3),round(v.x,3),round(v.z,3)) for v in coords],reverse=True)[:10])
