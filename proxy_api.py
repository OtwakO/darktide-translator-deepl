# -*- coding: utf-8 -*-
import json, random
import os, sys, time, requests, aiohttp, asyncio

from random import choice
from decouple import config
from loguru import logger
from aiohttp_proxy import ProxyConnector
from concurrent.futures import ThreadPoolExecutor

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

VALIDATOR_URL = f"https://httpbin.org/ip"


def chunks(L, n):
    return [L[x : x + n] for x in range(0, len(L), n)]


class ProxyGen:
    def __init__(self, country_code=None):
        self.country_code = country_code
        self.proxies = self.get_free_proxy()
        self.validated_proxies = asyncio.run(self.proxy_validator())
        logger.success(f"{len(self.validated_proxies)} proxies ready to be used.")
        logger.success(self.validated_proxies)
        self.proxies_choices = [*self.validated_proxies]

    def rand_proxy(self) -> str:
        if not self.proxies_choices:
            self.proxies_choices = [*self.validated_proxies]
        rand_proxy = choice(self.proxies_choices)
        self.proxies_choices.remove(rand_proxy)
        # logger.debug(f"Proxy chosen: {rand_proxy}")
        return rand_proxy

    # Function to seperate big list into smaller chunks

    def get_free_proxy(self):
        response = requests.get(
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        )
        proxy_urls = response.text.split("\r\n")
        proxy_urls = [f"http://{i}" for i in proxy_urls if i != ""]
        return proxy_urls

    def remove_proxy(self, proxy):
        try:
            self.validated_proxies.remove(proxy)
        except ValueError:
            pass
        # logger.success(
        #     f"{len(self.validated_proxies)=} || {len(self.proxies_choices)=}"
        # )
        if len(self.validated_proxies) == 0:
            self.validated_proxies = asyncio.run(self.proxy_validator())

    async def proxy_validator_task(self, proxy) -> str:
        session_timeout = aiohttp.ClientTimeout(total=5)
        try:
            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                async with session.get(VALIDATOR_URL, proxy=proxy) as response:
                    if response.status == 200:
                        resp = await response.json()
                        return None
                    else:
                        # logger.error(f"Error with response status: {response.status}.")
                        return proxy
        except TimeoutError:
            # logger.error(f"Proxy: {proxy} timed out.")
            return proxy
        except Exception as e:
            # logger.error(f"Proxy: {proxy} returns an error of: {e}")
            return proxy

    async def proxy_validator(self):
        proxy_chunks = chunks(self.proxies, 500)
        validated_proxies = [*self.proxies]
        total_proxies = len(validated_proxies)
        logger.success(f"Validating all proxies...")
        for chunk in proxy_chunks:
            tasks = []
            for proxy in chunk:
                tasks.append(asyncio.create_task(self.proxy_validator_task(proxy)))
            bad_proxies = [
                proxy for proxy in await asyncio.gather(*tasks) if proxy != None
            ]
            for proxy in bad_proxies:
                validated_proxies.remove(proxy)
        logger.success(
            f"Validation complete! [{len(validated_proxies)}/{total_proxies}] valid proxy."
        )
        return validated_proxies


if __name__ == "__main__":
    Proxy = ProxyGen()
