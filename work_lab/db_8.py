from pymongo import MongoClient

def connect_mongo():

    try:
        uri = 'mongodb+srv://jindalfactors_db_user:dY7W2xLyw8Za69ul@cluster0.emceph8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

        client = MongoClient(uri)

        db = client["Cluster0"]

        registration_collection = db["registartions"]
        print("MongoDB connected successfully!!")

        registration_collection.insert_many([
            {"name": "Rohan", "rollNum": "24BCS000", "email": "rohan@gmail.com"},
            {"name": "Travis", "rollNum": "24BCF020", "email": "travis@gmail.com"},
            {"name": "John", "rollNum": "24DCF020", "email": "john@gmail.com"}
        ])

        print("Data sent to the mongoDB successfully")

        print("Data Fetched from the db: ")
        for regs in registration_collection.find():
            print(regs)

    except Exception as e:
        print("Error in the db: ", e)

    finally:
        client.close()
        print("Connection to the database stopped!")

if __name__ == "__main__":
    connect_mongo()