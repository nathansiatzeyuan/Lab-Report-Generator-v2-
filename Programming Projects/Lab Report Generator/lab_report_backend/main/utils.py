import PyPDF2
import google.generativeai as genai
import os
from dotenv import load_dotenv


def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

def GPT_return_text(question):
    load_dotenv()

    genai.configure(api_key=os.environ["API_KEY"])

    # Create the model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    )

    chat_session = model.start_chat(
    history=[
    ]
    )
    response = chat_session.send_message(question)
    return response.text
