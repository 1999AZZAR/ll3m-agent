# LL3M Agent Skill (v3.0)

Expert 3D modeling assistant utilizing the LL3M (Large Language 3D Modelers) framework within Blender.

## Core Capabilities

This skill provides a unified interface for autonomous 3D asset generation, scene inspection, and visual refinement.

### 1. Modeling Workflow
Follow the Multi-Agent loop to ensure high-quality, physically plausible results:
- **PLAN**: Use `generate_modeling_plan` to architect the object.
- **RETRIEVE**: Use `get_api_docs` to get exact `bpy` signatures. Never guess the API.
- **WRITE**: Generate modular code using the `get_agent_instructions(agent="writer")` persona.
- **EXECUTE**: Run in Blender via `execute_blender_code`.
- **CRITIQUE**: Use `get_screenshot` or `render_viewport` to verify visually. Refine using the `debugger` persona.

### 2. Scene Management
- **`get_scene_summary`**: Use this at the start of any session to understand the current context (active objects, layers, collections).
- **`get_object_details`**: Inspect a specific object's mesh data, materials, and modifiers.
- **`save_blend`**: Persist your progress to a file.

### 3. Visual Feedback
- **Screenshots**: High-speed viewport capture (base64).
- **Rendering**: Full-quality image output (path-based).

## Technical Standards
- **Design Language**: Material You, Minimalism, Glassmorphism.
- **Color Palettes**: Pastel-focused.
- **Code Style**: Modular functions, `bmesh` for mesh editing, Geometry Nodes for procedurality.

## Agnostic Usage
Any LLM-based agent can utilize this skill by calling the associated `ll3m` tools. The server is 100% local and does not depend on external cloud services.
