import re

path= "../../../resources/files/regex/data.txt"

with open(path,"r") as f:
    d = f.read()
    # print(repr(d))
    patt = re.compile(r'^\w+\s\w+$\n.*$\n.*$\n.*@.*$',re.MULTILINE)

    comb = patt.finditer(d)
    lis = {}
    for i in comb:
        # a,b = i.span()
        # print(d[a:b])

        name,phone,address,email = i.group().splitlines()
        adpatt = re.compile(r'^(\d+.*\.),\s+(.+)\s([A-Z]+)\s(\d+)')
        ad = adpatt.finditer(address)




        print("names: ",name)
        print(f"phone:  {phone}")
        print("address: ")
        for x in ad:
            street,city,state,zipc = x.groups()
            print("\tstreet: ",street)
            print("\tcity: ",city)
            print("\tstate: ",state)
            print("\tzip: ",zipc)
        print("email: ",email,end="\n\n\n")

       

    # print(lis)