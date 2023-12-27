# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
import os, sys, time

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

import nest_asyncio
from fastapi import FastAPI
from utils.deepl_api import DeeplTranslator

nest_asyncio.apply()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global deeplEngine, timestamp_check
    timestamp_check = int(time.time())
    deeplEngine = DeeplTranslator()
    print("lifespan startup")
    yield
    print("Test")


app = FastAPI(lifespan=lifespan)


@app.post("/deepl")
async def translate_sentences(data: dict):
    global timestamp_check, deeplEngine
    current_timestamp = int(time.time())
    if current_timestamp - timestamp_check > 60 * 30:
        deeplEngine = DeeplTranslator()
        timestamp_check = int(time.time())
    print(data)
    source_lang = data.get("source_lang", "JP")
    target_lang = data.get("target_lang", "EN")
    response = deeplEngine.translate(
        data["Raw"], source_lang=source_lang, target_lang=target_lang
    )
    print(response)
    return {"Translation": response}
