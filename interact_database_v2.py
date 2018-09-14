import mysql.connector
import object_DL
import manage_data
import logging

class Database:
    def __init__(self, host, user, passwd, database_name):
        self.CONNECTED = False
        self.__host = host
        self.__user = user
        self.__pass = passwd
        self.__dbname = database_name
        try:
            self.__mydb = mysql.connector.connect(host=self.__host, user=self.__user, passwd=self.__pass, database=self.__dbname)
            self.__mydb.autocommit = True
            self.__mycursor = self.__mydb.cursor(dictionary=True)
            self.CONNECTED = True
            logging.info("Connect to database sucessfull")
        except mysql.connector.Error as err:
            logging.exception("ERR in __init__: {}".format(err))

    def __standardize_for_query(self, arr):
        cl = ""
        rf = ""
        for i in range(len(arr)):
            cl += arr[i]
            rf += "%s"
            if i != len(arr)-1:
                cl += ", "
                rf += ", "
        return cl, rf

    def __standardize_for_query_set(self, arr):
        cl = ""
        for i in range(len(arr)):
            cl += (arr[i] + " = %s")
            if i != len(arr)-1:
                cl += ", "
        return cl

    def countColumnsTable(self, table):
        if self.CONNECTED:
            sql = "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}'".format(table)
            try:
                self.__mycursor.execute(sql)
                return self.__mycursor.fetchone()[0]
            except mysql.connector.Error as err:
                logging.exception("ERR in countColumnsTable: {}".format(err))

    def infoColumnsSchema(self, table, arr_type=["column_name"]):
        if self.CONNECTED:
            type_ = ""
            for i in range(len(arr_type)):
                type_ += arr_type[i]
                if i != len(arr_type)-1:
                    type_ += ", "
            sql = "SELECT {} FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{}'".format(type_, table)
            try:
                self.__mycursor.execute(sql)
                return self.__mycursor.fetchall()
            except mysql.connector.Error as err:
                logging.exception("ERR in infoColumnsTable: {}".format(err))

    def infoTableSchema(self, table, arr_type=["table_name"]):
        if self.CONNECTED:
            type_ = ""
            for i in range(len(arr_type)):
                type_ += arr_type[i]
                if i != len(arr_type)-1:
                    type_ += ", "
            sql = "SELECT {} FROM INFORMATION_SCHEMA.TABLES WHERE table_name = '{}'".format(type_, table)
            try:
                self.__mycursor.execute(sql)
                return self.__mycursor.fetchall()
            except mysql.connector.Error as err:
                logging.exception("ERR in infoColumnsTable: {}".format(err))

## Insert database:
    def insertPerson(self, person):
        """ Insert new person into database
        @params person: Person
        @return person: Person with insert id
        """
        if self.CONNECTED:
            sql = "INSERT INTO person ({}) VALUES ({})".format(person.get_name_columns(), person.get_refer())
            val = person.get_value()
            try:
                self.__mycursor.execute(sql, val)
                self.__mydb.commit()
                person.id = self.__mycursor.lastrowid
                return person
            except mysql.connector.Error as err:
                logging.exception("ERR in insertPerson: {}".format(err))
                return None
        return None

    def insertCamera(self, camera):
        if self.CONNECTED:
            sql = "INSERT INTO camera ({}) VALUES ({})".format(camera.get_name_columns(), camera.get_refer())
            val = camera.get_value()
            try:
                self.__mycursor.execute(sql, val)
                self.__mydb.commit()
                camera.id = self.__mycursor.lastrowid
                return camera
            except mysql.connector.Error as err:
                logging.exception("ERR in insertCamera: {}".format(err))
                return None
        return None

    def insertImage(self, image):
        if self.CONNECTED:
            sql = "INSERT INTO image ({}) VALUES ({})".format(image.get_name_columns(), image.get_refer())
            val = image.get_value()
            try:
                self.__mycursor.execute(sql, val)
                self.__mydb.commit()
                image.id = self.__mycursor.lastrowid
                return image
            except mysql.connector.Error as err:
                logging.exception("ERR in insertImage: {}".format(err))
                return None
        return None

    def insertLocation(self, location):
        if self.CONNECTED:
            sql = "INSERT INTO location ({}) VALUES ({})".format(location.get_name_columns(), location.get_refer())
            val = location.get_value()
            try:
                self.__mycursor.execute(sql, val)
                self.__mydb.commit()
                location.id = self.__mycursor.lastrowid
                return location
            except mysql.connector.Error as err:
                logging.exception("ERR in insertLocation: {}".format(err))
                return None
        return None

## Select Database:
    def getPersons(self):
        if self.CONNECTED:
            sql = "SELECT * FROM person"
            try:
                self.__mycursor.execute(sql)
                rows = self.__mycursor.fetchall()
                results = []
                for row in rows:
                    person = object_DL.Person(id=row['idPerson'], 
                                            name=row['name'], 
                                            age=row['age'], 
                                            gender=row['gender'], 
                                            idcode=row['idCode'], 
                                            embedding=row['embedding'], 
                                            b64face=row['b64Face'], 
                                            b64image=row['b64Image'])
                    results.append(person)
                return results
            except mysql.connector.Error as err:
                logging.exception("ERR in getPersons: {}".format(err))
                return None
        return None

    def getPersonById(self, idPerson):
        if self.CONNECTED:
            sql = "SELECT * FROM person WHERE idPerson = {}".format(idPerson)
            try:
                self.__mycursor.execute(sql)
                rows = self.__mycursor.fetchall()
                for row in rows:
                    return object_DL.Person(id=row['idPerson'], 
                                            name=row['name'], 
                                            age=row['age'], 
                                            gender=row['gender'], 
                                            idcode=row['idCode'], 
                                            embedding=row['embedding'], 
                                            b64face=row['b64Face'], 
                                            b64image=row['b64Image'])
                return None
            except mysql.connector.Error as err:
                logging.exception("ERR in getPersonById: {}".format(err))
                return None
        return None

    def getPersonByIdCode(self, idCodePerson):
        if self.CONNECTED:
            table = "person"
            person = object_DL.Person()
            sql = "SELECT * FROM {} WHERE idCode = {}".format(table, idCodePerson)
            try:
                self.__mycursor.execute(sql)
                rows = self.__mycursor.fetchall()
                for row in rows:
                    return object_DL.Person(id=row['idPerson'], 
                                            name=row['name'], 
                                            age=row['age'], 
                                            gender=row['gender'], 
                                            idcode=row['idCode'], 
                                            embedding=row['embedding'], 
                                            b64face=row['b64Face'], 
                                            b64image=row['b64Image'])
            except mysql.connector.Error as err:
                logging.exception("ERR in getPersonByIdCode: {}".format(err))
                return None
        return None

    def getLocations(self):
        if self.CONNECTED:
            sql = "SELECT * FROM location"
            try:
                self.__mycursor.execute(sql)
                rows = self.__mycursor.fetchall()
                results = []
                for row in rows:
                    location = object_DL.Location(id=row['idLocation'],
                                                longtitude=row['longtitude'],
                                                latitude=row['latitude'],
                                                location=row['location'])
                    results.append(location)
                return results
            except mysql.connector.Error as err:
                logging.exception("ERR in getLocations: {}".format(err))
                return None
        return None

    def getLocationById(self, idLocation):
        if self.CONNECTED:
            sql = "SELECT * FROM location WHERE idLocation = {}".format(idLocation)
            try:
                self.__mycursor.execute(sql)
                rows = self.__mycursor.fetchall()
                for row in rows:
                    return object_DL.Location(id=row['idLocation'],
                                            longtitude=row['longtitude'],
                                            latitude=row['latitude'],
                                            location=row['location'])
            except mysql.connector.Error as err:
                logging.exception("ERR in getLocationById: {}".format(err))
                return None
        return None

    def getCameras(self):
        if self.CONNECTED:
            sql = "SELECT * FROM camera JOIN location ON camera.idLocation = location.idLocation"
            try:
                self.__mycursor.execute(sql)
                rows = self.__mycursor.fetchall()
                results = []
                for row in rows:
                    location = object_DL.Location(id=row['idLocation'],
                                                longtitude=row['longtitude'],
                                                latitude=row['latitude'],
                                                location=row['location'])
                    camera = object_DL.Camera(id=row['idCamera'],
                                            cameraname=row['cameraName'],
                                            httpurl=row['HTTPUrl'],
                                            rstpurl=row['RSTPUrl'],
                                            location=location)                     
                    results.append(camera)
                return results
            except mysql.connector.Error as err:
                logging.exception("ERR in getCameras: {}".format(err))
                return None
        return None

    def getCameraById(self, idCamera):
        if self.CONNECTED:
            sql = "SELECT * FROM camera JOIN location ON camera.idLocation = location.idLocation WHERE idCamera = {}".format(idCamera)
            try:
                self.__mycursor.execute(sql)
                rows = self.__mycursor.fetchall()
                for row in rows:
                    location = object_DL.Location(id=row['idLocation'],
                                                longtitude=row['longtitude'],
                                                latitude=row['latitude'],
                                                location=row['location'])
                    return object_DL.Camera(id=row['idCamera'],
                                            cameraname=row['cameraName'],
                                            httpurl=row['HTTPUrl'],
                                            rstpurl=row['RSTPUrl'],
                                            location=location)
            except mysql.connector.Error as err:
                logging.exception("ERR in getCameraById: {}".format(err))
                return None
        return None

    def getImages(self):
        if self.CONNECTED:
            sql = "SELECT * FROM image " \
                + "JOIN person ON image.idPerson = person.idPerson " \
                + "JOIN camera ON image.idCamera = camera.idCamera " \
                + "JOIN location ON location.idLocation = camera.idLocation"
            try:
                self.__mycursor.execute(sql)
                rows = self.__mycursor.fetchall()
                results = []
                for row in rows:
                    person = object_DL.Person(id=row['idPerson'], 
                                            name=row['name'], 
                                            age=row['age'], 
                                            gender=row['gender'], 
                                            idcode=row['idCode'], 
                                            embedding=row['embedding'], 
                                            b64face=row['b64Face'], 
                                            b64image=row['b64Image'])
                    location = object_DL.Location(id=row['idLocation'],
                                                longtitude=row['longtitude'],
                                                latitude=row['latitude'],
                                                location=row['location'])
                    camera = object_DL.Camera(id=row['idCamera'],
                                            cameraname=row['cameraName'],
                                            httpurl=row['HTTPUrl'],
                                            rstpurl=row['RSTPUrl'],
                                            location=location)    
                    image = object_DL.Image(id=row['idImage'],
                                            person=person,
                                            camera=camera,
                                            time=row['time'],
                                            b64image=row['b64Image'],
                                            b64face=row['b64Face'],
                                            embedding=row['embedding'],
                                            istrained=row['isTrained'])                 
                    results.append(image)
                return results
            except mysql.connector.Error as err:
                logging.exception("ERR in getImages: {}".format(err))
                return None
        return None

    def getImageById(self, idImage):
        if self.CONNECTED:
            sql = "SELECT * FROM image " \
                + "JOIN person ON image.idPerson = person.idPerson " \
                + "JOIN camera ON image.idCamera = camera.idCamera " \
                + "JOIN location ON location.idLocation = camera.idLocation " \
                + "WHERE idImage = {}".format(idImage)
            try:
                self.__mycursor.execute(sql)
                rows = self.__mycursor.fetchall()
                for row in rows:
                    person = object_DL.Person(id=row['idPerson'], 
                                            name=row['name'], 
                                            age=row['age'], 
                                            gender=row['gender'], 
                                            idcode=row['idCode'], 
                                            embedding=row['embedding'], 
                                            b64face=row['b64Face'], 
                                            b64image=row['b64Image'])
                    location = object_DL.Location(id=row['idLocation'],
                                                longtitude=row['longtitude'],
                                                latitude=row['latitude'],
                                                location=row['location'])
                    camera = object_DL.Camera(id=row['idCamera'],
                                            cameraname=row['cameraName'],
                                            httpurl=row['HTTPUrl'],
                                            rstpurl=row['RSTPUrl'],
                                            location=location)    
                    return object_DL.Image(id=row['idImage'],
                                            person=person,
                                            camera=camera,
                                            time=row['time'],
                                            b64image=row['b64Image'],
                                            b64face=row['b64Face'],
                                            embedding=row['embedding'],
                                            istrained=row['isTrained'])
            except mysql.connector.Error as err:
                logging.exception("ERR in getLocationById: {}".format(err))
                return None
        return None

## Delete database:
    def deleteFromPerson(self, wherePerson=None):
        if self.CONNECTED:
            table = "person"

            if wherePerson is not None and isinstance(wherePerson, object_DL.Person):
                arr_n = wherePerson.get_arr_name_columns()
                arr_v = wherePerson.get_value()
                f_arr_n = []
                f_arr_v = []
                for i in range(len(arr_v)):
                    if arr_v[i] is not None:
                        f_arr_n.append(arr_n[i])
                        f_arr_v.append(arr_v[i])

                columns, refer = self.__standardize_for_query(f_arr_n)
                sql = "DELETE FROM {} WHERE ({}) = ({})".format(table, columns, refer)
                val = f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in deleteFromPerson: {}".format(err))
                    return False
            else:
                sql = "DELETE FROM {}".format(table)
                try:
                    self.__mycursor.execute(sql)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in deleteFromPerson: {}".format(err))
                    return False
        return False

    def deleteFromCamera(self, whereCamera=None):
        if self.CONNECTED:
            table = "camera"

            if whereCamera is not None and isinstance(whereCamera, object_DL.Camera):
                arr_n = whereCamera.get_arr_name_columns()
                arr_v = whereCamera.get_value()
                f_arr_n = []
                f_arr_v = []
                for i in range(len(arr_v)):
                    if arr_v[i] is not None:
                        f_arr_n.append(arr_n[i])
                        f_arr_v.append(arr_v[i])

                columns, refer = self.__standardize_for_query(f_arr_n)
                sql = "DELETE FROM {} WHERE ({}) = ({})".format(table, columns, refer)
                val = f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in deleteFromCamera: {}".format(err))
                    return False
            else:
                sql = "DELETE FROM {}".format(table)
                try:
                    self.__mycursor.execute(sql)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in deleteFromCamera: {}".format(err))
                    return False
        return False

    def deleteFromImage(self, whereImage=None):
        if self.CONNECTED:
            table = "image"

            if whereImage is not None and isinstance(whereImage, object_DL.Image):
                arr_n = whereImage.get_arr_name_columns()
                arr_v = whereImage.get_value()
                f_arr_n = []
                f_arr_v = []
                for i in range(len(arr_v)):
                    if arr_v[i] is not None:
                        f_arr_n.append(arr_n[i])
                        f_arr_v.append(arr_v[i])

                columns, refer = self.__standardize_for_query(f_arr_n)
                sql = "DELETE FROM {} WHERE ({}) = ({})".format(table, columns, refer)
                val = f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in deleteFromImage: {}".format(err))
                    return False
            else:
                sql = "DELETE FROM {}".format(table)
                try:
                    self.__mycursor.execute(sql)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in deleteFromImage: {}".format(err))
                    return False
        return False

    def deleteFromLocation(self, whereLocation):
        if self.CONNECTED:
            table = "location"

            if whereLocation is not None and isinstance(whereLocation, object_DL.Location):
                arr_n = whereLocation.get_arr_name_columns()
                arr_v = whereLocation.get_value()
                f_arr_n = []
                f_arr_v = []
                for i in range(len(arr_v)):
                    if arr_v[i] is not None:
                        f_arr_n.append(arr_n[i])
                        f_arr_v.append(arr_v[i])

                columns, refer = self.__standardize_for_query(f_arr_n)
                sql = "DELETE FROM {} WHERE ({}) = ({})".format(table, columns, refer)
                val = f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in deleteFromLocation: {}".format(err))
                    return False
            else:
                sql = "DELETE FROM {}".format(table)
                try:
                    self.__mycursor.execute(sql)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in deleteFromLocation: {}".format(err))
                    return False
        return False

## Update table:
    def updatePerson(self, setPerson, wherePerson):
        if self.CONNECTED and isinstance(setPerson, object_DL.Person):
            table = "person"

            s_arr_n = setPerson.get_arr_name_columns()
            s_arr_v = setPerson.get_value()
            s_f_arr_n = []
            s_f_arr_v = []
            for i in range(len(s_arr_v)):
                if s_arr_v[i] is not None:
                    s_f_arr_n.append(s_arr_n[i])
                    s_f_arr_v.append(s_arr_v[i])
            s_columns = self.__standardize_for_query_set(s_f_arr_n)

            if wherePerson is not None and isinstance(wherePerson, object_DL.Person):
                arr_n = wherePerson.get_arr_name_columns()
                arr_v = wherePerson.get_value()
                f_arr_n = []
                f_arr_v = []
                for i in range(len(arr_v)):
                    if arr_v[i] is not None:
                        f_arr_n.append(arr_n[i])
                        f_arr_v.append(arr_v[i])

                columns, refer = self.__standardize_for_query(f_arr_n)
                sql = "UPDATE {} SET {} WHERE ({}) = ({})".format(table, s_columns, columns, refer)
                val = s_f_arr_v+f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in updatePerson: {}".format(err))
                    return False
            else:
                sql = "UPDATE {} SET {}".format(table, s_columns)
                val = s_f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in updatePerson: {}".format(err))
                    return False
        return False

    def updateCamera(self, setCamera, whereCamera):
        if self.CONNECTED and isinstance(setCamera, object_DL.Camera):
            table = "camera"

            s_arr_n = setCamera.get_arr_name_columns()
            s_arr_v = setCamera.get_value()
            s_f_arr_n = []
            s_f_arr_v = []
            for i in range(len(s_arr_v)):
                if s_arr_v[i] is not None:
                    s_f_arr_n.append(s_arr_n[i])
                    s_f_arr_v.append(s_arr_v[i])
            s_columns = self.__standardize_for_query_set(s_f_arr_n)

            if whereCamera is not None and isinstance(whereCamera, object_DL.Camera):
                arr_n = whereCamera.get_arr_name_columns()
                arr_v = whereCamera.get_value()
                f_arr_n = []
                f_arr_v = []
                for i in range(len(arr_v)):
                    if arr_v[i] is not None:
                        f_arr_n.append(arr_n[i])
                        f_arr_v.append(arr_v[i])

                columns, refer = self.__standardize_for_query(f_arr_n)
                sql = "UPDATE {} SET {} WHERE ({}) = ({})".format(table, s_columns, columns, refer)
                val = s_f_arr_v+f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in updateCamera: {}".format(err))
                    return False
            else:
                sql = "UPDATE {} SET {}".format(table, s_columns)
                val = s_f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in updateCamera: {}".format(err))
                    return False
        return False

    def updateLocation(self, setLocation, whereLocation):
        if self.CONNECTED and isinstance(setLocation, object_DL.Location):
            table = "location"

            s_arr_n = setLocation.get_arr_name_columns()
            s_arr_v = setLocation.get_value()
            s_f_arr_n = []
            s_f_arr_v = []
            for i in range(len(s_arr_v)):
                if s_arr_v[i] is not None:
                    s_f_arr_n.append(s_arr_n[i])
                    s_f_arr_v.append(s_arr_v[i])
            s_columns = self.__standardize_for_query_set(s_f_arr_n)

            if whereLocation is not None and isinstance(whereLocation, object_DL.Location):
                arr_n = whereLocation.get_arr_name_columns()
                arr_v = whereLocation.get_value()
                f_arr_n = []
                f_arr_v = []
                for i in range(len(arr_v)):
                    if arr_v[i] is not None:
                        f_arr_n.append(arr_n[i])
                        f_arr_v.append(arr_v[i])

                columns, refer = self.__standardize_for_query(f_arr_n)
                sql = "UPDATE {} SET {} WHERE ({}) = ({})".format(table, s_columns, columns, refer)
                val = s_f_arr_v+f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in updateLocation: {}".format(err))
                    return False
            else:
                sql = "UPDATE {} SET {}".format(table, s_columns)
                val = s_f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in updateLocation: {}".format(err))
                    return False
        return False

    def updateImage(self, setImage, whereImage):
        if self.CONNECTED and isinstance(setImage, object_DL.Image):
            table = "image"

            s_arr_n = setImage.get_arr_name_columns()
            s_arr_v = setImage.get_value()
            s_f_arr_n = []
            s_f_arr_v = []
            for i in range(len(s_arr_v)):
                if s_arr_v[i] is not None:
                    s_f_arr_n.append(s_arr_n[i])
                    s_f_arr_v.append(s_arr_v[i])
            s_columns = self.__standardize_for_query_set(s_f_arr_n)

            if whereImage is not None and isinstance(whereImage, object_DL.Image):
                arr_n = whereImage.get_arr_name_columns()
                arr_v = whereImage.get_value()
                f_arr_n = []
                f_arr_v = []
                for i in range(len(arr_v)):
                    if arr_v[i] is not None:
                        f_arr_n.append(arr_n[i])
                        f_arr_v.append(arr_v[i])

                columns, refer = self.__standardize_for_query(f_arr_n)
                sql = "UPDATE {} SET {} WHERE ({}) = ({})".format(table, s_columns, columns, refer)
                val = s_f_arr_v+f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in updateImage: {}".format(err))
                    return False
            else:
                sql = "UPDATE {} SET {}".format(table, s_columns)
                val = s_f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                    self.__mydb.commit()
                    return True
                except mysql.connector.Error as err:
                    logging.exception("ERR in updateAllImage: {}".format(err))
                    return False
        return False

# Some func
    def extract_features_labels(self):
        persons = self.getPersons()
        features = []
        labels = []
        for person in persons:
            features.append(manage_data.convert_bytes_to_embedding_vector(person.embedding))
            labels.append(person.id)
        return (persons, features, labels)

if __name__ == "__main__":
    test = Database("localhost", "root", "", "faceid")
    p = object_DL.Person(name='test', age=18, gender='female', idcode='123123')
    # rs = test.selectFromPerson(wherePerson=p)
    rows = test.getImages()
    for row in rows:
        print(row.camera.location.location)
    # for row in rows:
    #     print(row.location)
    