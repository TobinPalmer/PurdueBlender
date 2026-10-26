"""Independent R2 grading record for Campus Edge candidate eedf159.

Run with Python to print the evaluator result. The source/model inspection and
fresh Blender reopen were performed independently; this file preserves the
criterion-level decision and evidence contract for that candidate.
"""
import json


RESULT = {
    "candidate_commit": "eedf159332f5fa7b8ff35160e8997279c9c1ceae",
    "score": 8.5,
    "max_score": 10,
    "criteria": {
        "identity_and_source_backed_footprint": {
            "score": 2,
            "max_score": 2,
            "assessment": (
                "The named 134 Pierce Street OSM feature and Indiana LiDAR-derived "
                "footprint match in identity and outline; the reported 0.914 IoU "
                "and 1.06 m centroid gap support the footprint choice."
            ),
        },
        "position_orientation_and_dimensions": {
            "score": 1.5,
            "max_score": 2,
            "assessment": (
                "The saved asset reopens at the documented campus coordinates, and "
                "its structural podium bounds follow the source footprint. The "
                "project's degree-based local conversion is explicitly approximate, "
                "and there is no independent surveyed placement check."
            ),
        },
        "height_floors_and_roof_form": {
            "score": 1.5,
            "max_score": 2,
            "assessment": (
                "The three roof heights use per-zone 2018 NDHM medians, and the "
                "evidence correctly labels them normalized surface estimates rather "
                "than surveyed eaves or story datums. Tower boundaries and exact "
                "heights remain approximate."
            ),
        },
        "facade_entrances_and_distinctive_architecture": {
            "score": 1.5,
            "max_score": 2,
            "assessment": (
                "The official exterior image supports the podium, repeated glazed "
                "bays, brick accents, balconies, and entry canopy represented in the "
                "model. Their exact dimensions and positions are qualitative "
                "interpretations."
            ),
        },
        "modular_export_portability_and_evidence": {
            "score": 2,
            "max_score": 2,
            "assessment": (
                "The asset preserves its ID, collection, and coordinate contract. "
                "A fresh Blender 4.5.15 reopen found 15 local mesh objects, no linked "
                "libraries, and three distinct tower shells; source snapshots and "
                "uncertainty records are present."
            ),
        },
    },
    "evidence": [
        {
            "source": "audit/massing_campus_edge_343e3d8/source_record.json",
            "observation": (
                "Named OSM way 886359911 and Indiana LiDAR footprint OBJECTID "
                "407824 identify the building; their recorded comparison is 0.914 "
                "IoU with a 1.06 m centroid separation."
            ),
        },
        {
            "source": "audit/massing_campus_edge_343e3d8/sources/official_gallery_07.jpg",
            "observation": (
                "The official exterior photo shows three upper tower volumes above "
                "a continuous podium."
            ),
        },
        {
            "source": "audit/massing_campus_edge_343e3d8/sources/indiana_2023_orthophoto_campus_edge.jpg",
            "observation": (
                "The aerial roof pattern shows three roof-pad intervals separated "
                "by two dark open/recessed bands."
            ),
        },
        {
            "source": "audit/massing_campus_edge_343e3d8/orthophoto_roof_zone_interpretation.png",
            "observation": (
                "The marked row-based zones align approximately with the three "
                "visible roof pads; the saved method describes the projection, "
                "footprint clipping, and unsurveyed boundary limitations."
            ),
        },
        {
            "source": "audit/massing_campus_edge_343e3d8/campus_edge_roof_zone_analysis.json",
            "observation": (
                "Zone NDHM sample counts are 176, 267, and 246. Heights are "
                "identified as normalized surface medians, not surveyed eaves or "
                "story datums, with cell mixing and roof-boundary uncertainty stated."
            ),
        },
        {
            "source": "modular/buildings/massing_campus_edge_343e3d8.blend",
            "observation": (
                "Fresh Blender 4.5.15 reopen confirmed the expected scene and export "
                "collection, 15 asset mesh objects, no linked libraries, and three "
                "separate upper tower shells. The two intervening bands contain the "
                "low podium only."
            ),
        },
    ],
    "findings": [
        (
            "The separated tower masses and major recesses are supported "
            "qualitatively by the aerial roof pattern and official exterior photo, "
            "and are represented in the saved asset."
        ),
        (
            "Tower-band edges are approximate orthophoto row interpretations "
            "clipped to the footprint; exact structural wall lines and terrace "
            "elevations are not established."
        ),
        (
            "NDHM limitations are stated accurately. The roof medians remain "
            "estimates because 5-ft cells can include rooftop equipment and other "
            "surface returns."
        ),
    ],
    "passes_8_point_threshold": True,
}


def evaluate():
    """Return the required independent-grader contract for candidate eedf159."""
    return RESULT


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
