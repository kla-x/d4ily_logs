import requests
import time
import asyncio
import aiohttp

url = 'http://127.0.0.1:80/delay/'
baseurl = 'http://127.0.0.1:80/'

verbose = True
def timer_dec(finc):

    def modded_func(*args, **kwargs):
        
        start = time.time()
        finc(*args, **kwargs)
        stop = time.time()
        print('took: {} sec'.format(stop - start))

    return modded_func


@timer_dec
def make_req(sleep_t):
    option = '/delay/'
    r  = requests.get(baseurl + option + str(sleep_t))
    print(r.text)

# @timer_dec
def post_req(sleep_t, req_no):  
    body = {"request_no ": req_no}
    option = '/delay/'
    p = requests.post(baseurl + option + str(sleep_t),json=body)
    if verbose:
        print(p.json().get('data'))



# makes one get and post request with delay time as argument

# make_req(.2) # tells server to delay for .2 sec before response
# post_req(0.01, 5)

#making 5000 requests, uniform delay of .01 sec
async def async_post_req(session, sleep_t, req_no):  
    body = {"request_no ": req_no}
    option = '/delay/'
    async with session.post(baseurl + option + str(sleep_t),json=body) as ress:
        
        p = await ress.json()

        if verbose:
            print(p.get('data'))


@timer_dec
def sequential_reqs(delay,req_count):
    for i in range(req_count):
        post_req(delay, i+1)
    
    print('made: {} requests'.format(req_count))


# sequential_reqs(.01,500)

@timer_dec
def async_requests(delay, req_count):
     
    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = [async_post_req(session, delay,i) for i in range(req_count) ]
            await asyncio.gather(*tasks)
    asyncio.run(main())
    print('made: {} requests'.format(req_count))


sequential_reqs(0,50)
async_requests(0,50)