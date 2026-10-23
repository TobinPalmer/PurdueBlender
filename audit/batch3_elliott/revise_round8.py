"""Round 8: clarify Elliott upper entry, defer unverified cross-building connector, and improve interior evidence."""
import bpy, math, json, pathlib
from mathutils import Vector
ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); AUD=ROOT/'audit/batch3_elliott'; SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC)); scene=bpy.context.scene; COL=bpy.data.collections['Asset_elliott_hall_of_music']
# Make this script repeatable.
for ob in list(COL.objects):
    if ob.name.startswith('ELLT_R8_'): bpy.data.objects.remove(ob,do_unlink=True)
    elif ob.name.startswith('ELLT_R5_Hovde_Link_') or ob.name.startswith('ELLT_R4_Hovde_Walkway_') or ob.name=='ELLT_R4_Hovde_Lobby_Threshold_Estimated':
        bpy.data.objects.remove(ob,do_unlink=True)

def mat(name,color,rough=.65):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
    return m
stone=mat('ELLT_Exterior_Indiana_Limestone',(.66,.61,.51),.75)
glass=mat('ELLT_R8_Door_Glass_Estimated',(.055,.13,.16),.32)
frame=mat('ELLT_R8_Door_Frame_Estimated',(.12,.105,.075),.58)
landing_mat=mat('ELLT_R8_Interface_Landing_Estimated',(.47,.44,.38),.82)

def cube(name,loc,dims,ma,rot=0,evidence='Estimated geometry; dimensions and placement are unverified.'):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;o.rotation_euler.z=rot
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    COL.objects.link(o);o.data.materials.append(ma);o['evidence_status']=evidence;return o

# Re-project the documented Elliott-side upper walkway aperture to its exact
# modeled footprint edge. Its exact physical location/dimensions remain estimated.
ring=json.loads((AUD/'polygon.json').read_text());N=len(ring)
area=.5*sum(ring[i][0]*ring[(i+1)%N][1]-ring[(i+1)%N][0]*ring[i][1] for i in range(N))
def project(target):
    best=(1e30,None)
    for i,a in enumerate(ring):
        b=ring[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
        u=max(0,min(1,((target[0]-a[0])*dx+(target[1]-a[1])*dy)/den)) if den else 0
        p=(a[0]+u*dx,a[1]+u*dy);d=math.dist(p,target)
        if d<best[0]:
            ll=math.hypot(dx,dy);t=(dx/ll,dy/ll);n=(t[1],-t[0]) if area>0 else (-t[1],t[0]);best=(d,(p,t,n))
    return best
_,(p,t,n)=project((44.075,9.162));theta=math.atan2(t[1],t[0]);origin=Vector((p[0],p[1],0));t3=Vector((t[0],t[1],0));n3=Vector((n[0],n[1],0))
# Small Elliott-side landing terminating visibly in open space. This is an
# estimated interface pad, not a route to Hovde.
center=origin+n3*.82+Vector((0,0,4.00))
cube('ELLT_R8_Elliott_Side_Interface_Landing_Estimated',center,(3.8,1.65,.30),landing_mat,theta,
     'Estimated Elliott-side landing at documented second-floor walkway interface. It ends in open space; it is not a completed connection, and its position/dimensions need a measured plan.')

# Readable double-leaf portal and limestone surround inside the known aperture.
# Opening center/width/vertical extent come from the current estimated shell pass.
center_door=origin-n3*.10+Vector((0,0,5.62));w=3.22;h=2.76;zmid=5.58;depth=.10
for side,sign in [('L',-1),('R',1)]:
    cube('ELLT_R8_Upper_Portal_DoorLeaf_'+side+'_Estimated',center_door+t3*(sign*.80),(1.55,depth,h),glass,theta,
         'Two-leaf glazed door representation fitted within the modeled Elliott-side aperture. Door material, swing, exact clear width and dimensions are not verified.')
    # Simple three-rail door framing for visible glazing subdivisions.
    cube('ELLT_R8_Upper_Portal_Door_Rail_'+side+'_Estimated',center_door+t3*(sign*.80)+Vector((0,0,-.55)),(1.50,.13,.07),frame,theta)
    cube('ELLT_R8_Upper_Portal_Door_RailTop_'+side+'_Estimated',center_door+t3*(sign*.80)+Vector((0,0,.48)),(1.50,.13,.07),frame,theta)
for side,sign in [('L',-1),('R',1)]:
    cube('ELLT_R8_Upper_Portal_Limestone_Jamb_'+side+'_Estimated',origin+t3*(sign*1.78)-n3*.08+Vector((0,0,5.62)),(.28,.38,3.12),stone,theta,
         'Limestone surround follows documented material vocabulary; portal dimensions and exact surround are estimates.')
cube('ELLT_R8_Upper_Portal_Limestone_Lintel_Estimated',origin-n3*.08+Vector((0,0,7.23)),(3.78,.38,.26),stone,theta,
     'Limestone lintel is a visual interpretation; no measured portal elevation was found.')
# Canopy end supports frame the entry and bridge the apparent gap below the arch.
for i,sign in enumerate((-1,1),1):
    u=sign*2.28;loc=origin+t3*u+n3*.40+Vector((0,0,5.82))
    cube(f'ELLT_R8_Canopy_Support_Pier_{i}_Estimated',loc,(.38,.46,3.16),stone,theta,
         'Estimated limestone support added to clarify the SAH-described curved canopy at the modeled portal. Position, dimensions, and actual support type are unverified.')

# Add a review-only textual marker beyond the Elliott landing. It is stored in
# the editable Elliott module but tagged as a non-architectural workflow note.
# Text object faces the visible outside of the landing.
curve=bpy.data.curves.new('ELLT_R8_Interface_Status_Text','FONT');curve.body='LINK DEFERRED';curve.size=.34;curve.align_x='CENTER';curve.align_y='CENTER';curve.extrude=.008
label=bpy.data.objects.new('ELLT_R8_Interface_Status_ReviewOnly',curve);COL.objects.link(label)
label.location=origin+n3*1.45+Vector((0,0,4.6));label.rotation_euler=Vector((n[0],n[1],0)).to_track_quat('Z','Y').to_euler();label['review_only']=True
label['evidence_status']='Non-architectural workflow marker: Hovde portal and connector remain pending joint validation. Remove after the Hovde owner completes the portal and both modules are checked together.'

COL['inter_building_connection_status']='DEFERRED: Elliott-side portal is shown with a short landing ending in open space. Hovde portal and continuous connection are not modeled or claimed; coordinate joint review after Hovde portal work.'
# Save authored geometry and reopen before temporary render operations.
bpy.ops.wm.save_as_mainfile(filepath=str(SRC));bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene;COL=bpy.data.collections['Asset_elliott_hall_of_music']

# EEVEE shader renders: do not rely on Workbench's flat material preview.
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1600;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.eevee.taa_render_samples=32;scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.get('ELLT_R8_World') or bpy.data.worlds.new('ELLT_R8_World');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.19,.22,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45;scene.world=world
ld=bpy.data.lights.new('ELLT_R8_Key','SUN');ld.energy=2.2;light=bpy.data.objects.new('ELLT_R8_Key',ld);scene.collection.objects.link(light);light.rotation_euler=(math.radians(27),math.radians(-30),math.radians(-22))
from mathutils import Vector
def render(name,loc,target,scale,hide_prefixes=(),hide_exact=(),allowed=None):
    changed=[]
    for ob in scene.objects:
        if (allowed is not None and ob.name not in allowed) or any(ob.name.startswith(x) for x in hide_prefixes) or ob.name in hide_exact:
            changed.append((ob,ob.hide_render));ob.hide_render=True
    cd=bpy.data.cameras.new('TEMP_R8_'+name);cd.type='PERSP' if name=='interior_audience_round8' else 'ORTHO';cam=bpy.data.objects.new('TEMP_R8_'+name,cd);scene.collection.objects.link(cam);cam.location=loc
    if cd.type=='ORTHO':cd.ortho_scale=scale
    else:cd.lens=32
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
    scene.render.filepath=str(AUD/(name+'.png'));bpy.ops.render.render(write_still=True)
    for ob,v in changed:ob.hide_render=v
    bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(cd)

# Facade views show actual mesh and shader result. No unverified window schedule is added.
render('exterior_elevation_round8',(0,-142,18),(0,0,10),128,
       hide_prefixes=('ELLT_R4_Hovde_','ELLT_Access_'))
render('entry_portal_round8',(p[0]+n[0]*23,p[1]+n[1]*23,13),(p[0]+n[0]*.2,p[1]+n[1]*.2,5.8),18,
       hide_prefixes=('ELLT_R4_Hovde_',))
# No joint Hovde view this round: the separate portal has not been completed.
# Interior view from the audience toward the stage; shell and ceiling hidden for
# camera visibility only. Seating chart supports multiple curved blocks and
# balconies, but no scale is published, so no model dimensions are claimed.
interior_objects={'ELLT_B3_seat','ELLT_B3_stage','ELLT_B3_curtain','ELLT_B3_balcony'}
render('interior_audience_round8',(-15,-18,10),(13,15,6),63,allowed=interior_objects)
render('interior_plan_round8',(0,0,96),(0,0,5),84,
       allowed=interior_objects)
result={'round':8,'saved_and_reopened':True,'blender_version':bpy.app.version_string,'export_mesh_objects':sum(o.type=='MESH' for o in COL.objects),
 'round8_additions':['two-leaf Elliott-side portal','estimated limestone surround','two estimated canopy supports','estimated Elliott-only interface landing; cross-building connector removed pending Hovde-side portal','review-only LINK DEFERRED marker'],
 'connector_status':'Deferred: Elliott landing ends in open space; Hovde portal/bridge not modeled or claimed. Joint context render omitted until Hovde owner completes portal.',
 'window_status':'No window schedule modeled. Current primary sources found in this pass do not provide pixel-verifiable elevation/layout; facade remains explicitly unverified.',
 'interior_evidence':'Audience-to-stage EEVEE view and top-down plan view. Official Purdue seating chart supports main floor, first balcony, second balcony and curved seating blocks, but does not provide dimensions; all seat coordinates/aisles remain schematic.',
 'mesh_count':sum(o.type=='MESH' for o in COL.objects),'renders':['exterior_elevation_round8.png','entry_portal_round8.png','interior_audience_round8.png','interior_plan_round8.png'],
 'uncertainties':['facade window schedule','portal and canopy position/details','door material/operation and clear width','Hovde portal/connector and accessible-route continuity','all interior and seating dimensions/egress']}
(AUD/'result_round8.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

