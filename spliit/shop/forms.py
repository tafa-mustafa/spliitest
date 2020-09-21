from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddToCardForm(FlaskForm):
    produit = StringField('', validators=[DataRequired()])
    submit = SubmitField('Ajouter au panier')
