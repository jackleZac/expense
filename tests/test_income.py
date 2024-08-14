import unittest
import sys
import datetime
import json
import dotenv

# Add parent directory to Python path
sys.path.append('../')
from app import app, add_income, get_incomes, update_income, delete_income, connect_to_db;

class TestIncome(unittest.TestCase):
    """Test cases for handling income"""
    def setUp(self):
        # Create a connection to MongoDB Atlas
        self.client, self.db = connect_to_db()
        # Create a connection to collection 'income'
        self.collection = self.db['income']
        # Initialize test client to simulate requests to Flask App
        self.app = app.test_client()
        
    def tearDown(self):
        # Clean up resources in database
        self.collection.delete_many({})
        
    def test_add_income(self):
        """It should add income to database and assert that it exists"""
        test_income = {
            "source": "Salary",
            "amount": 6000,
            "description": "A monthly salary as Data Analyst",
            "date": datetime.datetime.now().isoformat(),
            "wallet_id": "A1"
        }
        # Make a request to add_income function
        response = self.app.post('/income', json=test_income)
        # Assert that an income has been created
        self.assertEqual(response.status_code, 201)
        # Fetch the income from MongoDB atlas
        income_from_database = self.collection.find_one({"description": test_income["description"]})
        # Assert the income is not null
        self.assertIsNotNone(income_from_database)
        # Assert that the details are accurate
        self.assertEqual(income_from_database["amount"], test_income["amount"])
        self.assertEqual(income_from_database["source"], test_income["source"])
        self.assertEqual(income_from_database["wallet_id"], test_income["wallet_id"])
    
    
    def test_list_income(self):
        """It should get a list of all existing incomes"""
        test_incomes = [{
            "source": "Salary",
            "amount": 6000,
            "description": "A monthly salary as Data Analyst",
            "date": datetime.datetime.now().isoformat(),
            "wallet_id": "A1"
        },
           {
            "source": "Bonus",
            "amount": 1200,
            "description": "A monthly bonus as a Data Analyts",
            "date": datetime.datetime.now().isoformat(),
            "wallet_id": "A1"
        },
           {
            "source": "Second Job",
            "amount": 2000,
            "description": "Part-time Gym Trainer at Eagle GYm, London",
            "date": datetime.datetime.now().isoformat(),
            "wallet_id": "A1"
        }]
        # Insert a list of incomes into MongoDB Atlas
        insert_income = self.collection.insert_many(test_incomes)
        self.assertTrue(insert_income.acknowledged)
        # Make a GET request to get a list of existing incomes
        response = self.app.get('/income')
        # Assert that the incomes have been successfully retrieved
        self.assertEqual(response.status_code, 200)
        # Convert JSON data to Python dict
        response_dict = json.loads(response.data)
        self.assertEqual(len(response_dict["incomes"]), len(test_incomes))
        
    def test_update_income(self):
        """It should update income and assert that it is accurate"""
        test_income = {
            "source": "Salary",
            "amount": 6000,
            "description": "A monthly salary as Data Analyst",
            "date": datetime.datetime.now().isoformat(),
            "wallet_id": "A1"
        }
        # Insert an income into MongoDB Atlas
        insert_income = self.collection.insert_one(test_income)
        self.assertTrue(insert_income.acknowledged)
        if (insert_income):
            # If succeeds, fetch the income from MongoDB Atlas
            inserted_income = self.collection.find_one({"description": test_income["description"]})
            # Assert that the income exists
            self.assertIsNotNone(inserted_income)
            print(inserted_income)
            # Get the income id
            test_income_id = inserted_income["_id"]
            # Make changes to income
            update_income = {
                "source": "Salary",
                "amount": 1000,
                "description": "Earn Side Hustle at Fiverr",
                "date": datetime.datetime.now().isoformat(),
                "wallet_id": "A2" }
            # Make a PUT request to update existing income
            response = self.app.put(f'/income/{test_income_id}', json=update_income, content_type='application/json')
            # Assert that an income has been successfully updated
            self.assertEqual(response.status_code, 200)
            # Fetch the income from MongoDB Atlas
            updated_income = self.collection.find_one({"_id": test_income_id})
            self.assertIsNotNone(updated_income)
            # Assert the income has been accurately updated
            self.assertEqual(updated_income["source"], update_income["source"])
            self.assertEqual(updated_income["amount"], update_income["amount"])
            self.assertEqual(updated_income["wallet_id"], update_income["wallet_id"])
        else:
            # Raise an error if income was not inserted
            self.fail("Failed to insert income into database")
            
    def test_delete_income(self):
        """It should delete an income"""
        test_income = {
            "source": "Salary",
            "amount": 1000,
            "description": "Earn Side Hustle at Fiverr",
            "date": datetime.datetime.now().isoformat(),
            "wallet_id": "A1" } 
        # Insert an income into MongoDB 
        insert_income = self.collection.insert_one(test_income)
        self.assertTrue(insert_income.acknowledged)
        # Retrieve income from database
        inserted_income = self.collection.find_one({"description": test_income["description"]})
        # Assert that the income exists
        self.assertIsNotNone(inserted_income)
        # Assert that the income ID is not None
        self.assertIsNotNone(inserted_income["_id"])
        test_income_id = inserted_income["_id"]
        print(test_income_id)
        # Make a DELETE request to delete income
        response = self.app.delete(f'/income/{test_income_id}')
        # Assert that the income has been successfully updated
        self.assertEqual(response.status_code, 200)
        # Make an attempt to fetch the income again
        deleted_income = self.collection.find_one({"_id": test_income_id})
        # Assert that the income is not found
        self.assertIsNone(deleted_income)    