import hashlib
import urllib
from mako.template import Template
from aiohttp import web, ClientSession

from . import client
from .config import config

routes = web.RouteTableDef()

## Anonymous requests require a page key which is a hash of SECRET_KEY + URL:
def page_key_hash(secret_key, url):
    return hashlib.sha256(f"{secret_key}:{url}".encode("utf-8")).hexdigest()


def verify_key(key, url):
    return page_key_hash(config["SECRET_KEY"], url) == key


### Root handler with form to add new URLs:
@routes.get(f"{config['PREFIX_PATH']}/")
async def index(request):
    template = Template(
        """
<form action="/page" method="post">
  <label for="url">URL:</label><br/>
  <input type="text" id="url" name="url"/><br/>
  <input type="submit" value="Get Archive Link"/>
</form>
"""
    )
    return web.Response(text=template.render(), content_type="text/html")


### Handler for adding new URLs:
@routes.post(f"{config['PREFIX_PATH']}/page")
async def add_page(request):
    data = await request.post()
    url = data["url"]

    files = await client.get_archive(url)
    try:
        singlefile = files["singlefile"]
    except KeyError:
        return web.HTTPNotFound(text="No archived page found")

    url = urllib.parse.quote_plus(url)
    key = page_key_hash(config["SECRET_KEY"], url)

    return web.json_response(
        {"url": f"{config['API_BASE_URL']}/page?url={url}&key={key}"}
    )


### Handler for retrieving archived page URL:
### Anonymous access requires a preshared page key:
@routes.get(f"{config['PREFIX_PATH']}/page")
async def get_page(request):
    url = request.query["url"]
    key = request.query["key"]

    ## Make sure the user passed a key that hashes to the SECRET_KEY + URL
    if not verify_key(key, url):
        return web.HTTPUnauthorized(text="Invalid page key hash")

    files = await client.get_archive(url)
    try:
        url = files["singlefile"]
    except KeyError:
        return web.HTTPNotFound(text="No archived page found")
    async with client.client_session() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return web.HTTPInternalServerError(
                    f"archive page returned status {response.status}"
                )
            print(response)
            page = await response.text()
            print(page)
            return web.Response(text=page, content_type="text/html")


async def app():
    a = web.Application()
    a.add_routes(routes)
    return a
