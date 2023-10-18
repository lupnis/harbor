import random
import datetime
import string

import hashlib
import datetime

class CodeGenerator:
    def __init__(self, hash_func = hashlib.md5):
        self.hash = hash_func()
        
    def generate(self, s):
        self.hash.update(s.encode())
        return self.hash.hexdigest()