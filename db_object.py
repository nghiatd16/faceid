from system_structure import db_structure
import json
class Camera:
    def __init__(self, id=None, cameraName=None, HTTPUrl=None, RSTPUrl=None, outHTTPUrl=None, location=None):
        self.id = id
        self.cameraName = cameraName
        self.HTTPUrl = HTTPUrl
        self.RSTPUrl = RSTPUrl
        self.outHTTPUrl = outHTTPUrl
        self.location = location
        self.idLocation = None
        if location is not None:
            self.idLocation = location.id
    @staticmethod
    def get_structure():
        return db_structure.camera

    def to_json(self):
        document = {}
        for attr in db_structure.camera:
            document[attr] = getattr(self, attr)
        return json.dumps(document)

    def __str__(self):
        return "[id: {} - cameraName: {} - httpurl: {} - rstpurl: {} - location: {}]".format(self.id, self.httpurl, self.rstpurl, self.location)

class Image:
    def __init__(self, id=None, person=None, camera=None, time=None, face=None, image=None, embedding=None, isTrained=None):
        self.id = id
        self.person = person
        self.idPerson = None
        if person is not None:
            self.idPerson = person.id
        self.camera = camera
        self.idCamera = None
        if camera is not None:
            self.idCamera = camera.id
        self.time = time
        self.face = face
        self.image = image
        self.embedding = embedding
        self.istrained = istrained

    @staticmethod
    def get_structure():
        return db_structure.image

    def to_json(self):
        document = {}
        for attr in db_structure.image:
            document[attr] = getattr(self, attr)
        return json.dumps(document)

    def __str__(self):
        return "[id: {} - idPerson: {} - idCamera: {} - timeCaptured: {} - isTrained: {}]".format(self.id, self.idPerson, self.idcamera, self.time, self.istrained)

class Location:
    def __init__(self, id=None, longtitude=None, latitude=None, address=None):
        self.id = id
        self.longtitude = longtitude
        self.latitude = latitude
        self.address = address

    @staticmethod
    def get_structure():
        return db_structure.location

    def to_json(self):
        document = {}
        for attr in db_structure.location:
            document[attr] = getattr(self, attr)
        return json.dumps(document)

    def __str__(self):
        return "[id: {} - longtitude: {} - latitude: {} - address: {}]".format(self.id, self.longtitude, self.latitude, self.address)

class Person:
    def __init__(self, id=None, name=None, unicodeName=None, birthDay=None, gender=None, idCode=None, country=None, description=None, embedding=None, face=None, avatar=None):
        self.id = id
        self.name = name
        self.unicodeName = None
        self.birthDay = birthDay
        self.gender = gender
        self.idCode = idCode
        self.country = country
        self.description = description
        self.embedding = embedding
        self.face = face
        self.avatar = avatar

    @staticmethod
    def get_structure():
        return db_structure.person

    def to_json(self):
        document = {}
        for attr in db_structure.person:
            document[attr] = getattr(self, attr)
        return json.dumps(document)

    def __str__(self):
        return "[id: {} - name: {} - birthday: {} - gender: {} - idCode: {} - country: {}]".format(self.id, self.name, self.birthday, self.gender, self.idcode, self.country)
if __name__ == "__main__":
    # l = Location(id=3, location="abc", longtitude="132", latitude="321")
    c = Camera(cameraName="abc", HTTPUrl="asdasd", location=None)
    print(c.to_json())
    print(c.get_structure())