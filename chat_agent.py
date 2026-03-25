import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from logger import log_message

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7,
    max_tokens=500,
    openai_api_key=OPENAI_API_KEY
)

_conversations = {}

def get_conversation(session_id: str):
    if session_id not in _conversations:
        memory = ConversationBufferMemory()
        _conversations[session_id] = ConversationChain(llm=llm, memory=memory)
    return _conversations[session_id]

def chat_with_ai(session_id: str, user_input: str) -> str:
    try:
        conversation = get_conversation(session_id)
        response = conversation.run(user_input)
        log_message(f" AI Response: {response}")
        return response
    except Exception as e:
        log_message(f" Chat Agent Error: {str(e)}", "error")
        raise

def clear_conversation(session_id: str):
    if session_id in _conversations:
        del _conversations[session_id]