import os
import sys
import logging
import hydra
import tornado

from omegaconf import DictConfig

from omdbweather.app import make_app

LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 8660

CONFIG_FILE = 'config/debug.yaml'
CONFIG_LOCATION = os.environ.get('CONFIG', CONFIG_FILE)
@hydra.main(config_name=CONFIG_LOCATION)
def run_app(cfg: DictConfig = None):
    LOGGER.info(F"Starting OmdbWeather debug-mode={cfg.debug}")
    local_location = f"{os.path.dirname(__file__)}/{CONFIG_FILE}" if os.environ.get('CONFIG') is None else os.environ.get('CONFIG')
    LOGGER.info(F"Loading configuration from {local_location}")
    app = make_app(cfg)
    
    if isinstance(app, bool) and app is False:
        sys.exit(1)
    
    LOGGER.info(F"Start listening on {os.environ.get('PORT', DEFAULT_PORT)}")
    
    try:
        app.listen(port=os.environ.get('PORT', DEFAULT_PORT), address="0.0.0.0")
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt as _:
        tornado.ioloop.IOLoop.current().stop()
        LOGGER.info("== Closing OmdbWeather ==")
        LOGGER.info("<Bye></Bye>")
    except Exception as e:
        LOGGER.exception(str(e))


if __name__ == "__main__":
    sys.exit(run_app())
    
