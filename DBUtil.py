import pymongo
from datetime import datetime  

def save_chat_history(config, user_id, user_message, bot_response):
    try:
        client = pymongo.MongoClient(config['MONGODB']['URI'])
        db = client[config['MONGODB']['DB_NAME']]
        collection = db['chat_history']

        record = {
            "user_id": user_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.now()  
        }
        collection.insert_one(record)

    except Exception as e:
        print("DB Save Error:", e)

def get_recent_chat_history(config, user_id, limit=3):
    try:
        client = pymongo.MongoClient(config['MONGODB']['URI'])
        db = client[config['MONGODB']['DB_NAME']]
        collection = db['chat_history']

        records = list(collection.find(
            {"user_id": user_id}
        ).sort("timestamp", pymongo.DESCENDING).limit(limit))

        records.reverse()
        return records

    except Exception as e:
        print("DB Query Error:", e)
        return []