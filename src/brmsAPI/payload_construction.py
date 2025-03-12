def payload_construction(nom:str, prenom:str, age:int, adresse:str, maisonPrice:int, sinistre:str = "Incendie"):
    
    payload = {
        "personne": {
            "name": prenom,
            "lastName": nom,
            "address": adresse,
            "disaster": sinistre,
            "age": age,
            "maisonPrice": maisonPrice
            }
        }

    return payload