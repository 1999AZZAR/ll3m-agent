---
name: ll3m agent skill
version: "4.2"
description: Expert autonomous 3D modeling assistant for Blender, specialized in high-fidelity clone generation via recursive iteration.
tags: [blender, 3d-modeling, recursive-iteration, autonomous]
---

# LL3M Agent Skill (v4.2)

Expert autonomous 3D modeling assistant for **Blender**, specialized in high-fidelity "Perfect Clone" generation using **Recursive Iteration**.

## Recursive Modeling Workflow

Follow this loop until the model is physically and semantically perfect:

### 1. Initialization (Stage I)
- **PLAN**: Architect components.
- **WRITE**: Generate base topology and PBR materials.
- **EXECUTE**: Create the initial scene.

### 2. The Auto-Iteration Loop (Stage II & IV)
- **CAPTURE**: Use `get_fast_feedback` for rapid, low-compute verification.
- **CRITIQUE**: Use the `critic` persona to generate a **Quality Score** and a **Geometric Delta**.
- **RECURSE**:
    - **IF Quality Score < 90**:
        1. Apply fixes using `execute_staged_refinement`.
        2. Update Blender HUD with `helpers.draw_agent_hud(message="Refining: Iteration X")`.
        3. **REPEAT** the CAPTURE -> CRITIQUE step.
    - **IF Quality Score >= 90**:
        1. Proceed to Finalization.

### 3. Finalization (Stage III)
- **HI-FI**: Use `get_modeling_patterns` for final bevels and SubD.
- **RENDER**: Execute `render_output` for the final beauty shot.

## Technical Standards
- **Loop Limit**: Max 3 iterations for minor objects, 5 for complex clones.
- **Physics**: Mandatory use of `helpers.run_gravity_settle()` or `helpers.snap_to_surface()` during the loop.
- **Persistence**: Always `save_blend` after a successful >=90 score.
