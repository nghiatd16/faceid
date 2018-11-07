from Vision import Vision
import os
import time
import numpy as np
import cv2
import pickle
vi_ob = Vision(mode = 'only_detect')
dataset_path = input('Dataset path: ')
dataset_path = os.path.abspath(dataset_path)
os.chdir(dataset_path)
cwd = os.getcwd()
for file in os.listdir():
    file = os.path.abspath(file)
    
    if file.endswith('.jpg') or file.endswith('.JPG') or file.endswith('.png'):
        img = cv2.imread(file)
        print("Processing {}".format(file))
        faces = vi_ob.face_detector(img)
        for bbox in faces:
            x, y, w, h =bbox
            im = img[max(0, y):y+h, max(0, x):x+w]
            im = cv2.resize(im, (160, 160))
            out_path = 'output\\{}.jpg'.format(time.time())
            cv2.imwrite(out_path, im)
            print('An image wrote on: {}'.format(os.path.abspath(out_path)))