# Material sources and limits

Scanned tileable brick sets by Poly Haven, CC0:

- https://polyhaven.com/a/red_brick — 2K diffuse, OpenGL normal, roughness and displacement; published tile width 1.4 m. Used for relatively cleaner red campus masonry, with building-specific tint review.
- https://polyhaven.com/a/brick_wall_001 — 2K diffuse, OpenGL normal, roughness and displacement; aged industrial masonry. The original published width is 3 m; workers compare apparent coursing with standard brick units and use explicit adjusted scale when appropriate. It is not a measured Purdue material sample.

Downloads are preserved under `textures/`, with semantic map filenames. Normal, roughness and height are interpreted as Non-Color. Normal and fine bump relief are used without adding large subdivision meshes to the campus. Height maps produce shader relief, not corrected masonry silhouettes. Metric face UVs preserve object transforms and avoid stretching brick courses over an entire wall.

Photorealistic appearance also depends on actual architectural geometry, glazing assemblies, landscaping, lighting and camera composition. Replacing a flat material cannot certify that an invented building facade is physically accurate. Building-specific reports record reference images and remaining limitations.
