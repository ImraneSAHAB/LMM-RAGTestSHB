from langchain_community.document_loaders import PyPDFDirectoryLoader
import chromadb
import os
import re
from datetime import datetime
import shutil

DATA_PATH = "data"
CHROMA_DB_PATH = "chroma_db"

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

def add_documents_to_db():
    print("Initialisation de ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = chroma_client.get_or_create_collection("documents")

    print("Chargement des documents...")
    loader = PyPDFDirectoryLoader(path=DATA_PATH)
    raw_documents = loader.load()
    print(f"Nombre de documents chargés : {len(raw_documents)}")

    documents = []
    metadatas = []
    ids = []

    for i, doc in enumerate(raw_documents):
        
        # Extraire les titres du document
        lines = doc.page_content.split('\n')
        titles = [line.strip() for line in lines if detect_title(line)]
        
        # Ajouter le document entier
        documents.append(doc.page_content)
        metadatas.append({
            "source": doc.metadata["source"],
            "page": doc.metadata.get("page", 0),
            "titles": ", ".join(titles) if titles else "Sans titre",
            "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        ids.append(str(i))

    if documents:
        print("\nAjout des documents à la base de données...")
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"Ajouté {len(documents)} documents à la base de données")
    else:
        print("Aucun nouveau document trouvé")

if __name__ == "__main__":
    # Supprimer le dossier chroma_db s'il existe
    if os.path.exists(CHROMA_DB_PATH):
        print(f"Suppression de l'ancienne base de données...")
        shutil.rmtree(CHROMA_DB_PATH)
        print(f"Base de données supprimée")
    
    # Créer le dossier data s'il n'existe pas
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Dossier {DATA_PATH} créé")
    
    print(f"Placez vos fichiers PDF dans le dossier '{DATA_PATH}' et appuyez sur Entrée...")
    input()
    
    add_documents_to_db()
    print("\nTraitement terminé!")