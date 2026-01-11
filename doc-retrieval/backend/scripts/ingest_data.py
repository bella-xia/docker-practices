import json
import requests
from tqdm import tqdm

BOUND=2000
BASE_URL='http://localhost:8000'

if __name__ == '__main__':
    data = []
    with open('data/News_Category_Dataset_v3.json', 'r', encoding='utf-8-sig') as f:
        for i, line in enumerate(f):
            if i < BOUND:
                continue
            elif i >= BOUND * 2:
                break
            try:
                data.append(json.loads(line))
            except Exception:
                continue
 
    endpoint = f'{BASE_URL}/api/events/upload/'
    for inst in tqdm(data):
        if 'headline' not in inst:
            continue
        json_data = {
            'text': inst['headline'],
            'metadata': {
               'category': inst.get('category', ''),
               'date': inst.get('date', ''),
               'link': inst.get('link', '')
                }
            }
        response = requests.post(endpoint, json=json_data)
        if not response.ok:
            print(f'request failed: {response.json()}')
