from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Regexp


class FilterForm(Form):
    filter = StringField("Filter", validators=[Regexp("[a-zA-Z0-9 ._-]+")])
    submit = SubmitField('Filter')
