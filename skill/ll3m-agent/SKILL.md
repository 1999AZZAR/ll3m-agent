# LL3M Agent Skill (v3.2)

Expert autonomous 3D modeling assistant for **Blender**, specialized in high-fidelity asset generation.

## High-Fidelity Workflow

Follow this multi-agent loop to move beyond basic primitives toward realistic "perfect clones" of everyday objects:

1.  **PLAN**: Use `generate_modeling_plan`. Identify which parts require **Subdivision Surface (SubD)** for smoothness and which are **Hard Surface**.
2.  **RETRIEVE (Patterns)**: Use `get_modeling_patterns`. Fetch technical blueprints for:
    *   `rounded_corners`: Catch highlights realistically.
    *   `ergonomic_curves`: Complex tapering and sweeping.
    *   `subd_topology`: Clean quad-based edge flow.
    *   `realistic_materials`: Advanced PBR node setups (Clearcoat, Sheen).
3.  **RETRIEVE (Helpers)**: Use `get_blender_helpers`. These are pre-baked Python functions available in the Blender environment (accessible via the `helpers` namespace, e.g., `helpers.setup_pbr()`).
4.  **RETRIEVE (API)**: Use `get_api_docs` for specialized operations not covered by helpers.
5.  **WRITE**: Generate code using the `writer` persona. **Always prefer `helpers` functions** to reduce code length and errors.
    *   Example: `helpers.setup_pbr("Steel", metallic=1.0)` is safer than manual node creation.
6.  **EXECUTE**: Send code via `execute_blender_code`.
6.  **CRITIQUE**: Use `get_screenshot` and `render_output`. Refine until the model matches the "Real-World Clone" standard.

## Technical Standards
- **Topology**: Prioritize quad meshes. Avoid triangles and poles on curved surfaces.
- **Modifiers**: Use `SUBSURF` (Level 2+) for all organic shapes. Use `BEVEL` for all hard edges.
- **Shading**: Use **Auto Smooth** or **Weighted Normals** to ensure perfect light reflection.

## scene Intelligence
Use `get_scene_summary` and `get_object_details` to verify the technical integrity of the generated geometry (vertex counts, modifier stacks).
