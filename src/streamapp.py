import streamlit as st
from generateS import Generate
from saveConversation import save_conversation, load_conversations, delete_conversation
# from memory import ChatbotMemory
import subprocess
import re

def get_model_list():
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    models = [line.split()[0] for line in lines[1:]] 
    return models

def get_conversation_history(sauvegarde):
    for index, row in sauvegarde.iterrows():
        st.session_state.history.append({"user": row['user'], "bot": row['bot']})

def remove_think_tags(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

def remove_think_tags_streaming(response, buffer, in_think):
    """
    Gère le texte partiellement chunké contenant des balises <think>...</think>.
    - buffer : stocke le texte temporaire lorsqu'on est à l'intérieur de <think>.
    - in_think : indique si on est actuellement à l'intérieur des balises <think>.
    """
    cleaned_response = ""

    i = 0
    while i < len(response):
        if not in_think:
            start_idx = response.find("<think>", i)
            if start_idx != -1:
                cleaned_response += response[i:start_idx]
                in_think = True
                i = start_idx + len("<think>")
            else:
                cleaned_response += response[i:]
                break
        else:
            end_idx = response.find("</think>", i)
            if end_idx != -1:
                in_think = False
                i = end_idx + len("</think>")
            else:
                break  # On attend le prochain chunk pour compléter la balise de fermeture

    return cleaned_response, in_think

def main():
    st.title("Chatbot Interface with Memory")

    model_options = get_model_list()
    # model_options = ["aya:35b", "openchat:latest", "llama3:latest"]
    selected_model = st.selectbox("Choisissez le modèle" , model_options, index=None,placeholder="mistral:latest selected by default")
    if selected_model is None:
        selected_model = "openchat:latest"

    if "chatbot" not in st.session_state or st.session_state.model_name != selected_model:
        st.session_state.chatbot = Generate(model=selected_model)
        st.session_state.model_name = selected_model
    
    chatbot = st.session_state.chatbot

    if "history" not in st.session_state:
        st.session_state.history = []

    # Charger les conversations sauvegardées
    conversations_df = load_conversations()
    st.sidebar.title("Conversations sauvegardées")
    conversation_titles = conversations_df["Titre"].tolist()
    selected_conversation = st.sidebar.selectbox("Sélectionnez une conversation", conversation_titles)
    if st.sidebar.button("Load") and selected_conversation:
        chatbot.remember(conversations_df)
        get_conversation_history(conversations_df)
    if st.sidebar.button("Delete") and selected_conversation:
        delete_conversation(selected_conversation)
        st.rerun()
        
    with st.form('question', clear_on_submit=True):
        # text_area pour gérer la taille de manière dynamique
        user_input = st.text_area("You:", key="input", height=100)
        # user_input = st.text_input("You:", key="input")
        submitted = st.form_submit_button("Submit")
    if submitted and user_input:
        st.session_state.history.append({"user": user_input, "bot": ""})
        st.rerun()

    # Gestion des réponses du chatbot après l'envoi du message
    # if st.session_state.history and st.session_state.history[-1]["bot"] == "":
    #     thinkTime = False
    #     user_input = st.session_state.history[-1]["user"]
    #     response_generator = chatbot.ans(user_input)
    #     response = ""
    #     response_placeholder = st.empty()

    #     for chunk in response_generator:
    #        response += chunk
    #        response_placeholder.markdown(f"""
    #     <div style="text-align: left; padding: 10px; margin: 10px 0;">
    #        <div><b>Stem:</b></div>
    #        <div style="background-color: #229954; border-radius: 10px; padding: 10px;">
    #            {response}
    #        </div>
    #     </div>
    #    """, unsafe_allow_html=True)

    #     st.session_state.history[-1]["bot"] = response
    #     st.rerun()
    
    if st.session_state.history and st.session_state.history[-1]["bot"] == "":
        user_input = st.session_state.history[-1]["user"]
        response_generator = chatbot.ans(user_input)
        response = ""
        response_placeholder = st.empty()

        buffer = ""      # Pour stocker le texte à l'intérieur des balises <think>
        in_think = False # Indique si on est à l'intérieur d'une balise <think>

        for chunk in response_generator:
            response += chunk
            cleaned_response, in_think = remove_think_tags_streaming(response, buffer, in_think)

            response_placeholder.markdown(f"""
            <div style="text-align: left; padding: 10px; margin: 10px 0;">
                <div><b>Stem:</b></div>
                <div style="background-color: #229954; border-radius: 10px; padding: 10px;">
                    {cleaned_response}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.session_state.history[-1]["bot"] = cleaned_response
        st.rerun()
    
    # Affichage de l'historique des conversations
    for chat in reversed(st.session_state.history):
        user_message = f"""
        <div style="text-align: right; padding: 10px; margin: 10px 0;">
            <div><b>Vous:</b></div>
            <div style="background-color: #2471A3; border-radius: 10px; padding: 10px;">
                {chat['user']}
            </div>
        </div>
        """
        bot_message = f"""
        <div style="text-align: left; padding: 10px; margin: 10px 0;">
            <div><b>Stem:</b></div>
            <div style="background-color: #229954; border-radius: 10px; padding: 10px;">
                {chat['bot']}
            </div>
        </div>
        """
        st.markdown(bot_message, unsafe_allow_html=True)
        st.markdown(user_message, unsafe_allow_html=True)

    save_title = st.text_input("Sauvegarder la conversation en tant que :", key="save_title")
    if st.button("Save") and save_title:
        save_conversation(save_title, st.session_state.history)
        st.rerun()
        
    
if __name__ == "__main__":
    main()
