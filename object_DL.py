class Camera:
    def __init__(self, id=None, name=None, httpurl=None, rstpurl=None, location=None):
        self.id = id
        self.name = name
        self.httpurl = httpurl
        self.rstpurl = rstpurl
        self.location = location

    def get_arr_name_columns(self):
        return ["id", "name", "httpurl", "rstpurl", "idlocation"]

    def get_name_columns(self):
        arr = self.get_arr_name_columns()
        rs = ""
        for i in range(len(arr)):
            rs += arr[i]
            if i != len(arr)-1:
                rs += ", "
        return rs

    def get_refer(self):
        return "%s, %s, %s, %s, %s"

    def get_value(self):
        self.idlocation = None
        if self.location is not None and isinstance(self.location, Location):
            self.idlocation = self.location.id
        return (self.id, self.name, self.httpurl, self.rstpurl, self.idlocation)

class Image:
    def __init__(self, id=None, person=None, camera=None, time=None, b64image=None, b64face=None, embedding=None, istrained=None):
        self.id = id
        self.person = person
        self.camera = camera
        self.time = time
        self.b64image = b64image
        self.b64face = b64face
        self.embedding = embedding
        self.istrained = istrained

    def get_arr_name_columns(self):
        return ["id", "idperson", "idcamera", "time", "b64image", "b64face", "embedding", "istrained"]

    def get_name_columns(self):
        arr = self.get_arr_name_columns()
        rs = ""
        for i in range(len(arr)):
            rs += arr[i]
            if i != len(arr)-1:
                rs += ", "
        return rs

    def get_refer(self):
        return "%s, %s, %s, %s, %s, %s, %s, %s"

    def get_value(self):
        self.idperson = None
        self.idcamera = None
        if self.person is not None and isinstance(self.person, Person):
            self.idperson = self.person.id
        if self.camera is not None and isinstance(self.camera, Camera):
            self.idcamera = self.camera.id
        return (self.id, self.idperson, self.idcamera, self.time, self.b64image, self.b64face, self.embedding, self.istrained)

class Location:
    def __init__(self, id=None, longtitude=None, latitude=None, location=None):
        self.id = id
        self.longtitude = longtitude
        self.latitude = latitude
        self.location = location

    def get_arr_name_columns(self):
        return ["id", "longtitude", "latitude", "location"]

    def get_name_columns(self):
        arr = self.get_arr_name_columns()
        rs = ""
        for i in range(len(arr)):
            rs += arr[i]
            if i != len(arr)-1:
                rs += ", "
        return rs

    def get_refer(self):
        return "%s, %s, %s, %s"

    def get_value(self):
        return (self.id, self.longtitude, self.latitude, self.location)

class Person:
    def __init__(self, id=None, name=None, age=None, gender=None, idcode=None, embedding=None, b64face=None, b64image=None):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.idcode = idcode
        self.embedding = embedding
        self.b64face = b64face
        self.b64image = b64image

    def get_arr_name_columns(self):
        return ["id", "name", "age", "gender", "idcode", "embedding", "b64face", "b64image"]

    def get_name_columns(self):
        arr = self.get_arr_name_columns()
        rs = ""
        for i in range(len(arr)):
            rs += arr[i]
            if i != len(arr)-1:
                rs += ", "
        return rs

    def get_refer(self):
        return "%s, %s, %s, %s, %s, %s, %s, %s"

    def get_value(self):
        return (self.id, self.name, self.age, self.gender, self.idcode, self.embedding, self.b64face, self.b64image)

if __name__ == "__main__":
    l = Location(id=3, location="abc", longtitude="132", latitude="321")
    c = Camera(name="abc", httpurl="asdasd", location=l)
    print(c.get_value())
