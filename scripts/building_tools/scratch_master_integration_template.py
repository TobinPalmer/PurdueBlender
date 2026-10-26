"""
Prototype master integration script for the 5 newly added buildings.
This script demonstrates how each building asset is linked into purdue_campus_linked.blend
and registered into modular/manifest.json and modular/source_transforms.json.
"""
import bpy
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / 'modular'
MANIFEST_PATH = BASE_DIR / 'manifest.json'
TRANSFORMS_PATH = BASE_DIR / 'source_transforms.json'
MASTER_BLEND = BASE_DIR / 'purdue_campus_linked.blend'

NEW_BUILDINGS = [
    {
        'id': 'stanley_coulter_hall',
        'code': 'SC',
        'fid': 56,
        'file': 'buildings/stanley_coulter_hall.blend',
        'collection': 'Asset_stanley_coulter_hall',
        'scene': 'Building_stanley_coulter_hall'
    },
    {
        'id': 'benjamin_harrison_hall',
        'code': 'HARR',
        'fid': 85,
        'file': 'buildings/benjamin_harrison_hall.blend',
        'collection': 'Asset_benjamin_harrison_hall',
        'scene': 'Building_benjamin_harrison_hall'
    },
    {
        'id': 'mccutcheon_hall',
        'code': 'MCUT',
        'fid': 57,
        'file': 'buildings/mccutcheon_hall.blend',
        'collection': 'Asset_mccutcheon_hall',
        'scene': 'Building_mccutcheon_hall'
    },
    {
        'id': 'hansen_life_sciences',
        'code': 'HANS',
        'fid': 237,
        'file': 'buildings/hansen_life_sciences.blend',
        'collection': 'Asset_hansen_life_sciences',
        'scene': 'Building_hansen_life_sciences'
    },
    {
        'id': 'niswonger_aviation_tech',
        'code': 'NISW',
        'fid': 870,
        'file': 'buildings/niswonger_aviation_tech.blend',
        'collection': 'Asset_niswonger_aviation_tech',
        'scene': 'Building_niswonger_aviation_tech'
    }
]

print("Master integration script template ready.")
