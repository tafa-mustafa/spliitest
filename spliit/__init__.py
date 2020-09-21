from datetime import datetime, timedelta
from authlib.integrations.flask_client import OAuth
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from spliit.config import Config
from flask_dance.contrib.twitter import make_twitter_blueprint

db = SQLAlchemy()
bcrypt = Bcrypt()
loginManager = LoginManager()
loginManager.login_view = 'main.home'
loginManager.login_message_category = 'info'
mail = Mail()
oauth = OAuth()
twitter_blueprint = make_twitter_blueprint(api_key='HkXw4wMJqkMW1ooBlDnONzOCq',
                                           api_secret='ceF37WAVEiMbjooVbiqI4LjsalNY01ANUeEziVG5pXIlfM4lW4')

facebook = oauth.register(
        name='facebook',
        base_url='https://graph.facebook.com/',
        request_token_url=None,
        access_token_url='/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        consumer_key="316037422989105",
        consumer_secret="e813ef662626a2a7469fd9bc5c82d024",
        request_token_params={'scope': 'email'}
    )

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    loginManager.init_app(app)
    oauth.init_app(app)
    # mail.init_app(app)

    # from promeet.user.routes import users
    # from promeet.posts.routes import posts
    from spliit.main.routes import main
    from spliit.contact.routes import contact
    from spliit.errors.handlers import errors
    # app.register_blueprint(users)
    # app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(contact)
    app.register_blueprint(errors)
    app.register_blueprint(twitter_blueprint, url_prefix='/login')

    google = oauth.register(
        name='google',
        client_id="430879469443-lhd5aegbhdaibocce1fvk39oreep64ib.apps.googleusercontent.com",
        client_secret="9wp48JO8s_zWxjT_MMYkdHfr",
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        # This is only needed if using openId to fetch user info
        client_kwargs={'scope': 'openid email profile'},
    )

    # app.secret_key = os.getenv("APP_SECRET_KEY")
    app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
    app.permanent_session_lifetime = timedelta(days=365)

    return app
