import bpy
for n in ['Tark_Dorm_Room118_Floor','Tark_Dorm_Room118_Wall_N','Tark_Dorm_Bed_Frame_0','Tark_Dorm_Bed_Mattress_0','Tark_Dorm_Desk_0','Tark_Dorm_Desk_Chair_0','Tark_Dorm_Wardrobes']:
 o=bpy.data.objects.get(n)
 print(n,'mats',[(m.name if m else None) for m in o.data.materials],'loc',tuple(o.matrix_world.translation),'dims',tuple(o.dimensions))
for n in ['Tark_Lobby_Terrazzo_Floor','Tark_Lobby_Lounge_Sofa_0','Tark_Lobby_Reception_Desk_Base','Tark_PetesZa_Tile_Floor','Tark_SharkTank_Carpet_Floor']:
 o=bpy.data.objects.get(n); print(n,'mats',[(m.name if m else None) for m in o.data.materials])
