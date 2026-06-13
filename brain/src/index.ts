import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";
import net from "net";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Paths relative to dist/ or src/
const BODY_PATH = path.join(__dirname, "../../body");
const BLENDER_MCP_DATA = path.join(BODY_PATH, "mcp/blmcp/data/api");
const TOOLS_CODE_PATH = path.join(BODY_PATH, "mcp/blmcp/tools");
const PYTHON_INTERPRETER = path.join(BODY_PATH, "venv/bin/python3");
const API_BRIDGE_PATH = path.join(__dirname, "api_docs_bridge.py");

// Blender Socket Params
const BLENDER_HOST = "localhost";
const BLENDER_PORT = 9876;

const server = new Server(
  {
    name: "ll3m-agent-server",
    version: "3.0.0",
    description: "Unified LL3M Agent with Integrated Blender Control & RAG",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * Communicates with the Blender addon via TCP socket.
 */
async function sendToBlender(code: string, strictJson: boolean = false): Promise<any> {
  return new Promise((resolve, reject) => {
    const client = new net.Socket();
    let responseData = Buffer.alloc(0);

    client.connect(BLENDER_PORT, BLENDER_HOST, () => {
      const request = JSON.stringify({
        type: "execute",
        code: code,
        strict_json: strictJson,
      }) + "\0";
      client.write(request);
    });

    client.on("data", (data: any) => {
      responseData = Buffer.concat([responseData, Buffer.from(data)]);
      if (responseData.includes(0)) {
        client.destroy();
      }
    });

    client.on("close", () => {
      try {
        const nullIndex = responseData.indexOf(0);
        const jsonStr = responseData.slice(0, nullIndex === -1 ? undefined : nullIndex).toString("utf8");
        if (!jsonStr) {
           resolve({ status: "error", message: "Empty response from Blender. Ensure 'Start Server' is clicked in the Blender addon." });
           return;
        }
        resolve(JSON.parse(jsonStr));
      } catch (e) {
        reject(e);
      }
    });

    client.on("error", (err) => {
      reject(new Error(`Connection failed: ${err.message}. Ensure Blender is open and the MCP addon server is running.`));
    });
    
    client.setTimeout(300000); 
    client.on("timeout", () => { client.destroy(); reject(new Error("Timeout")); });
  });
}

/**
 * Helper to run a tool code file from the body.
 */
async function runBodyTool(toolName: string, params: any = null): Promise<any> {
    const filePath = path.join(TOOLS_CODE_PATH, `${toolName}_toolcode.py`);
    let code = await fs.readFile(filePath, "utf8");
    
    // Inject templates or dependencies if needed (Simplification: we assume they are standalone or we use simple injection)
    const paramsJson = JSON.stringify(params);
    code += `
import json
try:
    params_dict = json.loads('${paramsJson}')
    # Simple check for Params class
    if 'Params' in locals() or 'Params' in globals():
        p = Params(**params_dict)
    else:
        p = params_dict
    result = main(p)
    if callable(result):
        res_data = {"status": "ok", "message": "Deferred task started"}
    else:
        res_data = result._asdict() if hasattr(result, "_asdict") else result
    print("__BLMCP_RESULT__" + json.dumps(res_data))
except Exception as e:
    import traceback
    print("__BLMCP_RESULT__" + json.dumps({"status": "error", "message": str(e), "trace": traceback.format_exc()}))
`;
    return await sendToBlender(code, true);
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "generate_modeling_plan",
        description: "Generate a multi-component 3D modeling plan.",
        inputSchema: { type: "object", properties: { prompt: { type: "string" } }, required: ["prompt"] },
      },
      {
        name: "get_agent_instructions",
        description: "Retrieve specialized persona instructions (planner/writer/debugger).",
        inputSchema: { type: "object", properties: { agent: { type: "string", enum: ["planner", "writer", "debugger"] } }, required: ["agent"] },
      },
      {
        name: "get_api_docs",
        description: "Get precise Blender Python API documentation and examples.",
        inputSchema: { type: "object", properties: { identifier: { type: "string", description: "Fully qualified name, e.g., 'bpy.types.Scene'" } }, required: ["identifier"] },
      },
      {
        name: "execute_blender_code",
        description: "Execute arbitrary Python code in Blender.",
        inputSchema: { type: "object", properties: { code: { type: "string" }, strict_json: { type: "boolean" } }, required: ["code"] },
      },
      {
        name: "get_scene_summary",
        description: "List all objects, collections, and active state in the scene.",
        inputSchema: { type: "object", properties: {} },
      },
      {
        name: "get_object_details",
        description: "Get technical details of a specific object.",
        inputSchema: { type: "object", properties: { object_name: { type: "string" } }, required: ["object_name"] },
      },
      {
        name: "render_viewport",
        description: "Quick render of current viewport to a file.",
        inputSchema: { type: "object", properties: { output_path: { type: "string" } } },
      },
      {
        name: "save_blend",
        description: "Save current .blend file.",
        inputSchema: { type: "object", properties: { filepath: { type: "string" } }, required: ["filepath"] },
      },
      {
        name: "get_screenshot",
        description: "Capture a screenshot of the Blender window (returns base64).",
        inputSchema: { type: "object", properties: {} },
      }
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "generate_modeling_plan":
      const planPrompt = await fs.readFile(path.join(__dirname, "agents/prompts/planner.md"), "utf8");
      return { content: [{ type: "text", text: `PLANNER_INSTRUCTIONS:\n${planPrompt}\n\nUSER_REQUEST: ${args?.prompt}` }] };

    case "get_agent_instructions":
      const instructions = await fs.readFile(path.join(__dirname, `agents/prompts/${args?.agent}.md`), "utf8");
      return { content: [{ type: "text", text: instructions }] };

    case "get_api_docs":
      try {
        const result = execSync(`${PYTHON_INTERPRETER} "${API_BRIDGE_PATH}" "${args?.identifier}"`, { encoding: "utf8" });
        return { content: [{ type: "text", text: result }] };
      } catch (e: any) {
        return { content: [{ type: "text", text: "Error fetching docs: " + e.message }] };
      }

    case "execute_blender_code":
        try {
          const result = await sendToBlender(args?.code as string, !!args?.strict_json);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (e: any) {
          return { content: [{ type: "text", text: "Error: " + e.message }] };
        }

    case "get_scene_summary":
        const sceneRes = await runBodyTool("get_objects_summary");
        return { content: [{ type: "text", text: JSON.stringify(sceneRes, null, 2) }] };

    case "get_object_details":
        const objRes = await runBodyTool("get_object_detail_summary", { object_name: args?.object_name });
        return { content: [{ type: "text", text: JSON.stringify(objRes, null, 2) }] };

    case "render_viewport":
        const rendRes = await runBodyTool("render_viewport_to_path", { output_path: args?.output_path || "render.png" });
        return { content: [{ type: "text", text: JSON.stringify(rendRes, null, 2) }] };

    case "save_blend":
        const saveCode = `import bpy; bpy.ops.wm.save_as_mainfile(filepath='${args?.filepath}')\nresult={"status":"saved"}`;
        const saveRes = await sendToBlender(saveCode, true);
        return { content: [{ type: "text", text: JSON.stringify(saveRes, null, 2) }] };

    case "get_screenshot":
        // Using window screenshot toolcode
        const screenRes = await runBodyTool("get_screenshot_of_window_as_image");
        return { content: [{ type: "text", text: JSON.stringify(screenRes, null, 2) }] };

    default:
      throw new Error("Tool not found");
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
