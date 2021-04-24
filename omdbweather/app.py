import logging
import os

import tornado.ioloop
import tornado.web
import tornado.util
import hydra

from omegaconf import DictConfig, OmegaConf

from tornado_swagger.setup import setup_swagger

from omdbweather.handlers.helper import HelperHandler
from omdbweather.handlers.movies import MoviesHandler
from omdbweather.cache_engine import MovieCacheEngine


LOGGER = logging.getLogger(__name__)



class ServerHeaderTransform(tornado.web.OutputTransform):
    def transform_first_chunk(self, status_code, headers, chunk, finishing):
        headers.pop('Server')
        return status_code, headers, chunk

class WebApp(tornado.web.Application):
    def __init__(self, cfg: DictConfig):
        data = OmegaConf.to_container(cfg)
        caches = self._setup_cache(cfg, "movies")
        _routes = [
            tornado.web.url (r"/api/help", HelperHandler),
            tornado.web.url(r"/api/movies", MoviesHandler, dict(caches=caches)),
            # tornado.web.url (r"/api/repository/(.*)", RepositoryHandler, dict(repos=data["repositories"])),
            # tornado.web.url (r"/api/credentials", CredentialsHandler),
            # tornado.web.url (r"/api/containers", ContainersHandler),
            # tornado.web.url (r"/api/container/(.*)", ContainerHandler),
            tornado.web.url(
            r"/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "client_files"), "default_filename": "index.html"}
            ),
        ]

        setup_swagger(
            _routes,
            swagger_url="/doc",
            api_base_url="/",
            description="Cmdbweather",
            api_version="1.0.1",
            title="omdbweather Service",
            contact="reubinoff@gmail.com",
            schemes=["http"]
        )
        self._config = cfg
        global_settings = {
            "debug": cfg.debug,
            "static_path": os.path.join(os.path.dirname(__file__), "client_files"),
            }
        super().__init__(_routes, transforms=[ServerHeaderTransform], **global_settings)

    def _setup_cache(self, cfg: DictConfig, idx_name) -> MovieCacheEngine:
        host = "myredis"
        if cfg.debug is True:
            host = "localhost"
        cache_engine = MovieCacheEngine(host)
        return {
            "movie": cache_engine
        }
            


def make_app(cfg: DictConfig = None):
    LOGGER.info("Creating Application")
    

    web_app = WebApp(cfg)
    return web_app


if __name__ == "__main__":
    @hydra.main(config_name=os.environ.get('CONFIG', 'config/debug.yaml'))
    def run(cfg: DictConfig=None):
        app = make_app(cfg)
        app.listen(os.environ.get('PORT', 8080))
        tornado.ioloop.IOLoop.current().start()
    run()

    
