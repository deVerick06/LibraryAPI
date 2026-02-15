from flask import Blueprint, jsonify, request
from models import db, Author
from flask_jwt_extended import jwt_required

authors_bp = Blueprint('authors', __name__)

@authors_bp.route('/api/authors/add', methods=["POST"])
@jwt_required()
def add_author():
    data = request.json

    if 'name' in data and data['name'].strip():
        query = db.select(Author).where(Author.name == data['name'])
        author_exist = db.session.execute(query).scalar()

        if author_exist:
            return jsonify({'message': 'Author already exists'}), 400

        author = Author(name=data['name'])
        db.session.add(author)
        db.session.commit()
        return jsonify({'message': 'Author added successfully'}), 201
    return jsonify({'message': 'Error. Invalid data!'}), 400


@authors_bp.route('/api/authors', methods=["GET"])
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


@authors_bp.route('/api/authors/<int:author_id>', methods=["GET"])
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
    return jsonify({'message': 'Author not exist.'}), 404

@authors_bp.route('/api/authors/delete/<int:author_id>', methods=["DELETE"])
@jwt_required()
def delete_author(author_id):
    author = db.session.get(Author, author_id)

    if author:
        if len(author.books) > 0:
            return jsonify({'message': 'Alert. This Author has books listed.'}), 400
        
        db.session.delete(author)
        db.session.commit()
        return jsonify({'message': 'Author deleted successfully'}), 200
    return jsonify({'message': 'Author not exist'}), 404


@authors_bp.route('/api/authors/update/<int:author_id>', methods=["PUT"])
@jwt_required()
def update_author(author_id):
    author = db.session.get(Author, author_id)

    if author:
        data = request.json

        if 'name' in data and data['name'].strip():
            author.name = data['name']
            db.session.commit()
            return jsonify({'message': 'Author updated successfully'}), 200
        else:
            return jsonify({'message': 'Invalid name'}), 400
    return jsonify({'message': 'Author not exist'}), 404