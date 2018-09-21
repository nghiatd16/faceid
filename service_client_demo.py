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
        self.detect_service_line = redis.StrictRedis(host='localhost', port=6379)
        self.identify_service_line = redis.StrictRedis(host='localhost', port=6379)
        self.subscribe_object = self.detect_service_line.pubsub()
        if self.camera is not None:
            try:
                self.capture = cv2.VideoCapture(camera.httpurl)
            except:
                self.capture = cv2.VideoCapture(camera.rstpurl)
                pass
            logging.info("Video Capture device is camera [ id: {} - name: {} - httpurl: {} - rstpurl: {} - location: {}]".format(\
                                                    camera.id, camera.cameraname, camera.httpurl, camera.rstpurl, camera.location))
        else:
            self.capture = cv2.VideoCapture(0)
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
                    self.frame_queue.put(np.copy(frame), timeout = 1)
                except:
                    pass
                # cv2.imshow("tmp", frame)
                # cv2.waitKey(1)
        threading.Thread(target=__rec, args=(self,)).start()
    
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
        ret, jpeg = cv2.imencode(".jpg", frame)
        bytebuf = jpeg.tobytes()
        self.detect_service_line.ltrim(IN, 0, 0)
        self.detect_service_line.lpush(IN, bytebuf)

    def get_response_detect_service(self, real_time = False):
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
            ret = True
        return (ret, bboxes)
    
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