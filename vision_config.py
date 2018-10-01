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
IDENTIFICATION_THRESH_HOLD = 0.20
# IDENTIFICATION_THRESH_HOLD = 0.64
BIGGEST_FACE = True
MANUAL_IDENTIFY = False
DETECT_SCALE = 2
FLIP = True
ENRICH_DATA = False
NUM_TRIED = 5
DELAY_TRIED = 0.3
# Screen config 
INPUT_SCALE = 2
SHOW_LOCAL_SCREEN = True
SIZE_OF_INPUT_IMAGE = 160
POS_COLOR = (0, 255, 0)
NEG_COLOR = (0, 0, 255)
MID_COLOR = (255, 255, 255)
THUMB_BOUNDER_COLOR = (255, 255, 255)
LINE_THICKNESS = 1
FONT_SIZE = 0.7
DIS_THUMB_X = 10
DIS_THUMB_Y = 30
DIS_BETWEEN_THUMBS = 5
FPS_POS = (10, 20)
SCREEN_SIZE = {
    'width' : 1280,
    'height' : 720
}
TRAINING_AREA = (320-128, 0, 320+128, 480)
PADDING = 5
SHOW_LOG_PREDICTION = True
SHOW_LOG_TRACKING = False
DEBUG_MOD = False
# Some necessary funtion
def set_screen_size(w, h):
    global SCREEN_SIZE, TRAINING_AREA
    w = int(w)
    h = int(h)
    SCREEN_SIZE['width'] = w
    SCREEN_SIZE['height'] = h
    TRAINING_AREA = (int(w/2-w/2) + PADDING, PADDING, int(w/2+w/2)-2*PADDING, h-2*PADDING)

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
ENCODE_MOD = "1"
IDEN_MOD = "0"
FLAG_REFETCH_DB = "-REFETCH_DB"

#Service client config
TRANSFER_LEARNING_MSG = "Transfer Learning"
NEW_LEARNING_MSG = "New Learning"
def set_service_token(token):
    global SERVICE_TOKEN, SERVICE_REGISTER_CLIENT , SERVICE_REGISTER_WORKER, IDENTIFY_QUEUE
    SERVICE_TOKEN = token
    SERVICE_REGISTER_CLIENT = SERVICE_TOKEN + '-CLIENT'
    SERVICE_REGISTER_WORKER = SERVICE_TOKEN + '-WORKER'
    IDENTIFY_QUEUE = SERVICE_TOKEN + '-IDENTIFY'


