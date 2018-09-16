class Camera:
    def __init__(self, id=None, cameraname=None, httpurl=None, rstpurl=None, location=None):
        self.id = id
        self.cameraname = cameraname
        self.httpurl = httpurl
        self.rstpurl = rstpurl
        self.location = location

    def get_arr_name_columns(self):
        return ["idcamera", "cameraname", "httpurl", "rstpurl", "idlocation"]

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
        return (self.id, self.cameraname, self.httpurl, self.rstpurl, self.idlocation)
    
    def __str__(self):
        return "[id: {} - cameraName: {} - httpurl: {} - rstpurl: {} - location: {}]".format(self.id, self.httpurl, self.rstpurl, self.location)

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
        return ["idimage", "idperson", "idcamera", "time", "b64image", "b64face", "embedding", "istrained"]

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

    def __str__(self):
        return "[id: {} - idPerson: {} - idCamera: {} - timeCaptured: {} - isTrained: {}]".format(self.id, self.idperson, self.idcamera, self.time, self.istrained)

class Location:
    def __init__(self, id=None, longtitude=None, latitude=None, location=None):
        self.id = id
        self.longtitude = longtitude
        self.latitude = latitude
        self.location = location

    def get_arr_name_columns(self):
        return ["idlocation", "longtitude", "latitude", "location"]

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

    def __str__(self):
        return "[id: {} - longtitude: {} - latitude: {} - location: {}]".format(self.id, self.longtitude, self.latitude, self.location)
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
        return ["idperson", "name", "age", "gender", "idcode", "embedding", "b64face", "b64image"]

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

    def __str__(self):
        return "[id: {} - name: {} - age: {} - gender: {} - idCode: {}]".format(self.id, self.name, self.age, self.gender, self.idcode)
if __name__ == "__main__":
    l = Location(id=3, location="abc", longtitude="132", latitude="321")
    c = Camera(name="abc", httpurl="asdasd", location=l)
    print(c.get_value())
