import chromadb
import ollama

DATA_PATH = "data"
CHROMA_DB_PATH = "chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

collection = chroma_client.get_or_create_collection("documents")

user_querry = input("Enter your questions about the documents : ")

results = collection.query(
    query_texts=[user_querry],
    n_results=1,
)

client = ollama.Client()

system_prompt = """
You are a helpful assistant that can answer questions about the documents.

if you don't know the answer, just say "I don't know".

---------

Here is the documents :


""" + str(results["documents"][0]) +"""
"""

response = client.chat(
    model="llama3.2",
    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_querry}],
    stream=True,
)

for chunk in response:
    print(chunk["message"]["content"], end="", flush=True)