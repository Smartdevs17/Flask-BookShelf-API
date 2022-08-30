import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random
import sys

from models import setup_db, Book

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    def paginate_books(request,books):
        page = request.args.get('page',1,type=int)
        start = (page - 1) * 10
        end = start + 10
            
        result = Book.query.order_by(Book.id).all()
        formatted_books = [book.format() for book in result]
        current_book = formatted_books[start:end]
        return current_book
    
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars
    @app.route('/books',methods=['GET'])
    def get_books():
        page = request.args.get('page',1,type=int)
        start = (page - 1) * 10
        end = start + 10
        
        result = Book.query.all()
        formatted_books = [book.format() for book in result]
        books = formatted_books[start:end]
        return jsonify({
            "success": True,
            "books": books,
            "total_books": len(formatted_books)
        })

    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
    
    @app.route("/books/<int:id>", methods=['PATCH'])
    def update_book(id):
        try:
            book = Book.query.filter(Book.id == id).one_or_none()
            if book is None:
                abort(404)
            else:
                rating = request.get_json().get('rating')
                book.rating = int(rating)
                book.update()
                return jsonify({
                    "success": True,
                    "book_id": book.id,
                })
        except : 
            abort(400)
            print(sys.exc_info())
    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'

    @app.route("/books/<int:id>", methods=['DELETE'])
    def delete_books(id):
        try:
            book = Book.query.filter(Book.id == id).one_or_none()
            if book is None:
                abort(404)
            else:
                book.delete()
                books = Book.query.order_by(Book.id).all()
                current_book = paginate_books(request, books)
                print(current_book)
                
            
            return jsonify({
                "success": True,
                "deleted": id,
                "books": current_book,
                "total_books": len(Book.query.all())
                })
            
        except:
            print(sys.exc_info())
            abort(404)

    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    @app.route("/books",methods=['POST'])
    def add_book():
        body = request.get_json()
        try:
            title = body.get('title')
            author = body.get('author')
            rating = body.get('rating')
            new_book = Book(title= title,author= author,rating= rating)
            new_book.insert()
            # db.session.add(new_book)
            # db.session.commit()
            
            page = request.args.get('page',1,type=int)
            start = (page - 1) * 10
            end = start + 10
            
            result = Book.query.order_by(Book.id).all()
            formatted_books = [book.format() for book in result]
            books = formatted_books[start:end]
            return jsonify({
                "success": True,
                "books": new_book.id,
                "total_books": len(Book.query.all())
            })
        except :
            print(sys.exc_info())
            abort(400)
            
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Resource not found"
            }),404
            
        @app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'success': False,
                'error': 400,
                'message': "please send a valid request"
            }),400
            
        @app.errorhandler(422)
        def unprocessable(error):
            return jsonify({
                'success': False,
                'error': 422,
                'message': "request cannot be processed"
            }),400       
    return app
