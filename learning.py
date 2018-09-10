from Vision import Vision
import vision_config
import manage_data
import numpy as np
import cv2
import os
import time
from object_DL import Person, Image, Camera, Location
import logging
import manage_data


def offline_learning(img_dir):
    feature_db, thumb_db = {}, {}    
    try:
        database = manage_data.read_database_from_disk(vision_config.DATABASE_DIR, vision_config.DATABASE_NAME_LOAD)
        feature_db, thumb_db = database
    except:
        database = None
        pass
    images, thumbs = manage_data.list_img_on_disk(img_dir)
    if len(images) == 0:
        raise Warning('No image found! This is not an error, make sure that you give system a correct directory! \
                        All experiences learned are untouched!')
        return
    vision_object = Vision(mode='only_identify')
    img_list = {}
    now = vision_config.get_time()
    logging.info('Preprocessing...')
    for name in thumbs:
        im = cv2.imread(thumbs[name])
        im = cv2.resize(im, (50, 50))
        thumb_db[name] = im
    for person in images:
        logging.info(person)
        for i in range(len(images[person])):
            im = cv2.imread(images[person][i])
            im = cv2.resize(im, (Vision.SIZE_OF_INPUT_IMAGE, Vision.SIZE_OF_INPUT_IMAGE))
            if person not in img_list:
                img_list[person] = [im]
            else:
                img_list[person].append(im)
    now = vision_config.get_time()
    logging.info('Preprocessing done!')
    if len(img_list) > 0:
        st = time.time()
        logging.info('System is being trained...')
        for person in img_list:
            embedding_list = vision_object.encode_embeddings(img_list[person])
            embedding_list = np.mean(embedding_list, axis=0)
            embedding_list = np.array([embedding_list])
            if person in feature_db:
                old_feature = feature_db[person]
                old_feature = np.concatenate((old_feature, embedding_list))
                new_feature = np.mean(old_feature, axis=0)
                feature_db[person] = np.array([new_feature])
            else:
                feature_db[person] = embedding_list
        database = (feature_db, thumb_db)
        logging.info('Training completed in {} seconds'.format(time.time() - st))
        manage_data.save_database_into_disk(database, vision_config.DATABASE_DIR, vision_config.DATABASE_NAME_SAVE)
        logging.info('Training completed!')

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

def online_learning(bbox_faces, img_faces, infor_pack, vision_object, multiTracker, database):
    if len(img_faces) == 0:
        return
    name, age, gender, idCode, idCam = infor_pack
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
    from interact_database_DL import Database
    database.insertValuesIntoPerson(new_person)
    database.refetch_table('person')
    person = database.selectFromPerson(new_person)[0]
    time = vision_config.get_time()
    cam = Camera(id = idCam)
    new_image = Image(None, person, cam, time, b64Img, b64Face, embed_vector, False)
    logging.info("New Image new_image.idPerson = {}".format(new_image.person))
    database.insertValuesIntoImage(new_image)
    # database.refetch_table('image')
    # feature_db, thumb_db = {}, {}
    # if database is not None:
    #     feature_db, thumb_db = database
    # thumb_db[name] = new_thumb
    # if name in feature_db:
    #     logging.info('{} has been already known. Transfer learning!'.format(name))
    #     old_feature = feature_db[name]
    #     logging.info(old_feature.shape)
    #     logging.info(embedding_list.shape)
    #     old_feature = np.concatenate((old_feature, embedding_list))
    #     new_feature = np.mean(old_feature, axis=0)
    #     feature_db[name] = np.array([new_feature])
    # else:
    #     feature_db[name] = embedding_list
        
    # database = (feature_db, thumb_db)
    vision_object.update_new_database(database)
    multiTracker.remove_tracker(bbox_faces)
    # return database