import service_client_demo
import vision_config
import cv2
import time
import logging
from interact_database_v2 import Database
from object_DL import Camera
from TrackingFace import MultiTracker
def start():
    database = Database(vision_config.DB_HOST,vision_config.DB_USER,vision_config.DB_PASSWD, vision_config.DB_NAME)
    # cam = Camera(id=1)
    cam = database.getCameraById(1)
    client = service_client_demo.ClientService(database, cam)
    client.subscribe_server()
    multi_tracker = MultiTracker()
    client.record()
    timer = time.time()
    while client.is_running():
        st = time.time()
        frame = client.get_frame_from_queue()
        if frame is None:
            time.sleep(0.001)
            continue
        print("get_frame_from_queue", time.time()-st)
        # st = time.time()
        fps = int(1./(time.time() - timer + 0.000001))
        timer = time.time()
        client.request_detect_service(frame)
        # print("request_detect_service", time.time()-st)
        # st = time.time()
        ret, bboxes = client.get_response_detect_service(real_time=False)
        # print("get_response_detect_service", time.time() - st)
        # st = time.time()
        multi_tracker.update_bounding_box(bboxes, database)
        # print("update_bounding_box", time.time()-st)
        # st = time.time()
        unidentified_tracker, identified_tracker = multi_tracker.cluster_trackers()
        # print("cluster_trackers", time.time() - st)
        trackers = multi_tracker.get_multitracker()
        for idx, tracker in enumerate(trackers):
            if tracker.person is None:
                # st = time.time()
                mode, content = client.get_response_identify_service(tracker.id)
                # print("get_response_identify_service", time.time() - st)
                if mode is not None:
                    tracker.receive += 1
                    if mode == vision_config.IDEN_MOD:
                        predicts = None
                        if content != -1:
                            predicts = content
                        multi_tracker.update_identification([tracker], [predicts])
        if len(unidentified_tracker) > 0:
            for tracker in unidentified_tracker:
                if tracker.person is None and tracker.tried < vision_config.NUM_TRIED and time.time() - tracker.last_time_tried >= vision_config.DELAY_TRIED:
                    # st = time.time()
                    face = tracker.get_bbox_image(frame)
                    # print("get_bbox_image", time.time() - st)
                    # st = time.time()
                    client.request_identify_service(face, tracker.id, mode = vision_config.IDEN_MOD)
                    # print("request_identify_service", time.time()-st)
                    tracker.last_time_tried = time.time()
                    tracker.tried += 1
        multi_tracker.show_info(frame)
        cv2.putText(frame, 'FPS ' + str(fps), \
                    vision_config.FPS_POS, cv2.FONT_HERSHEY_SIMPLEX, \
                    vision_config.FONT_SIZE, vision_config.POS_COLOR, \
                    vision_config.LINE_THICKNESS, cv2.LINE_AA)
        cv2.imshow(client.cid, frame)  # logging.info frame
        # print("--------------------------------------------")
        if cv2.waitKey(1) == 27:
            client.stop_service()
            break
    cv2.destroyAllWindows()