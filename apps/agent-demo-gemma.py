import gradio as gr
import re
import json
from ollama import chat
from ollama import ChatResponse

# --- Helper functions ---

model = 'gemma3:4b-it-qat'  # or use 'gemma3:12b-it-qat' if you have enough memory

def model_call(prompt):
    response: ChatResponse = chat(
        model=model,
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )
    return response['message']['content']

def augmented_model_call(system_prompt, user_prompt, print_prompt=False):
    combined_prompt = f"{system_prompt}\n{user_prompt}"
    if print_prompt:
        print(combined_prompt)
    return model_call(combined_prompt)

pattern = r"```json\n(.*?)\n```"

def parse_response(model_response):
    if tool_call := re.search(pattern, model_response, re.DOTALL):
        return json.loads(tool_call.groups(0)[0])[0]

def get_weather(city):
    """Simple hardcoded weather lookup."""
    if city.lower() in {"austin", "sydney"}:
        return "sunny"
    else:
        return "cloudy"

# --- Gradio app function ---

def gradio_chat_interaction(user_prompt):
    system_prompt = '''
    You have the following functions available:

    def get_weather(city: str)
    """Given a city returns the weather for that city"""

    If you call this function return the json [{"city": city}] and nothing else
    otherwise respond normally.
    '''

    # Get initial model response
    model_response = augmented_model_call(system_prompt, user_prompt)

    # Try parsing a function call
    function_call_json = parse_response(model_response)

    if not function_call_json:
        return model_response, "No tool call detected."

    # If function call detected, call the tool
    weather = get_weather(function_call_json["city"])
    function_response_prompt = f"The weather in {function_call_json['city']} is {weather}, tell me the weather nicely"
    final_model_response = model_call(function_response_prompt)

    return final_model_response, f"Tool call detected: city = {function_call_json['city']}, weather = {weather}"

# --- Gradio Interface ---

iface = gr.Interface(
    fn=gradio_chat_interaction,
    inputs=gr.Textbox(lines=2, placeholder="Type your message here..."),
    outputs=[
        gr.Textbox(label="Final Model Response"),
        gr.Textbox(label="Under the Hood (Tool Calls)"),
    ],
    title="Agent Demo: Chat with Tool Usage",
    description="Type a message. If a tool call is needed, the system will call the tool and update the response.",
)

if __name__ == "__main__":
    iface.launch()