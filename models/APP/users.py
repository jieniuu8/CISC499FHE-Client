from app import *
from etc.config.externalLib import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

class Session:
    def __init__(self):
        self.key_size = 0
        self.session_name = ""
        self.set = {}
        self.all_int_set = []

    def getName(self):
        return self.session_name

    def setName(self, name):
        self.session_name = name

    def setKeySize(self, key_size):
        self.key_size = key_size

    def setServerId(self, id):
        self.server_id = id

    def setFHEObject(self, dataType):
        self.data_type = dataType
        self.fhe = FHE_Client.FHE_Client(self.key_size)
