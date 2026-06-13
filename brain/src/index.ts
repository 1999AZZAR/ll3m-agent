import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";
import net from "net";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Path to Blender MCP data (RAG source)
const BLENDER_MCP_DATA = path.join(__dirname, "../../body/mcp/blmcp/data/api");

// Blender Socket Params
const BLENDER_HOST = "localhost";
const BLENDER_PORT = 9876;

const server = new Server(
  {
    name: "ll3m-agent-server",
    version: "2.0.0",
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
           resolve({ status: "error", message: "Empty response from Blender. Is the addon server started?" });
           return;
        }
        resolve(JSON.parse(jsonStr));
      } catch (e) {
        reject(e);
      }
    });

    client.on("error", (err) => {
      reject(new Error(`Failed to connect to Blender at ${BLENDER_HOST}:${BLENDER_PORT}. Make sure the addon is installed and "Start Server" is clicked.`));
    });
    
    client.setTimeout(300000); // 5 min timeout
    client.on("timeout", () => {
        client.destroy();
        reject(new Error("Blender connection timed out."));
    });
  });
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "generate_modeling_plan",
        description: "Generate a multi-component 3D modeling plan (Planner Persona).",
        inputSchema: {
          type: "object",
          properties: {
            prompt: { type: "string", description: "User's creation request." },
          },
          required: ["prompt"],
        },
      },
      {
        name: "get_agent_instructions",
        description: "Retrieve specialized instructions for LL3M agents (Planner, Writer, Debugger).",
        inputSchema: {
          type: "object",
          properties: {
            agent: { type: "string", enum: ["planner", "writer", "debugger"] },
          },
          required: ["agent"],
        },
      },
      {
        name: "retrieve_blender_api_context",
        description: "Search local Blender API documentation (RST) for correct usage examples.",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "API keyword, function, or task." },
          },
          required: ["query"],
        },
      },
      {
        name: "execute_blender_code",
        description: "Execute Python code directly inside Blender via the MCP addon bridge.",
        inputSchema: {
          type: "object",
          properties: {
            code: { type: "string", description: "Python code to execute." },
            strict_json: { type: "boolean", description: "Whether to enforce strict JSON results.", default: false },
          },
          required: ["code"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "generate_modeling_plan":
      const planPrompt = await fs.readFile(path.join(__dirname, "agents/prompts/planner.md"), "utf8");
      return {
        content: [
          { type: "text", text: `PLANNER_INSTRUCTIONS:\n${planPrompt}\n\nUSER_REQUEST: ${args?.prompt}` }
        ],
      };

    case "get_agent_instructions":
      const agentPath = path.join(__dirname, `agents/prompts/${args?.agent}.md`);
      const instructions = await fs.readFile(agentPath, "utf8");
      return {
        content: [{ type: "text", text: instructions }],
      };

    case "retrieve_blender_api_context":
      try {
        const query = (args?.query as string).replace(/['"]/g, '');
        const cmd = `grep -ri "${query}" "${BLENDER_MCP_DATA}" | head -n 20`;
        const result = execSync(cmd, { encoding: "utf8" });
        return {
          content: [{ type: "text", text: result || "No relevant documentation found." }],
        };
      } catch (e) {
        return {
          content: [{ type: "text", text: "Error searching documentation: " + e }],
        };
      }

    case "execute_blender_code":
      try {
        const result = await sendToBlender(args?.code as string, !!args?.strict_json);
        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (e: any) {
        return {
          content: [{ type: "text", text: "Error executing code: " + e.message }],
        };
      }

    default:
      throw new Error("Tool not found");
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
