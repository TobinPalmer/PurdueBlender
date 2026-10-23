exec(open('audit/batch2_lawson/improve.py').read().split('# Trace official')[0])
for o in list(C.all_objects):
 if any(k in o.name for k in ['Office_Desk','Commons_Table']):
  x,y,z=o.location
  for dx in [-.58,.58]:
   for dy in [-.26,.26]:cube('LWSN_Table_Leg',(x+dx,y+dy,(z-.04+.4)/2),(.045,.045,z-.44),metal)
 if any(k in o.name for k in ['Office_Chair','Commons_Chair','1142_Seat']):
  x,y,z=o.location;cube('LWSN_Chair_Support',(x,y,(z+.4)/2),(.06,.06,max(.12,z-.4)),metal);cube('LWSN_Chair_Base',(x,y,.44),(.4,.4,.05),metal)
for px,py,direction in [(313,756,1),(555,103,1),(493,739,1)]:
 for i in range(19):
  x,y=xy(px,py+i*2.85);cube('LWSN_Stair_Flight',(x,y,.4+i*.18),(2.3,.29,.18),wall)
for px,py in [(563,753),(578,753),(593,753),(563,797),(578,797),(593,797)]:
 x,y=xy(px,py);cube('LWSN_Restroom_Fixture_Illustrative',(x,y,.72),(.44,.65,.55),wall)
# Continuous ground floor only inside footprint through copy of foundation top.
base=bpy.data.objects['LWSN_Foundation_Base'];floor=base.copy();floor.data=base.data.copy();floor.name='LWSN_First_Floor_Surface';C.objects.link(floor);floor.location.z+=.015
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
