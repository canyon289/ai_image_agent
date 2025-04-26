"""Gemma MCP Client,

TODO: Understand prompts and how to use them. How does LLM or framework select which prompt to use
TODO: Figure out what resources are

Prompts are user controlled, the user decides if they want them
Resources are client controlled
Tools are model controlled


Oh I see, the user prompt is augmented
"""

import asyncio
import re
from typing import Optional
from contextlib import AsyncExitStack
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ollama import chat
from ollama import ChatResponse

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather app")
TOOL_PATTERN = f"```json\n(.*?)\n``"

import json
import re

logging.basicConfig(
    level=logging.DEBUG, # Log everything from DEBUG level upwards
)


###########################################
# All these are the same from the notebook
###########################################

def model_call(model_prompt, model='gemma3:12b'):
    
    response: ChatResponse = chat(model=model, messages=[
      {
        'role': 'user',
        'content': model_prompt,
      },
    ])
    return response['message']['content']

def augmented_model_call(system_prompt, user_prompt, print_prompt = False):
    combined_prompt = f"{system_prompt}\n{user_prompt}"
    return model_call(combined_prompt)

def parse_response(model_response):
    if tool_call := re.search(TOOL_PATTERN, model_response):
        parsed_arg = json.loads(tool_call.groups(0)[0])[0]
        return parsed_arg

###########################################
# These are all new
###########################################

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
    
    async def model_call(prompt):
        model = 'gemma3:12b'
        response: ChatResponse = chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        return response['message']['content']

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

        messages = [
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        all_tools = await self.session.list_tools()

        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in all_tools.tools]

        # Get all prompts
        all_prompts = await self.session.list_prompts()

        available_prompts = [prompt for prompt in all_prompts.prompts]
        
        # We also can get one prompt
        # https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#writing-mcp-clients
        prompt = await self.session.get_prompt("weather_prompt")
        system_prompt = prompt.messages[0].content.text

        # import pdb; pdb.set_trace()

        # Put together system prompt and
        model_response = augmented_model_call(system_prompt=system_prompt, user_prompt=user_prompt)

        # Detect if a response is a tool call or text
        function_call_json = parse_response(model_response)

        final_text = []
        assistant_message_content = []

        # Tool call is found
        if function_call_json:
            logging.debug("Tool call with %s" % function_call_json)

            result = await self.session.call_tool('weather_tool', function_call_json)

            # Get the weather
            weather_result = result.content[0].text

            # This is how we can construct the prompt
            # There also seems to be an mcp.response functionality but I don't know how to use it
            weather_prompt = await self.session.get_prompt("weather_response_prompt", 
                                                            parameters = {function_call_json["city"], weather_result})
            import pdb; pdb.set_trace()

            # We already checked for weather so we don't need to go again
            model_response = model_call(function_response_prompt)

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
                # user_prompt = "Whats the weather in london?"
                logging.info("User prompt is %s", user_prompt)

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
