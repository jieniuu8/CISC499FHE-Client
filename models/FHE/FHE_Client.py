from app import *
from etc.config.externalLib import *

class FHE_Client:
    def __init__(self, size):
        self.m = int.from_bytes(os.urandom(int(size)//8), byteorder='big')
        self.p = int.from_bytes(os.urandom(int(size)//8), byteorder='big')
        while self.p <= self.m:
            self.p = int.from_bytes(os.urandom(int(size)//8), byteorder='big')


    def decrypt_int(self, xp, q, p):
        x = (xp + self.m * q) - p
        return x
