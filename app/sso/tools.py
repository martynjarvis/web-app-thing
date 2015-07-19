from contextlib import contextmanager
import time

from flask import session

from pycrest.eve import AuthedConnection

from app import eve

# Keep alive connections and reuse them whenever possible
CON_CACHE = {}


def get_connection(access_token, refresh_token, expires):
    con = CON_CACHE.get(refresh_token, None)
    if con is not None:
        print "Hit connection cache"
        if con.expires - int(time.time()) < 20:
            print "Refreshing token......."
            con.refresh()
        return con
    print "Missed connection cache"

    res = {'access_token': access_token,
           'refresh_token': refresh_token,
           'expires_in': 0}
    con = AuthedConnection(
        res,
        endpoint=eve._authed_endpoint,
        oauth_endpoint=eve._oauth_endpoint,
        client_id=eve.client_id,
        api_key=eve.api_key,
        cache_dir=eve.cache_dir,
        )
    if expires - int(time.time()) < 20:
        print "Refreshing token......."
        con.refresh()
    else:
        con.expires = expires

    CON_CACHE[refresh_token] = con

    return con


def dump_connection(con):
    return (con.token, con.refresh_token, con.expires)


@contextmanager
def auth_connection():
    access_token, refresh_token, expires = session['eve_sso_data']
    con = get_connection(access_token, refresh_token, expires)
    yield con
    if con.token != access_token:
        session['eve_sso_data'] = dump_connection(con=con)
