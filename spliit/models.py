from datetime import datetime
from flask import current_app
from sqlalchemy.sql import expression
from spliit import db, loginManager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    # username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), default='default.png')
    password = db.Column(db.String(60), nullable=False)
    commandes = db.relationship('Commande', backref='author', lazy=True)
    # posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"



class Produit(db.Model):
    __tablename__ = 'Produit'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(100), default='default.jpg')
    prix = db.Column(db.DECIMAL, default=0)
    qte_stock = db.Column(db.Integer, default=0)


commander = db.Table('commander',
                     db.Column('commande_id', db.Integer, db.ForeignKey('Commande.id')),
                     db.Column('produit_id', db.Integer, db.ForeignKey('Produit.id'))
                     )


class Commande(db.Model):
    __tablename__ = 'Commande'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    montant = db.Column(db.DECIMAL, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    etat_payement = db.Column(db.Boolean, server_default=expression.false(), default=False, nullable=False)
    etat_validation = db.Column(db.Boolean, server_default=expression.false(), default=False, nullable=False)
    produits = db.relationship("Produit",
                               secondary=commander)




'''
association_table = db.Table('association', db.metadata,
                             db.Column('left_id', db.Integer, db.ForeignKey('left.id')),
                             db.Column('right_id', db.Integer, db.ForeignKey('right.id'))
                             )


class Parent(db):
    __tablename__ = 'left'
    id = db.Column(db.Integer, primary_key=True)
    children = db.relationship("Child",
                               secondary=association_table)


class Child(db):
    __tablename__ = 'right'
    id = db.Column(db.Integer, primary_key=True)'''

'''
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date}')"
'''


@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def load_produit(produit_id):
    return Produit.query.get(int(produit_id))