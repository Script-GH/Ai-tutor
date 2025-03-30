from pymongo import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

def test_connection():
    # MongoDB connection details
    username = "Script_DB"
    password = "Adarsh@2006"
    cluster_url = "cluster0.vriyoyl.mongodb.net"
    
    # Escape username and password
    username_escaped = quote_plus(username)
    password_escaped = quote_plus(password)
    
    # Construct the URI
    uri = f"mongodb+srv://{username_escaped}:{password_escaped}@{cluster_url}/?retryWrites=true&w=majority"
    
    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Create a test document
        db = client['edutech_db']
        result = db.test_collection.insert_one({"test": "Hello MongoDB!"})
        print("✅ Successfully inserted a test document!")
        
        # Read the test document
        doc = db.test_collection.find_one({"_id": result.inserted_id})
        print("✅ Successfully read the test document:", doc)
        
        # Clean up - delete the test document
        db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Successfully cleaned up test data!")
        
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if 'client' in locals():
            client.close()
            print("Connection closed.")

if __name__ == "__main__":
    test_connection() 