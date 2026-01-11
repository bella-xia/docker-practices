import os
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from typing import Optional, List
from bson import ObjectId
from pymongo import ReturnDocument
from datetime import datetime

from ..db.schemas import (QuerySchema, ResponseSchema, 
                    ViewableDocumentSchema, CustomDocumentSchema,
                    StatsSchema)
from ..db.mongo import get_db
# from ..core.search import find_top_k
from ..core.executor import embed_worker, execute_embed
from ..core.indexer import indexer

router : APIRouter = APIRouter()

EMBED_MAX_BACKGROUND = 4
EMBED_MAX_QUERY = 2
_background_sema = asyncio.Semaphore(EMBED_MAX_BACKGROUND)
_query_sema = asyncio.Semaphore(EMBED_MAX_QUERY)

def _get_docs():
    db = get_db()
    docs = db.get_collection('documents')
    return docs

def init_index():
    docs = _get_docs()
    docs.create_index('status')
    docs.update_many(
        {"status": "processing"},
        {"$set": {"status": "error", "metadata.msg": "worker restart"}}
    ) # make any unqueued processing into error
    doc_arr = list(docs.find({'status': 'ready'}))
    for doc in doc_arr:
        indexer.add(doc['_id'], doc['embed'])

async def _compute_and_update_embed(doc_id: ObjectId, text: str):
    global _background_sema
    try:
        async with _background_sema:
            embed = await asyncio.get_running_loop().run_in_executor(
                    embed_worker, execute_embed, text)
        docs = _get_docs()
        docs.update_one({'_id': doc_id}, 
                        {'$set': {'embed': embed, 'status': 'ready',
                                  'modified_at': datetime.utcnow()}})
        indexer.add(doc_id, embed)
    except Exception as e:
        print(f'failed to compute embedding for doc {doc_id}: {e}')
        docs.update_one({'_id': doc_id}, 
                        {'$set': {'status': 'error', 
                                  'metadata': {'msg': str(e)},
                                  'modified_at': datetime.utcnow()}})

@router.post("/query/", response_model=List[ResponseSchema])
async def query_doc(payload: QuerySchema):
    global _query_sema
    async with _query_sema:
        embed = await asyncio.get_running_loop().run_in_executor(
                embed_worker, execute_embed, payload.text)
    res = indexer.search(embed, payload.top_k)
    if not res:
        return []
    docs = _get_docs()
    topk_docs = docs.find(
        {"_id": {"$in": list(res.keys())}},
        {'embed': 0})
    doc_map = {doc['_id']: doc for doc in topk_docs}
    return [{'score': score, **doc_map[oid]} for oid, score in res.items() if oid in doc_map]

@router.post("/upload/", response_model=ViewableDocumentSchema)
async def upload_doc(payload: CustomDocumentSchema):
    new_doc = payload.model_dump(by_alias=True)
    new_doc['embed'] = None
    new_doc['status'] = 'processing'
    new_doc['created_at'] = datetime.utcnow()
    new_doc['modified_at'] = datetime.utcnow()
    docs = _get_docs() 
    res = docs.insert_one(new_doc)
    new_doc['_id'] = res.inserted_id
    loop = asyncio.get_running_loop()
    loop.create_task(_compute_and_update_embed(new_doc['_id'], payload.text))
    return new_doc

@router.get('/documents/', response_model=List[ViewableDocumentSchema])
def read_docs(bound: int = 10):
    docs = _get_docs()
    return docs.find({}).to_list(bound)

@router.get('/document/{doc_id}', response_model=ViewableDocumentSchema)
def read_doc(doc_id: str):
    docs = _get_docs()
    doc = docs.find_one({'_id': ObjectId(doc_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail=f'Invalid read: document #{doc_id} not found')
    return doc

@router.put('/document/{doc_id}', response_model=ViewableDocumentSchema)
async def update_doc(doc_id: str, payload: CustomDocumentSchema):
    updates = payload.model_dump(by_alias=True, exclude_unset=True)
    updates['modified_at'] = datetime.utcnow()
    if not updates:
        raise HTTPException(status_code=400, default='Invalid update: no updatable fields')
    if 'text' in updates:
        updates['embed'] = None
        updates['status'] = 'processing'
                
        loop = asyncio.get_running_loop()
        loop.create_task(_compute_and_update_embed(ObjectId(doc_id), updates['text']))
        
    docs = _get_docs()
    updated_doc = docs.find_one_and_update(
        {"_id": ObjectId(doc_id)},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
        )
    if updated_doc is not None:
        return updated_doc
    raise HTTPException(status_code=404, detail=f'Invalid update: document #{doc_id} not found')

@router.delete('/document/{doc_id}')
def delete_doc(doc_id: str):
    docs = _get_docs()
    delete_op = docs.delete_one({'_id': ObjectId(doc_id)})
    if delete_op.deleted_count < 1:
        raise HTTPException(status_code=404, detail=f'Invalid delete: document #{doc_id} not found')
    return Response(status_code=204)

@router.get('/stats', response_model=StatsSchema)
def index_stats():
    docs = _get_docs()
    total = docs.count_documents({})
    ready = docs.count_documents({'status': 'ready'})
    processing = docs.count_documents({'status': 'processing'})
    error = docs.count_documents({'status': 'error'})
    return {
        'total': total,
        'ready': ready,
        'processing': processing,
        'error': error,
        'embedded_ratio': ready / total if total else 1.0,
        'indexed_ratio': indexer.size() / total if total else 1.0
    }
