import socket
import re
import base64

with socket.create_connection(("challenge01.root-me.org",52023),timeout=10) as s:
    data = s.recv(1000)
    print(data)
    
    pattern = re.compile(r"\s'(.*)'")
    st = pattern.finditer(str(data))
    for i in st:
        print("")
        enc = i.group().split("'")[1]
        print(f"encoded string: {enc}")
    rb_dec = base64.b64decode(enc)
    dec = str(rb_dec).split("'")[1]
    print(f"decoded string: {dec}")
    
    s.sendall(rb_dec+b"\n")
    resp = s.recv(1000)
    print(resp)
    