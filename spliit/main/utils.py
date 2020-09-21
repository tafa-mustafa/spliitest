import os
import secrets
import string
import random

from PIL import Image
from flask import url_for, current_app
import requests


def save_picture(form_picture):
    response = requests.get(form_picture)

    stri = string.ascii_lowercase
    aleatoire = "U"
    for i in range(0, 15):
        aleatoire += stri[random.randint(0, len(stri)-1)]
    picture_path = current_app.root_path+"/static/img/users/"+aleatoire+".png"
    file = open(picture_path, "wb")
    file.write(response.content)
    file.close()

    '''
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext("sample_image.png")
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/assets/img/users', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    

    file.save(picture_path)
    '''

    return aleatoire+".png"


def save_picture_formForm(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/img/users/', picture_fn)
    '''
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    '''

    form_picture.save(picture_path)

    return picture_fn
