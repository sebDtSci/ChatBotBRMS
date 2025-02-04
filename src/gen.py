import ollama
import logging
import streamlit as st
import os
import asyncio

# ChatBot integration
from shortterm_memory.ChatbotMemory import ChatbotMemory
# from rag.new_chromadb import rag_pipeline

# BRMS integration
from brmsAPI.brmsAssurance import brmsCall, clear_dialog_element

# Désactiver le parallélisme pour éviter les deadlocks
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Param logger
logging.basicConfig(filename="app.log", filemode="w", level=logging.WARNING)

class Generate:
    def __init__(self, model: str = "mistral:latest", ollama_options=None):
        self.model = model
        self._ollama_option = ollama_options if ollama_options else {'temperature': 1}
        self.memory = ChatbotMemory()
        self.memoire_contextuel_assurance = ""

    def remember(self, sauvegarde) -> None:
        try:
            for _, row in sauvegarde.iterrows():
                self.memory.update_memory(row['user'], row['bot'])
            st.sidebar.success("Chargement effectué !")
        except Exception as e:
            st.sidebar.error(f"Erreur : {e}")

    async def _async_brms_call(self, user_input):
        return brmsCall(user_input)

    async def ans(self, user_input: str):
        user_input += self.memoire_contextuel_assurance if self.memoire_contextuel_assurance else ""

        # Appel BRMS si nécessaire
        brms_task = asyncio.create_task(self._async_brms_call(user_input)) if "assurance" in user_input else None

        # Préparer le prompt
        prompt = (
            "Tu es un assistant intelligent. Utilise les informations suivantes pour aider l'utilisateur.\n\n"
            f"Mémoire du chatbot :\n{self.memory.get_memory()}\n\n"
            f"Question de l'utilisateur :\n{user_input}\n\n"
            "Réponds de manière claire, concise et structurée :\n"
        )

        # Générer la réponse avec Ollama
        result = ollama.generate(
            model=self.model,
            prompt=prompt,
            stream=True,
            options=self._ollama_option
        )

        response = ""
        async for chunk in result:
            response += chunk['response']
            yield chunk['response']

        # Traitement de la réponse BRMS si applicable
        if brms_task:
            sentence, liste_element, solve_status = await brms_task
            if solve_status:
                user_input = clear_dialog_element(user_input, liste_element)
                self.memoire_contextuel_assurance = ""
            else:
                self.memoire_contextuel_assurance = f" Ces éléments sont à retenir pour l'assurance : {liste_element}"

        self.memory.update_memory(user_input, response)
        logging.info(f"Réponse générée avec le modèle : {self.model}")
