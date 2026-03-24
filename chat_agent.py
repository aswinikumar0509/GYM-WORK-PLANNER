from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7, openai_api_key=OPENAI_API_KEY)

def create_conversation():
    memory = ConversationBufferMemory()
    return ConversationChain(llm=llm, memory=memory)

def chat_with_ai(conversation, user_input):
    return conversation.run(user_input)