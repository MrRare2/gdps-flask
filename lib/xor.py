class XORCipher:

    @staticmethod
    def cipher(plaintext, key):
        key = XORCipher.text2ascii(str(key))
        plaintext = XORCipher.text2ascii(plaintext)

        keysize = len(key)
        input_size = len(plaintext)

        cipher = ""
        for i in range(input_size):
            cipher += chr(plaintext[i] ^ key[i % keysize])

        return cipher

    @staticmethod
    def crack(cipher, keysize):
        cipher = XORCipher.text2ascii(cipher)
        occurrences = [{} for _ in range(keysize)]
        key = [0] * keysize
        input_size = len(cipher)

        for i in range(input_size):
            j = i % keysize
            val = cipher[i]
            occurrences[j][val] = occurrences[j].get(val, 0) + 1
            if occurrences[j][val] > occurrences[j].get(key[j], 0):
                key[j] = val

        # assume space (32) is the most common plaintext byte
        key = [b ^ 32 for b in key]
        return XORCipher.ascii2text(str(key))

    @staticmethod
    def plaintext(cipher, key):
        key = XORCipher.text2ascii(str(key))
        cipher = XORCipher.text2ascii(cipher)

        keysize = len(key)
        input_size = len(cipher)

        plaintext = ""
        for i in range(input_size):
            plaintext += chr(cipher[i] ^ key[i % keysize])

        return plaintext

    @staticmethod
    def text2ascii(text):
        return [ord(c) for c in text]

    @staticmethod
    def ascii2text(ascii_list):
        result = ""
        for c in ascii_list:
            result += chr(c)
        return result
