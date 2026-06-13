# LL3M Agent (Monorepo)

Unified system for autonomous 3D modeling in Blender.

## Main Idea & Sources

This project is an integration of the **Model Context Protocol (MCP)** with advanced 3D modeling agents. It combines the local execution power of Blender with the multi-agent reasoning described in the LL3M framework.

- **Primary Source**: [LL3M (Large Language 3D Modelers)](https://github.com/threedle/ll3m) - A multi-agent framework for generating 3D assets.
- **Platform Idea**: [Blender Lab: MCP Server](https://www.blender.org/lab/mcp-server/) - The official vision for Blender as an MCP-enabled tool.

## Structure

- `brain/`: Node.js MCP server. Handles multi-agent logic (Planner, Writer, Debugger) and local Blender API RAG.
- `body/`: Python component containing the execution engine and extensive Blender API documentation.
- `skill/ll3m-agent/SKILL.md`: Gemini CLI Skill definition to orchestrate the modeling workflow.

## Setup

1. **Config**: Add the `ll3m` server to your `~/.claude.json` (or equivalent) pointing to `brain/dist/index.js`.
2. **Blender**: Install the addon from `body/addon/blender_mcp_addon/`.
3. **Connect**: Click "Start Server" in the Blender addon preferences.

## Usage

Enable the skill and provide a natural language request:
> "Use the ll3m-agent skill to create a minimalist cyberpunk lounge"

The system will follow the LL3M workflow: **PLAN** -> **RETRIEVE** -> **WRITE** -> **EXECUTE** -> **CRITIQUE**.
