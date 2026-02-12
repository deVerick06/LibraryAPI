from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'

db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    types = db.Column(db.String(20), unique=True, nullable=False)
    books = db.relationship('Book', backref='category')

    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    books = db.relationship('Book', backref='author')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    resume = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

@app.route('/')
def initial():
    return 'Welcome to LibraryAPI'

#Author
@app.route('/api/author/add', methods=["POST"])
def add_author():
    data = request.json

    if 'name' in data and data['name'].strip():
        query = db.select(Author).where(Author.name == data['name'])
        author_exist = db.session.execute(query).scalar()

        if author_exist:
            return jsonify({'message': 'Author already exists.'}), 400
        
        new_author = Author(name=data['name'])
        db.session.add(new_author)
        db.session.commit()
        return jsonify({'message': 'Author added successfully'}), 201
    return jsonify({'message': 'Invalid data author'}), 400


#Route Books
@app.route('/api/books/add', methods=["POST"])
def add_book():
    data = request.json

    if 'name' in data and data['name'].strip() and 'price' in data and data['price'] > 0 and 'category_id' in data and 'author_id' in data:
        category_exist = db.session.get(Category, data['category_id'])
        autthor_exist = db.session.get(Author, data['author_id'])

        if not category_exist or not autthor_exist:
            return jsonify({'message': 'Error. Category or Author not exist.'}), 404
        
        book = Book(
            name=data['name'],
            price=data['price'],
            resume=data.get('resume', ''),
            category_id=data['category_id'],
            author_id=data['author_id']
        )
        db.session.add(book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully'}), 201
    return jsonify({'meesage': 'Invalid data'}), 400


#Categories
@app.route('/api/categories/add', methods=["POST"])
def add_category():
    data = request.json

    if 'types' in data and data['types'].strip():
        query = db.select(Category).where(Category.types == data['types'])
        category_exist = db.session.execute(query).scalar()

        if category_exist:
            return jsonify({'message': 'Category already exists'}), 400
        
        category = Category(types=data['types'])
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': 'Category added successfully'}), 201
    return jsonify({'message': 'Invalid data'}), 400

@app.route('/api/categories', methods=["GET"])
def get_categories():
    categories = db.session.execute(db.select(Category)).scalars().all()

    categories_list = []
    for category in categories:
        content_category = {
            "id": category.id,
            "name": category.types,
            "qnt_books": len(category.books)
        }
        categories_list.append(content_category)
    return jsonify(categories_list)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

