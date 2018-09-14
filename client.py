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
FLAG_TRAINING = False
FLAG_TAKE_PHOTO = False
info_pack = ()
tim_elapsed = 0.4
time_take_photo = 2
bbox_list_online = []
img_list_online = []
timer = time.time()
train_timer = time.time()
def start():
    global info_pack, FLAG_TAKE_PHOTO, FLAG_TRAINING, timer, train_timer, time_take_photo, tim_elapsed, bbox_list_online, img_list_online
    database = Database(vision_config.DB_HOST,vision_config.DB_USER,vision_config.DB_PASSWD, vision_config.DB_NAME)
    cam = database.getCameraById(1)
    client = service_client_demo.ClientService(database, None)
    client.subscribe_server()
    multi_tracker = MultiTracker()
    client.record()
    train_area = vision_config.TRAINING_AREA
    while client.is_running():
        frame = client.get_frame_from_queue()
        if frame is None:
            time.sleep(0.001)
            continue
        fps = int(1./(time.time() - timer + 0.000001))
        timer = time.time()
        client.request_detect_service(frame)
        ret, bboxes = client.get_response_detect_service(real_time=False)
        multi_tracker.update_bounding_box(bboxes, database)
        unidentified_tracker, identified_tracker = multi_tracker.cluster_trackers()
        trackers = multi_tracker.get_multitracker()
        if interface.STATUS == interface.STATUS_DONE and not FLAG_TRAINING:
            FLAG_TRAINING = True
            person = interface.result
            name = person.name
            age = person.age
            gender = person.gender
            idCode = person.idcode
            idCam = 1
            info_pack = (name, age, gender, idCode, idCam)
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
                        training_bbox_faces, training_img_faces = service_client_demo.ClientService.face_in_training_area(frame, bboxes, \
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
                            flag_training_online = False
                            name_interface = None
                            time_take_photo = 2
            if FLAG_TAKE_PHOTO == False and len(bbox_list_online) > 0:
                # learning.online_learning(bbox_list_online, img_list_online, \
                #                                     info_pack, vision_object, multi_tracker, database)
                embed_list = client.request_embed_faces(img_list_online)
                name, age, gender, idCode, idCam = info_pack
                pass_pack = (name, age, gender, idCode, idCam, embed_list)
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
                    tracker.receive += 1
                    if mode == vision_config.IDEN_MOD:
                        predicts = None
                        if content != -1:
                            predicts = content
                        multi_tracker.update_identification([tracker], [predicts])
        if len(unidentified_tracker) > 0:
            for tracker in unidentified_tracker:
                if tracker.person is None and tracker.tried < vision_config.NUM_TRIED and (time.time() - tracker.last_time_tried) >= vision_config.DELAY_TRIED:
                    face = tracker.get_bbox_image(frame)
                    client.request_identify_service(face, tracker.id, mode = vision_config.IDEN_MOD)
                    tracker.last_time_tried = time.time()
                    tracker.tried += 1
        multi_tracker.show_info(frame)
        cv2.putText(frame, 'FPS ' + str(fps), \
                    vision_config.FPS_POS, cv2.FONT_HERSHEY_SIMPLEX, \
                    vision_config.FONT_SIZE, vision_config.POS_COLOR, \
                    vision_config.LINE_THICKNESS, cv2.LINE_AA)
        cv2.imshow(client.cid, frame) 
        key = cv2.waitKey(1)
        if key == 27:
            client.stop_service()
            break
        if key == 32 and not FLAG_TRAINING:
            threading.Thread(target=interface.get_idCode, args=(database,)).start()
            # interface.get_idCode()
            continue
        if key == 32 and FLAG_TRAINING:
            FLAG_TAKE_PHOTO = True
    cv2.destroyAllWindows()