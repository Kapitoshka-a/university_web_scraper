import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Any
import json
import conf
import asyncio
import aiofiles

URL = conf.URL
UNIVERSITY_DATA_MAP = conf.UNIVERSITY_DATA_MAP
UNIVERSITY_DATA_SCHEMA = conf.UNIVERSITY_DATA_SCHEMA


async def fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def get_next_page(document: BeautifulSoup):
    next_page_span = document.find('span', class_="next")
    try:
        next_page_url = next_page_span.find('a').get('href')
        if next_page_url:
            response_text = await fetch('https://osvita.ua/' + next_page_url)
            return BeautifulSoup(response_text, "html.parser")
    except AttributeError:
        return None


async def get_universities(document: BeautifulSoup) -> List[Dict]:
    universities_data = []
    data = document.find_all('div', class_='block-frame-2047')
    for university in data:
        link_tag = university.find('a', class_='link-educational')
        href = link_tag.get('href')
        title = link_tag.get('title')
        address = university.find('span', class_='adress-educational').string
        universities_data.append({'title': title,
                                  'link': href,
                                  'address': address})

    return universities_data


async def update_university_details(university: Dict) -> Dict:
    university_data = UNIVERSITY_DATA_SCHEMA.copy()
    university_data['title'] = university['title']
    university_data['address'] = university['address']
    university_data['link'] = university['link']

    response_text = await fetch('https://osvita.ua/' + university['link'])
    detail_page = BeautifulSoup(response_text, "html.parser")
    data = detail_page.find('table', class_='table table-striped table-bordered').tbody
    rows = data.find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        if cells[0].string is not None:
            key = UNIVERSITY_DATA_MAP.get(cells[0].string)
            university_data[key] = cells[1].string
        else:
            cells[0] = cells[0].find('a').string + ':'
            key = UNIVERSITY_DATA_MAP.get(cells[0])
            university_data[key] = cells[1].string
    return university_data


async def update_universities_details(universities: List[Dict]):
    tasks = [update_university_details(university) for university in universities]
    return await asyncio.gather(*tasks)


async def main(url: str) -> tuple[Any]:
    universities = []
    response_text = await fetch(url)
    soup = BeautifulSoup(response_text, "html.parser")
    while True:
        universities += await get_universities(soup)
        next_page = await get_next_page(soup)
        if next_page:
            soup = next_page
        else:
            break
    universities_data = await update_universities_details(universities)
    return universities_data


async def convert_universities_to_json(universities: List[Dict]):
    json_universities = json.dumps(universities, indent=4, ensure_ascii=False)
    async with aiofiles.open('data/universities.json', 'w', encoding='utf-8') as file:
        await file.write(json_universities)


if __name__ == "__main__":
    collected_universities = asyncio.run(main(URL))
    asyncio.run(convert_universities_to_json(collected_universities))
