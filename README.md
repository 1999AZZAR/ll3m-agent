# LL3M Agent (Monorepo)

Unified system for 3D modeling in Blender.

## Structure

- `brain/`: Node.js MCP server (Planning, Local RAG, Prompt Delivery).
- `body/`: Python Blender MCP server (Execution Engine & API Data).
- `skill/ll3m-agent/SKILL.md`: Gemini CLI Skill definition.

## Setup

1. **Config**: Ensure `~/.claude.json` points to the new paths.
2. **Blender**: Install the addon from `body/addon/blender_mcp_addon/` (or use the root `blender_mcp_addon.zip`).

## Usage

Follow the LL3M skill workflow: **PLAN** -> **RETRIEVE** -> **WRITE** -> **EXECUTE** -> **CRITIQUE**.
