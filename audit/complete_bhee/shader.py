exec(open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_bhee/render.py').read().split('# first-floor')[0])
s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1000;s.render.resolution_y=850
w=bpy.data.worlds.new('ReviewWorld');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.55,.6,.7,1);w.node_tree.nodes['Background'].inputs[1].default_value=.65;s.world=w
ld=bpy.data.lights.new('Sun','SUN');lo=bpy.data.objects.new('Sun',ld);s.collection.objects.link(lo);lo.rotation_euler=(.4,-.6,-.5);ld.energy=3
s.render.filepath=str(D/'shader_overview.png');bpy.ops.render.render(write_still=True)
