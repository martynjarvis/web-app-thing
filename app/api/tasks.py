import eveapi
import functools

from app import db, celery
from .models import Character, Api

# TODO, check access mask?
# TODO, cache?

def access_mask(access_mask):
    def decorator(method):
        @functools.wraps(method)
        def f(*args, **kwargs):
            this_api = db.session.query(Api).get(args[0])
            if (this_api.accessMask & access_mask) > 1:
                method(*args, **kwargs)
            return
        return f
    return decorator

@celery.task()
def character_sheet(*args):
    return _character_sheet(*args)

@access_mask(8)
def _character_sheet(keyID, vCode, characterID):
    auth = eveapi.EVEAPIConnection().auth(keyID=keyID, vCode=vCode)
    me = auth.character(characterID)
    character = Character.get_by(characterID=characterID)
    character.populate_from_object(me.CharacterSheet())
    db.session.commit()
