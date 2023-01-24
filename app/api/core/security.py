import os
import rsa
import string, secrets
from passlib.context import CryptContext
from hdwallet.utils import generate_mnemonic

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#(publicKey, privateKey) = rsa.newkeys(1024)


class Security:

    @classmethod
    def generate_uuid(cls, bits: int = 32):

        rand = secrets.randbits(bits)
        rand_1 = secrets.choice(string.ascii_letters).upper()
        rand_2 = secrets.choice(string.ascii_letters).upper()
        return rand_1 + rand_2 + str(rand)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    def verify_password(cls, password: str, hash_str: str) -> bool:
        return pwd_context.verify(password, hash_str)

    @classmethod
    def __generateKeys(cls):
        (publicKey, privateKey) = rsa.newkeys(1024)
        if not os.path.exists('publcKey.pem'):

            with open('publcKey.pem', 'wb') as p:
                p.write(publicKey.save_pkcs1('PEM'))
            with open('privateKey.pem', 'wb') as p:
                p.write(privateKey.save_pkcs1('PEM'))

    @classmethod
    def __loadKeys(cls):
        if not os.path.exists('publcKey.pem'):
            cls.__generateKeys()

        with open('publicKey.pem', 'rb') as p:
            public_Key = rsa.PublicKey.load_pkcs1(p.read())
        with open('privateKey.pem', 'rb') as p:
            private_Key = rsa.PrivateKey.load_pkcs1(p.read())
        return private_Key, public_Key

    @classmethod
    def encrypt(cls, key: str):
        (private_Key, public_Key) = cls.__loadKeys
        return rsa.encrypt(key.encode('ascii'), public_Key)

    @classmethod
    def decrypt(cls, encode_key: bytes):
        (private_Key, public_Key) = cls.__loadKeys
        try:
            return rsa.decrypt(encode_key, private_Key).decode('ascii')
        except:
            return False

    @classmethod
    def generate_mnemonic(cls):
        return cls.encrypt(generate_mnemonic(language="english", strength=256))
