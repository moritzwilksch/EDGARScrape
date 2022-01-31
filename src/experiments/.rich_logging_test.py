import logging
from rich.logging import RichHandler

logging.basicConfig(
    level="DEBUG", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")
log.info("Hello, World!")

x = 42

log.info(f"x = {x}")
log.warning("didnt work")
log.error("error")
log.critical("critical")
log.debug("debug")
log.exception("exception")

try:
    raise KeyError("key error")
except KeyError as e:
    log.exception(e)
