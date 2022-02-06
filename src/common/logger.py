from rich.logging import RichHandler
import logging

# logging.getLogger("requests").setLevel(logging.WARNING)  # silence requests DEBUG
logging.getLogger("urllib3").propagate = False

logging.basicConfig(
    level="DEBUG", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")
