from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from flask.ext.wtf import Form
from wtforms import fields
from wtforms.validators import Email, InputRequired, ValidationError
import eveapi

from .models import Api

class ApiForm(Form):
    id = fields.IntegerField("API ID", validators=[InputRequired()])
    vcode = fields.StringField("VCode", validators=[InputRequired()])

    def validate_id(form, field):
        api = Api.query.filter(Api.id == field.data).first()
        if api is not None:
            raise ValidationError("That API key already exists")

    def validate_vcode(form, field):
        auth = eveapi.EVEAPIConnection().auth(keyID=form.id.data,
                                              vCode=form.vcode.data)
        try:
            APIKeyInfo = auth.account.APIKeyInfo()
        except eveapi.Error, e:
            raise ValidationError("Invalid API.") # TODO better reasons

        # keep api information on form object
        form.auth = APIKeyInfo
