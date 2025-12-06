
# 1. Root-Me TCP Encoded String Challenge 
## Challenge
A TCP service (`challenge01.root-me.org:52023`) sends a base64 encoded string and expects the decoded value as a reply.  
If correct, the server returns the flag.

You have 2 seconds to send reply.
## TL;DR
whats happening
- Connect to `challenge01.root-me.org:52023`  
- Receive base64 string → decode → send back  
- Get the flag 🎉  
```python
import socket, re, base64

with socket.create_connection(("challenge01.root-me.org",52023)) as s:
    enc = re.search(r"'(.*)'", str(s.recv(1000))).group(1)
    rb_dec = base64.b64decode(enc)
    s.sendall(rb_dec+b"\n")
    print(s.recv(1000))
```

## Solution Walkthrough

### 1. Create a TCP Connection
```python
with socket.create_connection(("challenge01.root-me.org",52023),timeout=10) as s:
```
`socket.create_connection()` - establishes a TCP connection.

`timeout=10` - avoids hanging forever.
### 2. Receive Server Data

```python
data = s.recv(1000)
print(data)
```

`recv(1000)` - reads up to 1000 bytes.

Server responds with instructions and the encoded string:

```bash
b"\n==================\n ENCRYPTED STRING \n==================\nTell me the clear content of this string !\n\nmy string is '[RANDOM_BASE64_ENCODED_STRING]'. What is your answer ? "
```
example output
```bash
b"\n==================\n ENCRYPTED STRING \n==================\nTell me the clear content of this string !\n\nmy string is 'ZllsRlBHSExYZHN0'. What is your answer ? "
```

### 3. Extract Encoded String
```python 
pattern = re.compile(r"\s'(.*)'")
st = pattern.finditer(str(data))
for i in st:
    enc = i.group().split("'")[1]
    print(f"encoded string: {enc}")
```
`Regex \s'(.*)'` - finds the text between quotes.

Example output:
```bash
encoded string: ZllsRlBHSExYZHN0
```

### 4. Decode Base64
```python
rb_dec = base64.b64decode(enc)
dec = str(rb_dec).split("'")[1]
print(f"decoded string: {dec}")
```
`base64.b64decode()` - converts encoded string  to decoded raw bytes.

example output:
```bash
rb_dec = b'fYlFPGHLXdst'
```
Converting rb_dec to string for printing.
```bash
dec = str(rb_dec).split("'")[1]
```
now dec is:
```bash
decoded string: fYlFPGHLXdst
```

### 5. Send Decoded Value

```python
s.sendall(rb_dec+b"\n")
resp = s.recv(1000)
print(resp)
```
`sendall()` - sends decoded value + newline (server expects it).

`recv()` - reads server response.

Example output:
```bash
b'[+] Good job ! Here is your flag: [INTENTIONALLY_OMMITED_FLAG] \n'
```

### CONCEPTS
`Sockets` → connect, send, receive

`Regex` → extract quoted substring

`Base64` → decode encoded string

`Bytes vs Strings` → must send b"\n"

### Example Run

```bash
$ python root-me-TCP-Encoded-String.py
encoded string: ZllsRlBHSExYZHN0
decoded string: fYlFPGHLXdst
b'[+] Good job ! Here is your flag: FLAG_OMMITED\n'
```


[back to top](#1-root-me-tcp-encoded-string-challenge)

[HOME](/README.md)