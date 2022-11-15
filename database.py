from pymongo import MongoClient
import certifi

MONGO_URI = 'mongodb+srv://si:si@ene.7z0t4vm.mongodb.net/?retryWrites=true&w=majority'
ca = certifi.where()

def dbConnection():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db = client['ene']
    except ConnectionError:
        print('Error connecting to database')
    return db