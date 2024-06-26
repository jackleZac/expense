from flask import Flask, request, jsonify
from dotenv import load_dotenv
from bson import ObjectId
import pymongo
import datetime
import os 



app = Flask(__name__)

# Load config from .env file
load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']

def connect_to_db():
    # Set up a connection to MongoDB cluster
    try:
        client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        if client.server_info():
            print('SUCCESS: MongoDB is connected!')
            # Getting a database
            db = client['myfinance']
            # Getting a collection
            collection = db['expense']
            return collection
        else:
            print('ERROR: MongoDB is not connected!')
    except pymongo.errors.ServerSelectionTimeoutError:
        print('ERROR: MongoDB connection timed out!')
    except Exception as e:
        print('ERROR: An unexpected error occurrred: {e}')
    
expense_collection = connect_to_db()

############################################################################################
#####                         ADD FUNCTIONS HERE                                      ######
############################################################################################

@app.route('/expense', methods=['POST'])
def add_expense():
    """It should add an expense to database"""
    # Receive parsed data sent from the front-end (React)
    expense = request.json
    # Parse ISO 8601 formatted date string from the request
    iso_date_string = expense["date"]
    date = datetime.datetime.strptime(iso_date_string, "%Y-%m-%dT%H:%M:%S.%f")
    # Update the format of expense date
    expense["date"] = date
    # Insert an expense into MongoDB Atlas
    expense_collection.insert_one(expense)
    # Return a success message
    return jsonify({"Message": "An expense has been succesfully added"}), 201

@app.route('/expense', methods=['GET'])
def get_expenses():
    """It should return a list of all available expenses"""
    # Get a list of expenses from MongoDB
    list_of_expenses = expense_collection.find({})
    # Convert the ObjectId instances to a JSON serializable format
    expenses = [
        {"_id": str(expense["_id"]), "amount": expense["amount"], "date": expense["date"], 
         "category": expense["category"],"description": expense["description"], "repeatMonthly": expense["repeatMonthly"]} 
        for expense in list_of_expenses
    ]
    # Return a JSON document to the front-end
    return jsonify({'expenses': expenses})

@app.route('/expense/<string:_id>', methods=["PUT"])
def update_expense(_id):
    """It should update an expense"""
    # Get a content of updated expense
    updated_expense = request.json
    # Parse ISO 8601 formatted date string from the request
    iso_date_string = updated_expense["date"]
    date = datetime.datetime.strptime(iso_date_string, "%Y-%m-%dT%H:%M:%S.%f")
    # Update the format of expense date
    updated_expense["date"] = date
    # Log the received ID for debugging
    app.logger.debug(f"Received ID: {_id}")
    # Find and update the expense in MongoDB
    response = expense_collection.find_one_and_update(
        {"_id": ObjectId(_id)},
        {"$set": updated_expense} )
    if response is None:
        # An expense with the specified id is not found
        return jsonify({"message": f'Expense with id: {_id} is not found'}), 404
    else:
        # An expense is found and updated
        return jsonify({"message": f'Expense with id: {_id} is updated'}), 200

@app.route('/expense/<string:_id>', methods=["DELETE"])
def delete_expense(_id):
    """It should delete an expense"""
    # Find and delete an expense from MongoDB
    response = expense_collection.find_one_and_delete({"_id": ObjectId(_id)})
    if response is None:
        # An expense is not found hence causing failure to delete
        return jsonify({"message": f'Failed to delete expense with id: {_id}'}), 404
    else:
        # An expense is found and deleted
        return jsonify({"message": f'Expense with id: {_id} is deleted'}), 200

if __name__ == '__main__':   
    app.run(host='0.0.0.0', port=5000)
    


        

