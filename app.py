from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

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

#  Auth
@app.route('/api/signup', methods=["POST"])
def signup():
    data = request.json

    if data.get('username') and data.get('email') and data.get('password'):
        queryUsername = db.select(User).where(User.username == data['username'])
        queryEmail = db.select(User).where(User.email == data['email'])
        username_exist = db.session.execute(queryUsername).scalar()
        email_exist = db.session.execute(queryEmail).scalar()

        if username_exist:
            return jsonify({'message': 'Error. Username already exists'}), 400
       
        if email_exist:
            return jsonify({'message': 'Error. Email already exists'}), 400
        
        hashed_password = generate_password_hash(data['password'])
        user = User(username=data['username'], email=data['email'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    return jsonify({'message': 'Invalid data'}), 400

@app.route('/api/login', methods=["POST"])
def login():
    data = request.json
 
    if data.get('email') and data.get('password'):
        query = db.select(User).where(User.email == data['email'])
        user = db.session.execute(query).scalar()
 
        if user and check_password_hash(user.password, data['password']):
            return jsonify({'message': 'Login successful!'}), 200
   
        return jsonify({'message': 'Invalid credentials'}), 401
    return jsonify({'message': 'Email and Password are required'}), 400

#Author
@app.route('/api/authors/add', methods=["POST"])
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

@app.route('/api/authors', methods=["GET"])
def get_authors():
    query = db.select(Author)
    authors = db.session.execute(query).scalars().all()

    authors_list = []

    for author in authors:
        author_content = {
            "id": author.id,
            "name": author.name,
            "qnt_books": len(author.books)
        }
        authors_list.append(author_content)
    return jsonify(authors_list), 200

@app.route('/api/authors/<int:author_id>', methods=["GET"])
def search_author_specific(author_id):
    author = db.session.get(Author, author_id)

    if author:
        books_list = []
        for book in author.books:
            books_list.append({
                "id": book.id,
                "title": book.name
            })
        
        return jsonify({
            "id": author.id,
            "name": author.name,
            "books": books_list
        }), 200
    return jsonify({'message': 'Author not exist'}), 404

@app.route('/api/authors/delete/<int:author_id>', methods=["DELETE"])
def delete_author(author_id):
    author = db.session.get(Author, author_id)

    if author:
        if len(author.books) > 0:
            return jsonify({'message': 'Alert. This Author has books listed'}), 400
        
        db.session.delete(author)
        db.session.commit()
        return jsonify({'message': 'Author deleted successfully'}), 200
    return jsonify({'message': 'Author not exist'}), 404

@app.route('/api/authors/update/<int:author_id>', methods=["PUT"])
def update_author(author_id):
    author = db.session.get(Author, author_id)

    if author:
        data = request.json
        if 'name' in data and data['name'].strip():
            author.name = data['name']
            db.session.commit()
            return jsonify({'message': 'Author updated successfully'}), 200
        else:
            return jsonify({'message': 'Invalid data'}), 400
    return jsonify({'message': 'Author not exist'}), 404


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

@app.route('/api/books', methods=["GET"])
def get_books():
    query = db.select(Book)
    books = db.session.execute(query).scalars().all()
    book_list = []

    for book in books:
        book_content = {
            'name': book.name,
            'price': book.price,
            'author': book.author.name if book.author else "Desconhecido",
            'category': book.category.types if book.category else "Sem Categoria"
        }
        book_list.append(book_content)
    return jsonify(book_list), 200

@app.route('/api/books/search', methods=["GET"])
def search_book():
    search_term = request.args.get('name', '')
    query = db.select(Book).where(Book.name.ilike(f"%{search_term}%"))
    books = db.session.execute(query).scalars().all()

    books_list = []

    for book in books:
        book_content = {
            'name': book.name,
            'price': book.price,
            'author': book.author.name if book.author else "Desconhecido",
            'category': book.category.types if book.category else "Sem Categoria"
        }
        books_list.append(book_content)
    return jsonify(books_list), 200

@app.route('/api/books/search/price', methods=["GET"])
def search_filter_max_price():
    max_price_str = request.args.get('price', '')

    try:
        max_price = float(max_price_str)
        query = db.select(Book).where(Book.price <= max_price)
        books = db.session.execute(query).scalars().all()

        books_list = []

        for book in books:
            book_content = {
            'name': book.name,
            'price': book.price,
            'author': book.author.name if book.author else "Desconhecido",
            'category': book.category.types if book.category else "Sem Categoria"
            }
            books_list.append(book_content)
        return jsonify(books_list), 200
    except ValueError:
        return jsonify({'message': 'Invalid price value. Please use numbers.'})


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

@app.route('/api/categories/delete/<int:category_id>', methods=["DELETE"])
def delete_category(category_id):
    category_exist = db.session.get(Category, category_id)

    if not category_exist:
        return jsonify({'message': 'Category not exist'}), 404
    
    if len(category_exist.books) > 0:
        return jsonify({'message': 'Category has books listed'}), 400
    
    db.session.delete(category_exist)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

