import logging
import os

import tornado.ioloop
import tornado.web
import tornado.util
import hydra

from omegaconf import DictConfig, OmegaConf

from tornado_swagger.setup import setup_swagger


LOGGER = logging.getLogger(__name__)



class ServerHeaderTransform(tornado.web.OutputTransform):
    def transform_first_chunk(self, status_code, headers, chunk, finishing):
        headers.pop('Server')
        return status_code, headers, chunk
        
class WebApp(tornado.web.Application):
    def __init__(self, cfg: DictConfig):
        data = OmegaConf.to_container(cfg)
        _routes = [
            tornado.web.url (r"/api/main", MainHandler),
            tornado.web.url(r"/api/repositories", RepositorysHandler, dict(
                repos=data["repositories"], working_dir=data["working_directory"], validator_settings=data["validator_settings"])),
            tornado.web.url (r"/api/repository/(.*)", RepositoryHandler, dict(repos=data["repositories"])),
            tornado.web.url (r"/api/credentials", CredentialsHandler),
            tornado.web.url (r"/api/containers", ContainersHandler),
            tornado.web.url (r"/api/container/(.*)", ContainerHandler),
            tornado.web.url(
            r"/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "client_files"), "default_filename": "index.html"}
            ),
        ]

        setup_swagger(
            _routes,
            swagger_url="/doc",
            api_base_url="/",
            description="Cmdbweather",
            api_version="1.0.0",
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




def make_app(cfg: DictConfig = None):
    LOGGER.info("Creating Application")
    

    web_app = WebApp(cfg)
    return web_app


if __name__ == "__main__":
    pass
    
