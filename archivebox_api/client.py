import aiohttp
import asyncio
import urllib
from bs4 import BeautifulSoup
from .config import config

import logging

log = logging.getLogger(__name__)


def client_session():
    return aiohttp.ClientSession(
        config["ARCHIVEBOX_BASE_URL"], headers=config["headers"]
    )


async def debug_response(response):
    print("Status:", response.status)
    print("Content-type:", response.headers["content-type"])

    data = await response.text()
    print(data)


async def parse_csrf_middleware_token(response, form_id):
    if response.status != 200:
        raise AssertionError(
            f"Could not get the form page, response={response.status}, url={response.url}"
        )
    data = await response.text()
    soup = BeautifulSoup(data, "html.parser")
    form = soup.find(id=form_id)
    for input in form.find_all("input"):
        if input.has_attr("name") and input["name"] == "csrfmiddlewaretoken":
            return input["value"]
    else:
        raise LoginError("Could not find CSRF Middleware Token on login page")


async def login(session):
    ## Get the Login page to parse the CSRF Middleware Token:
    async with session.get("/admin/login/") as response:
        login_token = await parse_csrf_middleware_token(response, "login-form")
    ## Login:
    async with session.post(
        "/admin/login/",
        data={
            "username": config["ARCHIVEBOX_USERNAME"],
            "password": config["ARCHIVEBOX_PASSWORD"],
            "csrfmiddlewaretoken": login_token,
            "next": "/admin/",
        },
    ) as response:
        if response.status != 200:
            raise AssertionError(
                "Could not login. response={response.status}, url={response.url}"
            )


async def add_url(url, parser="auto", tag="", depth=0, archive_methods=""):
    """Add URL for ArchiveBox to archive"""
    log.info(f"Adding URL: {url}")
    async with client_session() as session:
        await login(session)
        ## Get the Add URL page to parse the CSRF Middleware Token:
        async with session.get("/add/") as response:
            add_token = await parse_csrf_middleware_token(response, "add-form")
        ## Add the URL:
        form_data = {
            "url": url,
            "parser": parser,
            "tag": tag,
            "depth": str(depth),
            "archive_methods": archive_methods,
            "csrfmiddlewaretoken": add_token,
        }
        async with session.post("/add/", data=form_data) as response:
            if response.status != 200:
                raise AssertionError(
                    f"Could not add URL, response={response.status}, url={response.url}"
                )
            soup = BeautifulSoup(await response.text(), "html.parser")
            print(soup)


async def search_url(url):
    """Search for an already archived URL"""
    log.info(f"Searching for URL: {url}")
    async with client_session() as session:
        async with session.get(
            f"/public/?q={urllib.parse.quote_plus(url)}"
        ) as response:
            if response.status != 200:
                raise AssertionError(
                    "Could not get the search results. response={response.status}, url={response.url}"
                )
            data = {}

            soup = BeautifulSoup(await response.text(), "html.parser")
            # Find the first row of the results only:
            row = soup.find(id="table-bookmarks").find("tbody").find("tr")
            if row == None:
                log.info(f"No results found for URL: {url}")
                return {}
            columns = row.find_all("td")
            data["date"] = columns[0].get_text().strip()
            data["title"] = columns[1].find("span").get_text().strip()
            # Find all archive file types (singlefile, warc, etc):
            data["files"] = {}
            for span in columns[2].find_all("span"):
                if span.has_attr("class") and "files-icons" in span["class"]:
                    for a in span.find_all("a"):
                        if a.has_attr("class") and "exists-True" in a["class"]:
                            data["files"][a["title"]] = a["href"]
                            log.info(f"Found cached URL: {url}")
            return data


async def get_archive(url):
    existing = await search_url(url)
    if len(existing):
        return existing
    else:
        await add_url(url, archive_methods=["singlefile", "title"])
        return await search_url(url)


async def main():
    url = "https://time.xmission.com"
    print(await get_archive(url))


if __name__ == "__main__":
    asyncio.run(main())
