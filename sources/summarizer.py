import os
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
import time


# Read the api key from a file
with open("api-key.txt", "r") as file:
    api_key = file.read().strip()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = api_key


def summarize_url(url):
    time.sleep(0.1)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Write a concise summary of the user provided text."),
        ("human", "{context}")
    ])
    chain = create_stuff_documents_chain(llm, prompt)
    loader = WebBaseLoader(url)
    docs = loader.load()
    return chain.invoke({"context": docs})

def summarize_text(text):
    time.sleep(0.1)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Write a concise summary of the user provided text."),
        ("human", "{context}")
    ])
    chain = create_stuff_documents_chain(llm, prompt)
    docs = [Document(text)]
    return chain.invoke({"context": docs})
