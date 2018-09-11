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
    client = service_client_demo.ClientService(database, None)
    client.subscribe_server()
    multi_tracker = MultiTracker()
    client.record()
    timer = time.time()
    while client.is_running():
        frame = client.get_frame_from_queue()
        fps = int(1./(time.time() - timer + 0.000001))
        timer = time.time()
        client.request_detect_service(frame)
        ret, bboxes = client.get_response_detect_service()
        multi_tracker.update_bounding_box(bboxes, database)
        unidentified_tracker, identified_tracker = multi_tracker.cluster_trackers()
        trackers = multi_tracker.get_multitracker()
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
                if tracker.person is None and tracker.tried < vision_config.NUM_TRIED and time.time() - tracker.last_time_tried >= vision_config.DELAY_TRIED:
                    face = tracker.get_bbox_image(frame)
                    client.request_identify_service(face, tracker.id, mode = vision_config.IDEN_MOD)
                    tracker.last_time_tried = time.time()
                    tracker.tried += 1
        multi_tracker.show_info(frame)
        cv2.putText(frame, 'FPS ' + str(fps), \
                    vision_config.FPS_POS, cv2.FONT_HERSHEY_SIMPLEX, \
                    vision_config.FONT_SIZE, vision_config.POS_COLOR, \
                    vision_config.LINE_THICKNESS, cv2.LINE_AA)
        cv2.imshow(client.cid, frame)  # logging.info frame
        if cv2.waitKey(1) == 27:
            client.stop_service()
            break
    cv2.destroyAllWindows()