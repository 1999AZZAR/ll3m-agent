# LL3M Agent Audit TODO

Prioritized from a repository-wide review on 2026-07-26. Items marked complete must have regression coverage or a verification command.

## Critical

- [x] Replace shell-interpolated `get_api_docs` execution with argument-safe subprocess execution (`brain/src/index.ts`).
- [x] Fix the Brain-to-Blender tool wrapper so expanded tool code returns its real `result` and preserves deferred callbacks (`brain/src/index.ts`).
- [x] Make clean Brain builds copy required prompts and `api_docs_bridge.py` without hiding copy failures (`brain/package.json`).
- [x] Import `bpy` and `bmesh` where the Blender add-on constructs its execution namespace (`body/addon/blender_mcp_addon/mcp_to_blender_server.py`).
- [x] Restrict the Blender socket bridge to loopback addresses because it executes unauthenticated Python (`body/addon/blender_mcp_addon/mcp_to_blender_server.py`).
- [x] Secure MCP HTTP mode: loopback-only binding, DNS-rebinding protection, and non-wildcard CORS (`body/mcp/blmcp/__init__.py`).

## High

- [x] Serialize `save_blend` paths safely instead of interpolating them into Python source (`brain/src/index.ts`).
- [x] Correct Brain tool mappings and parameters for linked libraries, object details, screenshots, and fast feedback (`brain/src/index.ts`).
- [x] Validate Blender socket responses are JSON objects before callers use `.get()` (`body/mcp/blmcp/tools_helpers/connection.py`).
- [x] Preserve all matching context when overlapping RST search hits are merged (`body/mcp/blmcp/tools_helpers/rst_doc_search.py`).
- [x] Prevent empty RST section titles from leaking into sibling section text (`body/mcp/blmcp/tools_helpers/rst_parse_docs.py`).
- [x] Make deferred non-strict results use the synchronous path's JSON fallback and always close/remove clients on serialization failure (`body/addon/blender_mcp_addon/deferred_tool.py`).
- [x] Add bounded, non-blocking LLM HTTP calls in the chat client (`body/chat_client/chat_client.py`).
- [x] Preserve MCP error state in Anthropic `tool_result` messages (`body/chat_client/chat_client.py`).

## Medium

- [x] Reject malformed OpenAI tool arguments instead of invoking tools with `{}` (`body/chat_client/chat_client.py`).
- [x] Parse quoted `--server-command` values with `shlex.split` and reject empty commands (`body/chat_client/chat_client.py`).
- [ ] Replace tick-based incomplete-client expiration with monotonic deadlines (`body/addon/blender_mcp_addon/mcp_to_blender_server.py`).
- [ ] Cap concurrent incomplete Blender socket clients (`body/addon/blender_mcp_addon/mcp_to_blender_server.py`).
- [ ] Implement buffered writes for non-blocking Blender client sockets; current `sendall()` can truncate under backpressure (`body/addon/blender_mcp_addon/mcp_to_blender_server.py`).
- [x] Replace the writer prompt's undefined `mesh_data`/`obj` example with runnable code (`brain/src/agents/prompts/writer.md`).
- [ ] Add Brain unit tests for tool mappings, source generation, subprocess argument safety, and clean-build assets.

## Existing User Work Requiring Follow-up

These findings are documented but the existing modified file is not changed by this audit without explicit coordination.

- [x] Replace unsupported `bmesh.ops.intersect_with_mesh` and free temporary meshes in `check_collisions` (`body/addon/blender_mcp_addon/blmcp_helpers.py`).
- [x] Restore render engine when `auto_bake_textures` rejects a non-mesh object (`body/addon/blender_mcp_addon/blmcp_helpers.py`).
- [x] Restore all render settings in `get_fast_feedback`, including on exceptions (`body/addon/blender_mcp_addon/blmcp_helpers.py`).
