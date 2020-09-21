from flask import render_template

from spliit.contact import contact

@contact.route("/contact", methods=['GET', 'POST'])
def contacts():
    return render_template('contact/contact.html')
