from ollama import chat

def test_ollama():
    try:
        while True:
            user_question = input("\nRequête (laisser vide pour quitter) : ")
            if user_question == "" : return print("Au revoir!")
            
            conversation.append({'role': 'user', 'content': user_question})
            stream = chat(model='llama3.2', messages=conversation, stream=True)
            
            for chunk in stream: print(chunk['message']['content'], end='', flush=True)
            
    except Exception as e: print(f"\nErreur : {str(e)}")

if __name__ == "__main__":
    conversation = []
    prompt = input("Prompt (laisser vide pour aucun) : ")
    if prompt != None: conversation.append({'role': 'system', 'content': prompt})
    test_ollama()