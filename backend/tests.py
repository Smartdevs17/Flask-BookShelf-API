#Import all dependencies
import unittest
import json
from flaskr import create_app
from models import setup_db,Book

class BooksTestCase(unittest.TestCase):
    def setUp(self):
        # Define test variables and initialize app.
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "booktestDB"
        # self.database_name = "bookDB"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','testpassword','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_book = {
            "author": "smartdev",
            "title": "day in the life of mathematician",
            "rating": 9
        }
        
    def tearDown(self):
        """Executed after each test"""
        pass
    
    def get_all_books_behavior(self):
        """Test _____________ """
        res = self.client().get('/books')
        self.assertEqual(res.status_code, 200)
        
    def test_get_paginated_books(self):
        res = self.client().get("/books")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"],True)
        self.assertEqual(data['total_books'],5)
        self.assertEqual(len(data['books']),5)
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/books/1000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')
        
    def test_get_book_search_with_result(self):
        res = self.client().post('/books', json={'search': "book two"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_books'])
        self.assertEqual(len(data['books']), 1)
    
    def test_get_book_search_without_results(self):
        res = self.client().post('/books',json={'search': 'applejacks'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_books'], 0)
        self.assertEqual(len(data['books']), 0)
        
    def test_update_book_rating(self):
        res = self.client().patch("/books/3",json={"rating": 6})
        data = json.loads(res.data)
        book = Book.query.filter(Book.id == 3).one_or_none()
            
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(book.format()['rating'], 6)
            
    def test_400_for_failed_update(self):
        res = self.client().patch("/books/2")
        data = json.loads(res.data)
            
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'please send a valid request')
            
    # def test_delete_book(self):
    #     res = self.client().delete("/books/2")
    #     data = json.loads(res.data)
          
    #     book = Book.query.filter(Book.id == 2).one_or_none()
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['deleted'], 2)
    #     self.assertTrue(data['total_books'])
    #     self.assertEqual(book, None)
        
    def test_create_new_book(self):
        res = self.client().post("/books",json=self.new_book)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200) 
        self.assertEqual(data['success'], True) 
        self.assertTrue(data['created'])
        self.assertTrue(len(data['books']))
        
    # def test_405_if_book_creation_not_allowed(self):
    #     res = self.client().post("/books/5")
    #     data = json.loads(res.data)
        
    #     self.assertEqual(res.status_code, 405)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'method not allowed')
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()       