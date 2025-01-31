import ollama
import re
import brmsAPI.payload_construction as pc
import brmsAPI.api as ap

def extract_number(s):
    """Extrait le nombre d'une chaîne de caractères."""
    match = re.search(r'\d+', s)
    return int(match.group()) if match else None


def brmsCall(user_input:str)->str:
    #TODO: refactoriser cette fonction avec "maisonPrice" !
    request = (
                "Tu es un expêrt en data capture, ton role est d'extraire uniquement les données requises.\n\n"
                "Extrait les informations au format liste suivant :\n Nom ; Prenom ; Age ; Adresse.\n\n."
                "Si il y a des informations manquantes laisse les zonnes vides.\n\n"
                "Si il y a des données manquantes n'écris rien, laisse vide.\n\n"
                "Ne répond rien d'autre que la liste. Nom ; Prenom ; Age ; Adresse ; prixMaison.\n\n"
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
                "Exemple numéro 11; utilisateur: 'Salut, je voudrais des renseignements sur l'assurance d'Alice Golen, qui a 24 ans et qui vie au 4 rue peroque, à paris 75000, sa maison vaut 20000 euros'\n réponse: Golen ; Alice ; 24 ; 75000 ; 20000\n\n"

                "Exemple numéro 12; Utilisateur : “Nous devons enregistrer les informations pour l’assurance de monsieur Jean Dupont, qui a 43 ans et habite au 12 avenue des Champs, Lyon 69000. Il possède une maison d’une valeur de 300000€.” Réponse : Dupont ; Jean ; 43 ; 69000 ; 300000"
                "Exemple numéro 13; Utilisateur : “Madame Louise Martin souhaite souscrire une assurance. Elle a 52 ans et vit au 78 boulevard Haussmann, Paris 75008.” Réponse : Martin ; Louise ; 52 ; 75008"
                "Exemple numéro 14; Utilisateur : “Je veux une assurance pour ma tante, elle s’appelle Sophie Lemaitre et réside à Bordeaux, 33000.” Réponse : Lemaitre ; Sophie ; ; 33000"
                "Exemple numéro 15; Utilisateur : “Il faut une assurance habitation pour monsieur Paul Lefebvre, qui vit à Nice, 06000, et dont la maison vaut 180000€.” Réponse : Lefebvre ; Paul ; ; 06000 ; 180000"
                "Exemple numéro 16; Utilisateur : “Je cherche une assurance pour Alice Dubois, qui a 37 ans et vit à Marseille, 13001.” Réponse : Dubois ; Alice ; 37 ; 13001"
                "Exemple numéro 17; Utilisateur : “Je veux une assurance pour monsieur Jacques, qui a 50 ans et vit au 10 rue de la Paix, Paris 75000.” Réponse : ; Jacques ; 50 ; 75000 ;"
                "Exemple numéro 18; Utilisateur : 'et pour l'assurance de Arthure Grore , qui à 24 ans' Réponse : Grore ; Arthure ; 24 ; ;  "
                "Example numéro 19; Utilisateur : 'le prix de sa maison est de 100000 et il vit à Paris 75000 + ces éléments ont déjà été mentionné et sont à retenir pour l'assurance : ['Grore', 'Arthure', '24']' reéponse: Grore ; Arthure ; 24 ; 75000 ; 100000"


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
        maisonPrice= extract_number(elements3[4]) if len(elements3) > 4 and elements3[4] else None
    )
    
    api = ap.ApiCall(url="http://localhost:8080/ruleflow", payload=payload, headers={'Content-Type': 'application/json'})
    print('debug API',api)
    test_completion, erreur = api.test_arguments()
    print("3: ------------------------------------------------>>>>>>", test_completion)
    if erreur:
        sentence = "Tu dois indiquer à ton interlocuteur que tu ne peux pas répondre pour la raison suivante : ", test_completion, "Il dois ipérativement te donner toutes les informations dans l'ordre si possible. \n\n Répond uniquement que tu ne peux pas répondre sans ces informations primordiales! Aide toi des raisons données pour expliquer. \n\n Il doit impérativement te redonner toutes les informations ! Nom, Prénom, Age, Adresse "
        solve = False
    else:

        resApi:dict = api.call_api()  # Appel API

        if isinstance(resApi, dict) and 'res' in resApi:
            answer = resApi['res'].get('montantIndemnisation', "Indemnisation inconnue")
        else:
            answer = "Erreur : réponse invalide de l'API"

        sentence = f"D'après les informations que tu as renseignées, le prix de l'assurance calculé par le modèle est : {answer}"
        solve = isinstance(resApi, dict) and 'res' in resApi  # True si la clé 'res' est bien présente

        # resApi:dict = api.call_api()
        # if resApi['res']:
        #     answer = api.call_api()['res']['montantIndemnisation']
        # else: 
        #     answer = api.call_api()
        # sentence = "D'après les informations que tu as renseignée le prix de l'assurance calculer par le model est : ", answer
        # solve = True
    
    print(solve)
    
    return sentence, elements3, solve

def clear_dialog_element(input:str, liste_element:list)->str:
    liste_element.append('assurance')
    clear_input = [element for element in input[0].split() if not element in liste_element]
    
    return " ".join(clear_input)
