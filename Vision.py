import tensorflow as tf
import vision_config
import manage_data
import align.detect_face as df
import cv2
import os
import time
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from external_lib import facenet
from interact_database_v2 import Database
from object_DL import Person, Image, Camera, Location
from tensorflow.contrib import predictor
import logging
                    
class Vision:
    __detect_face_minsize = 100
    __detect_face_threshold = [ 0.89, 0.89, 0.9 ]
    __detect_face_factor = 0.709
    SIZE_OF_INPUT_IMAGE = 160

    def __init__(self, database = None, mode = 'both'):
        self.mode = mode
        if mode != 'both' and mode != 'only_detect' and mode != 'only_identify':
            raise TypeError("Doesn't support mode " + mode)
        if mode != 'only_detect' and database is None:
            raise TypeError("You have to pass database with mode '{}'".format(mode))
        logging.info("An vision object has been created with mode `{}`".format(mode))
        if mode != 'only_detect':
            #gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
            config = tf.ConfigProto(); config.gpu_options.allow_growth = True
            self.__embedding_encoder = predictor.from_saved_model("exported_model", config=config)
            self.__database_empty = True
            self.__classifier = KNeighborsClassifier(n_neighbors=5, algorithm='ball_tree', metric=facenet.distance)
        if mode != 'only_identify':
            self.__pnet, self.__rnet, self.__onet = self.load_detect_face_model(device= vision_config.DETECT_DEVICE)
        if mode != 'only_detect':
            self.__database = database
            self.__person, self.__feature, self.__label = database.extract_features_labels()
            if len(self.__feature) > 0:
                self.__database_empty = False
                self.__classifier.fit(self.__feature, self.__label)
    
    def get_working_mode(self):
        return self.mode
    
    def update_new_database(self):
        if self.mode == 'only_detect':
            raise Exception("vision_object is on mode only_detect, doesn't support update database")
        before = len(self.__label)
        self.__person, self.__feature, self.__label = self.__database.extract_features_labels()
        self.__database_empty = False
        logging.info("Refetch database succesfull. Before-After refetch {} - {} person(s)".format(before, len(self.__label)))
        self.__classifier.fit(self.__feature, self.__label)

    @staticmethod
    def load_detect_face_model(device = 'auto'):
        with tf.Graph().as_default():
            if 'cpu' in device:
                config = tf.ConfigProto(device_count = {'GPU': 0})
                sess = tf.Session(config=config)
            else:
                #gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
                config = tf.ConfigProto(); config.gpu_options.allow_growth = True
                sess = tf.Session(config= config)
            with sess.as_default():
                pnet, rnet, onet = df.create_mtcnn(sess, None)
        return (pnet, rnet, onet)

    @staticmethod
    def align_faces(bbox_faces, full_coordinate):
        res = []
        for face in bbox_faces:
            x,y,x1,y1 = face
            if not full_coordinate:
                x, y, w, h = face
                x1 = x + w
                y1 = y + h
            size_img = max(x1-x, y1-y)
            center_x = int((x1+x)/2)
            x = int(center_x - size_img/2)
            center_y = int((y1+y)/2)
            y = int(center_y - int(size_img/2))
            if size_img > 0 and x >= 0 and y >= 0:
                res.append((x, y, size_img, size_img))
        return res

    def face_detector(self, frame):
        if self.mode == 'only_identify':
            raise Exception('vision_object is on mode only_identify, cannot detect face')
        bboxes, _ = df.detect_face(frame, self.__detect_face_minsize,\
                                   self.__pnet, self.__rnet, self.__onet, \
                                   self.__detect_face_threshold, self.__detect_face_factor)
        faces = []
        for bbox in bboxes:
            x1 = int(bbox[2])
            y1 = int(bbox[3])
            x = int(bbox[0])
            y = int(bbox[1])
            if (x1-x) > 0 and (y1-y) > 0 and x >= 0 and y >= 0:
                faces.append((x, y, x1-x, y1-y))
        return faces
    
    def list_face_detector(self, list_frame):
        if self.mode == 'only_identify':
            raise Exception('vision_object is on mode only_identify, cannot detect face')
        list_dt_frame = []
        for frame in list_frame:
            list_dt_frame.append(dt_frame)
        rets = df.bulk_detect_face(list_dt_frame, 1/5,\
                                   self.__pnet, self.__rnet, self.__onet, \
                                   self.__detect_face_threshold, self.__detect_face_factor)
        list_faces = []
        for ret in rets:
            if ret is None:
                list_faces.append([])
                continue
            bboxes, _ = ret
            faces = []
            for bbox in bboxes:
                x1 = int(bbox[2])
                y1 = int(bbox[3])
                x = int(bbox[0])
                y = int(bbox[1])
                if (x1-x) > 0 and (y1-y) > 0:
                    faces.append((x, y, x1, y1))
            faces = Vision.align_faces(faces, full_coordinate= True)
            list_faces.append(faces)
        return list_faces

    
    def encode_embeddings(self, img_list):
        if self.mode == 'only_detect':
            raise Exception('vision_object is on mode only_detect, cannot encode faces to embedding vectors')
        images = facenet.load_images(img_list, Vision.SIZE_OF_INPUT_IMAGE)
        feed_dict = {"images": images, "phase": False}
        emb_array = self.__embedding_encoder(feed_dict)["embeddings"]
        return emb_array


    def identify_person_by_tracker(self, frame, unidentified_trackers):
        if self.mode == 'only_detect':
            raise Exception('vision_object is on mode only_detect, cannot identify person')
        prediction = []
        img_faces = []
        for tracker in unidentified_trackers:
            x, y, w, h = tracker.bounding_box
            im = frame[max(0, y):y+h, max(0, x):x+w]
            im = cv2.resize(im, (self.SIZE_OF_INPUT_IMAGE, self.SIZE_OF_INPUT_IMAGE))
            img_faces.append(im)
            tracker.tried += 1
            tracker.receive += 1
        if self.__database_empty:
            prediction = [None] * len(img_faces)
            return (img_faces, prediction)
        if len(img_faces) > 0:
            embedding_list = self.encode_embeddings(img_faces)
            distances, preds = self.__classifier.kneighbors(embedding_list, n_neighbors=1, return_distance=True)
            distances = np.squeeze(distances)
            preds = np.squeeze(preds)
            if distances.shape == ():
                if distances > vision_config.IDENTIFICATION_THRESH_HOLD:
                    prediction.append(None)
                else:
                    prediction.append(self.__person[preds])
                predict_text = ''
                if prediction[-1] != None:
                    predict_text = str(prediction[-1].id) + '-' + str(prediction[-1].name)
                else:
                    predict_text = 'None'
                if vision_config.SHOW_LOG_PREDICTION:
                    logging.info('Bounding box: {}; prediction: {}; verdict: {}; distance: {}'.format(unidentified_trackers[0].bounding_box, 
                                                                                                    predict_text, 
                                                                                                    self.__person[preds].name, 
                                                                                                    distances))
            else:
                for i in range(len(distances)):
                    if distances[i] > vision_config.IDENTIFICATION_THRESH_HOLD:
                        prediction.append(None)
                    else: 
                        prediction.append(self.__person[preds[i]])

                    predict_text = ''
                    if prediction[-1] != None:
                        predict_text = str(prediction[-1].id) + '-' + str(prediction[-1].name)
                    else:
                        predict_text = 'None'
                    if vision_config.SHOW_LOG_PREDICTION:
                        logging.info('Bounding box: {}; prediction: {}; verdict: {}; distance: {}'.format(unidentified_trackers[i].bounding_box, 
                                                                                                        predict_text, 
                                                                                                        self.__person[preds].name, 
                                                                                                        distances[i]))
        return (img_faces, prediction)

    def identify_person_by_img(self, img_faces, resize=False):
        if self.mode == 'only_detect':
            raise Exception('vision_object is on mode only_detect, cannot identify person')
        prediction = []
        embedding_list = []
        if resize:
            new_img_faces = []
            for im in img_faces:
                im = cv2.resize(im, (self.SIZE_OF_INPUT_IMAGE, self.SIZE_OF_INPUT_IMAGE))
                new_img_faces.append(im)
            img_faces = new_img_faces

        if self.__database_empty:
            prediction = [None] * len(img_faces)
            return (img_faces, prediction)
        if len(img_faces) > 0:
            embedding_list = self.encode_embeddings(img_faces)
            distances, preds = self.__classifier.kneighbors(embedding_list, n_neighbors=1, return_distance=True)
            distances = np.squeeze(distances)
            preds = np.squeeze(preds)
            if distances.shape == ():
                if distances > vision_config.IDENTIFICATION_THRESH_HOLD:
                    prediction.append(None)
                else:
                    prediction.append(self.__person[preds])
                predict_text = ''
                if prediction[-1] != None:
                    predict_text = str(prediction[-1].id) + '-' + str(prediction[-1].name)
                else:
                    predict_text = 'None'
                if vision_config.SHOW_LOG_PREDICTION:
                    logging.info('prediction: {}; verdict: {}; distance: {}'.format(predict_text, 
                                                                                    self.__person[preds].name, 
                                                                                    distances))
            else:
                for i in range(len(distances)):
                    if distances[i] > vision_config.IDENTIFICATION_THRESH_HOLD:
                        prediction.append(None)
                    else: 
                        prediction.append(self.__person[preds[i]])
                    predict_text = ''
                    if prediction[-1] != None:
                        predict_text = str(prediction[-1].id) + '-' + str(prediction[-1].name)
                    else:
                        predict_text = 'None'
                    if vision_config.SHOW_LOG_PREDICTION:
                        logging.info('prediction: {}; verdict: {}; distance: {}'.format(predict_text, 
                                                                                        self.__person[preds].name, 
                                                                                        distances[i]))
        return (embedding_list, prediction)

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