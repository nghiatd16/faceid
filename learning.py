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
def offline_learning(dataset_path):
    def extract_info_text(path):
        info = open(path, "r")
        name, birthday, gender, idcode, country = info.readlines()
        name = name[:-1]
        birthday = manage_data.std_date_format(birthday[:-1])
        gender = gender[:-1]
        idcode = idcode[:-1]
        info.close()
        return (name, birthday, gender, idcode, country)
    database = Database(vision_config.DB_HOST, vision_config.DB_USER, vision_config.DB_PASSWD, vision_config.DB_NAME)
    vision_object = Vision(database, mode="only_identify")
    cwd = os.getcwd()
    os.chdir(dataset_path)
    error_counter = 0
    total_person = len(os.listdir())
    st = time.time()
    for folder in os.listdir():
        logging.info("Processing `{}`".format(os.path.abspath(folder)))
        try:
            person_folder = os.path.abspath(folder)
            list_img = []
            for file in os.listdir(person_folder):
                file = os.path.join(person_folder, os.path.basename(file))
                if (file.endswith(".jpg") or file.endswith(".png")) and os.path.basename(file) != "__avatar__.jpg":
                    img = cv2.imread(file)
                    try:
                        img = cv2.resize(img, (Vision.SIZE_OF_INPUT_IMAGE, Vision.SIZE_OF_INPUT_IMAGE))
                    except Exception as e:
                        logging.info("{} - {}".format(file, img.shape))
                        logging.error(e)
                        error_counter += 1
                        pass
                    list_img.append(img)
                    print("Add an image : {}".format(os.path.abspath(file)))
            embedding_list = vision_object.encode_embeddings(list_img)
            embedding_vector = np.mean(embedding_list, axis=0)
            name, birthday, gender, idcode, country = extract_info_text(os.path.join(folder, "__info__.txt"))
            check_person = database.getPersonByIdCode(idcode)
            if check_person is not None:
                logging.info("person {} is known. Proceed Transfer Learning!".format(check_person))
                embedding_known = manage_data.convert_bytes_to_embedding_vector(check_person.embedding)
                embedding_list = [embedding_known]
                embedding_list.append(embedding_vector)
                embedding_list = np.array(embedding_list)
                embedding_vector = np.mean(embedding_list, axis=0)
                embedding_vector = manage_data.convert_embedding_vector_to_bytes(embedding_vector)
                database.updatePerson(Person(embedding=embedding_vector), check_person)
                continue
            avatar_path = os.path.join(folder, "__avatar__.jpg")
            avatar = cv2.imread(avatar_path)
            avatar = cv2.resize(avatar, (200, 200))
            b64_img = manage_data.convert_image_to_b64(avatar)
            face_path = os.path.join(folder, "__face__.jpg")
            face = cv2.imread(face_path)
            face = cv2.resize(face, (Vision.SIZE_OF_INPUT_IMAGE, Vision.SIZE_OF_INPUT_IMAGE))
            b64_face = manage_data.convert_image_to_b64(face)
            embedding_vector = manage_data.convert_embedding_vector_to_bytes(embedding_vector)
            person = Person(name= name, birthday= birthday, gender= gender, idcode= idcode, country=country, embedding= embedding_vector, b64face= b64_face, b64image= b64_img)
            logging.info("New Learning a person {}".format(person))
            database.insertPerson(person)
        except Exception as e:
            logging.error(e)
            error_counter += 1
            pass
    delta = time.time() - st
    elapsed = None
    if delta < 60:
        elapsed = time.strftime("%S seconds", time.gmtime(delta))
    elif delta < 3600:
        elapsed = time.strftime("%M minutes : %S seconds", time.gmtime(delta))
    else:
        elapsed = time.strftime("%H hours : %M minutes : %S seconds", time.gmtime(delta))
    logging.info("Training complete in: {}".format(elapsed))
    logging.info("Successfull training : {}/{} person".format(total_person - error_counter, total_person))
    os.chdir(cwd)
        
            

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
    name, birthday, gender, idCode, idCam = info_pack
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

    new_person = Person(None, name, birthday, gender, idCode, embed_vector, b64Face,  b64Img)
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
    msg, name, birthday, gender, idCode, country, description, b64Img, idCam, embedding_list = info_pack
    # manage_data.save_img(img_faces, name)
    # new_thumb = cv2.resize(img_faces[0], (50,50))
    
    embed_vector = np.mean(embedding_list, axis=0)
    embed_vector = np.array(embed_vector)
    learning_person = None
    img_faces = add_data(img_faces)
    b64Face = manage_data.convert_image_to_b64(img_faces[0])
    if b64Img is None:
        # min(1, len(img_faces)-1) : avoid bug when len(img_faces) == 1
        b64Img = manage_data.convert_image_to_b64(img_faces[min(1, len(img_faces)-1)])
    if msg == vision_config.NEW_LEARNING_MSG:
        embed_vector = manage_data.convert_embedding_vector_to_bytes(embed_vector)
        learning_person = Person(None, name, birthday, gender, idCode, country, description, embed_vector, b64Face,  b64Img)
        learning_person = database.insertPerson(learning_person)
    elif msg == vision_config.TRANSFER_LEARNING_MSG:
        learning_person = database.getPersonByIdCode(idCode)
        embedding_known = manage_data.convert_bytes_to_embedding_vector(learning_person.embedding)
        embedding_list = [embedding_known]
        embedding_list.append(embed_vector)
        embedding_list = np.array(embedding_list)
        embed_vector = np.mean(embedding_list, axis=0)
        embed_vector = manage_data.convert_embedding_vector_to_bytes(embed_vector)
        database.updatePerson(Person(embedding=embed_vector), learning_person)
        learning_person = database.getPersonByIdCode(idCode)
    time_cap = vision_config.get_time()
    cam = Camera(id = idCam)
    new_image = Image(None, learning_person, cam, time_cap, b64Img, b64Face, embed_vector, True)
    database.insertImage(new_image)
    client.send_refetch_db_signal()
    time.sleep(0.6)
    # vision_object.update_new_database(database)
    multiTracker.remove_tracker(bbox_faces)

if __name__ == "__main__":
    dataset_path = input("Dataset path: ")
    offline_learning(os.path.abspath(dataset_path))