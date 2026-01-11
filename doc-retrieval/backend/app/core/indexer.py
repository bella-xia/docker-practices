from typing import List, Sequence
from bson import ObjectId
import numpy as np
import faiss
import threading

class Indexer:
    def __init__(self, embed_dim=384):
        self.index = faiss.IndexFlatIP(embed_dim)
        self._lock = threading.Lock()
        self._faiss2oid = {}
        self._oid2faiss = {}

    def add(self, oid: ObjectId, embed: Sequence) -> None:
        v = np.asarray(embed, dtype=np.float32).reshape(1, -1)

        with self._lock:
            idx = self.index.ntotal
            self.index.add(v)
            self._faiss2oid[idx] = oid
            self._oid2faiss[oid] = idx
    
    def search(self, embed: np.ndarray, k: int) -> dict[ObjectId, float]:
        if self.index.ntotal == 0:
            return []
        q = np.asarray(embed, dtype=np.float32).reshape(1, -1)
        scores, idxs = self.index.search(q, k=k)
        res = {}
        for faiss_id, score in zip(idxs[0], scores[0]):
            if faiss_id == -1:
                continue
            res[self._faiss2oid[int(faiss_id)]] = float(score)
        return res
    
    def size(self) -> int:
        return self.index.ntotal


indexer = Indexer()
