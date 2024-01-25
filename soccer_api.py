import os
import json
import requests

def get_team_data(first_team, second_team, competition):
    headers = {
        "X-RapidAPI-Key": "",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    url_team = "https://api-football-v1.p.rapidapi.com/v3/teams"
    url_players = "https://api-football-v1.p.rapidapi.com/v3/players/squads"

    querystring_first = {"name": first_team}
    querystring_second = {"name": second_team}

    first_data = requests.get(url_team, headers=headers, params=querystring_first)
    secon_data = requests.get(url_team, headers=headers, params=querystring_second)

    first_json = first_data.json()
    second_json = secon_data.json()

    folder_path = 'data'
    first_json_file_path = os.path.join(folder_path, 'first_team_data.json')
    second_json_file_path = os.path.join(folder_path, 'second_team_data.json')

    os.makedirs(folder_path, exist_ok=True)

    with open(first_json_file_path, 'w') as file:
        json.dump(first_json, file, indent=4)

    with open(second_json_file_path, 'w') as file:
        json.dump(second_json, file, indent=4)

    first_id = first_json['response'][0]['team']['id']
    second_id = second_json['response'][0]['team']['id']

    querystring_first_team = {'team': first_id}
    querystring_second_team = {'team': second_id}

    first_team_players = requests.get(url_players, headers=headers, params=querystring_first_team)
    second_team_players = requests.get(url_players, headers=headers, params=querystring_second_team)

    first_players_json = first_team_players.json()
    second_players_json = second_team_players.json()

    first_players_json_file_path = os.path.join(folder_path, 'first_team_players.json')
    second_players_json_file_path = os.path.join(folder_path, 'second_team_players.json')

    with open(first_players_json_file_path, 'w') as file:
        json.dump(first_players_json, file, indent=4)

    with open(second_players_json_file_path, 'w') as file:
        json.dump(second_players_json, file, indent=4)

    first_players_list = first_players_json['response'][0]['players']
    second_players_list = second_players_json['response'][0]['players']

    first_players_extracted = [player['name'] for player in first_players_list]
    second_players_extracted = [player['name'] for player in second_players_list]

    first_players_filter = [name for player in first_players_extracted for name in player.split(' ')]
    second_players_filter = [name for player in second_players_extracted for name in player.split(' ')]

    return first_players_filter, second_players_filter




import json
import requests

def get_api_data(url, params):
    headers = {
        "X-RapidAPI-Key": "445088a04bmshf38acde11d7c250p13801fjsn7bb80ece68e1",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()

def save_json_to_file(data, file_path):
    folder_path = 'data'
    os.makedirs(folder_path, exist_ok=True)
    full_file_path = os.path.join(folder_path, file_path)

    with open(full_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def get_team_id(team_name):
    url_team = "https://api-football-v1.p.rapidapi.com/v3/teams"
    params = {"name": team_name}
    team_data = get_api_data(url_team, params)
    save_json_to_file(team_data, f'{team_name.lower()}_team_data.json')
    return team_data['response'][0]['team']['id']

def get_players_data(team_id, team_name):
    url_players = "https://api-football-v1.p.rapidapi.com/v3/players/squads"
    params = {"team": team_id}
    players_data = get_api_data(url_players, params)
    save_json_to_file(players_data, f'{team_name.lower()}_players.json')
    return players_data['response'][0]['players']

def extract_player_names(players_data):
    return [player['name'] for player in players_data]

def filter_player_names(player_names):
    return [name for player in player_names for name in player.split(' ')]

def get_team_data(first_team, second_team):
    first_team_id = get_team_id(first_team)
    second_team_id = get_team_id(second_team)

    first_players_data = get_players_data(first_team_id, first_team)
    second_players_data = get_players_data(second_team_id, second_team)

    first_players = extract_player_names(first_players_data)
    second_players = extract_player_names(second_players_data)

    first_players_filtered = filter_player_names(first_players)
    second_players_filtered = filter_player_names(second_players)

    return first_players_filtered, second_players_filtered

#first_team_input = input("First Team: ")
#second_team_input = input("Second Team: ")
#competition_input = input("Competition: ")

#get_team_data(first_team_input, second_team_input, competition_input)