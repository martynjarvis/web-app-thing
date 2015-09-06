import flask_wtf as wtf  # from flask.ext.wtf import Form
from wtforms import fields
from wtforms.validators import InputRequired


class SearchForm(wtf.Form):
    search_term = fields.StringField(
        "Search term",
        validators=[InputRequired()])


class ImportForm(wtf.Form):
    destination = fields.SelectField(u'Destination', coerce=int)
    source = fields.SelectField(
        u'Source',
        coerce=int,
        choices=[
            (60003760, u'Jita IV - Moon 4 - Caldari Navy Assembly Plant'),
            (60008494, u'Amarr VIII (Oris) - Emperor Family Academy'),
        ]
    )
    cost = fields.IntegerField('Cost')


class UpdateForm(wtf.Form):
    task = fields.SelectField(
        u'Task',
        coerce=int,
        choices=[
            (0, u'Update Items'),
            (1, u'Update Map'),
            (2, u'Update Market Prices (Universe Average)'),
        ]
    )


class UpdateMarketForm(wtf.Form):
    region = fields.SelectField(u'Region', coerce=int)
    task = fields.SelectField(
        u'Task',
        coerce=int,
        choices=[
            (0, u'Update Market History'),
            (1, u'Update Market Stats'),
        ]
    )
    items = fields.SelectField(
        u'Items',
        coerce=int,
        choices=[
            (0, u'All'),
            (1, u'Popular Only'),
            (2, u'Favourites Only'),
        ]
    )
