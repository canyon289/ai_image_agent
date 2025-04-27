"""Gemma MCP Client,"""

import asyncio
import re
from typing import Optional
from contextlib import AsyncExitStack
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.fastmcp import FastMCP

from ollama import chat
from ollama import ChatResponse

from google import genai


mcp = FastMCP("Weather app")

logging.basicConfig(
    level=logging.DEBUG, # Log everything from DEBUG level upwards
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_user_prompt(self, user_prompt: str) -> str:
        """Process a user_prompt using Gemma and available tools"""

        all_tools = await self.session.list_tools()

        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        } for tool in all_tools.tools]

        # Send request with function declarations
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Or your preferred model supporting function calling
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                tools=[tools],
            ),  # Example other config
        )

        final_text = []
        assistant_message_content = []

        if response.candidates[0].content.parts[0].function_call:
            logging.info("Tool call with %s" % function_call_json)

            function_call = response.candidates[0].content.parts[0].function_call

            result = await self.session.call_tool(function_call, function_call.args)

            contents.append(types.Content(role="user", parts=tool_response_parts))
            logging.info(f"Added {len(tool_response_parts)} tool response parts to history.")

            response = await client.aio.models.generate_content(
                model=model,
                contents=contents,  # Send updated history
                config=types.GenerateContentConfig(
                    temperature=1.0,
                    tools=[tools],
                ),  # Keep sending same config
            )
            contents.append(response.candidates[0].content)


            # We already checked for weather so we don't need to go again
            model_response = model_call(weather_prompt_text)
            final_text.append(model_response)

        # No tool call
        else:
            logging.debug("No tool call")
            final_text.append(model_response)
            assistant_message_content.append(model_response)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                user_prompt = input("\nuser_prompt: ").strip()
                logging.info("User prompt is: %s", user_prompt)

                if user_prompt.lower() == 'q':
                    break

                response = await self.process_user_prompt(user_prompt)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        # Hardcode the client for now
        server = "weather_server.py"
        await client.connect_to_server(server)
        # await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
