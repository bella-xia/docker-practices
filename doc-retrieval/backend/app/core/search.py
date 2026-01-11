import numpy
from numpy import dot
from numpy.linalg import norm
from typing import Sequence, List

from ..db.schemas import DocumentModel, ResponseSchema 

def find_top_k(query_embed: Sequence[float], 
        doc_arr: List[DocumentModel], 
        k: int) -> List[ResponseSchema]:
    valid_indices, embeds = [], []
    for idx, doc in enumerate(doc_arr):
        embed = doc.get('embed')
        if embed is not None:
            embeds.append(embed)
            valid_indices.append(idx)
    if not embeds:
        return []
    doc_np = numpy.asarray(embeds, dtype=numpy.float32)
    query_np = numpy.asarray(query_embed, dtype=numpy.float32)
    assert doc_np.shape[1] == query_np.shape[0]
    scores = doc_np @ query_np
    k = min(k, len(scores))
    if k == 0:
        return []
    topk_idx = numpy.argpartition(scores, -k)[-k:]
    topk_idx = topk_idx[numpy.argsort(scores[topk_idx])[::-1]]
    res = [{'score': float(scores[i]), **(doc_arr[valid_indices[i]])} for i in topk_idx]
    return res


