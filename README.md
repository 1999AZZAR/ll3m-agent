# LL3M Agent (Monorepo)

A unified autonomous 3D modeling system for Blender, built on the Model Context Protocol (MCP).

[![LL3M Agent Demo](https://img.youtube.com/vi/BnbDg1-be4g/0.jpg)](https://www.youtube.com/watch?v=BnbDg1-be4g)

This project integrates the multi-agent reasoning framework from the LL3M research with a local Blender execution bridge. It provides a production-ready stack for generating 3D assets, inspecting scene hierarchies, and performing iterative refinements via natural language.

## Architecture and Origins

The system is derived from two foundational concepts:
- **LL3M (Large Language 3D Modelers)**: A multi-agent methodology for 3D generation through interpretable Python code. [Source](https://github.com/threedle/ll3m)
- **Blender Lab MCP**: The official vision for exposing Blender as a tool for large language models. [Documentation](https://www.blender.org/lab/mcp-server/)

## System Capabilities (v3.1)

### Autonomous Modeling Pipeline
The system implements a structured multi-agent loop to ensure geometric and physical accuracy:
- **Planner**: Decomposes natural language requests into discrete geometric components and spatial requirements.
- **Writer**: Translates modeling plans into modular Python scripts utilizing `bpy` and `bmesh`.
- **Debugger**: Analyzes execution tracebacks and visual feedback to perform automated error correction.

### Local Retrieval-Augmented Generation (RAG)
Integrated Python-based RST parser that provides agents with:
- Fully qualified API signatures for `bpy` and `bmesh`.
- Contextual usage examples extracted from official documentation.
- Automatic truncation and navigation for large module references.

### Scene and Object Intelligence
- **Hierarchical Summarization**: Detailed mapping of collections, object visibility, and active selection states.
- **Technical Inspection**: Direct access to mesh data, material node trees, and modifier stacks.
- **Visual Feedback**: Real-time viewport screenshot capture and high-resolution background rendering.

## Repository Structure

- `/brain`: Node.js/TypeScript MCP server handling agent orchestration and documentation retrieval.
- `/body`: Python environment containing the Blender bridge, modeling tools, and full API RAG dataset.
- `/skill`: Gemini CLI skill definition for managing the autonomous workflow.

## Installation and Setup

### 1. MCP Configuration
Register the server in your configuration (e.g., `~/.claude.json`):
```json
"ll3m": {
  "command": "node",
  "args": ["/path/to/ll3m-agent/brain/dist/index.js"]
}
```

### 2. Blender Add-on
- Install the add-on located in `body/addon/blender_mcp_addon/`.
- Enable "Start Server" within the add-on preferences (Default Port: 9876).

## Operation

Execute the modeling loop by providing a technical or descriptive request:
> "Use the ll3m-agent skill to generate a minimalist industrial interior with a glass-top table."

The system will proceed through the PLAN → RETRIEVE → WRITE → EXECUTE cycle automatically.
