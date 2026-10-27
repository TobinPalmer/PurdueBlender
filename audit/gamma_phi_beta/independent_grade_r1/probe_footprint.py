import bpy,json,math
p='audit/gamma_phi_beta/gis_feature_fid_759.json'
data=json.load(open(p)); feat=data['features'][0]; geom=feat['geometry']; rings=geom['rings']; ring=rings[0][:-1]
origin=(-1030.3176174569167,706.9364654213132)
proj=[]
for lon,lat in ring:
    proj.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274))-origin[0],(lat-40.4274)*111040-origin[1]))
wall=[o for o in bpy.data.collections['Asset_gamma_phi_beta'].objects if o.name.startswith('GPB GIS exterior wall')]
# Gather each wall's mesh coords in local asset frame at z near base
verts=[]
for o in wall:
    for v in o.data.vertices:
        co=o.matrix_world@v.co
        if abs(co.z)<1e-5:
            xy=(round(co.x,5),round(co.y,5))
            if xy not in verts: verts.append(xy)
# nearest map and reverse matching
errors=[]
for x,y in proj:
    errors.append(min(math.hypot(x-vx,y-vy) for vx,vy in verts))
result={'gis_ring_count':len(proj),'unique_shell_base_vertices':len(verts),'per_gis_nearest_residual_m':errors,'max_residual_m':max(errors),'area_transform_m2':abs(sum(proj[i][0]*proj[(i+1)%len(proj)][1]-proj[(i+1)%len(proj)][0]*proj[i][1] for i in range(len(proj)))/2)}
open(r'audit/gamma_phi_beta/independent_grade_r1/footprint_probe.json','w').write(json.dumps(result,indent=2))
