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
            self.__mycursor = self.__mydb.cursor()
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

    def refetch_table(self, table):
        if self.CONNECTED:
            query = "SELECT * FROM " + str(table)
            self.__mycursor.execute(query)
            self.__mycursor.fetchall()
            logging.info("Refetch table `{}` successfull".format(table))
        else:
            logging.error("Cannot access to database")
## Insert database:

    def insertValuesIntoPerson(self, person):
        if self.CONNECTED:
            sql = "INSERT INTO {} ({}) VALUES ({})".format("person", person.get_name_columns(), person.get_refer())
            val = [person.get_value()]
            try:
                self.__mycursor.executemany(sql, val)
                self.__mydb.commit()
                logging.info("Insert success")
            except mysql.connector.Error as err:
                logging.exception("ERR in insertValuesIntoPerson: {}".format(err))

    def insertValuesIntoCamera(self, camera):
        if self.CONNECTED:
            sql = "INSERT INTO {} ({}) VALUES ({})".format("camera", camera.get_name_columns(), camera.get_refer())
            val = [camera.get_value()]
            try:
                self.__mycursor.executemany(sql, val)
                self.__mydb.commit()
                logging.info("Insert success")
            except mysql.connector.Error as err:
                logging.exception("ERR in insertValuesIntoCamera: {}".format(err))

    def insertValuesIntoImage(self, image):
        if self.CONNECTED:
            sql = "INSERT INTO {} ({}) VALUES ({})".format("image", image.get_name_columns(), image.get_refer())
            val = [image.get_value()]
            try:
                self.__mycursor.executemany(sql, val)
                self.__mydb.commit()
                logging.info("Insert success")
            except mysql.connector.Error as err:
                logging.exception("ERR in insertValuesIntoImage: {}".format(err))

    def insertValuesIntoLocation(self, location):
        if self.CONNECTED:
            sql = "INSERT INTO {} ({}) VALUES ({})".format("location", location.get_name_columns(), location.get_refer())
            val = [location.get_value()]
            try:
                self.__mycursor.executemany(sql, val)
                self.__mydb.commit()
                logging.info("Insert success")
            except mysql.connector.Error as err:
                logging.exception("ERR in insertValuesIntoLocation: {}".format(err))
## Select Database:

    def selectFromPerson(self, wherePerson=None, max_row=None):
        if self.CONNECTED:
            table = "person"
            person = object_DL.Person()
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
                sql = "SELECT {} FROM {} WHERE ({}) = ({})".format(person.get_name_columns(), table, columns, refer)
                val = f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                except mysql.connector.Error as err:
                    logging.exception("ERR in selectFromPerson: {}".format(err))
                    return None
            else:
                sql = "SELECT {} FROM {}".format(person.get_name_columns(), table)
                try:
                    self.__mycursor.execute(sql)
                except mysql.connector.Error as err:
                    logging.exception("ERR in selectFromPerson: {}".format(err))
                    return None

            if max_row is not None:
                rs = self.__mycursor.fetchmany(max_row)
            else:
                rs = self.__mycursor.fetchall()

            obj_rs = []
            for x in rs:
                obj_rs.append(object_DL.Person(id=x[0], name=x[1], age=x[2], gender=x[3], idcode=x[4], embedding=x[5], b64face=x[6], b64image=x[7]))
            return obj_rs

    def selectFromCamera(self, whereCamera=None, max_row=None):
        if self.CONNECTED:
            table = "camera"
            camera = object_DL.Camera()
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
                sql = "SELECT {} FROM {} WHERE ({}) = ({})".format(camera.get_name_columns(), table, columns, refer)
                val = f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                except mysql.connector.Error as err:
                    logging.exception("ERR in selectFromCamera: {}".format(err))
                    return None
            else:
                sql = "SELECT {} FROM {}".format(camera.get_name_columns(), table)
                try:
                    self.__mycursor.execute(sql)
                except mysql.connector.Error as err:
                    logging.exception("ERR in selectFromCamera: {}".format(err))
                    return None

            if max_row is not None:
                rs = self.__mycursor.fetchmany(max_row)
            else:
                rs = self.__mycursor.fetchall()

            obj_rs = []
            for x in rs:
                obj_rs.append(object_DL.Camera(id=x[0], name=x[1], httpurl=x[2], rstpurl=x[3], location=self.selectFromLocation(whereLocation=object_DL.Location(id=x[4]), max_row=1)[0]))
            return obj_rs

    def selectFromImage(self, whereImage=None, max_row=None):
        if self.CONNECTED:
            table = "image"
            image = object_DL.Image()
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
                sql = "SELECT {} FROM {} WHERE ({}) = ({})".format(image.get_name_columns(), table, columns, refer)
                val = f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                except mysql.connector.Error as err:
                    logging.exception("ERR in selectFromImage: {}".format(err))
                    return None
            else:
                sql = "SELECT {} FROM {}".format(image.get_name_columns(), table)
                try:
                    self.__mycursor.execute(sql)
                except mysql.connector.Error as err:
                    logging.exception("ERR in selectFromImage: {}".format(err))
                    return None

            if max_row is not None:
                rs = self.__mycursor.fetchmany(max_row)
            else:
                rs = self.__mycursor.fetchall()

            obj_rs = []
            for x in rs:
                obj_rs.append(object_DL.Image(id=x[0], person=self.selectFromPerson(wherePerson=object_DL.Person(id=x[1]), max_row=1)[0], camera=self.selectFromCamera(whereCamera=object_DL.Camera(id=x[2]), max_row=1)[0], time=x[3], b64image=x[4], b64face=x[5], embedding=x[6], istrained=x[7]))
            return obj_rs

    def selectFromLocation(self, whereLocation=None, max_row=None):
        if self.CONNECTED:
            table = "location"
            location = object_DL.Location()
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
                sql = "SELECT {} FROM {} WHERE ({}) = ({})".format(location.get_name_columns(), table, columns, refer)
                val = f_arr_v
                try:
                    self.__mycursor.execute(sql, val)
                except mysql.connector.Error as err:
                    logging.exception("ERR in selectFromLocation: {}".format(err))
                    return None
            else:
                sql = "SELECT {} FROM {}".format(location.get_name_columns(), table)
                try:
                    self.__mycursor.execute(sql)
                except mysql.connector.Error as err:
                    logging.exception("ERR in selectFromLocation: {}".format(err))
                    return None

            if max_row is not None:
                rs = self.__mycursor.fetchmany(max_row)
            else:
                rs = self.__mycursor.fetchall()

            obj_rs = []
            for x in rs:
                obj_rs.append(object_DL.Location(id=x[0], longtitude=x[1], latitude=x[2], location=x[3]))
            return obj_rs

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
    def extract_features_and_labels(self):
        all_person = self.selectFromPerson()
        emb_all = []
        label_all = []
        for person in all_person:
            emb_all.append(manage_data.convert_bytes_to_embedding_vector(person.embedding))
            label_all.append(person.id)
        return (emb_all, label_all, all_person)

    def get_list_person_in_id_order(self, list_id):
        rs = []
        for id in list_id:
            p = object_DL.Person(id=id)
            rs.append(self.selectFromPerson(wherePerson=p)[0])
        return rs

if __name__ == "__main__":
    test = Database("localhost", "root", "", "faceid")
    p = object_DL.Person()
    p.id = 19
    rs = test.selectFromPerson(wherePerson=p)
    logging.info("Fetch data successfully")
    for person in rs:
        print(person.name)
    