import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = 'postgresql://'\
    f"{os.getenv('DB_USERNAME')}:"\
    f"{os.getenv('DB_PASSWORD')}@"\
    f"{os.getenv('DB_SERVER')}/"\
    f"{os.getenv('DB_NAME')}"
