import hashlib
import urllib
from mako.template import Template
from aiohttp import web, ClientSession

from . import client
from .config import config
from .errors import error_middleware

from .logs import setup_logs
import logging

setup_logs()
log = logging.getLogger(__name__)

routes = web.RouteTableDef()

## Anonymous requests require a page key which is a hash of SECRET_KEY + URL:
def page_key_hash(secret_key, url):
    return hashlib.sha256(f"{secret_key}:{url}".encode("utf-8")).hexdigest()


def verify_key(key, url):
    return page_key_hash(config["SECRET_KEY"], url) == key


### Root handler with form to add new URLs:
@routes.get(f"{config['PATH_PREFIX']}/")
async def index(request):
    template = Template(
        """
<form action="${path_prefix}/page" method="post">
  <label for="url">URL:</label><br/>
  <input type="text" id="url" name="url"/><br/>
  <input type="submit" value="Get Archive Link"/>
</form>
"""
    )
    return web.Response(
        text=template.render(path_prefix=config["PATH_PREFIX"]),
        content_type="text/html",
    )


### Handler for adding new URLs:
@routes.post(f"{config['PATH_PREFIX']}/page")
async def add_page(request):
    data = await request.post()
    url = data["url"]

    archive = await client.get_archive(url)
    log.debug(archive)
    try:
        singlefile = archive["files"]["singlefile"]
    except KeyError:
        return web.HTTPNotFound(text="No archived page found")

    key = page_key_hash(config["SECRET_KEY"], url)

    return web.json_response(
        {
            "url": f"{config['API_BASE_URL']}/page?url={urllib.parse.quote_plus(url)}&key={key}",
            "original_url": url,
            **archive,
        }
    )


### Handler for retrieving archived page URL:
### Anonymous access requires a preshared page key:
@routes.get(f"{config['PATH_PREFIX']}/page")
async def get_page(request):
    url = request.query["url"]
    key = request.query["key"]

    ## Make sure the user passed a key that hashes to the SECRET_KEY + URL
    if not verify_key(key, url):
        return web.HTTPUnauthorized(text="Invalid page key hash")

    archive = await client.get_archive(url)
    try:
        url = f"{archive['files']['singlefile']}"
    except KeyError:
        return web.HTTPNotFound(text="No archived page found")
    async with client.client_session() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return web.HTTPInternalServerError(
                    f"archive page returned status {response.status}"
                )
            page = await response.text()
            return web.Response(text=page, content_type="text/html")


async def app():
    log.info("Starting..")
    a = web.Application()
    a.add_routes(routes)
    a.middlewares.append(error_middleware)
    return a
