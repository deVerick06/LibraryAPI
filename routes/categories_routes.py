from flask import Blueprint, jsonify, request
from models import db, Category
from flask_jwt_extended import jwt_required

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/api/categories/add', methods=["POST"])
@jwt_required()
def add_category():
    data = request.json

    if 'types' in data and data['types'].strip():
        query = db.select(Category).where(Category.types == data['types'])
        category_exist = db.session.execute(query).scalar()

        if category_exist:
            return jsonify({'message': 'Error. Category already exists'}), 400
       
        category = Category(types=data['types'])
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': 'Category created successfully'}), 201
    return jsonify({'message': 'Invalid data'}), 400

         

@categories_bp.route('/api/categories', methods=["GET"])
def get_categories():
    categories = db.session.execute(db.select(Category)).scalars().all()

    category_list = []

    for category in categories:
        category_content = {
            "id": category.id,
            "name": category.types,
            "qnt_books": len(category.books)
        }
        category_list.append(category_content)
    return jsonify(category_list)


@categories_bp.route('/api/categories/delete/<int:category_id>', methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    category_exist = db.session.get(Category, category_id)

    if not category_exist:
        return jsonify({'message': 'Category not exist'}), 404
   
    if len(category_exist.books) > 0:
        return jsonify({'message': 'This Category has books listed'}), 400
   
    db.session.delete(category_exist)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'}), 200