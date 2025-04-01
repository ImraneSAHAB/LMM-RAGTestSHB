from langchain_community.document_loaders import PyPDFDirectoryLoader
import os
import re

def detect_title(text):
    # Critères pour détecter un titre
    title_patterns = [
        r'^[A-Z\s]{2,}$',  # Texte tout en majuscules (modifié pour accepter 2 caractères minimum)
        r'^[0-9]+\.[0-9]*\s+[A-Z]',  # Titres numérotés (ex: 1.2 TITRE)
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Titres en CamelCase
        r'^[IVX]+\.\s+[A-Z]',  # Titres en chiffres romains
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*:$',  # Titres suivis de deux points
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\([^)]*\)$',  # Titres avec parenthèses
    ]
    
    text = text.strip()
    for pattern in title_patterns:
        if re.match(pattern, text):
            return True
    return False

def test_titles():
    data_path = "data"
    print(f"Vérification du dossier : {data_path}")
    print(f"Contenu du dossier : {os.listdir(data_path)}")
    
    try:
        loader = PyPDFDirectoryLoader(path=data_path)
        print("Chargement des documents...")
        raw_documents = loader.load()
        print(f"Nombre de documents chargés : {len(raw_documents)}")
        
        for doc in raw_documents:
            print(f"\nAnalyse du document : {doc.metadata['source']}")
            print("-" * 50)
            
            lines = doc.page_content.split('\n')
            print(f"Nombre de lignes analysées : {len(lines)}")
            
            for line in lines:
                if detect_title(line):
                    print(f"Titre détecté : {line.strip()}")
            print("-" * 50)
    except Exception as e:
        print(f"Erreur lors du traitement : {str(e)}")

if __name__ == "__main__":
    test_titles() 