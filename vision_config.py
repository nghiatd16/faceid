import logging
logging.basicConfig(format='[%(levelname)s|%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
# Database config
DATABASE_DIR = 'database'
DATABASE_NAME_LOAD = 'newest_database.pkl'
DATABASE_NAME_SAVE = 'newest_database.pkl'
SAVE_DATABASE = False
RAW_IMAGES_DIR = 'images'
#http://192.168.137.214:8080/video
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWD = ''
DB_NAME = 'faceid'

# Model Config
MODEL_DIR = 'model'
IMAGES_DIR = 'images'
DETECT_DEVICE = 'auto'
ENCODE_EMBEDD_DEVICE = 'auto'
# IDENTIFICATION_THRESH_HOLD = 0.59
IDENTIFICATION_THRESH_HOLD = 0.64
DETECT_SCALE = 2
FLIP = True
ENRICH_DATA = False
NUM_TRIED = 5

# Screen config 
SIZE_OF_INPUT_IMAGE = 160
POS_COLOR = (0, 255, 0)
NEG_COLOR = (0, 0, 255)
MID_COLOR = (255, 0, 0)
THUMB_BOUNDER_COLOR = (255, 255, 255)
LINE_THICKNESS = 1
FONT_SIZE = 0.5
DIS_THUMB_X = 10
DIS_THUMB_Y = 30
DIS_BETWEEN_THUMBS = 5
FPS_POS = (10, 20)
SCREEN_SIZE = {
    'width' : 1280,
    'height' : 720
}
TRAINING_AREA = (384, 0, 640, 480)
PADDING = 5
SHOW_LOG_PREDICTION = True
SHOW_LOG_TRACKING = True

# Some necessary funtion
def set_screen_size(w, h):
    global SCREEN_SIZE, TRAINING_AREA
    w = int(w)
    h = int(h)
    SCREEN_SIZE['width'] = w
    SCREEN_SIZE['height'] = h
    TRAINING_AREA = (int(3*w/5) + PADDING, PADDING, w-2*PADDING, h-2*PADDING)

def get_time():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# Service config
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
MAX_CLIENT = 5
MAX_WORKER = 5
SERVICE_TOKEN = 'AAA'
SERVICE_REGISTER_CLIENT = SERVICE_TOKEN + '-REG-CLIENT'
SERVICE_REGISTER_WORKER = SERVICE_TOKEN + '-REG-WORKER'
WORKER_OFFLINE = -1
WORKER_ONLINE = 0
WORKER_RUNNING = 1

MAX_TIME_CLIENT_REGISTER = 10
MAX_TIME_WORKER_REGISTER = 10

# Service identify config
BATCH = 1
IDENTIFY_QUEUE = SERVICE_TOKEN + '-IDENTIFY'

def set_service_token(token):
    global SERVICE_TOKEN, SERVICE_REGISTER_CLIENT , SERVICE_REGISTER_WORKER, IDENTIFY_QUEUE
    SERVICE_TOKEN = token
    SERVICE_REGISTER_CLIENT = SERVICE_TOKEN + '-CLIENT'
    SERVICE_REGISTER_WORKER = SERVICE_TOKEN + '-WORKER'
    IDENTIFY_QUEUE = SERVICE_TOKEN + '-IDENTIFY'


