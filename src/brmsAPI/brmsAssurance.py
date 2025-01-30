import ollama
import re
import src.brmsAPI.payload_construction as pc
import src.brmsAPI.api as ap

def brmsCall(user_input:str)->str:
    #TODO: refactoriser cette fonction avec "maisonPrice" !
    request = (
                "Tu es un expêrt en data capture, ton role est d'extraire uniquement les données requises.\n\n"
                "Extrait les informations au format liste suivant :\n Nom ; Prenom ; Age ; Adresse.\n\n."
                "Si il y a des informations manquantes laisse les zonnes vides.\n\n"
                "Si il y a des données manquantes n'écris rien, laisse vide.\n\n"
                "Ne répond rien d'autre que la liste. Nom ; Prenom ; Age ; Adresse .\n\n"
                "Voici quelques exemples pour te montrer: \n\n"
                "Exemple numéro 1; utilisateur:'Je veux une information sur une assurance, il s'agit de madame Durant Jenny' reponse: Durant ; Jenny.\n\n"
                "Exemple numéro 2; utilisateur:'Nous voulons les données d'assurance de monsieur Alexandre Gigof agé de 56 ans et résident au 6 rue labradore, Paris 75000' reponse: Gigof ; Alexandre ; 56 ; 75000 .\n\n"
                "Exemple numéro 3; utilisateur:'' reponse: .\n\n"
                "Exemple numéro 4; utilisateur:'j'aurais une question sur l assurance' reponse: .\n\n"
                "Exemple numéro 5; utilisateur:'Pardon, elle a 65 ans et vie au 34 rue du chaine, Paris 75000 + ces éléments ont déjà été mentionné et sont à retenir pour l'assurance : ['Desmons', 'Clara']' reponse: Desmons ; Clara ; 65 ; 75000  .\n\n"
                "Exemple numéro 6; utilisateur:'Elle s'appelle Corrine Petit + ces éléments ont déjà été mentionné et sont à retenir pour l'assurance : ['87', '34000']' reponse: Petit ; Corrine ; 87 ; 34000  .\n\n"
                "Exemple numéro 7; utilisateur: 'Nous voulons les données d'assurance de monsieur Alexandre Gigof agé de 56 ans, résident au 6 rue Labradore, Paris 75000, et dont la maison vaut 200000€' réponse: Gigof ; Alexandre ; 56 ; 75000 ; 200000\n\n"
                "Exemple numéro 8; utilisateur: 'Elle s'appelle Corrine Petit et sa maison vaut 250000€' réponse: Petit ; Corrine ; ; ; 250000\n\n"
                "Exemple numéro 9; utilisateur: '' réponse: \n\n"
                "Exemple numéro 10; utilisateur: 'j'aurais une question sur l'assurance'\n réponse: \n\n"

                "Voici la phrase cible: " f"{user_input}"
                )
            
    elements = ollama.generate(
        model="mistral:latest",
        prompt=request,
        stream=False,
        options= {'temperature': 1}
    )
    print("1 : ------------------------------------------------>>>>>>------------------------------------------------>>>>>>------------------------------------------------>>>>>>",elements["response"])
    
    elements2 = re.sub(r'[^a-zA-Z0-9;]', '', elements["response"])
    elements3 = [elem.strip() for elem in elements2.split(';') if elem.strip()]
    print("2: ------------------------------------------------>>>>>>------------------------------------------------>>>>>>",elements3)
    # payload = pc.payload_construction(nom=elements3[0], prenom=elements3[1], age=elements3[2], adresse=elements3[3])
    payload = pc.payload_construction(
        nom=elements3[0] if len(elements3) > 0 and elements3[0] else None,
        prenom=elements3[1] if len(elements3) > 1 and elements3[1] else None,
        age=elements3[2] if len(elements3) > 2 and elements3[2] else None,
        adresse=elements3[3] if len(elements3) > 3 and elements3[3] else None,
        maisonPrice=elements3[4] if len(elements3) > 4 and elements3[4] else None
    )
    
    api = ap.ApiCall(url="http://10.21.8.3:9090/DecisionService/rest/v1/assurance_deploy/OD_assurance/", payload=payload, headers={'Content-Type': 'application/json'})
    test_completion, erreur = api.test_arguments()
    print("3: ------------------------------------------------>>>>>>", test_completion)
    if erreur:
        sentence = "Tu dois indiquer à ton interlocuteur que tu ne peux pas répondre pour la raison suivante : ", test_completion, "Il dois ipérativement te donner toutes les informations dans l'ordre si possible. \n\n Répond uniquement que tu ne peux pas répondre sans ces informations primordiales! Aide toi des raisons données pour expliquer. \n\n Il doit impérativement te redonner toutes les informations ! Nom, Prénom, Age, Adresse "
        solve = False
    else:
        sentence = "D'après les informations que tu as renseignée le prix de l'assurance calculer par le model est : ", api.call_api()
        solve = True
    
    print(solve)
    
    return sentence, elements3, solve

def clear_dialog_element(input:str, liste_element:list)->str:
    liste_element.append('assurance')
    clear_input = [element for element in input[0].split() if not element in liste_element]
    
    return " ".join(clear_input)