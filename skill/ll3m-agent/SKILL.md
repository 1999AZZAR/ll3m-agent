# LL3M Agent Skill (v3.1)

Unified interface for high-end autonomous 3D modeling in Blender.

## Core Multi-Agent Workflow
1.  **PLAN**: `generate_modeling_plan` -> Architect the scene components.
2.  **RETRIEVE**: `get_api_docs` -> Fetch exact `bpy` signatures and code examples from the local RAG.
3.  **WRITE**: `get_agent_instructions(agent="writer")` -> Generate modular Python scripts.
4.  **EXECUTE**: `execute_blender_code` -> Send scripts to Blender.
5.  **CRITIQUE**: `get_screenshot` / `render_output` -> Visual verification.
6.  **DEBUG**: `get_agent_instructions(agent="debugger")` -> Fix errors found in tracebacks.

## Advanced Scene Inspection
- **`get_scene_summary`**: List objects, collections, modes, and active selection.
- **`get_object_details`**: Technical breakdown of mesh data, materials, and modifiers.
- **`get_blendfile_summary`**: Inspect datablocks, path info, and missing files.

## Navigation & Persistence
- **`navigation`**: Jump to specific tabs or focus the 3D view on an object.
- **`save_blend`**: Persist the session or save a copy of the scene.

## Design Standards
- **Style**: Minimalism, Cyberpunk, Glassmorphism, Material You.
- **Colors**: Pastel palettes.
- **Code**: `bmesh` for geometry, Shader Nodes for materials, Geometry Nodes for procedurality.
