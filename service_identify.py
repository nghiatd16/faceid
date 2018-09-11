import redis
import pickle
import cv2
import vision_config
import manage_data
import numpy as np
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
                print(mode, type(mode))
                face = np.frombuffer(msg[2+len_ID:], dtype=np.uint8)
                if len(face) == 76800:
                    face = np.reshape(face, (160, 160, 3))
                    IDs.append(ID)
                    modes.append(mode)
                    faces.append(face)
                if len(faces) == vision_config.BATCH:
                    break
            if len(faces) > 0:
                embedding_list, predictions = self.vision_object.identify_person_by_img(faces)
                for i in range(len(IDs)):
                    if modes[i] == vision_config.IDEN_MOD:
                        if predictions[i] is not None:
                            self.rd.lpush(IDs[i], modes[i], predictions[i].id)
                        else:
                            self.rd.lpush(IDs[i], modes[i], -1)
                    else:
                        self.rd.lpush(IDs[i], modes[i], manage_data.convert_embedding_vector_to_bytes(embedding_list[i]))
# if __name__ == '__main__':
#     fis = FaceIdentifyService()
#     fis.run()