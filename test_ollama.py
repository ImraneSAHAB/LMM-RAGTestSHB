from ollama import chat

def test_ollama():
    try:
        # Définir le prompt initial
        system_prompt = {
            'role': 'system',
            'content': 'Tu es un assistant amical et serviable qui parle français. Tu dois répondre de manière concise.'
        }
        
        # Initialiser la conversation avec le prompt système
        conversation = [system_prompt]
        
        while True:
            # Demander la question à l'utilisateur
            user_question = input("\nEntrez votre question (ou 'q' pour quitter) : ")
            
            if user_question.lower() == 'q':
                print("Au revoir!")
                break
            
            # Ajouter la question à la conversation
            conversation.append({
                'role': 'user',
                'content': user_question,
            })
            
            response = chat(model='llama3.2', messages=conversation)
            
            # Ajouter la réponse à la conversation
            conversation.append({
                'role': 'assistant',
                'content': response['message']['content']
            })
            
            print(f"\nQuestion : {user_question}")
            print("\nRéponse :", response['message']['content'])
            
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")

if __name__ == "__main__":
    print("Test de connexion à Ollama...")
    test_ollama() 