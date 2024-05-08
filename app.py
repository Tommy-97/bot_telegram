#app.py
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///F:/SQLete/Auto_base.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

