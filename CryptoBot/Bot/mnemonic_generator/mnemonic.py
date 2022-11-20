import hashlib
import itertools
import os
import secrets
import unicodedata
from typing import AnyStr, List, Union


class Mnemonic(object):
    def __init__(self, language: str = "english"):
        self.language = language
        self.radix = 2048
        d = os.path.join(os.path.dirname(__file__), f"words/{language}.txt")
        if os.path.exists(d) and os.path.isfile(d):
            with open(d, "r", encoding="utf-8") as f:
                self.wordlist = [w.strip() for w in f.readlines()]
            if len(self.wordlist) != self.radix:
                raise ValueError(
                    f"Wordlist should contain 2048 words, but it's {len(self.wordlist)} words long instead."
                )
        else:
            raise FileExistsError("Language not detected")
        # Japanese must be joined by ideographic space
        self.delimiter = "\u3000"

    @staticmethod
    def ref_string(txt: AnyStr) -> str:
        if isinstance(txt, bytes):
            utxt = txt.decode("utf8")
        elif isinstance(txt, str):
            utxt = txt
        else:
            raise TypeError("String value expected")

        return unicodedata.normalize("NFKD", utxt)

    def generate_mnemo(self, strength: int = 128) -> str:
        """
        Create a new mnemonic using a random generated number as entropy.

        As defined in BIP39, the entropy must be a multiple of 32 bits, and its size must be between 128 and 256 bits.
        Therefore the possible values for `strength` are 128, 160, 192, 224 and 256.

        The return is a list of words that encodes the generated entropy.

        :param strength: Number of bytes used as entropy
        :type strength: int
        :return: A randomly generated mnemonic
        :rtype: str
        """
        if strength not in [128, 160, 192, 224, 256]:
            raise ValueError(
                "Invalid strength value. Strength not supported"
            )
        return self.to_mnemonic(secrets.token_bytes(strength // 8))

    def to_entropy(self, words: Union[List[str], str]) -> bytearray:
        if not isinstance(words, list):
            words = words.split(" ")
        if len(words) not in [12, 15, 18, 21, 24]:
            raise ValueError(
                "Number of words must be one of the following: [12, 15, 18, 21, 24], but it is not (%d)."
                % len(words)
            )

        concatLenBits = len(words) * 11
        concatBits = [False] * concatLenBits
        wordindex = 0
        for word in words:
            ndx = self.wordlist.index(word)
            if ndx < 0:
                raise LookupError('Unable to find "%s" in word list.' % word)
            for ii in range(11):
                concatBits[(wordindex * 11) + ii] = (ndx & (1 << (10 - ii))) != 0
            wordindex += 1
        checksumLengthBits = concatLenBits // 33
        entropyLengthBits = concatLenBits - checksumLengthBits
        # Extract original entropy as bytes.
        entropy = bytearray(entropyLengthBits // 8)
        for ii in range(len(entropy)):
            for jj in range(8):
                if concatBits[(ii * 8) + jj]:
                    entropy[ii] |= 1 << (7 - jj)

        hashBytes = hashlib.sha256(entropy).digest()
        hashBits = list(
            itertools.chain.from_iterable(
                [c & (1 << (7 - i)) != 0 for i in range(8)] for c in hashBytes
            )
        )

        for i in range(checksumLengthBits):
            if concatBits[entropyLengthBits + i] != hashBits[i]:
                raise ValueError("Failed checksum.")
        return entropy

    def to_mnemonic(self, data: bytes) -> str:
        if len(data) not in [16, 20, 24, 28, 32]:
            raise ValueError(
                f"Data length should be one of the following: [16, 20, 24, 28, 32], but it is not {len(data)}."
            )
        h = hashlib.sha256(data).hexdigest()
        b = (
            bin(int.from_bytes(data, byteorder="big"))[2:].zfill(len(data) * 8)
            + bin(int(h, 16))[2:].zfill(256)[: len(data) * 8 // 32]
        )
        result = []
        for i in range(len(b) // 11):
            idx = int(b[i * 11: (i + 1) * 11], 2)
            result.append(self.wordlist[idx])
        return self.delimiter.join(result)