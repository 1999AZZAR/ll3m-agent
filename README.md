# LL3M Agent (Monorepo) v3.1

Autonomous 3D modeling agent stack for **Blender**, powered by the **Model Context Protocol (MCP)**. 

This project integrates the local execution power of Blender with the multi-agent reasoning framework described in the **LL3M** paper, providing a unified "Brain and Body" for high-end 3D asset generation and scene management.

## 🚀 Main Idea & Sources

- **Primary Source**: [LL3M (Large Language 3D Modelers)](https://github.com/threedle/ll3m) - A multi-agent framework for generating 3D assets via code.
- **Platform Vision**: [Blender Lab: MCP Server](https://www.blender.org/lab/mcp-server/) - The official vision for Blender as an AI-enabled creative tool.

## ✨ Key Features (v3.1)

### 🧠 Unified Modeling Brain
- **Multi-Agent Workflow**: Built-in personas for **Planner**, **Writer**, and **Debugger** roles.
- **Advanced local RAG**: A sophisticated Python-based RST parser that provides agents with precise Blender API signatures, documentation, and real-world code examples.
- **Cloud-Independent**: 100% local execution. No dependency on retired external servers.

### 🛠️ High-Level Tooling
- **Scene Mapping**: `get_scene_summary` provides a complete hierarchical map of collections, objects, and active states.
- **Object Inspection**: `get_object_details` offers deep technical dives into mesh data, material slots, and modifiers.
- **File Intelligence**: `get_blendfile_summary` reports on datablocks, missing external assets, and linked libraries.

### 👁️ Visual Intelligence
- **High-Speed Screenshots**: Instant base64 viewport capture for real-time agent feedback.
- **Production Rendering**: Dedicated tools for viewport renders and thumbnail generation.

### 🕹️ UI Navigation
- **Workspace Control**: Agents can "jump" the Blender UI to specific tabs (Shading, Geometry Nodes, etc.).
- **Viewport Focus**: Automatically center the 3D view on any specific object.

## 📁 Structure

- **`brain/`**: Node.js MCP server (TypeScript). The central orchestrator for RAG, Planning, and Execution.
- **`body/`**: Python component containing the Blender execution bridge, specialized modeling tools, and the full Blender API documentation set.
- **`skill/`**: Gemini CLI Skill definition to enable the autonomous modeling loop.

## ⚙️ Setup

1.  **Configuration**: Add the `ll3m` server to your MCP config (e.g., `~/.claude.json`):
    ```json
    "ll3m": {
      "command": "node",
      "args": ["/path/to/ll3m-agent/brain/dist/index.js"]
    }
    ```
2.  **Blender Addon**: Install the addon from `body/addon/blender_mcp_addon/` (or use the root `.zip`).
3.  **Activation**: Click **"Start Server"** in the Blender addon preferences (Port 9876).

## 🎮 Usage

Simply provide a natural language request to your agent:
> *"Create a minimalist cyberpunk lounge with a glass table and a neon bookshelf"*

The agent will follow the verified LL3M loop: **PLAN** → **RETRIEVE** → **WRITE** → **EXECUTE** → **CRITIQUE**.
