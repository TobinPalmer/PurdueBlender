# Python scripts

## Current building workflow

Each current building has its own source and builder in `modular/buildings/`. Those files are the maintained, reproducible building models. Follow the repository root `AGENT.md` and `modular/AGENTS.md` when adding or changing a building.

## Shared building tools

`scripts/building_tools/` contains utilities intended to be reused across buildings or across the modular campus library, such as asset checks, batch surface work, campus-wide audits, and export helpers. Run scripts from the repository root unless a script says otherwise; several older Blender utilities use repository-relative file paths.

## Building-specific project scripts

`scripts/building_projects/` contains the earlier one-off modeling and refinement scripts for named buildings. They are kept together because some runner scripts call their companion builder scripts by filename. New maintained building builders belong in `modular/buildings/` instead.

## Miscellaneous utilities

`scripts/misc/` contains GIS fetchers, experiments, render helpers, inspections, and parser or material probes that do not form part of the repeatable building workflow.

The root directory is reserved for project entry points and documentation. This organization changes script locations, not their repository-root working-directory convention.
