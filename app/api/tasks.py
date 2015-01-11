import eveapi
import functools

from app import db, celery
from .models import Corporation, Character, Api

# TODO, cache?

def api_requirements(access_mask=None, allowed_types=None):
    def decorator(method):
        @functools.wraps(method)
        def f(**kwargs):
            this_api = db.session.query(Api).get(kwargs['keyID'])
            if (access_mask is None) or ((this_api.accessMask & access_mask) > 1):
                if (allowed_types is None) or (this_api.type in allowed_types):
                    method(**kwargs)
                    return True
            return False
        return f
    return decorator

@celery.task()
def character_sheet(**kwargs):
    return _character_sheet(**kwargs)

@api_requirements(access_mask=8, allowed_types=['Account', 'Character'])
def _character_sheet(keyID, vCode, characterID):
    auth = eveapi.EVEAPIConnection().auth(keyID=keyID, vCode=vCode)
    sheet = auth.character(characterID).CharacterSheet()
    character = Character.get_or_create(characterID=characterID)
    character.populate_from_object(sheet)
    db.session.commit()

@celery.task()
def corporation_sheet(**kwargs):
    return _corporation_sheet(**kwargs)

@api_requirements(access_mask=8, allowed_types=['Corporation'])
def _corporation_sheet(**kwargs):
    if 'keyID' in kwargs:
        auth = eveapi.EVEAPIConnection().auth(keyID=kwargs['keyID'],
                                              vCode=kwargs['vCode'])
        sheet = auth.corp.CorporationSheet()
    elif 'characterID' in kwargs:
        auth = eveapi.EVEAPIConnection()
        sheet = auth.corp.CorporationSheet(characterID=kwargs['characterID'])
    else:
        raise KeyError
    corporation = Corporation.get_or_create(corporationID=sheet.corporationID)
    corporation.populate_from_object(sheet)
    db.session.commit()

@celery.task()
def transactions(**kwargs):
    #TODO corp or character transactions?
    return _transactions(**kwargs)

@api_requirements(access_mask=8, allowed_types=['Corporation'])
def _transactions(**kwargs):
    pass
