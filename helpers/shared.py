import os
import logging

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def join_path(x, y):
    return os.path.join(x, y)
