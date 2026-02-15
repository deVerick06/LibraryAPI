from flask import Flask
from models import db
from routes.auth_routes  import auth_bp
from routes.authors_routes import authors_bp
from routes.books_routes import books_bp
from routes.categories_routes import categories_bp
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['JWT_SECRET_KEY'] = os.getenv('KEY_JWT')

jwt = JWTManager(app)
db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(authors_bp)
app.register_blueprint(books_bp)
app.register_blueprint(categories_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 