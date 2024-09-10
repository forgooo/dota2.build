import requests
import time
import os
import json

def load_last_match_id(filename="last_match_id.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return None


def save_last_match_id(last_match_id, filename="last_match_id.json"):
    with open(filename, 'w') as file:
        json.dump(last_match_id, file)


def save_match_ids(match_ids, filename="match_ids.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_data = json.load(file)
        match_ids.update(existing_data) 
    with open(filename, 'w') as file:
        json.dump(list(match_ids), file)


def find_high_mmr_matches(min_rank=73, limit=1000, max_requests=1000):
    url = "https://api.opendota.com/api/publicMatches"
    all_match_ids = set()
    
    last_match_id = load_last_match_id()

    for _ in range(max_requests):
        params = {
            "min_rank": min_rank,
            "less_than_match_id": last_match_id
        }

        response = requests.get(url, params=params)
        print(f"Запрос {response.status_code}: Получение данных...")
        matches_data = response.json()

        if not matches_data:
            print("Нет новых матчей для обработки.")
            break

        new_match_ids = [match['match_id'] for match in matches_data]
        all_match_ids.update(new_match_ids)

        last_match_id = new_match_ids[-1]

        os.system('cls')
        print(f"Найдено {len(all_match_ids)} уникальных матчей.")

        save_match_ids(all_match_ids)
        save_last_match_id(last_match_id)

        time.sleep(1)

        if len(all_match_ids) >= limit:
            break

    return list(all_match_ids)

match_ids = find_high_mmr_matches(min_rank=73, limit=1000, max_requests=1000)

print(f"Найдено {len(match_ids)} уникальных матчей.")
