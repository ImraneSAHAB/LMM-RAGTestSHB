from ollama import chat

def test_ollama():
    try:
        while True:
            user_question = input("\Requête (q pour quitter) : ")
            if user_question.lower() == 'q': return print("Au revoir!")
            
            conversation.append({'role': 'user', 'content': user_question})
            stream = chat(model='llama3.2', messages=conversation, stream=True)
            
            for chunk in stream: print(chunk['message']['content'], end='', flush=True)
            
    except Exception as e: print(f"\nErreur : {str(e)}")

if __name__ == "__main__":
    conversation = []
    prompt = input("Prompt (* pour aucun) : ")
    if prompt != '*': conversation.append({'role': 'system', 'content': prompt})
    test_ollama()