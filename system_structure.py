import json
import tensorflow
import os
class DatabaseParser:
    def __init__(self, file_structure):
        self.__parse_json_structure(file_structure)
        
    def __parse_json_structure(self, file_structure):
        struct_file = open(file_structure)
        db_structure = json.load(struct_file)
        struct_file.close()
        db_name = list(db_structure.keys())[0]
        self.db_name = db_name
        self.num_collections = len(db_structure[db_name])
        self.collections = tuple(db_structure[db_name].keys())
        db_collections = db_structure[db_name]
        for key in db_collections.keys():
            setattr(self, key, tuple(db_collections[key]))

db_structure = DatabaseParser("db_structure.json")
# print(db_structure.collections)
def gen_code():
    for p in db_structure.person:
        print(p, end = '=None, ')
    print()
    for p in db_structure.person:
        print(p, end = ', ')
    print()
gen_code()
# print(getattr(db_structure))
# tmp = {
#     "image": ["a", "b", 1],
#     "lsd": "dfsdfs",
#     "vbv": None,
#     "gfb": b'123123'
# }
# print(json.dumps(tmp))