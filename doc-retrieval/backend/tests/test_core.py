import pytest
from app.core.embedder import Embedder
from app.core.search import find_top_k

def test_embedder():
    text = 'hello world'
    embedder = Embedder(model_name='sentence-transformers/all-MiniLM-L6-v2')
    embedding = embedder.embed(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert isinstance(embedding[0], float)

def test_top_k_search():
    query_embed = [1.0, 0.0]
    docs = [
        {'embed': [1.0, 0.0], 'text': 'A'},
        {'embed': [0.0, 1.0], 'text': 'B'},
    ]
    results = find_top_k(query_embed, docs, k=1)
    assert results[0]['text'] == 'A'

