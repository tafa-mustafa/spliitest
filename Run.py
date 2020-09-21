from spliit import db, create_app
from spliit import models

app = create_app()

'''
db.drop_all(app=create_app())
db.create_all(app=create_app())'''
if __name__ == '__main__':
    # app.run(host="0.0.0.0", debug=True)
    app.run(debug=True)


