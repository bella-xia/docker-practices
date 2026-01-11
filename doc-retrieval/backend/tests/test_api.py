import pytest
import requests

BASE_URL = 'http://localhost:8000/api/events'

def test_single_doc():
    new_doc = {'text': 'hello world'}
    res1 = requests.post(f'{BASE_URL}/upload/', json=new_doc)
    assert res1.status_code == 200
    res1_json = res1.json()

    query = {'text': 'hello world', 'top_k': 5}
    res2 = requests.post(f'{BASE_URL}/query/', json=query)
    assert res2.status_code == 200
    res2_json = res2.json()
    assert len(res2_json) == 5
    assert res2_json[0]['text'] == 'hello world'

    res3 = requests.get(f"{BASE_URL}/document/{res1_json['_id']}")
    assert res3.status_code == 200
    res3_json = res3.json()
    assert res3_json['text'] == 'hello world'
    
    res4 = requests.delete(f"{BASE_URL}/document/{res1_json['_id']}")
    assert res4.status_code == 204
