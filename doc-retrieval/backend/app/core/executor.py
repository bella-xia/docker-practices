import os
from typing import List, Optional
from concurrent.futures import ProcessPoolExecutor
from .embedder import Embedder

DEFAULT_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
# per executor worker process context
_embedder: Optional[Embedder] = None

def _init_embed_worker():
    global _embedder
    if _embedder is None:
        _embedder = Embedder(os.environ.get('MODEL_NAME', DEFAULT_MODEL))

embed_worker = ProcessPoolExecutor(max_workers=2,     
               initializer=_init_embed_worker)

def execute_embed(text: str) -> List[float]:
    global _embedder
    if _embedder is None:
        raise RuntimeError('unable to embed text: embedder not initialized')
    return _embedder.embed(text)

