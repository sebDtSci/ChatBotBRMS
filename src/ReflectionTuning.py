import ollama

class GenerateReflexion:
    def __init__(self, model:str='mistral:latest', ollama_option=None) -> None:
        self.model = model
        self._ollama_option = ollama_option if ollama_option else {'temperature':1}
        self.reponse = ''
        
    def gen(self, input:str, memory:str)->str:
        self.reponse = ''
        prompt = (
            "Vous êtes un assistant intelligent dédié au 'Reflection-Tuning'."
            "S'il s'agit de banalité, remerciment, salutation ou de conversation simple ne répond rien!"
            "pour tous ce qui ne porte pas sur des maths, de la programation ou de l'ingénieurie ne répond rien!"
            "Si le sujet porte sur des maths, de la programation ou de l'ingénieurie voici les étape à suivre :\n\n"
            "Votre rôle est de clarifier, corriger, et enrichir l'input de l'utilisateur pour qu'un autre agent puisse fournir une réponse optimale.\n\n"
            "1. **Analyse et correction** : Identifiez les parties de l'input utilisateur qui sont ambiguës ou potentiellement incorrectes, et proposez des corrections ou reformulations.\n\n"
            "2. **Mise en évidence des étapes** : Élaborez les étapes nécessaires pour répondre à la question ou résoudre le problème. Soyez aussi exhaustif que possible.\n\n"
            "3. **Outils et méthodes** : Suggérez des outils techniques ou des approches spécifiques pour traiter la question. Justifiez pourquoi ces outils ou méthodes sont appropriés dans ce contexte.\n\n"
            "Votre but n'est pas de répondre directement à l'utilisateur, mais de fournir une base claire et détaillée pour que le prochain agent puisse répondre efficacement.\n\n"
            "Voici l'input de l'utilisateur :\n"
            f"{input}\n\n"
            "Voici la mémoire du chatbot (les échanges précédents). Utilise les informations présentes dans la mémoire du chatbot pour mieux contextualiser l'input et apporter des clarifications supplémentaires si nécessaire UNIQUEMENT si elles sont en rapport avec le nouvel input:\n"
            f"{memory}\n\n"
            )
        result = ollama.generate(
            model = self.model,
            prompt=prompt,
            stream=False,
            options=self._ollama_option
        )
        print("#######################\n\n",result["response"],'\n\n',"#######################")
        return result["response"]
    
    