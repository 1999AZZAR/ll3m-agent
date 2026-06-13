# LL3M Agent Skill

Expert 3D modeling assistant utilizing the LL3M (Large Language 3D Modelers) framework within Blender.

## Workflow

1. **PLAN**: Break request into components (seat, legs, backrest).
2. **RETRIEVE**: Get `bpy` API context from `ll3m-mcp-server`.
3. **WRITE**: Generate modular Python code (BMesh, GeoNodes, Shaders).
4. **EXECUTE**: Run in Blender via `blender-mcp-server`.
5. **CRITIQUE**: Render/Screenshot -> Self-correct logic/geometry.

## Visual Standards
- Pastel palettes.
- Material You / Minimalism.
- Glassmorphism for UI elements.
