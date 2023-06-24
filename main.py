import asyncio
import re

import aiohttp
from more_itertools import chunked

from models import Base, Session, SwapiPeople, engine

MAX_CHUNK_SIZE = 10


async def get_people(people_id):
    session = aiohttp.ClientSession()
    resource = await session.get(f"https://swapi.dev/api/people/{people_id}")
    json_data = await resource.json()
    await session.close()
    return {people_id: json_data}


async def insert_to_db(people_json_list):
    async with Session() as session:
        swapi_people_list = SwapiPeople(
            id=int(people_json_list["id"]),
            birth_year=people_json_list["birth_year"],
            eye_color=people_json_list["eye_color"],
            films=people_json_list["films"],
            gender=people_json_list["gender"],
            hair_color=people_json_list["hair_color"],
            height=people_json_list["height"],
            homeworld=people_json_list["homeworld"],
            mass=people_json_list["mass"],
            name=people_json_list["name"],
            skin_color=people_json_list["skin_color"],
            species=people_json_list["species"],
            starships=people_json_list["starships"],
            vehicles=people_json_list["vehicles"],
        )

        session.add(swapi_people_list)
        await session.commit()


async def film_name(url_film):
    session = aiohttp.ClientSession()
    resource = await session.get(f"{url_film}")
    json_data = await resource.json()
    await session.close()

    return json_data


async def check(check_list, key=None):
    final_list = []
    len_film = len(check_list)
    if len_film > 0:
        for f in range(len_film):
            if key is not None:
                film_n = check_list[f][key]
            else:
                film_n = check_list[f]
            final_list.append(film_n)
    else:
        return [{"None": "None"}]

    return final_list


async def go():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)

    for ids_chunk in chunked(range(1, 91), MAX_CHUNK_SIZE):
        get_people_coros = [get_people(people_id) for people_id in ids_chunk]
        people_json_list = await asyncio.gather(*get_people_coros)
        length = len(people_json_list)
        for i in range(length):
            numbers = re.findall("[0-9]+", str(people_json_list[i].keys()))
            id_p = int(numbers[0])
            if "detail" not in people_json_list[i][id_p]:
                film = [
                    film_name(film_url)
                    for film_url in people_json_list[i][id_p]["films"]
                ]
                film_json = await asyncio.gather(*film)
                films_people = await check(film_json, "title")
                species = [
                    film_name(species_url)
                    for species_url in people_json_list[i][id_p]["species"]
                ]
                species_json = await asyncio.gather(*species)
                species_people = await check(species_json)
                species_final = "".join(
                    "{}: {}, ".format(key, val)
                    for key, val in species_people[0].items()
                )
                starships = [
                    film_name(starships_url)
                    for starships_url in people_json_list[i][id_p]["starships"]
                ]
                starships_json = await asyncio.gather(*starships)
                starships_people = await check(starships_json, "name")
                vehicles = [
                    film_name(vehicles_url)
                    for vehicles_url in people_json_list[i][id_p]["vehicles"]
                ]
                vehicles_json = await asyncio.gather(*vehicles)
                vehicles_people = await check(vehicles_json, "name")
                p_d = {
                    "id": int(id_p),
                    "birth_year": people_json_list[i][id_p]["birth_year"],
                    "eye_color": people_json_list[i][id_p]["eye_color"],
                    "films": ", ".join(films_people),
                    "gender": people_json_list[i][id_p]["gender"],
                    "hair_color": people_json_list[i][id_p]["hair_color"],
                    "height": people_json_list[i][id_p]["height"],
                    "homeworld": people_json_list[i][id_p]["homeworld"],
                    "mass": people_json_list[i][id_p]["mass"],
                    "name": people_json_list[i][id_p]["name"],
                    "skin_color": people_json_list[i][id_p]["skin_color"],
                    "species": str(species_final),
                    "starships": str(starships_people[0]),
                    "vehicles": str(vehicles_people[0]),
                }
                asyncio.create_task(insert_to_db(p_d))

    current_task = asyncio.current_task()
    tasks_sets = asyncio.all_tasks()
    tasks_sets.remove(current_task)

    await asyncio.gather(*tasks_sets)
    await engine.dispose()


asyncio.run(go())
