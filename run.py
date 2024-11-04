import gradio as gr
import time
from checker import checker
# Assuming you have a function `checker(query)` that takes a user query and returns the verified response.


# Token streaming generator
def stream_response(user_input):
    response = checker(user_input)
    print(response)
    for token in response:
        yield token
        time.sleep(0.04)  # Simulate delay between tokens to mimic real-time response

# Defining the Gradio UI for the RAG model
def chat_interface(user_input, history):
    history = history or []
    response_stream = stream_response(user_input)
    response = ""
    for token in response_stream:
        response += token
        yield history + [(user_input, response)], history + [(user_input, response)]

# Create Gradio Blocks Interface
def run_interfaces():
    with gr.Blocks() as ui:
        gr.Markdown("# Chat with RAG Model for Truth Verification")
        
        chatbot = gr.Chatbot(label="Chat")
        user_input = gr.Textbox(label="Your Query", placeholder="Enter your question here...")
        submit_button = gr.Button("Submit")
        clear_button = gr.Button("Clear Chat")

        # Maintain history state across interactions
        state = gr.State([])

        # Set up the submit button to trigger the response generation
        submit_button.click(fn=chat_interface, inputs=[user_input, state], outputs=[chatbot, state], api_name="stream")

        # Set up the clear button to reset the chat history
        clear_button.click(fn=lambda: ([], []), inputs=None, outputs=[chatbot, state])
    # Launch the Gradio UI
    ui.queue().launch(share=True)

def run():
    run_interfaces()

if __name__ == "__main__":
    run()
