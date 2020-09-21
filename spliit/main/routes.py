from flask import render_template, request, flash, redirect, url_for, session
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.twitter import twitter
from flask_login import login_user, logout_user, current_user, login_required
import requests
import hashlib
from sqlalchemy.orm.exc import NoResultFound
from spliit import bcrypt, oauth, db, twitter_blueprint, facebook
from spliit.main import main
from spliit.main.utils import save_picture, save_picture_formForm
from spliit.models import User, Produit, load_produit
from spliit.shop.forms import AddToCardForm
from spliit.users.forms import LoginForm, RegistrationForm, UpdateAccountForm


@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    produits = Produit.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    print(url_for('main.facebook_login') + " " + url_for('main.googleAuth') + " " + url_for('main.twitter_login'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('index.html', form=form, produits=produits)


@main.route("/inscription", methods=['GET', 'POST'])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    if request.form:
        prenom = request.form["prenom"]
        nom = request.form["nom"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(nom=nom, prenom=prenom, email=email,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        next_page = request.args.get('next')
        flash('You have been logged in!', 'success')
        return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
    return render_template('inscription.html', form=form)


@main.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    formCard = AddToCardForm()
    produits = Produit.query.all()
    # session.clear()
    prixTotal = 0
    nbArticles = 0
    if 'prixTotal' in session and 'nbArticles' in session:
        prixTotal = session.get('prixTotal')
        nbArticles = session.get('nbArticles')
    else:
        session['prixTotal'] = 0
        session['nbArticles'] = 0

    if formCard.validate_on_submit():
        produit = Produit.query.filter_by(id=formCard.produit.data).first()
        if produit:
            cart_item = {'id': str(produit.id) + "", 'titre': produit.titre + "", 'prix': str(produit.prix) + "",
                         'qte': str(1) + ""}
            if 'items' in session:
                pos = -1
                items = list(session.get('items'))
                for i in range(len(items)):
                    if items[i]['id'] == cart_item['id']:
                        pos = i
                if pos != -1:
                    print("TROUVE AT " + str(pos))
                    print(items[pos]['qte'])
                    items[pos]['qte'] = str(int(items[pos]['qte']) + 1)
                    print(items[pos]['qte'])
                    session['items'] = items
                else:
                    '''
                    list(session.get('items')).append(0)
                    session['items'][len(list(session.get('items'))) - 1] = cart_item'''
                    items.append(cart_item)
                    session['items'] = items
                    session['nbArticles'] = str(int(session.get('nbArticles')) + 1)
            else:
                session['items'] = [cart_item]
                session['nbArticles'] = str(int(session.get('nbArticles')) + 1)
            session['prixTotal'] = str(int(session.get('prixTotal')) + produit.prix)
            prixTotal = session.get('prixTotal')
            nbArticles = session.get('nbArticles')
            print("OK")
        else:
            print("NON OK")
    return render_template('dashboard.html', produits=produits, formCard=formCard, prixTotal=prixTotal,
                           nbArticles=nbArticles, user=current_user)


@main.route("/logout", )
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@main.route("/clearsession")
@login_required
def clearsession():
    session.clear()
    return redirect(url_for('main.home'))


@main.route("/card")
@login_required
def card():
    prixTotal = 0
    nbArticles = 0
    items = []
    if 'prixTotal' in session and 'nbArticles' in session and 'items' in session:
        prixTotal = session.get('prixTotal')
        nbArticles = session.get('nbArticles')
        items = session.get('items')
    else:
        session['prixTotal'] = 0
        session['nbArticles'] = 0
    return render_template('card.html', prixTotal=prixTotal, nbArticles=nbArticles, items=items,
                           load_produit=load_produit, user=current_user)


@main.route("/payer")
def payer():
    prixTotal = 0
    nbArticles = 0
    message = ""
    if 'prixTotal' in session and 'nbArticles' in session and 'items' in session:
        prixTotal = session.get('prixTotal')
        nbArticles = session.get('nbArticles')
        items = session.get('items')
        message = "IL EXISTE DES ELEMENTS"
        m = hashlib.sha256()
        test = {'id': 'test-order-1', 'amount': '3', 'currency': 'USD', 'secretKey': 'ec69f0443bfca8b7394eed3a'}
        '''m.update(str(
            "|'amount' => '3'|'currency' => 'USD'|'id' => 'test-order-1'|'secretKey' => 'ec69f0443bfca8b7394eed3a'|").encode(
            'utf-8'))'''
        m.update(str(
            "||3|USD|test-order-1|ec69f0443bfca8b7394eed3a|").encode(
            'utf-8'))
        jsonInvoice = {
            "publicKey": "application-e5b8004f-54ad-4db8-8c0c-f64dc64eef5b",
            "order": {
                "id": "test-order-1",
                "amount": "3",
                "currency": "USD",
                "items": [
                    {
                        "id": "487",
                        "name": "Item 1",
                        "price": "0.8999999999999999"
                    },
                    {
                        "id": "358",
                        "name": "Item 2",
                        "price": "2.0999999999999996"
                    }
                ],
                "description": ""
            },
            "signature": m.hexdigest(),
            # "signature": "3445000c1f55f447b853fe068529c23fc4188e36aa4984e37836538d95f8e015",
            "payer": {
                "email": "vich22032203@gmail.com",
                "phone": "00221774988948",
                "name": "Tito VICH",
                "extraFields": {
                    "nationalid": "5579844567",
                    "name": "Human"
                }
            },
            "paymentMethod": 261,
            "language": "en",
            "resultUrl": url_for('main.payement_result', token=int(0)),
            "failPath": url_for('main.payement_result', token=int(0))
        }
        res = requests.post('https://payop.com/v1/invoices/create', json=jsonInvoice)
        if res.ok:
            print(res.json())
            message = res.json()
        print(res.json())
        message = "https://payop.com/v1/invoices/create return " + str(res.json())
    else:
        return redirect(url_for('main.card'))
    return render_template('payement.html', prixTotal=prixTotal, nbArticles=nbArticles, message=message,
                           user=current_user)


@main.route("/increase/<int:id>", methods=['GET', 'POST'])
def increase(id):
    if 'prixTotal' in session and 'nbArticles' in session and 'items' in session and id:
        gerer_quantite(id, 1)
        return redirect(url_for('main.card'))
    else:
        return redirect(url_for('main.dashboard'))


@main.route("/decrease/<int:id>", methods=['GET', 'POST'])
def decrease(id):
    if 'prixTotal' in session and 'nbArticles' in session and 'items' in session and id:
        gerer_quantite(id, -1)
        return redirect(url_for('main.card'))
    else:
        return redirect(url_for('main.dashboard'))


def gerer_quantite(id, sens):
    prixTotal = session.get('prixTotal')
    nbArticles = session.get('nbArticles')
    items = session.get('items')
    produit = Produit.query.filter_by(id=id).first()
    if 'items' in session and produit:
        pos = -1
        items = list(session.get('items'))
        print(items)
        print(produit.id)
        for i in range(len(items)):
            if items[i]['id'] == str(produit.id):
                pos = i
        if pos != -1:
            print("TROUVE AT $pos")
            if sens == -1:
                items[pos]['qte'] = str(int(items[pos]['qte']) - 1)
                session['prixTotal'] = str(int(session.get('prixTotal')) - produit.prix)
                if int(items[pos]['qte']) == 0:
                    items.pop(pos)
                    session['nbArticles'] = str(int(session.get('nbArticles')) - 1)
            else:
                items[pos]['qte'] = str(int(items[pos]['qte']) + 1)
                session['prixTotal'] = str(int(session.get('prixTotal')) + produit.prix)
            session['items'] = items


@main.route("/payement_result/<int:token>")
def payement_result(result):
    prixTotal = 0
    nbArticles = 0
    if 'prixTotal' in session and 'nbArticles' in session and 'items' in session:
        prixTotal = session.get('prixTotal')
        nbArticles = session.get('nbArticles')
    message = result
    # post = Post.query.get_or_404(post_id)
    return render_template('payement.html', prixTotal=prixTotal, nbArticles=nbArticles, message=message)


def login_get_user(user):
    u = User.query.filter_by(email=user.email).first()
    if u:
        login_user(u)
    else:
        db.session.add(user)
        db.session.commit()
        login_user(user)


@main.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    # user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    hashed_password = bcrypt.generate_password_hash(user_info['id']).decode('utf-8')
    user = User(nom=user_info['family_name'], prenom=user_info['given_name'], email=user_info['email'],
                password=hashed_password, image_file=save_picture(user_info['picture']))
    login_get_user(user)
    next_page = request.args.get('next')
    flash('You have been logged in!', 'success')
    return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
    '''session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')'''


@main.route('/googleAuth')
def googleAuth():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('main.authorize', _external=True)
    print(url_for('main.authorize', _external=True))
    return google.authorize_redirect(redirect_uri)


@main.route("/login/twitter/authorized", methods=['GET', 'POST'])
def twitter_login():
    if not twitter.authorized:
        # return str(twitter.authorized(callback=url_for('main.twitter_login')))
        return redirect(url_for("twitter.login"))
        # print(twitter)
    else:
        account_info = twitter.get('account/settings.json')
        account_info_json = account_info.json()
        return account_info_json
    '''
    if request.args:
        
        account_info = twitter.get('account/settings.json')
        account_info_json = account_info.json()
        return account_info_json
        # return request.args['oauth_token']
    else:'''
    # return redirect(url_for('main.dashboard'))
    '''
    account_info = twitter.get('account/settings.json')
    account_info_json = account_info.json()'''
    # assert resp.ok
    # return redirect(url_for('main.dashboard'))
    return "NON OK"


@main.route('/login/facebook')
def facebook_login():
    return render_template('message.html', message="API FACEBOOK TEMPORAIREMENT INACESSIBLE !!", user=current_user)
    '''return facebook.authorize(callback=url_for('main.facebook_authorized',
                                               next=request.args.get('next') or request.referrer or None,
                                               _external=True))'''


'''
@main.route('/login/facebook/authorized')
# @facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
           (me.data['id'], me.data['name'], request.args.get('next'))


# @facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')'''

'''
@main.route('/twitter')
def twitter_login():
    print("EUH")
    if not twitter.authorized:
        print("NON ATHORIZE")
        return redirect(url_for('twitter.login'))
    else:
        print("ATHORIZE")
    account_info = twitter.get('account/settings.json')
    account_info_json = account_info.json()

    return '<h1>Your Twitter name is @{}'.format(account_info_json['screen_name'])


@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    account_info = blueprint.session.get('account/settings.json')

    if account_info.ok:
        account_info_json = account_info.json()
        username = account_info_json['screen_name']

    return "OK"
    query = User.query.filter_by(username=username)

    try:
        user = query.one()
    except NoResultFound:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()

    login_user(user)
'''


@main.route("/security")
def security():
    return render_template('security/security.html')


@main.route("/privacy-policies")
def confidentialite():
    return render_template('confidentialite/confidentialite.html')


@main.route("/legals")
def legals():
    return render_template('legals/legal.html')


@main.route("/contrat-lemonway")
def contrat():
    return render_template('cgu/contrat-lemonway.html')


@main.route("/cgu")
def cgu():
    return render_template('cgu/cgu.html')


@main.route("/blog")
def blog():
    return render_template('blog/blog.html')


@main.route("/infos", methods=['GET', 'POST'])
def infos():
    form = UpdateAccountForm()
    '''print("TEST")
    if request.form:
        print(request.form)'''
    if form.validate_on_submit():
        print("OK")
        current_user.nom = form.nom.data
        current_user.prenom = form.prenom.data
        if form.picture.data:
            picture_file = save_picture_formForm(form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        return redirect(url_for('main.infos'))
    return render_template('infos.html', message="yeAh", form=form, user=current_user)
