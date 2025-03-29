from flask import Flask ,render_template,request, redirect, url_for, flash
from config import Config
from extension import db, migrate

app = Flask(__name__)

app.config.from_object(Config)
# db = SQLAlchemy(app)
db.init_app(app)
migrate.init_app(app, db)

from models import *
from routes import *




if __name__ == '__main__':
    with app.app_context():
        db.create_all
    app.run(debug=True)
