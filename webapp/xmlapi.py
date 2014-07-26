from flask import session
import datetime
from sqlalchemy.exc import IntegrityError

from evewallet.webapp import models, db
import evewallet.eveapi as eveapi

API_TYPES = {'Account':1, 'Character':2, 'Corporation':3}
ALLOWED_API_TYPES = [2,3]

def all_keys():
    api_keys = db.session.query(models.Api).all()
    return api_keys
    
def add_api(id,vcode):
    # add api
    api = models.Api(id=id, vcode=vcode)
    auth = eveapi.EVEAPIConnection().auth(keyID=id, vCode=vcode)
    try: 
        APIKeyInfo = auth.account.APIKeyInfo()
    except eveapi.Error, e:
        return None
    
    api.type = API_TYPES[APIKeyInfo.key.type]
    if api.type not in ALLOWED_API_TYPES:
        return None
    api.accessMask = int(APIKeyInfo.key.accessMask)
    try: 
        api.expires = datetime.datetime.fromtimestamp(APIKeyInfo.key.expires)
    except ValueError:
        api.expires = None
    
    # add character
    assert(len(APIKeyInfo.key.characters)==1)
    row = APIKeyInfo.key.characters[0]
      
    character = db.session.query(models.Character).get(row.characterID)
    if character is None:
        character = models.Character(id = row.characterID, name = row.characterName)
    api.character = character
        
    # if corp key, add char
    if APIKeyInfo.key.type == 'Corporation':
        corporation = db.session.query(models.Corporation).get(row.corporationID)
        if corporation is None:
            corporation = models.Corporation(id = row.corporationID, name = row.corporationName)
        api.corporation = corporation
    
    db.session.add(api)
    try: 
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None    
    return api
    
def delete_api(id): 
    api = db.session.query(models.Api).get(id)
    if api is None:                 
        return None
    db.session.delete(api)
    try: 
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    return True
 
def all_corporations():
    corporations = db.session.query(models.Corporation).all()
    return corporations
    
def all_characters():
    characters = db.session.query(models.Character).all()
    return characters    
