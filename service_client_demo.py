import redis
import cv2
import uuid
import time
import queue
import threading
import numpy as np

import vision_config
import manage_data
from TrackingFace import MultiTracker
from interact_database_v2 import Database
from object_DL import Person, Camera, Location, Image
import logging
#This import is only for serving demo TIS
import interface
class ClientService:
    class FLAG:
        def __init__(self):
            self.RUNNING = True
            self.SUBSCRIBED = False
    def __init__(self, database, camera):
        self.__FLAGS = ClientService.FLAG()
        self.database = database
        self.camera = camera
        self.capture = None
        self.subscribed_server_info = {}
        self.cid = str(uuid.uuid4())
        self.detect_service_line = redis.StrictRedis(host=vision_config.REDIS_HOST, port=vision_config.REDIS_PORT)
        self.identify_service_line = redis.StrictRedis(host=vision_config.REDIS_HOST, port=vision_config.REDIS_PORT)
        self.subscribe_object = self.detect_service_line.pubsub()
        if self.camera is not None:
            try:
                self.capture = cv2.VideoCapture(camera.rstpurl)
            except:
                self.capture = cv2.VideoCapture(camera.httpurl)
                pass
            logging.info("Video Capture device is camera ".format(camera))
        else:
            self.capture = cv2.VideoCapture(1)
            logging.info("Video Capture device is default webcam")
        self.capture.set(cv2.CAP_PROP_FPS, 60)
        width = self.capture.get(3)
        height = self.capture.get(4)
        vision_config.set_screen_size(width, height)
        self.frame_queue = queue.Queue(maxsize=2)

    def is_running(self):
        return self.__FLAGS.RUNNING

    def send_refetch_db_signal(self):
        self.detect_service_line.set(vision_config.FLAG_REFETCH_DB, b"1")
    def record(self):
        def __rec(self):
            while self.__FLAGS.RUNNING and self.capture.isOpened():
                try:
                    ret, frame = self.capture.read()
                    if ret and self.frame_queue.full():
                        self.frame_queue.get(timeout = 1)
                    w, h, channel = frame.shape
#                     frame = cv2.resize(frame, (int(frame.shape[1]/vision_config.INPUT_SCALE), int(frame.shape[0]/vision_config.INPUT_SCALE)))
                    self.frame_queue.put(np.copy(frame), timeout = 1)
                except:
                    pass
                # cv2.imshow("tmp", frame)
                # cv2.waitKey(1)
        threading.Thread(target=__rec, args=(self,), daemon=True).start()
    
    def subscribe_server(self):
        if self.__FLAGS.SUBSCRIBED:
            IN = self.subscribed_server_info["IN"]
            OUT = self.subscribed_server_info["OUT"]
            CHANNEL = self.subscribed_server_info["CHANNEL"]
            raise Exception("Client Service is subscribed to server :: {}  :: {} :: {}".format(IN, OUT, CHANNEL))
            pass
        cid = self.cid
        logging.info('Client {}'.format(cid))
        self.detect_service_line.lpush(vision_config.SERVICE_REGISTER_CLIENT, cid)
        st = time.time()
        while self.detect_service_line.exists(cid) == False:
            if time.time() - st > 10.:
                logging.exception('Wait too long!!!')
                RUNNING = False
                return
            time.sleep(0.1)
        msg = self.detect_service_line.get(cid)
        if msg is None or msg == b'NONE':
            logging.info('Server is busy!')
            self.detect_service_line.delete(cid)
            return
        info = msg.split()
        IN = info[0]
        OUT = info[1]
        CHANNEL = info[2]
        self.subscribe_object.subscribe(CHANNEL)
        logging.info('Connected to server :: {} :: {} :: {}'.format(IN, OUT, CHANNEL))
        self.subscribed_server_info["IN"] = IN
        self.subscribed_server_info["OUT"] = OUT
        self.subscribed_server_info["CHANNEL"] = CHANNEL
        self.__FLAGS.SUBSCRIBED = True
    
    def stop_service(self):
        self.subscribe_object.unsubscribe(self.subscribed_server_info["CHANNEL"])
        self.__FLAGS.RUNNING = False

    def request_detect_service(self, frame):
        IN = self.subscribed_server_info["IN"]
        dt_frame = cv2.resize(frame, (int(frame.shape[1]/vision_config.DETECT_SCALE), int(frame.shape[0]/vision_config.DETECT_SCALE)))
        ret, jpeg = cv2.imencode(".jpg", dt_frame)
        bytebuf = jpeg.tobytes()
        self.detect_service_line.ltrim(IN, 0, 0)
        self.detect_service_line.lpush(IN, bytebuf)

    def get_response_detect_service(self, upscale=1, real_time = False):
        OUT = self.subscribed_server_info["OUT"]
        while not self.detect_service_line.exists(OUT):
            time.sleep(0.001)
            continue
        bboxes = np.frombuffer(self.detect_service_line.get(OUT), dtype=np.uint16)
        if not real_time:
            self.detect_service_line.delete(OUT)
        ret = False
        if len(bboxes) > 0:
            bboxes = np.reshape(bboxes, (-1, 4))
            bboxes = bboxes * vision_config.DETECT_SCALE
            # bboxes = np.matmul(bboxes, vision_config.DETECT_SCALE)
            ret = True
        if vision_config.BIGGEST_FACE == False:
            return (ret, bboxes)
        max_sq = -1
        res = None
        for bbox in bboxes:
            x, y, w, h = bbox
            x = int(x*upscale)
            y = int(y*upscale)
            w = int(w*upscale)
            h = int(h*upscale)
            left_bound = int(vision_config.SCREEN_SIZE['width']/2 - vision_config.SCREEN_SIZE['height']/2)
            right_bound = int(vision_config.SCREEN_SIZE['width']/2 + vision_config.SCREEN_SIZE['height']/2)
            if max(w,h)**2 > max_sq and max(w,h) >= 160 and left_bound <= x and x+w <= right_bound:
                res = bbox
                max_sq = max(w,h)**2
        if res is None:
            return (False, [])
        return (True, [res])
    
    def request_identify_service(self, face, tracker_id, mode, mode_push = "lpush"):
        if mode != vision_config.ENCODE_MOD and mode != vision_config.IDEN_MOD:
            logging.error("Doesn't support mode {}".format(mode))
            return
        face = np.squeeze(face)
        if face.shape != (160, 160, 3):
            logging.error("Face Image must have shape (160, 160, 3), got {}".format(face.shape))
            return
        ret, jpeg = cv2.imencode(".jpg", face)
        msg = np.array([len(tracker_id)], dtype=np.uint8).tobytes() + str.encode(tracker_id) + str.encode(mode) + jpeg.tobytes()
        if mode_push == "lpush":
            self.identify_service_line.lpush(vision_config.IDENTIFY_QUEUE, msg)
        else:
            self.identify_service_line.rpush(vision_config.IDENTIFY_QUEUE, msg)

    def get_response_identify_service(self, tracker_id, mode_pop = "rpop"):
        if mode_pop != "rpop" and mode_pop != "lpop":
            raise TypeError("Doesn't support mode_pop `{}`".format(mode_pop))
        if mode_pop == "rpop":
            msg = self.identify_service_line.rpop(tracker_id)
        if mode_pop == "lpop":
            msg = self.identify_service_line.lpop(tracker_id)
        ret = None
        if msg is not None:
            mode = msg[0:1]
            mode = mode.decode('utf-8')
            content = msg[1:]
            
            if mode == vision_config.ENCODE_MOD:
                ret = manage_data.convert_bytes_to_embedding_vector(content)
            else:
                predict_id = int(content)
                if predict_id != -1:
                    ret = self.database.getPersonById(predict_id)
            return (mode, ret)
        return (None, None)

    def request_embed_faces(self, faces):
        num_faces = len(faces)
        embed_lst = []
        id_req = str(uuid.uuid4())
        for face in faces:
            face = cv2.resize(face, (160, 160))
            self.request_identify_service(face, id_req, vision_config.ENCODE_MOD)
        receive = 0
        while receive < num_faces:
            mode, ret = self.get_response_identify_service(id_req)
            if mode == vision_config.ENCODE_MOD:
                embed_lst.append(ret)
                receive += 1
            time.sleep(0.1)
        return embed_lst
    def get_frame_from_queue(self):
        try:
            frame = self.frame_queue.get(timeout = 1)
        except:
            return None
        return frame
    def __sub_task_admin_reviewer(self, multi_tracker, database):
        #This function is only for serving demo TIS
        logging.info("Admin Reviewer is ready")
        while True:
            try:
                if interface.msg_admin_reviewer is not None:
                    if interface.msg_admin_reviewer.id == -1:
                        multi_tracker.get_multitracker().clear()
                        interface.msg_admin_reviewer = None
                        continue
                    tracker = multi_tracker.get_multitracker()[0]
                    tracker.judgement = interface.msg_admin_reviewer
                    tracker.person = interface.msg_admin_reviewer
                    interface.msg_admin_reviewer = None
                    image = tracker.image[-1]
                    b64_img = manage_data.convert_image_to_b64(image)
                    new_image = Image(None, tracker.person, Camera(id=1), vision_config.get_time(),b64_img, b64_img, None, False)
                    database.insertImage(new_image)
            except Exception as e:
                logging.info("{}".format(e))
                pass
            time.sleep(0.1)
    def admin_reviewer(self, multi_tracker, database):
        #This function is only for serving demo TIS
        if vision_config.BIGGEST_FACE == False:
            logging.exception("Admin Reviewer function only available on `BIGGEST_FACE` mode. Please setting vision_config")
            return
        threading.Thread(target=self.__sub_task_admin_reviewer, args=(multi_tracker, database,), daemon=True).start()
        
    @staticmethod
    def face_in_training_area(frame, bbox_faces, training_area):
        x, y, b_w, b_h = training_area
        ans_bbox_faces = []
        ans_img_faces = []
        for idx, bbox in enumerate(bbox_faces):
            x_, y_, w_, h_ = bbox
            if x_ >= x and y_ >= y and x + w_ <= b_w and y + h_ <= b_h:
                ans_bbox_faces.append((x_, y_, w_, h_))
                im = frame[max(y_,0):y_+h_, max(x_,0):x_+w_]
                ans_img_faces.append(im)
        return (ans_bbox_faces, ans_img_faces)   