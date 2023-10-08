import logging
TOKEN = "5873954578:AAH8DQTB2DY6ejRlo4kdJrN5WVRcCjDBSk8" 
DEVELOPER_USERNAME = "WayDBae"
DIRECTIONS = ["Информатика", "Экономика", "Металлургия"]
COURSES = ["1 курс", "2 курс", "3 курс", "4 курс"]
GROUPS = {
    "Информатика": ["Группа А", "Группа Б"],
    "Металлургия": ["Группа А", "Группа Б"],
    "Экономика": ["Группа А"]
}
# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
logger.addHandler(handler)
