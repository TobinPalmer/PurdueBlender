# Sigma Kappa FID 780 — source record

## Primary identity and footprint

Purdue GIS FeatureServer FID 780 names Sigma Kappa at 427 Russell St. The unmodified query response is preserved in `source_fid780.json`. It is returned in EPSG:4326, retrieved 2026-10-28; the record supplies no capture date. The 21-vertex ring is projected with the local approximation documented in `modular/AGENTS.md`, not a surveyed CRS.

The locally projected ring has bounds X -509.762..-482.565 m, Y 162.815..201.154 m, shoelace area 623.97 m² and perimeter 133.40 m. The ArcGIS `Shape__Area` / `Shape__Length` values are 1078.62109375 / 175.42974979181577, which do not agree with the local projected ring metrics. Those attributes are preserved but not used to modify the source geometry. The overlay is by construction and is not independent survey validation.

## Visual and identity references

- Two Tulips Boutique, artwork by Courtney Day, [Purdue Sorority custom House Drawing](https://twotulips.com/products/purdue-sorority-custom-house-drawing), retrieved 2026-10-28. Saved as `house_illustration_reference.jpg`. The drawing names Sigma Kappa and 427 N Russell Street and supports a qualitative red-brown brick composition, central light portico, flanking gabled wings and four dormers. It is a stylized secondary illustration without measured dimensions or source date.
- Purdue University Archives, [MSP 19 News Service catalog PDF](https://archives.lib.purdue.edu/fa/MSP19_News_Service.pdf), item 19.003.277, “Sigma Kappa Sorority, 427 Russell St.,” dated 1952-07-23. This is a catalog listing only; the photograph scan was not obtained and is not used for facade geometry.
- Purdue FSCL, [official chapter listing](https://www.purdue.edu/fscl/councils/pha/chapters.php), retrieved 2026-10-28; identity corroboration only.
- `facade_reference_current.png` is deliberately excluded from visual evidence: the image downloaded from the Panhellenic Sigma Kappa page shows a person in a Delta Zeta sweatshirt in a vehicle and no house.

## Uncertainty

The GIS record reports `NUM_LEVELS=1`, while the secondary drawing shows two facade levels; `Extrution=12` has no supplied units or definition. The model shows the illustrated multi-level composition but treats all vertical dimensions as estimates. The current north-facing entry is a provisional interpretation of the wide GIS edge; the illustration has no geographic bearing or measured elevation. The one-level interior preview is a schematic insert, not an as-built plan.
