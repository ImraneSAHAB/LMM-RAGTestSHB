import ollama
import requests
import json
import sys
import time

class Agent:
    def __init__(self, name: str, role: str, goal: str, backstory: str, model: str):
        self.name, self.role, self.goal, self.backstory, self.model = name, role, goal, backstory, model

    def think(self, context: str) -> str:
        prompt = f"""En tant que {self.role}, {self.goal}

Votre contexte : {self.backstory}

Contexte actuel :
{context}

Fournissez une réponse courte et structurée.
"""
        response_text = ""
        for chunk in ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            options={
                "num_predict": 200,  # Limite la longueur de la réponse
                "temperature": 0.7,   # Réduit la créativité pour des réponses plus directes
                "top_k": 10,          # Limite le nombre de tokens considérés
                "top_p": 0.7          # Réduit la diversité des réponses
            }
        ):
            if 'message' in chunk and 'content' in chunk['message']:
                response_text += chunk['message']['content']
        return response_text

class WebSearchSystem:
    def __init__(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.searcher = Agent(
                name="Chercheur",
                role=self.config['agents']['searcher']['role'],
                goal=self.config['agents']['searcher']['goal'],
                backstory=self.config['agents']['searcher']['backstory'],
                model=self.config['model']['name']
            )
            
            self.analyzer = Agent(
                name="Analyste",
                role=self.config['agents']['analyzer']['role'],
                goal=self.config['agents']['analyzer']['goal'],
                backstory=self.config['agents']['analyzer']['backstory'],
                model=self.config['model']['name']
            )
            
            self.writer = Agent(
                name="Rédacteur",
                role=self.config['agents']['writer']['role'],
                goal=self.config['agents']['writer']['goal'],
                backstory=self.config['agents']['writer']['backstory'],
                model=self.config['model']['name']
            )
            
            self.citer = Agent(
                name="Citation",
                role=self.config['agents']['citer']['role'],
                goal=self.config['agents']['citer']['goal'],
                backstory=self.config['agents']['citer']['backstory'],
                model=self.config['model']['name']
            )
            
        except Exception as e:
            print(f"Erreur de configuration : {str(e)}")
            sys.exit(1)

    def search_web(self, query: str) -> str:
        try:
            data = requests.post(
                self.config['search']['url'],
                json={
                    "api_key": self.config['search']['api_key'],
                    "query": query,
                    **self.config['search']
                },
                timeout=self.config['search']['timeout']
            ).json()

            results = []
            if 'answer' in data:
                results.append({
                    'title': 'Résumé',
                    'snippet': data['answer'],
                    'url': 'Résumé généré par l\'API',
                    'source_type': 'résumé'
                })
            if 'results' in data:
                results.extend([{
                    'title': r.get('title', ''),
                    'snippet': r.get('content', ''),
                    'url': r.get('url', 'URL non disponible'),
                    'source_type': 'web',
                    'published_date': r.get('published_date', 'Date non disponible')
                } for r in data['results'][:5]])  # Augmenté à 5 résultats
            
            return json.dumps(results or [{'title': 'Aucun résultat', 'snippet': 'Essayez de reformuler.', 'url': 'N/A', 'source_type': 'aucun'}], ensure_ascii=False)
            
        except Exception as e:
            return json.dumps([{'title': 'Erreur', 'snippet': str(e), 'url': 'N/A', 'source_type': 'erreur'}], ensure_ascii=False)

    def process_results(self, search_results: str) -> str:
        try:
            results = json.loads(search_results)
            if not results:
                return "Aucun résultat trouvé."

            # Le chercheur analyse les résultats
            search_analysis = self.searcher.think(
                f"Analysez ces résultats de recherche et identifiez les informations clés (réponse courte) :\n{json.dumps(results, ensure_ascii=False, indent=2)}"
            )

            # L'analyste synthétise l'analyse
            analysis = self.analyzer.think(
                f"En vous basant sur l'analyse du chercheur, fournissez une synthèse finale courte et structurée :\n{search_analysis}"
            )
            
            # Le rédacteur écrit la réponse
            response = self.writer.think(
                f"Rédigez une réponse claire et concise en utilisant les informations suivantes :\n{analysis}"
            )
            
            # Préparer les informations de source pour l'agent citer
            source_info = []
            for i, result in enumerate(results):
                if result.get('source_type') != 'aucun' and result.get('source_type') != 'erreur':
                    source_info.append(f"Source {i+1}: {result.get('title')} - {result.get('url')} - {result.get('published_date', 'Date non disponible')}")
            
            # Le gestionnaire de citations ajoute les sources avec le contexte complet
            citations = self.citer.think(
                f"Citez toutes les sources utilisées dans la réponse précédente. Utilisez le format suivant pour chaque source :\n" +
                f"Source pour [description de l'information] : [titre de la source] (URL: [url]) (Date: [date])\n\n" +
                f"IMPORTANT : Assurez-vous que chaque citation correspond exactement à la source qui contient l'information mentionnée. Ne citez pas une source pour une information qu'elle ne contient pas.\n\n" +
                f"Réponse à citer :\n{response}\n\n" +
                f"Sources disponibles :\n{chr(10).join(source_info)}"
            )
            
            # Vérifier que toutes les sources sont citées
            source_count = len([s for s in results if s.get('source_type') not in ['aucun', 'erreur']])
            citation_lines = [line for line in citations.split('\n') if line.strip() and not line.startswith('Note:')]
            
            if len(citation_lines) < source_count:
                citations += f"\n\nNote : Seules {len(citation_lines)} sources sur {source_count} ont été citées correctement."
            
            # Vérification supplémentaire pour s'assurer que les citations sont correctes
            # Si l'utilisateur signale que les citations sont incorrectes, nous pouvons ajouter une note
            citations += "\n\nNote : Si vous constatez des erreurs dans les citations, veuillez les signaler."
            
            # Combiner la réponse et les citations
            final_response = f"{response}\n\nSources :\n{citations}"
            
            return final_response
            
        except Exception as e:
            return f"Erreur de traitement : {str(e)}"

    def research(self, query: str):
        print("\nAnalyse en cours...")
        analysis = self.process_results(self.search_web(query))
        print("\nRéponse :")
        print(analysis)
        print("\n")

def main():
    try:
        system = WebSearchSystem()
        print("Système de recherche web multi-agents (tapez 'q' pour quitter)")
        
        while True:
            query = input("\nQue souhaitez-vous rechercher ? ")
            if query.lower() == 'q':
                break
            system.research(query)
            
    except Exception as e:
        print(f"Erreur : {str(e)}")

if __name__ == "__main__":
    main() 