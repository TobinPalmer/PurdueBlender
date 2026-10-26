import bpy
pref=('UNIV_Wall_East_','UNIV_Wall_South','UNIV_Win_','UNIV_WinSill','UNIV_WinHood','UNIV_WinKeystone','UNIV_R2_Mansard','UNIV_R2_Dormer','UNIV_R2_RidgeDeck','UNIV_R2_SlateStandingSeam','UNIV_R5_Mansard','UNIV_R5_Dormer','UNIV_R5_Belfry','UNIV_R5_Lantern','UNIV_R5_Weathervane','UNIV_R5_Finial','UNIV_R5_Portico','UNIV_Tower_','UNIV_Belfry_','UNIV_Cupola_','UNIV_R3_East_Clock','UNIV_R3_West_Clock','UNIV_R3_North_Clock','UNIV_R3_South_Clock','UNIV_R3_ArchedWindowMoulds','UNIV_R3_North_Window','UNIV_R3_South_Window','UNIV_R3_East_Window','UNIV_R3_West_Window','UNIV_WaterTable_East','UNIV_WaterTable_South','UNIV_Beltcourse_E','UNIV_Beltcourse_S','UNIV_Quoin','UNIV_Portico','UNIV_East_Step')
for o in bpy.data.objects:
 if o.type=='MESH' and o.matrix_world.translation.z>15 and not o.name.startswith(pref):
  print(o.name, tuple(round(a,1) for a in o.matrix_world.translation),tuple(round(a,1) for a in o.dimensions))
