import service_client_demo
import vision_config
import cv2
import time
import logging
import learning
import threading
import interface
from interact_database_v2 import Database
from object_DL import Camera
from TrackingFace import MultiTracker
from face_graphics import GraphicPyGame, GraphicOpenCV
from flask import Flask, Response
import queue
import pygame

RUNNING = True

SHOW_GRAPHICS = True
STREAM = vision_config.STREAM
HOST = '0.0.0.0'
PORT = 8080

FLAG_TRAINING = False
FLAG_TAKE_PHOTO = False
info_pack = ()
tim_elapsed = 0.4
time_take_photo = 2
bbox_list_online = []
img_list_online = []
timer = time.time()
train_timer = time.time()

def sub_task(database, client, graphics=None):
    global RUNNING, info_pack, SHOW_GRAPHICS, STREAM, FLAG_TAKE_PHOTO, FLAG_TRAINING, timer, train_timer, time_take_photo, tim_elapsed, bbox_list_online, img_list_online
    client.subscribe_server()
    multi_tracker = MultiTracker()
    client.record()
    train_area = vision_config.TRAINING_AREA
    if vision_config.ADMIN_REVIEWER:
        client.admin_reviewer(multi_tracker, database)
    while client.is_running():
        raw_frame = client.get_frame_from_queue()
        if raw_frame is None:
            time.sleep(0.001)
            continue
        frame = cv2.resize(raw_frame, (int(raw_frame.shape[1]/vision_config.INPUT_SCALE), int(raw_frame.shape[0]/vision_config.INPUT_SCALE)))
        img = frame.copy()
        fps = int(1./(time.time() - timer + 0.000001))
        timer = time.time()
        client.request_detect_service(frame)
        ret, bboxes = client.get_response_detect_service(upscale=vision_config.INPUT_SCALE, real_time=False)
        multi_tracker.update_bounding_box(bboxes, database)
        unidentified_tracker, identified_tracker = multi_tracker.cluster_trackers()
        trackers = multi_tracker.get_multitracker()
        if interface.STATUS == interface.STATUS_DONE and not FLAG_TRAINING:
            FLAG_TRAINING = True
            person = interface.result
            name = person.name
            birthday = person.birthday
            gender = person.gender
            idCode = person.idcode
            country = person.country
            description = person.description
            b64img = person.b64image
            idCam = 0
            if client.camera is not None:
                idCam = client.camera.id
            info_pack = (interface.msg_result, name, birthday, gender, idCode, country, description, b64img, idCam)
            interface.reset()
        if FLAG_TRAINING:
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
            if FLAG_TAKE_PHOTO:
                if time.time() - train_timer >= 0.1:
                    train_timer = time.time()
                    time_take_photo = max(0, time_take_photo-0.1)
                    time_take_photo = round(time_take_photo,1)
                    if train_timer - tim_elapsed >= 0.4 and time_take_photo > 0:
                        tim_elapsed = time.time()
                        training_bbox_faces, training_img_faces = service_client_demo.ClientService.face_in_training_area(img, bboxes, \
                                                                                                train_area)                                                                       
                        if len(training_bbox_faces) == 1:
                            bbox_list_online.append(training_bbox_faces[0])
                            img_list_online.append(training_img_faces[0])
                            logging.info('Take successfully')
                        else: logging.info('No face')
                    if time_take_photo == 0:
                        logging.info('Time_take_photo out')
                        FLAG_TAKE_PHOTO = False
                        if len(bbox_list_online) == 0:
                            info_pack = None
                            bbox_list_online.clear()
                            img_list_online.clear()
                            FLAG_TRAINING = False
                            name_interface = None
                            time_take_photo = 2
            if FLAG_TAKE_PHOTO == False and len(bbox_list_online) > 0:
                # learning.online_learning(bbox_list_online, img_list_online, \
                #                                     info_pack, vision_object, multi_tracker, database)
                embed_list = client.request_embed_faces(img_list_online)
                msg, name, birthday, gender, idCode, country, description, b64img, idCam = info_pack
                pass_pack = (msg, name, birthday, gender, idCode, country, description, b64img, idCam, embed_list)
                learning.online_learning_service(bbox_list_online, img_list_online, client,\
                                                pass_pack, multi_tracker, database)
                info_pack = None
                bbox_list_online.clear()
                img_list_online.clear()
                FLAG_TRAINING = False
                time_take_photo = 2
        for idx, tracker in enumerate(trackers):
            if tracker.person is None:
                mode, content = client.get_response_identify_service(tracker.id)
                if mode is not None:
                    if mode == vision_config.IDEN_MOD:
                        predicts = None
                        if content != -1:
                            predicts = content
                        # multi_tracker.update_identification([tracker], [predicts])
                        if tracker.judgement is not None:
                            predicts = tracker.judgement
                        tracker.update_identification(predicts, database)
        if len(unidentified_tracker) > 0:
            for tracker in unidentified_tracker:
                if tracker.person is None and tracker.tried < vision_config.NUM_TRIED and (time.time() - tracker.last_time_tried) >= vision_config.DELAY_TRIED:
                    face = tracker.get_bbox_image(raw_frame, up_scale=vision_config.INPUT_SCALE)
                    client.request_identify_service(face, tracker.id, mode = vision_config.IDEN_MOD)
                    tracker.add_image(face)
        if SHOW_GRAPHICS or STREAM:
            graphics.put_update(frame, multi_tracker)
            if not graphics.running:
                client.stop_service()
                break
        # multi_tracker.show_info(frame)
        # cv2.putText(frame, 'FPS ' + str(fps), \
        #             vision_config.FPS_POS, cv2.FONT_HERSHEY_SIMPLEX, \
        #             vision_config.FONT_SIZE, vision_config.POS_COLOR, \
        #             vision_config.LINE_THICKNESS, cv2.LINE_AA)
        # cv2.imshow(client.cid, frame) 
        # key = cv2.waitKey(1)
        # if key == 27:
        #     client.stop_service()
        #     break
        # if key == 32 and not FLAG_TRAINING:
        #     threading.Thread(target=interface.get_idCode, args=(database,)).start()
        #     # interface.get_idCode()
        #     continue
        # if key == 32 and FLAG_TRAINING:
        #     FLAG_TAKE_PHOTO = True

        # if SHOW_GRAPHICS:
        #     if graphics.key is not None:
        #         if graphics.key == pygame.K_SPACE and not FLAG_TRAINING and interface.STATUS == interface.STATUS_INACTIVE:
        #             threading.Thread(target=interface.get_idCode, args=(database,)).start()
        #             continue
        #         if graphics.key == pygame.K_SPACE and FLAG_TRAINING:
        #             FLAG_TAKE_PHOTO = True
        
        if SHOW_GRAPHICS or STREAM:
            if graphics.key is not None:
                if graphics.key == 32 and not FLAG_TRAINING and interface.STATUS == interface.STATUS_INACTIVE:
                    threading.Thread(target=interface.get_idCode, args=(database,), daemon=True).start()
                    continue
                if graphics.key == 32 and FLAG_TRAINING:
                    FLAG_TAKE_PHOTO = True
                if graphics.key == 27:
                    RUNNING = False
                    exit(0)
                # if graphics.key == ord('a') and interface.showing_admin_review == False:
                #     interface.showing_admin_review = True
                    threading.Thread(target=interface.identification_review, args=(database,), daemon=True).start()
                if graphics.key == ord('m') and not FLAG_TRAINING and interface.STATUS == interface.STATUS_INACTIVE:
                    threading.Thread(target=interface.auto_gen_info, args=(database,), daemon=True).start()
                    continue
                if graphics.key == ord('q') and FLAG_TRAINING:
                    info_pack = None
                    bbox_list_online.clear()
                    img_list_online.clear()
                    FLAG_TRAINING = False
                    FLAG_TAKE_PHOTO = False
                    interface.reset()
                    name_interface = None
                    time_take_photo = 2

    RUNNING = False
    cv2.destroyAllWindows()


app = Flask(__name__)
FRAME = None
q_FRAME = queue.Queue(maxsize=2)
FPS_FRAME = 24

def gen_frame():
    global FRAME, RUNNING
    while RUNNING:
        FRAME = q_FRAME.get()

def gen_client():
    global FRAME, FPS_FRAME, RUNNING
    while RUNNING:
        time.sleep(1./FPS_FRAME)
        if FRAME is None:
            continue
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + FRAME + b'\r\n\r\n')

@app.route('/video')
def video_feed():
    return Response(gen_client(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def start_web():
    global app, HOST, PORT
    threading.Thread(target=gen_frame, args=(), daemon=True).start()
    threading.Thread(target=app.run, args=(HOST, PORT, False), daemon=True).start()

def start(cam_id = None, port=8888):
    global STREAM, SHOW_GRAPHICS, PORT
    PORT = port
    database = Database(vision_config.DB_HOST,vision_config.DB_USER,vision_config.DB_PASSWD, vision_config.DB_NAME)
    cam = None
    if cam_id is not None:
        cam = database.getCameraById(int(cam_id))
    client = service_client_demo.ClientService(database, cam)
    if not SHOW_GRAPHICS and not STREAM:
        sub_task(database, client)
    else:
        if SHOW_GRAPHICS and not STREAM:
            graphics = GraphicOpenCV(display=True, queue=None)
        elif SHOW_GRAPHICS and STREAM:
            graphics = GraphicOpenCV(display=True, queue=q_FRAME)
            start_web()
        elif not SHOW_GRAPHICS and STREAM:
            graphics = GraphicOpenCV(display=False, queue=q_FRAME)
            start_web()
        threading.Thread(target=sub_task, args=(database, client, graphics,), daemon=True).start()
        graphics.run()
