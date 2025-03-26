from langchain_community.document_loaders import PyPDFDirectoryLoader
import chromadb
import re
from datetime import datetime

DATA_PATH = "data"
CHROMA_DB_PATH = "chroma_db"
MAX_CHUNK_SIZE = 2000  # Taille maximale avant découpage

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

def process_document(doc):
    content = doc.page_content
    
    # Si le document est petit, le garder entier
    if len(content) <= MAX_CHUNK_SIZE:
        return [{
            'content': content,
            'type': 'full_doc',
            'titles': extract_titles(content)
        }]
    
    # Sinon, découper en sections basées sur les titres
    sections = []
    current_section = ""
    current_titles = []
    
    for line in content.split('\n'):
        if detect_title(line):
            # Sauvegarder la section précédente si elle existe
            if current_section:
                sections.append({
                    'content': current_section,
                    'type': 'section',
                    'titles': current_titles
                })
            current_section = line + "\n"
            current_titles = [line.strip()]
        else:
            current_section += line + "\n"
    
    # Ajouter la dernière section
    if current_section:
        sections.append({
            'content': current_section,
            'type': 'section',
            'titles': current_titles
        })
    
    return sections

def extract_titles(content):
    return [line.strip() for line in content.split('\n') if detect_title(line)]

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
    doc_id = 0

    for doc in raw_documents:
        print(f"\nTraitement du document : {doc.metadata['source']}")
        processed_sections = process_document(doc)
        
        for section in processed_sections:
            documents.append(section['content'])
            metadatas.append({
                "source": doc.metadata["source"],
                "page": doc.metadata.get("page", 0),
                "titles": ", ".join(section['titles']) if section['titles'] else "Sans titre",
                "type": section['type'],
                "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            ids.append(str(doc_id))
            doc_id += 1

    if documents:
        print("\nAjout des documents à la base de données...")
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"Ajouté {len(documents)} sections à la base de données")
    else:
        print("Aucun nouveau document trouvé")

if __name__ == "__main__":
        
    print(f"Placez vos fichiers PDF dans le dossier '{DATA_PATH}' et appuyez sur Entrée...")
    input()
    
    add_documents_to_db()
    print("\nTraitement terminé!")