import bpy, json

bpy.ops.wm.open_mainfile(filepath='modular/buildings/wiley_hall.blend')
m = bpy.data.materials['Wiley | warm russet brick / real-size 230 x 76 mm.003']
details = {'nodes': {}, 'links': []}

for n in m.node_tree.nodes:
    inputs = {}
    for i in n.inputs:
        val = getattr(i, 'default_value', None)
        if val is not None:
            if hasattr(val, '__iter__'):
                inputs[i.name] = list(val)
            else:
                inputs[i.name] = val
    props = {}
    for p in ['brick_type', 'offset', 'offset_frequency', 'squash', 'squash_frequency', 'operation', 'blend_type', 'data_type']:
        if hasattr(n, p):
            props[p] = str(getattr(n, p))
    details['nodes'][n.name] = {
        'type': n.type,
        'props': props,
        'inputs': inputs
    }

for l in m.node_tree.links:
    details['links'].append({
        'from_node': l.from_node.name,
        'from_socket': l.from_socket.name,
        'to_node': l.to_node.name,
        'to_socket': l.to_socket.name
    })

print(json.dumps(details, indent=2))
