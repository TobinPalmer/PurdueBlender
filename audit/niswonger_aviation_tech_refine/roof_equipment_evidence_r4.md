# Niswonger R4 roof equipment evidence and limits

## Direct roof evidence

- The Esri World Imagery z20 overhead mosaic at `arcgis_world_imagery/composite_z20.jpg` shows a compact mechanical/service-equipment group on the eastern/northeastern portion of the large classroom addition, alongside broad dark-gray and light metal roof zones. Esri's service metadata credits Esri, Vantor, Earthstar Geographics and the GIS User Community. The tile endpoint does not expose an acquisition date; no date is inferred.
- OpenStreetMap way 256667242 (`osm_footprint_way256667242.json`, OSM version 3, timestamp 2020-02-08) identifies the 1401 Aviation Drive building footprint. It is a public reference footprint, not an as-built roof drawing.
- A qualitative overlay `registered_roof_overlay_r3.png` compares the OSM outline, original GIS model outline and inferred R2 plate bounds over the aerial. The outlines do not coincide after centroid-based registration, so the overlay is retained as a warning against claiming exact local-XY registration. Equipment placement uses a broad east/northeast zone inference only.
- Purdue Board of Trustees' 2019 airport HVAC/window project record (https://www.purdue.edu/bot/meetings/past-meetings/2019/06.%20aug/pfc/508_Airport-HVAC-Window-Overhead-Door.pdf) confirms HVAC work at Niswonger but does not establish unit number, model, positions or roof curbs. MSKTD photos (https://msktd.com/project/purdue-university-niswonger-aviation-technology/) support the connector/clerestory assembly and architectural finishes, but not the full overhead roof plan.

## R4 change

One joined export mesh, `NISW_R4_Roof_HVAC_Cluster`, adds three generic curb-mounted AHU-like housings with intake louvers and two fan housings each, plus a shared duct transition. It sits within the approximate classroom roof plate near its east/northeast side, guided by the orthophoto's visible equipment concentration. Shape, count, dimensions and exact local XY remain illustrative; no manufacturer/model identification, as-built mechanical layout or survey dimensions are claimed. The existing roof plates and elevations were not moved.
