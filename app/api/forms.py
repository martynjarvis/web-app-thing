import flask_wtf as wtf  # from flask.ext.wtf import Form
from wtforms import fields
from wtforms.validators import InputRequired, ValidationError
import eveapi

from .models import Api


class ApiForm(wtf.Form):
    keyID = fields.IntegerField("API ID", validators=[InputRequired()])
    vCode = fields.StringField("VCode", validators=[InputRequired()])

    def validate_keyID(self, field):
        api = Api.query.filter(Api.keyID == field.data).first()
        if api is not None:
            raise ValidationError("That API key already exists")

    def validate_vCode(self, field):
        auth = eveapi.EVEAPIConnection().auth(keyID=self.keyID.data,
                                              vCode=self.vCode.data)
        try:
            APIKeyInfo = auth.account.APIKeyInfo()
        except eveapi.Error:
            raise ValidationError("Invalid API.")  # TODO better reasons

        # keep api information on form object
        self.key = APIKeyInfo.key
