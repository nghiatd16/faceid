import redis
import cv2
import time
import vision_config
import uuid
import manage_data
import numpy as np

from Vision import Vision
from TrackingFace import MultiTracker

import logging

class FaceDetectionWorker:
    def __init__(self):
        self.RUNNING = True

        self.vision_object = Vision(mode='only_detect')
        self.multi_tracker = MultiTracker()

        self.sid = vision_config.SERVICE_TOKEN
        self.reg = vision_config.SERVICE_REGISTER_WORKER
        self.idworker = str(uuid.uuid4())
        logging.info('Worker:: {}'.format(self.idworker))
        self.rd = redis.StrictRedis(host=vision_config.REDIS_HOST, port=vision_config.REDIS_PORT)
        self.ps = self.rd.pubsub()

    def register_work_service(self):
        self.rd.lpush(self.reg, self.idworker)
        st = time.time()
        while self.rd.exists(self.idworker) == False:
            if time.time() - st > 10.:
                logging.info('Wait too long!!!')
                return
            time.sleep(0.1)
        msg = self.rd.get(self.idworker)
        if msg is None or msg == b'NONE':
            logging.info('Server is busy!')
            self.rd.delete(self.idworker)
            self.RUNNING = False
            return
        info = msg.split()
        self.IN = info[0]
        self.OUT = info[1]
        self.CHANNEL = info[2]
        self.ps.subscribe(self.CHANNEL)
        logging.info('Connected to server :: {} :: {} :: {}'.format(self.IN, self.OUT, self.CHANNEL))

    def run_service(self):
        logging.info('Detection service is running ...')
        while self.RUNNING:
            msg = self.rd.rpop(self.IN)
            if msg is not None:
                # shape_buffer = msg[:6]
                frame_buffer = msg
                # shape = np.frombuffer(shape_buffer, dtype=np.uint16)
                frame = np.frombuffer(frame_buffer, dtype=np.uint8)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                # frame = np.reshape(frame, (shape[0], shape[1], shape[2]))
                face = self.vision_object.face_detector(frame)
                face = np.array(face, dtype=np.uint16)
                self.rd.set(self.OUT, face.tobytes())
            time.sleep(0.001)

# if __name__ == '__main__':
#     worker = FaceDetectionWorker()
#     worker.register_work_service()
#     worker.run_service()