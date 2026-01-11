import os
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database

_client : Optional[MongoClient] = None
_db: Optional[Database] = None

def init_db() -> None:
    global _client, _db

    if _client is not None:
        return # already initialized previously

    _client = MongoClient(os.environ['MONGODB_URL'])
    _db = _client['appdb']

    try:
        if 'documents' not in _db.list_collection_names():
            _db.create_collection('documents')
            print('collection "documents" created inside mongo database')
        else:
            print('using existing collection "documents"')
    except Exception as e:
        raise RuntimeError(f'encountering error when creating database: {str(e)}')

def get_db() -> Database:
    if _db is None:
        raise RuntimeError('database failed to initialize')
    return _db
