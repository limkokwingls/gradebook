from pathlib import Path
import base64

__FILE = 'credentials'
key = "I'm having 2 cows"


def read_credentials() -> list[str]:
    res = []
    if Path(__FILE).is_file():
        with open(__FILE, 'r') as f:
            data = f.read().splitlines()
            res = [
                decode(data[0]),
                decode(data[1]),
            ]
    return res


def write_credentials(username, password):
    with open(__FILE, 'w') as f:
        f.write(encode(username))
        f.write('\n')
        f.write(encode(password))


def encode(clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()


def decode(enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)
