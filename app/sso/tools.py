import time

from flask import session

from pycrest.eve import AuthedConnection

from app import eve

def get_connection():
    # There is a bug here involving hitting refresh which sends the old stale
    # auth I think...
    con = load_connection(*session['eve_sso_data'])

    if con.token != session['eve_sso_data'][0]:
        # maybe check that this worked?
        session['eve_sso_data'] = dump_connection(con=con)

    return con

def load_connection(access_token, refresh_token, expires):
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
        con.refresh()
    else:
        con.expires = expires
    return con

def dump_connection(con=None):
    if con is None:
        con = get_connection()
    return (con.token, con.refresh_token, con.expires)

