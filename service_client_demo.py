import redis
import cv2
import uuid
import time
import queue
import _thread
import numpy as np

import vision_config
import manage_data
from TrackingFace import MultiTracker
from interact_database_DL import Database
from object_DL import Person, Camera, Location, Image
# from Vision import Vision

import logging

try:
    database = Database(host=vision_config.DB_HOST, \
                        user=vision_config.DB_USER, \
                        passwd=vision_config.DB_PASSWD, \
                        database_name= vision_config.DB_NAME)
except:
    raise ConnectionError('Cannot connect to database')
RUNNING = True
max_client = 1
url = input('URL : ')
if url == '0':
    url = 0
cap = cv2.VideoCapture(url)
cap.set(cv2.CAP_PROP_FPS, 60)
q_array = []
for i in range(max_client):
    q_array.append(queue.Queue(maxsize=2))

def record():
    global RUNNING
    while cap.isOpened() and RUNNING:
        ret, frame = cap.read()
        for i in range(max_client):
            if q_array[i].full():
                q_array[i].get()
            q_array[i].put(np.copy(frame))

def client(thread_idx):
    global RUNNING
    cid = str(uuid.uuid4())
    logging.info('Client {}'.format(cid))
    r = redis.StrictRedis(host='localhost', port=6379)
    r_remote = redis.StrictRedis(host='localhost', port=6379)
    p = r.pubsub()
    r.lpush(vision_config.SERVICE_REGISTER_CLIENT, cid)
    st = time.time()
    while r.exists(cid) == False:
        if time.time() - st > 10.:
            logging.exception('Wait too long!!!')
            RUNNING = False
            return
        time.sleep(0.1)
    msg = r.get(cid)
    if msg is None or msg == b'NONE':
        logging.info('Server is busy!')
        r.delete(cid)
        # RUNNING = False
        return
    info = msg.split()
    IN = info[0]
    OUT = info[1]
    CHANNEL = info[2]
    p.subscribe(CHANNEL)
    logging.info('Connected to server :: {} :: {} :: {}'.format(IN, OUT, CHANNEL))
    
    # database = manage_data.read_database_from_disk(vision_config.DATABASE_DIR, vision_config.DATABASE_NAME_LOAD)
    # vision_object = Vision(database)
    multi_tracker = MultiTracker()
    bboxes = []
    timer = time.time()
    old_frame = None
    while RUNNING:
        frame = q_array[thread_idx].get()
        fps = int(1./(time.time() - timer + 0.000001))
        timer = time.time()
        bytebuf = np.array([frame.shape[0], frame.shape[1], frame.shape[2]], dtype=np.uint16).tobytes() + frame.tobytes()
        r.ltrim(IN, 0, 0)
        r.lpush(IN, bytebuf)
        while not r.exists(OUT):
            time.sleep(0.001)
            continue
        bboxes = np.frombuffer(r.get(OUT), dtype=np.uint16)
        r.delete(OUT)
        if len(bboxes) > 0:
            bboxes = np.reshape(bboxes, (-1, 4))
        # try:
        multi_tracker.update_bounding_box(bboxes, database)
        unidentified_tracker, identified_tracker = multi_tracker.cluster_trackers()
        trackers = multi_tracker.get_multitracker()
        # t1 = time.time()
        for idx, tracker in enumerate(trackers):
            if tracker.person is None:
                msg = r_remote.rpop(tracker.id)
                if msg is not None:
                    # print("AAA {} {}".format(tracker.id, msg))
                    tracker.receive += 1
                    if tracker.person is None:
                        logging.info("{} - {}".format("Unknown", tracker.receive))
                    else:
                        logging.info("{} - {} - {}".format(tracker.person.id, tracker.person.name, tracker.receive))
                    predict_id = int(msg)
                    predicts = [None]
                    if predict_id != -1:
                        pred_p = Person(id=predict_id)
                        predicts = database.selectFromPerson(pred_p)
                    multi_tracker.update_identification([tracker], predicts)
        # t2 = time.time()
        if len(unidentified_tracker) > 0:
            for tracker in unidentified_tracker:
                if tracker.person is None and tracker.tried < vision_config.NUM_TRIED:
                    len_ID = len(tracker.id)
                    ID = tracker.id
                    face = tracker.get_bbox_image(frame)
                    tracker.set_image(face)
                    msg = np.array([len_ID], dtype=np.uint8).tobytes() + str.encode(ID) + face.tobytes()
                    r_remote.lpush(vision_config.IDENTIFY_QUEUE, msg)
                tracker.tried += 1
        # t3 = time.time()
        # logging.info("{} {}".format(t2-t1, t3-t2))
    
        multi_tracker.show_info(frame)
        # except:
        #     continue
        #     pass
        cv2.putText(frame, 'FPS ' + str(fps), \
                    vision_config.FPS_POS, cv2.FONT_HERSHEY_SIMPLEX, \
                    vision_config.FONT_SIZE, vision_config.POS_COLOR, \
                    vision_config.LINE_THICKNESS, cv2.LINE_AA)
        cv2.imshow(cid, frame)  # logging.info frame
        if cv2.waitKey(1) == 27:
            p.unsubscribe(CHANNEL)
            RUNNING = False
            break
    cap.release()
    cv2.destroyAllWindows()

_thread.start_new_thread(record, ())
for i in range(max_client):
    _thread.start_new_thread(client, (i,))

while RUNNING:
    time.sleep(1)