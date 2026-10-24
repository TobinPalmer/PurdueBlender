"""Independent full-building evaluation for Lyles-Porter Hall round 1."""
import json


def evaluate():
    criteria = {
        "identity_and_footprint": {
            "score": 1.9,
            "max_score": 2,
            "evidence": (
                "Purdue BuildingShapesZip4 FID 891 identifies Lyles-Porter Hall. "
                "Independent extraction of the saved shell's z=0 40-vertex face "
                "measured 3524.4204 m2 versus 3520.2580 m2 for the raw GIS ring "
                "(0.118% area difference); the GIS envelope bounds also match the "
                "model local envelope."
            ),
            "uncertainty": "The GIS footprint is generalized; 0.4 m vertex simplification can omit small wall jogs.",
        },
        "position_orientation_and_scale": {
            "score": 1.8,
            "max_score": 2,
            "evidence": (
                "The master Placement_lyles_porter_hall empty is at the manifest's "
                "(-257.675, -717.457) m origin, with zero rotation and unit scale. "
                "The source asset uses the documented local GIS-envelope-center transform."
            ),
            "uncertainty": "No surveyed control point independently validates the local GIS-to-campus projection.",
        },
        "height_floors_and_roof": {
            "score": 1.4,
            "max_score": 2,
            "evidence": (
                "Purdue's 2026 emergency plan describes three stories plus a partial basement. "
                "GIS F01/F02/R values support the modeled 15/30/45 ft level datums; the shell is "
                "modeled to 45 ft with a partial basement."
            ),
            "uncertainty": "GIS vertical field units/semantics are undocumented; basement extent, roof shape, and mechanical heights are not surveyed.",
        },
        "facade_entrances_and_distinctive_features": {
            "score": 1.4,
            "max_score": 2,
            "evidence": (
                "Purdue photographs and the cited Google Street View captures support red brick, "
                "pale horizontal precast bands, punched dark glazing, and a projecting entrance canopy. "
                "The model includes these elements, rooftop mechanical cues, and schematic reception, "
                "clinic, fitness, and audiology props."
            ),
            "uncertainty": "The facade repetition and entrance are generalized; the interior is sparse and schematic, with no dimensioned floor plan or modeled 30-booth layout.",
        },
        "modular_export_portability_and_evidence": {
            "score": 1.7,
            "max_score": 2,
            "evidence": (
                "The saved Asset_lyles_porter_hall collection reopened with 11 objects, 10 meshes, "
                "10 materials, nine texture-connected materials, and no external image dependencies. "
                "The audit preserves the raw GIS snapshot and records source URLs, CRS, retrieval dates, "
                "measurement method, and uncertainties."
            ),
            "uncertainty": "The material and geometry validation is strong, but the asset lacks a multi-view exterior/interior evidence set and explicit automated GIS-fit report.",
        },
    }
    score = round(sum(item["score"] for item in criteria.values()), 1)
    return {
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": [
            "Purdue GIS FeatureServer layer 0, FID 891: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0",
            "Purdue 2026 Building Emergency Plan: https://www.purdue.edu/operations/emergency-preparedness/lyle/",
            "Purdue 2014 dedication page/photos: https://www.purdue.edu/newsroom/archive/releases/2014/Q3/purdue-dedicates-building-for-health-research,-training,-patient-services.html",
            "Evidence and raw GIS files: audit/lyles_porter_hall/evidence.json, gis_feature_891.geojson, gis_live_response.geojson",
            "Saved source asset: modular/buildings/lyles_porter_hall.blend; master marker checked read-only against modular/manifest.json.",
        ],
        "findings": [
            "Passes the project's 8/10 acceptance threshold for a detailed model.",
            "Retain the generalized facade, room layout, basement, roof, and vertical-unit limits in the evidence record; this grade is not a full surveyed-geometry certification.",
            "Recommended next improvement: provide a readable cutaway or floor-by-floor interior preview and a facade close-up from the main public entrance.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
