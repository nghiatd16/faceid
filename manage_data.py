import pickle
import os
import vision_config
import numpy as np
import cv2
import time
import base64
import datetime
import logging

                    
def list_img_on_disk(disk_dir):
    if not os.path.isdir(disk_dir):
        raise Exception(disk_dir + ' is not exist')
    cwd = os.getcwd()
    os.chdir(disk_dir)
    list_img = {}
    list_thumb = {}
    for person in os.listdir():
        path = os.path.abspath(person)
        name = os.path.basename(path)
        get_thumb = False
        for file in os.listdir(path):
            base = (os.path.abspath(os.path.join(path, file)))
            if file.endswith(".jpg") or file.endswith(".png"):
                if not get_thumb:
                    list_thumb[person] = base
                    get_thumb = True
                if name not in list_img:
                    list_img[name] = [base]
                else:
                    list_img[name].append(base)
    os.chdir(cwd)
    return (list_img, list_thumb)

def find_max_index(disk_dir):
    return len(os.listdir(disk_dir))

def save_img(img_faces, name_online, dir_path=vision_config.RAW_IMAGES_DIR):
    path = os.path.abspath(dir_path)
    if not os.path.isdir(path):
        os.mkdir(path)
    person_path = os.path.join(path, name_online)
    if not os.path.isdir(person_path):
        os.mkdir(person_path)
    for im in img_faces:
        path = os.path.join(person_path, str(time.time()) + '.jpg')
        cv2.imwrite(path, im)
        logging.info('Write an image on:'.format(path))

def std_date_format(date):
    if date is None:
        return None
    date = date.replace("/", "-")
    date = date.replace(".", "-")
    return datetime.datetime.strptime(date, '%d-%m-%Y')

def convert_date_format(date):
    if date is None:
        return None
    return date.strftime('%d-%m-%Y')

def convert_image_to_b64(image):
    img_bytes = cv2.imencode('.jpg', image)[1].tostring()
    img_b64 = base64.b64encode(img_bytes)
    return img_b64
    
def convert_b64_to_image(b64_str, to_rgb = False):
    img_b64 = base64.b64decode(b64_str)
    image = cv2.imdecode(np.frombuffer(img_b64, dtype=np.uint8), cv2.IMREAD_COLOR)
    if to_rgb:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image
    
def convert_embedding_vector_to_bytes(embedding_vector):
    embedding_vector.astype(np.float32)
    return embedding_vector.tobytes()
    
def convert_bytes_to_embedding_vector(bytes):
    return np.frombuffer(bytes, dtype=np.float32)

def load_b64_img(avt_path):
    assert os.path.isfile(avt_path) == True
    img = cv2.imread(avt_path)
    img = cv2.resize(img, (200,200))
    return convert_image_to_b64(img)