import requests
import csv
import time
import json

# Функция для получения данных о матче
def get_match_data(match_id):
    url = f"https://api.opendota.com/api/matches/{match_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        match_data = response.json()
        return match_data
    else:
        print(f"Ошибка при получении данных о матче {match_id}. Код ответа: {response.status_code}")
        return None

# Функция для извлечения информации о герое, включая KDA, позиции, победу/поражение и покупки
def extract_player_data(match_data):
    players = match_data.get('players', [])
    player_info = []
    radiant_win = match_data.get('radiant_win')  # True, если выиграла команда Radiant

    # Чтобы отслеживать дублирование ролей
    radiant_roles = {"Safe Lane (Carry)": 0, "Mid Lane": 0, "Offlane": 0}
    dire_roles = {"Safe Lane (Carry)": 0, "Mid Lane": 0, "Offlane": 0}

    for player in players:
        hero_id = player.get('hero_id')
        player_slot = player.get('player_slot')
        
        # Определяем, в какой команде был игрок: Radiant или Dire
        is_radiant = player_slot < 128  # Если player_slot < 128, игрок в Radiant
        win = radiant_win if is_radiant else not radiant_win  # Победил ли игрок
        
        # Извлекаем KDA (Kills, Deaths, Assists)
        kills = player.get('kills')
        deaths = player.get('deaths')
        assists = player.get('assists')
        
        # Определение позиции героя (lane_role), если доступно
        lane_role = player.get('lane_role', None)
        role = lane_role_to_string(lane_role, is_radiant, radiant_roles if is_radiant else dire_roles)

        # Лог покупок предметов
        purchase_log = player.get('purchase_log', [])
        purchases = [purchase['key'] for purchase in purchase_log if 'key' in purchase]  # Только названия предметов
        
        # Формируем строку для таблицы
        player_info.append({
            'hero_id': hero_id,
            'team': 'Radiant' if is_radiant else 'Dire',
            'win': win,
            'kills': kills,
            'deaths': deaths,
            'assists': assists,
            'role': role,
            'purchases': ", ".join(purchases) if purchases else "None"  # Объединяем покупки в строку
        })
    
    return player_info

# Функция для определения позиции героя на основе lane_role и проверки на дублирование ролей
def lane_role_to_string(lane_role, is_radiant, roles_counter):
    if lane_role == 1:
        role = 'Safe Lane (Carry)'
    elif lane_role == 2:
        role = 'Mid Lane'
    elif lane_role == 3:
        role = 'Offlane'
    elif lane_role == 4:
        role = 'Roaming/Support'
    else:
        role = 'Unknown'
    
    # Проверяем на дублирование Carry, Mid, Offlane
    if role in ['Safe Lane (Carry)', 'Mid Lane', 'Offlane']:
        if roles_counter[role] >= 1:
            # Если уже есть герой на этой позиции, назначаем Support
            role = 'Support'
        else:
            # Увеличиваем счетчик для позиции
            roles_counter[role] += 1

    return role

# Функция для сохранения данных в CSV
def save_to_csv(player_data, filename='match_data.csv'):
    # Указываем заголовки для CSV файла
    fieldnames = ['hero_id', 'team', 'win', 'kills', 'deaths', 'assists', 'role', 'purchases']
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Если файл пустой, записываем заголовки
        if file.tell() == 0:
            writer.writeheader()

        for player in player_data:
            writer.writerow(player)  # Записываем данные каждого игрока

    print(f"Данные успешно добавлены в {filename}")

# Функция для обработки матчей из файла
def process_matches_from_file(filename):
    with open(filename, 'r') as file:
        match_ids = json.load(file)

    for match_id in match_ids:
        match_data = get_match_data(match_id)
        if match_data:
            player_data = extract_player_data(match_data)
            save_to_csv(player_data, 'match_data.csv')  # Сохраняем данные в CSV
        time.sleep(1)  # Небольшая задержка между запросами

# Обрабатываем матч-идентификаторы из файла
process_matches_from_file('match_ids.json')  # Замените на имя вашего файла с match_ids
