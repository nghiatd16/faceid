import redis
import pickle
import cv2
import vision_config
import manage_data
import numpy as np
import time
import threading
from Vision import Vision
from interact_database_v2 import Database
from object_DL import Camera, Person, Image, Location

import logging

class FaceIdentifyService:
    def __init__(self):
        self.key = vision_config.IDENTIFY_QUEUE
        self.rd = redis.StrictRedis(host='localhost', port=6379)
        self.rd.delete(self.key)
        try:
            database = Database(host=vision_config.DB_HOST, \
                                user=vision_config.DB_USER, \
                                passwd=vision_config.DB_PASSWD, \
                                database_name= vision_config.DB_NAME)
        except:
            raise ConnectionError('Cannot connect to database')
        self.vision_object = Vision(mode='only_identify', database=database)
        threading.Thread(target=self.refetch_db, daemon= True).start()
    def refetch_db(self):
        self.rd.set(vision_config.FLAG_REFETCH_DB, b"0")
        while True:
            flag_value = self.rd.get(vision_config.FLAG_REFETCH_DB)
            if flag_value is not None and flag_value == b"1":
                self.rd.set(vision_config.FLAG_REFETCH_DB, b"0")
                self.vision_object.update_new_database()
            time.sleep(0.5)
    def run(self):
        logging.info('Service identify is running ...')
        while True:
            faces = []
            IDs = []
            modes = []
            while True:
                msg = self.rd.rpop(self.key)
                if msg is None:
                    break
                len_ID = int(msg[0])
                ID = msg[1:1+len_ID].decode('utf-8')
                mode = msg[len_ID+1:len_ID+2].decode('utf-8')
                face = np.frombuffer(msg[2+len_ID:], dtype=np.uint8)
                face = cv2.imdecode(face, cv2.IMREAD_COLOR)
                if face.shape == (160, 160, 3):
                    IDs.append(ID)
                    modes.append(mode)
                    # print(mode)
                    faces.append(face)
                if len(faces) == vision_config.BATCH:
                    break
            if len(faces) > 0:
                embedding_list, predictions = self.vision_object.identify_person_by_img(faces)
                for i in range(len(IDs)):
                    if modes[i] == vision_config.IDEN_MOD:
                        msg = ""
                        if predictions[i] is not None:
                            msg = modes[i].encode("utf-8") + str(predictions[i].id).encode("utf-8")
                            # print(predictions[i].id)
                            self.rd.lpush(IDs[i], msg)
                        else:
                            msg = modes[i].encode("utf-8") + b"-1"
                            self.rd.lpush(IDs[i], msg)
                    else:
                        content = manage_data.convert_embedding_vector_to_bytes(embedding_list[i])
                        msg = modes[i].encode("utf-8") + content
                        self.rd.lpush(IDs[i], msg)
# if __name__ == '__main__':
#     fis = FaceIdentifyService()
#     fis.run()