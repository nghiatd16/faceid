import vision_config
import manage_data
import cv2
import time
import learning
import vision_config
from Vision import Vision
from TrackingFace import MultiTracker
import interface
import threading
import queue
import logging
from interact_database_v2 import Database
from object_DL import Person, Image, Camera, Location
                    
name_interface = None
q_frame = queue.Queue(maxsize=2)
q_faces = queue.Queue(maxsize=2)
q_identify = queue.Queue(maxsize=2)
RUNNING = True

flag_training_online = False
flag_take_photo = False

database = None
vision_object = None
multi_tracker = None

def read_camrea(url=0):
    global RUNNING
    vc = cv2.VideoCapture(url)
    width = vc.get(3)   # float
    height = vc.get(4)
    # logging.info(width, height)
    vision_config.set_screen_size(width, height)
    # logging.info(vision_config.SCREEN_SIZE)
    # logging.info(vision_config.TRAINING_AREA)
    while vc.isOpened() and RUNNING:
        ret , frame = vc.read()
        if ret:
            if vision_config.FLIP:
                frame = cv2.flip(frame, 1)
            if q_frame.full():
                q_frame.get()
            q_frame.put(frame)
    else: RUNNING = False

def detect_face():
    global vision_object, multi_tracker
    while RUNNING:
        frame = q_frame.get()
        faces = vision_object.face_detector(frame)
        if q_faces.full():
            q_faces.get()
        q_faces.put((frame, faces))

def identify():
    global vision_object, multi_tracker, database
    global flag_training_online, flag_take_photo, name_interface, RUNNING
    tim_elapsed = 0.4
    time_take_photo = 2
    bbox_list_online = []
    img_list_online = []
    infor_pack = None
    database_changed = False
    timer = time.time()
    bbox_faces = None
    while RUNNING:
        train_area = vision_config.TRAINING_AREA
        frame, bbox_faces = q_faces.get()
        try:
            multi_tracker.update_bounding_box(bbox_faces, database)
            unidentified_tracker, identified_tracker = multi_tracker.cluster_trackers()
            if len(unidentified_tracker) > 0:
                img_faces, predictions = vision_object.identify_person_by_tracker(frame, unidentified_tracker)
                multi_tracker.update_identification(unidentified_tracker, predictions, img_list=img_faces)
            multi_tracker.show_info(frame)
        except:
            continue
            pass
        if flag_training_online:
            if infor_pack is None:
                name = input('Name: ')
                age = int(input('Age: '))
                gender = input('Gender: ')
                idCode = input('Id Code: ')
                idCam = 1
                infor_pack = (name, age, gender, idCode, idCam)
            if time_take_photo > 0.2:
                cv2.rectangle(frame, (train_area[0], train_area[1]) , \
                                (train_area[2], train_area[3]), \
                                vision_config.NEG_COLOR, \
                                vision_config.LINE_THICKNESS+1)
                cv2.putText(frame, 'Time Remaining: ' + str(round(time_take_photo,1)) + 's', \
                            (train_area[0] + 10, train_area[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, \
                            vision_config.FONT_SIZE+0.1, vision_config.NEG_COLOR, \
                            vision_config.LINE_THICKNESS*2, cv2.LINE_AA)
            else:
                cv2.putText(frame, 'System is being trained .... ', \
                            (100, 100), cv2.FONT_HERSHEY_SIMPLEX, \
                            vision_config.FONT_SIZE*2, vision_config.NEG_COLOR, \
                            vision_config.LINE_THICKNESS*2, cv2.LINE_AA)
            if flag_take_photo:
                if time.time() - timer >= 0.1:
                    timer = time.time()
                    time_take_photo = max(0, time_take_photo-0.1)
                    time_take_photo = round(time_take_photo,1)
                    if timer - tim_elapsed >= 0.4 and time_take_photo > 0:
                        tim_elapsed = time.time()
                        training_bbox_faces, training_img_faces = Vision.face_in_training_area(frame, bbox_faces, \
                                                                                                train_area)                                                                       
                        if len(training_bbox_faces) == 1:
                            bbox_list_online.append(training_bbox_faces[0])
                            img_list_online.append(training_img_faces[0])
                            logging.info('Take successfully')
                        else: logging.info('No face')
                    if time_take_photo == 0:
                        logging.info('Time_take_photo out')
                        flag_take_photo = False
                        if len(bbox_list_online) == 0:
                            infor_pack = None
                            bbox_list_online.clear()
                            img_list_online.clear()
                            flag_training_online = False
                            name_interface = None
                            time_take_photo = 2
            if flag_take_photo == False and len(bbox_list_online) > 0:
                learning.online_learning(bbox_list_online, img_list_online, \
                                                    infor_pack, vision_object, multi_tracker, database)
                if vision_config.SAVE_DATABASE:
                    manage_data.save_database_into_disk(database, vision_config.DATABASE_DIR, vision_config.DATABASE_NAME_SAVE)
                infor_pack = None
                bbox_list_online.clear()
                img_list_online.clear()
                flag_training_online = False
                name_interface = None
                time_take_photo = 2
        if q_identify.full():
            q_identify.get()
        q_identify.put(frame)
def show():
    global flag_take_photo, flag_training_online, name_interface, RUNNING
    timer = time.time() - 0.1
    while RUNNING:
        # if not q_identify.empty():
        frame = q_identify.get()
        fps = int(round(1/(time.time() - timer + 0.001)))
        timer = time.time()
        cv2.putText(frame, 'FPS ' + str(fps), \
                    vision_config.FPS_POS, cv2.FONT_HERSHEY_SIMPLEX, \
                    vision_config.FONT_SIZE, vision_config.POS_COLOR, \
                    vision_config.LINE_THICKNESS, cv2.LINE_AA)
                
        cv2.imshow('Face ID', frame)
        # if (interface.STATUS == interface.STATUS_DONE):
        #     flag_training_online = True
        #     name_interface = interface.label
        #     tim_elapsed = time.time()
        #     interface.reset()
        key = cv2.waitKey(1)
        if key == 32 and not flag_training_online:
            flag_training_online = True
            continue
            # if (interface.STATUS == interface.STATUS_INACTIVE):
            #     threading.Thread(target=interface.layout_text, args=()).start()
        if key == 32 and flag_training_online:
            flag_take_photo = True
        if key == 27: # exit on ESC
            RUNNING = False
            # break
    # clean 
    cv2.destroyWindow("Face ID")

def run(url=None):
    global vision_object, multi_tracker, database
    try:
        database = Database(host=vision_config.DB_HOST, \
                            user=vision_config.DB_USER, \
                            passwd=vision_config.DB_PASSWD, \
                            database_name= vision_config.DB_NAME)
    except:
        raise ConnectionError('Cannot connect to database')
    vision_object = Vision(database)
    multi_tracker = MultiTracker()
    if url is not None:
        threading.Thread(target= read_camrea, args=(url, )).start()
    else:
        threading.Thread(target= read_camrea, args=()).start()
    threading.Thread(target= detect_face, args=()).start()
    threading.Thread(target= identify, args=()).start()
    threading.Thread(target= show, args=()).start()
    