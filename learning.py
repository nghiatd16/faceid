from Vision import Vision
import vision_config
import manage_data
import numpy as np
import cv2
import os
import time
from object_DL import Person, Image, Camera, Location
from interact_database_v2 import Database
import logging
import manage_data


# def offline_learning(img_dir):
    

def add_data(img_faces):
    new_img_faces = []
    for i in range(len(img_faces)):
        img_faces.append(cv2.resize(img_faces[i], (120,120)))
    for i in range(len(img_faces)):
        img_faces.append(cv2.flip(img_faces[i], 1))
    for i in range(len(img_faces)):
        im = cv2.resize(img_faces[i], (Vision.SIZE_OF_INPUT_IMAGE, Vision.SIZE_OF_INPUT_IMAGE))
        new_img_faces.append(im)
    return new_img_faces

def online_learning(bbox_faces, img_faces, info_pack, vision_object, multiTracker, database):
    if len(img_faces) == 0:
        return
    name, age, gender, idCode, idCam = info_pack
    manage_data.save_img(img_faces, name)
    # new_thumb = cv2.resize(img_faces[0], (50,50))
    
    img_faces = add_data(img_faces)
    embedding_list = vision_object.encode_embeddings(img_faces)
    embedding_list = np.mean(embedding_list, axis=0)
    embed_vector = np.array(embedding_list)
    embedding_list = np.array([embedding_list])
    embed_vector = manage_data.convert_embedding_vector_to_bytes(embed_vector)
    b64Face = manage_data.convert_image_to_b64(img_faces[0])
    b64Img = manage_data.convert_image_to_b64(img_faces[1])

    new_person = Person(None, name, age, gender, idCode, embed_vector, b64Face,  b64Img)
    new_person = database.insertPerson(new_person)
    database.refetch_table('person')
    # person = database.getPer(new_person)[0]
    time_cap = vision_config.get_time()
    cam = Camera(id = idCam)
    new_image = Image(None, new_person, cam, time_cap, b64Img, b64Face, embed_vector, False)
    database.insertImage(new_image)
    vision_object.update_new_database()
    multiTracker.remove_tracker(bbox_faces)

def online_learning_service(bbox_faces, img_faces, client, info_pack, multiTracker, database):
    if len(img_faces) == 0:
        return
    msg, name, age, gender, idCode, idCam, embedding_list = info_pack
    # manage_data.save_img(img_faces, name)
    # new_thumb = cv2.resize(img_faces[0], (50,50))
    
    embed_vector = np.mean(embedding_list, axis=0)
    embed_vector = np.array(embed_vector)
    learning_person = None
    b64Face = manage_data.convert_image_to_b64(img_faces[0])
    b64Img = manage_data.convert_image_to_b64(img_faces[1])
    if msg == vision_config.NEW_LEARNING_MSG:
        embed_vector = manage_data.convert_embedding_vector_to_bytes(embed_vector)
        learning_person = Person(None, name, age, gender, idCode, embed_vector, b64Face,  b64Img)
        learning_person = database.insertPerson(learning_person)
    elif msg == vision_config.TRANSFER_LEARNING_MSG:
        learning_person = database.getPersonByIdCode(idCode)
        embedding_known = manage_data.convert_bytes_to_embedding_vector(learning_person.embedding)
        embedding_list = [embedding_known]
        embedding_list.append(embed_vector)
        embedding_list = np.array(embedding_list)
        embed_vector = np.mean(embedding_list, axis=0)
        print(embed_vector.shape)
        embed_vector = manage_data.convert_embedding_vector_to_bytes(embed_vector)
        database.updatePerson(Person(embedding=embed_vector), learning_person)
        learning_person = database.getPersonByIdCode(idCode)
    time_cap = vision_config.get_time()
    cam = Camera(id = idCam)
    new_image = Image(None, learning_person, cam, time_cap, b64Img, b64Face, embed_vector, True)
    database.insertImage(new_image)
    client.send_refetch_db_signal()
    time.sleep(0.5)
    # vision_object.update_new_database(database)
    multiTracker.remove_tracker(bbox_faces)