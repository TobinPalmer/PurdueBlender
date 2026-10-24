import bpy, bmesh, math, json
src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend')
facade=bpy.data.collections['Facade_Details']; interior=bpy.data.collections['Schematic_Interior']; structure=bpy.data.collections['Structure']
# Fix the stair sequence so every flight terminates on a landing and the landing connects into the next run.
old=bpy.data.objects.get('KRCH | four-story visible switchback stair and etched glass guard')
assert old
if old: bpy.data.objects.remove(old,do_unlink=True)
for o in list(bpy.data.objects):
 if o.name.startswith('KRCH | continuous stair handrail') or o.name.startswith('KRCH | lobby landing guard'):
  bpy.data.objects.remove(o,do_unlink=True)

def mat(name,color,rough=0.6,metal=0,alpha=1.0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,alpha); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 if bs:
  bs.inputs['Base Color'].default_value=(*color,alpha); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; bs.inputs['Alpha'].default_value=alpha
 if alpha<1: m.surface_render_method='DITHERED'
 return m
stone=mat('KRCH | visible lobby stair cast stone',(0.86,0.81,0.68),0.62)
railglass=mat('KRCH | translucent etched glass gallery guards',(0.64,0.73,0.73),0.36,0,0.32)
railmetal=mat('KRCH | dark handrail cap',(0.12,0.15,0.16),0.28,0.65)
verts=[]; faces=[]; mat_index=[]
def box(cx,cy,cz,sx,sy,sz):
 k=len(verts); verts.extend([(cx-sx/2,cy-sy/2,cz-sz/2),(cx+sx/2,cy-sy/2,cz-sz/2),(cx+sx/2,cy+sy/2,cz-sz/2),(cx-sx/2,cy+sy/2,cz-sz/2),(cx-sx/2,cy-sy/2,cz+sz/2),(cx+sx/2,cy-sy/2,cz+sz/2),(cx+sx/2,cy+sy/2,cz+sz/2),(cx-sx/2,cy+sy/2,cz+sz/2)])
 faces.extend([(k,k+3,k+2,k+1),(k+4,k+5,k+6,k+7),(k,k+1,k+5,k+4),(k+1,k+2,k+6,k+5),(k+2,k+3,k+7,k+6),(k+3,k,k+4,k+7)]); mat_index.extend([0]*6)
def quad(a,b,c,d,mi=1):
 k=len(verts); verts.extend([a,b,c,d]); faces.append((k,k+1,k+2,k+3)); mat_index.append(mi)
levels=[-0.92,2.98,6.88,10.78,14.68]; x0=-23.35; xm=-19.45; xe=-15.55; ya=-10.55; yb=-8.05; n=11; width=1.75
center_y=(ya+yb)/2; landing_width=4.95
# Base landing starts the documented staircase at the basement floor.
box(x0-0.55,center_y,levels[0]+0.04,1.1,landing_width,0.18)
for story,(lo,hi) in enumerate(zip(levels[:-1],levels[1:])):
 mid=(lo+hi)/2; rise=(hi-lo)/2; tread=(xm-x0)/n
 for j in range(n):
  za=lo+(j+1)*rise/n; xa=x0+(j+0.5)*tread
  box(xa,ya,za-0.09,tread+0.02,width,0.18)
  zb=mid+(j+1)*rise/n; xb=xe-(j+0.5)*tread
  box(xb,yb,zb-0.09,tread+0.02,width,0.18)
 # Half-floor landing connects Flight A at xm to Flight B at xe.
 box((xm+xe)/2,center_y,mid-0.10,xe-xm,landing_width,0.20)
 # Upper landing runs from the high end of Flight B back to the low end of the next story's Flight A.
 # It is intentionally within the multi-level atrium void, where source photos show open galleries.
 box((x0+xm)/2,center_y,hi-0.10,xm-x0,landing_width,0.20)
 # Glass guards along both sides of each inclined flight.
 for y in [ya-width/2-0.10,ya+width/2+0.10]:
  quad((x0,y,lo+0.16),(xm,y,mid+0.16),(xm,y,mid+0.98),(x0,y,lo+0.98),1)
 for y in [yb-width/2-0.10,yb+width/2+0.10]:
  quad((xe,y,mid+0.16),(xm,y,hi+0.16),(xm,y,hi+0.98),(xe,y,mid+0.98),1)
 # Edge protection continues across the mid-flight turn and the top-floor connector.
 for y in [ya-width/2-0.10,yb+width/2+0.10]:
  quad((xm,y,mid+0.16),(xe,y,mid+0.16),(xe,y,mid+0.98),(xm,y,mid+0.98),1)
  quad((x0,y,hi+0.16),(xm,y,hi+0.16),(xm,y,hi+0.98),(x0,y,hi+0.98),1)
me=bpy.data.meshes.new('KRCH connected switchback flights and gallery void guard')
me.from_pydata(verts,[],faces); me.materials.append(stone); me.materials.append(railglass); me.update()
for p,mi in zip(me.polygons,mat_index): p.material_index=mi
st=bpy.data.objects.new('KRCH | four-story visible switchback stair and etched glass guard',me); interior.objects.link(st)
st['source_basis']='Purdue Stories Krach stairwell photograph (2022) shows stacked switchback flights and landings; McGrory Glass documents etched laminated glass guards on multilevel lobby galleries.'
st['source_photo']='audit/krach_leadership_center/purdue_krach_stairwell_reference.jpg'
st['continuity']='Each lower flight meets its half-floor landing; the next flight leaves that landing; each upper flight meets a full-floor connector landing spanning x0 to xm, and the next level flight begins on that same connector.'
st['uncertainty']='Flight plan coordinates, tread count, widths, exact landing geometry and elevations are schematic, not measured. Floor-to-floor rhythm remains the existing estimated 3.90 m.'
st['flight_count']=8; st['tread_count']=88; st['landing_count']=9

# Add identifiable pale parapet/coping, visible on the architect's corner image. Preserve the GIS roof outline.
shell=bpy.data.objects['KRCH structural shell | GIS outline']
base=next(p for p in shell.data.polygons if all(abs(shell.data.vertices[i].co.z+1.0)<1e-4 for i in p.vertices))
ring=[shell.data.vertices[i].co.copy() for i in base.vertices]; area=sum(ring[i].x*ring[(i+1)%len(ring)].y-ring[(i+1)%len(ring)].x*ring[i].y for i in range(len(ring)))/2
parapet=bpy.data.objects.get('KRCH | photo-backed pale limestone roof-edge fascia')
if parapet: bpy.data.objects.remove(parapet,do_unlink=True)
pv=[]; pf=[]
for i,a in enumerate(ring):
 b=ring[(i+1)%len(ring)]; dx=b.x-a.x; dy=b.y-a.y; L=math.hypot(dx,dy)
 # outward normal based on source ring winding
 nx,ny=(dy/L,-dx/L) if area>0 else (-dy/L,dx/L)
 off=0.035; x0=a.x+nx*off; y0=a.y+ny*off; x1=b.x+nx*off; y1=b.y+ny*off
 k=len(pv); pv.extend([(x0,y0,15.02),(x1,y1,15.02),(x1,y1,15.60),(x0,y0,15.60)]); pf.append((k,k+1,k+2,k+3))
pme=bpy.data.meshes.new('KRCH pale parapet fascia | GIS perimeter ring'); pme.from_pydata(pv,[],pf)
parapet=bpy.data.objects.new('KRCH | photo-backed pale limestone roof-edge fascia',pme); facade.objects.link(parapet)
stoneframe=bpy.data.materials.get('KRCH | Sasaki photo-backed pale limestone frame'); pme.materials.append(stoneframe)
parapet['reference']='Sasaki architect corner-view photograph shows a light stone/coping band at the flat roof edge.'
parapet['source_url']='https://www.sasaki.com/wp-content/uploads/2019/10/01-Krach_CornerView_2014_8789-1800x1200.jpg'
parapet['height_m']=0.58; parapet['uncertainty']='Fascia height interpreted from perspective photo; no measured elevation detail.'

# The engineering consultant confirms a mechanical penthouse, but its location and dimensions are not published.
# Model a restrained, explicitly schematic screened volume set back on the flat roof.
for o in list(bpy.data.objects):
 if o.name.startswith('KRCH | schematic mechanical penthouse') or o.name.startswith('KRCH | penthouse louver cue'):
  bpy.data.objects.remove(o,do_unlink=True)
roofmat=bpy.data.materials.get('KRACH_LEADERSHIP_CENTER | evidence palette roof')
if roofmat:
 roofmat.diffuse_color=(0.34,0.37,0.37,1); roofmat.use_nodes=True
 bs=roofmat.node_tree.nodes.get('Principled BSDF')
 if bs: bs.inputs['Base Color'].default_value=(0.34,0.37,0.37,1); bs.inputs['Roughness'].default_value=0.84
# Roof box at center set back from the street parapet; exact footprint and height deliberately approximate.
def add_cube(name,center,dims,material,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center); ob=bpy.context.object; ob.name=name; ob.dimensions=dims
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(ob.users_collection): c.objects.unlink(ob)
 col.objects.link(ob); ob.data.materials.append(material); return ob
pent=add_cube('KRCH | schematic mechanical penthouse (location estimated)',(7.0,4.0,16.68),(9.2,4.8,1.92),roofmat,structure)
pent['source_basis']='Fink Roberts & Petrie engineering project page states that Krach includes a mechanical penthouse.'
pent['source_url']='https://frpinc.com/projects/krach-leadership-center/'
pent['uncertainty']='Penthouse presence is documented; exact size, location, cladding and roof elevation are unavailable. This is a low schematic enclosure only.'

# Source tags connect facade family groups to identifiable photograph/text references.
for name,obs,url in [
 ('KRCH | 4-story corner lobby curtainwall panes','Full-height glazed corner bay visible at the near corner in Sasaki exterior photograph.','https://www.sasaki.com/wp-content/uploads/2019/10/01-Krach_CornerView_2014_8789-1800x1200.jpg'),
 ('KRCH | limestone punched-window reveals','Repeated narrow upper-story windows with pale stone surrounds visible across the brick wings in Sasaki exterior photograph.','https://www.sasaki.com/wp-content/uploads/2019/10/01-Krach_CornerView_2014_8789-1800x1200.jpg'),
 ('KRCH | transparent Main Street ground-floor storefront','First-floor Main Street is described as a transparent public/social space by Sasaki.','https://www.sasaki.com/projects/purdue-university-krach-leadership-center/'),
 ('KRCH | pale stone entrance canopy and supports','Main street entry canopy and glazed entry interpreted from Sasaki exterior photograph.','https://www.sasaki.com/wp-content/uploads/2019/10/01-Krach_CornerView_2014_8789-1800x1200.jpg')]:
 o=bpy.data.objects.get(name)
 if o: o['reference_observation']=obs; o['reference_url']=url
# Keep the roof surface flat as pictured; field finish is not claimed as surveyed.
roof=bpy.data.objects.get('KRCH flat roof cap')
if roof: roof['roof_detail_status']='Flat roof cap; parapet band and existence of mechanical penthouse supported by sources. Roof membrane, penthouse dimensions and placement remain estimated.'

bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'stair_bounds_m':[[min(v.co[i] for v in me.vertices),max(v.co[i] for v in me.vertices)] for i in range(3)],'flights':8,'treads':88,'landings':9,'parapet_faces':len(pf),'penthouse_bounds_m':list(pent.dimensions)},indent=2))

