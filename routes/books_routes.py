from flask import Blueprint, jsonify, request
from models import db, Book, Author, Category
from flask_jwt_extended import jwt_required

books_bp = Blueprint('books', __name__)

@books_bp.route('/api/books/add', methods=["POST"])
@jwt_required()
def add_book():
    data = request.json

    if 'name' in data and data['name'].strip() and 'price' in data and data['price'] > 0 and 'category_id' in data and 'author_id' in data:
        author_exist = db.session.get(Author, data['author_id'])
        category_exist = db.session.get(Category, data['category_id'])

        if not category_exist or not author_exist:
            return jsonify({'message': 'Error. Category or Author not exist'}), 404

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
    return jsonify({'message': 'Error. Invalid data!'}), 400


@books_bp.route('/api/books', methods=["GET"])
def get_books():
    query = db.select(Book)
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


#Search Route Books
@books_bp.route('/api/books/search', methods=["GET"])
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

@books_bp.route('/api/books/search/price', methods=["GET"])
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
        return jsonify({'message': 'Error. Invalid price value. Please use numbers.'}), 400