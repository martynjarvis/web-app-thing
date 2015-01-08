from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from flask.ext.wtf import Form
from wtforms import fields
from wtforms.validators import Email, InputRequired, ValidationError
import eveapi

#from .models import Api, Character, Corporation

class ApiForm(Form):
    id = fields.IntegerField("API ID", validators=[InputRequired()])
    vcode = fields.StringField("VCode", validators=[InputRequired()])

    def validate_api(form, field):
        auth = eveapi.EVEAPIConnection().auth(keyID=id, vCode=vcode)
        try:
            APIKeyInfo = auth.account.APIKeyInfo()
        except eveapi.Error, e:
            raise ValidationError("Invalid API key")

        # keep api information on form object
        form.auth = APIKeyInfo
