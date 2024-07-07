import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.japan_to_user_time import japan_to_user_time


def scrape_mal_id(anime_schedule_relative_url):
    url = f'https://animeschedule.net/{anime_schedule_relative_url}'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('Failed to retrieve MyAnimeList ID from AnimeSchedule', response.status_code)

    soup = BeautifulSoup(response.content, 'html.parser')

    mal_url = soup.find('a', class_='myanimelist-link')['href']
    mal_id = mal_url.split('/')[-1]
    # check if the mal_id is a number
    if not mal_id.isdigit():
        mal_id = mal_url.split('/')[-2]
    return mal_id


def fetch_details(relative_url):
    try:
        mal_id = scrape_mal_id(relative_url)
    except Exception:
        mal_id = None
    return mal_id


def scrape_anime_schedule(year, week):
    url = f'https://animeschedule.net/?year={year}&week={week}'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('Failed to retrieve data from AnimeSchedule', response.status_code)

    soup = BeautifulSoup(response.content, 'html.parser')

    schedule = []
    day_columns = soup.find_all('div', class_='timetable-column')
    anime_cards = []

    for day_column in day_columns:
        anime_cards.extend(day_column.find_all_next(
            'div', class_=['timetable-column-show aired', 'timetable-column-show aired expanded']
        ))

    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_index = {executor.submit(fetch_details, anime_card.find_next('a', class_='show-link')['href']): index
                           for index, anime_card in enumerate(anime_cards)}
        mal_ids = [None] * len(anime_cards)

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                mal_ids[index] = future.result()
            except Exception as exc:
                mal_ids[index] = None

    for index, anime_card in enumerate(anime_cards):
        episode = anime_card.find_next('span', class_='show-episode').text.strip()
        air_date = anime_card.find_next('time', class_='show-air-time')  # get the datetime attribute
        air_date = air_date['datetime'] if air_date else None
        air_date = japan_to_user_time(air_date) if air_date else None
        title = anime_card.find_next('h2', class_='show-title-bar').text.strip()
        picture = anime_card.find_next('img', class_='show-poster')['src']
        mal_id = mal_ids[index]

        if any(d['title'] == title for d in schedule):
            continue

        schedule.append({
            'title': title,
            'episode': episode.replace('Ep ', '') if episode else None,
            'air_date': air_date,
            'picture': picture,
            "mal_id": mal_id
        })

    return schedule
