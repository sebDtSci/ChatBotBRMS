def payload_construction(nom:str,prenom:str,age:int,adresse:str, maisonPrice:int):
    
    payload = {
        "personne": {
            "name": prenom,
            "lastName": nom,
            "address": adresse,
            "disaster": "Incendie",
            "age": age,
            "maisonPrice": maisonPrice
            }
        }

    return payload