import pymongo

def save_chat_history(config, user_id, user_msg, bot_reply):
    try:
        client = pymongo.MongoClient(config['MONGODB']['URI'])
        db = client[config['MONGODB']['DB_NAME']]
        coll = db['chat_history']

        coll.insert_one({
            "user_id": user_id,
            "user_message": user_msg,
            "bot_response": bot_reply
        })

        client.close()
    except Exception as e:
        print("DB Error:", e)