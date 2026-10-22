import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix
import sys
from pathlib import Path
ROOT = Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
sys.path.insert(0, str(ROOT / 'materials'))
import pbr_upgrade as pbr

# Setup materials
mat_brick = pbr.upgrade_brick(bpy.data.materials['Purdue_Red_Brick'], tint=(.88,.84,.78,1))
mat_limestone = get_or_create_mat("Indiana_Bedford_Limestone", (0.85, 0.82, 0.77, 1.0), roughness=0.68)
mat_spandrel = get_or_create_mat("Harrison_Enamel_Spandrel", (0.20, 0.32, 0.36, 1.0), roughness=0.25) # Teal/slate blue enamel
mat_glass = get_or_create_mat("Solar_Ribbon_Glass", (0.10, 0.16, 0.20, 1.0), roughness=0.04, transmission=0.85, ior=1.52)
mat_aluminum = get_or_create_mat("Anodized_Aluminum", (0.78, 0.78, 0.80, 1.0), roughness=0.30, metallic=0.85)
mat_bronze = get_or_create_mat("Aged_Architectural_Bronze", (0.32, 0.24, 0.16, 1.0), roughness=0.35, metallic=0.75)
mat_roof = get_or_create_mat("Roof_Membrane", (0.24, 0.24, 0.25, 1.0), roughness=0.85)
mat_concrete = get_or_create_mat("Concrete_Pavement", (0.65, 0.64, 0.62, 1.0), roughness=0.75)
mat_screen = get_or_create_mat("Solar_Screen_Concrete", (0.82, 0.80, 0.76, 1.0), roughness=0.70)
mat_louver = get_or_create_mat("Dark_Mechanical_Louver", (0.18, 0.18, 0.19, 1.0), roughness=0.50, metallic=0.6)
mat_cyan_wire = get_or_create_mat("Ref_Emissive_Cyan", (0.0, 1.0, 1.0, 1.0), emission_color=(0.0, 1.0, 1.0, 1.0), emission_strength=5.0)

def build_benjamin_harrison_hall():