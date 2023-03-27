""" logging things """

import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.StreamHandler()
    ]
)

def LOGGER(name: str) -> logging.Logger:
    """ get a Logger object """
    return logging.getLogger(name)


""" import statements """

import asyncio
import os
import re
from aiohttp import ClientSession
from datetime import datetime


""" wrapper for getting the credentials """

def get_config(name: str, d_v=None, should_prompt=False):
    """ accepts one mandatory variable
    and prompts for the value, if not available """
    val = os.environ.get(name, d_v)
    if not val and should_prompt:
        try:
            val = input(f"enter {name} value: ")
        except EOFError:
            val = d_v
        print("\n")
    return val


async def getImdbId(jwUrl: str) -> str:
    async with ClientSession() as session:
        one = await session.get(jwUrl)
        two = await one.text()
    rgxExpo = get_config("A", "A")
    mbSrchPoxe = re.search(rgxExpo, two)
    if mbSrchPoxe:
        mbId = mbSrchPoxe.group(1)
        if ":" in mbId:
            mbId = mbId.split(":")[0].strip()
        return mbId


async def jw():
    D = get_config("D", "D")
    F = get_config("F", "F")
    ct = datetime.now()
    yyyy = ct.year
    mm = ct.month
    dd = ct.day
    jsonData = {
        "operationName": get_config("C", "C"),
        "variables": {
            "first": int(get_config("H", "100")),
            "pageType": "NEW",
            "date": f"{yyyy}-{mm}-{dd - 3}",
            "filter": {
                "ageCertifications": [],
                "excludeGenres": [],
                "excludeProductionCountries": [],
                "genres": [],
                "objectTypes": [],
                "productionCountries": [],
                "packages": [],
                "excludeIrrelevantTitles": False,
                "presentationTypes": [],
                "monetizationTypes": [],
            },
            "language": "en",
            "country": "IN",
            "priceDrops": False,
            "platform": "WEB",
            "showDateBadge": False,
            "availableToPackages": [],
        },
        "query": get_config("B", "B"),
    }
    async with ClientSession() as session:
        one_response = await session.post(
            get_config("E", "E"),
            headers={
                "User-Agent": "TelegramBot (like TwitterBot)"
            },
            json=jsonData
        )
        second_response = await one_response.json()
    newTitles = second_response.get("data").get("newTitles")
    totalCount = newTitles.get("totalCount", 0)
    LOGGER("TOTAL COUNT: ").info(totalCount)
    edges = newTitles.get("edges", [])
    LOGGER("COUNT: ").info(len(edges))
    for edge in edges:
        jwId = edge.get("node").get("id")
        content = edge.get("node").get("content")
        fullPath = D + content.get("fullPath", "")
        imdbId = await getImdbId(fullPath)
        title = content.get("title", "")
        if (
            imdbId and
            not os.path.exists(imdbId)
        ):
            async with ClientSession() as session:
                one = await session.post(
                    f"https://api.telegram.org/bot{F}/createForumTopic",
                    json={
                        "chat_id": get_config("G", 0),
                        "name": imdbId,
                    }
                )
                two = await one.json()
            mtId = two.get("result").get("message_thread_id")
            with open(imdbId, "w+") as fod:
                fod.write(f"{jwId}\n{mtId}")
        await asyncio.sleep(10)

asyncio.run(jw())
