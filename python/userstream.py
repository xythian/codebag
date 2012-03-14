#
# A little toy that connects to a Twitter userstream and rebroadcasts on a ZMQ PUB socket.
# It also writes the raw data into a msgpack file.
#

import sys
import eventlet
eventlet.monkey_patch()
import oauth2 as oauth
from eventlet.green import urllib2, zmq
import traceback
import json
import time
import logging
from msgpack import Packer

LOG = logging.getLogger('userstream')

class EndException(Exception):
    pass

def read_bytes(source, cnt, prefix=""):
    data = prefix
    remaining = cnt - len(data) 
    while remaining:
        chunk = source.read(remaining)
        if not chunk:
            raise EndException('EOL during chunk')
        data += chunk
        remaining = cnt - len(data)
    return data

def read_line(source):
    # TODO: smarter buffering/parsing, but given the volume of my userstream it doesn't matter
    c = source.read(1)
    result = []
    while c:
        if c == '\n':
            return "".join(result)        
        result.append(c)
        c = source.read(1)
    raise EndException("EOF")

def read_events(response):
    sock = ctx.socket(zmq.PUB)
    sock.connect('inproc://raw_events')
    data = ""    
    try:
        while True:
            line = read_line(response).strip()
            if not line:
                continue            
            l = int(line.strip())
            event = read_bytes(response, l)
            sock.send(event)
    except EndException, e:
        LOG.info("EOF while reading stream, retry in 10")
        eventlet.spawn_after(10, consume_stream)
    except:
        del response
        traceback.print_exc()        

def consume_stream():
    url = "https://userstream.twitter.com/2/user.json"
    token = oauth.Token(key=TOKEN_KEY
                        secret=TOKEN_SECRET)
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)

    req = oauth.Request.from_consumer_and_token(consumer, token=token, http_method="GET", http_url=url + "?replies=all&delimited=length", parameters=None, body='', is_form_encoded=False)
    
    signature_method = oauth.SignatureMethod_HMAC_SHA1()

    req.sign_request(signature_method, consumer, token)
    hrequest = urllib2.Request(url=req.to_url())
    response = urllib2.urlopen(hrequest)

    if response.code == 200:
        LOG.info("Consuming stream")
        eventlet.spawn_n(read_events, response)
    else:
        LOG.info('Retry consume_stream')
        eventlet.spawn_after(60, consume_stream)

def configure_logging():
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    output = logging.FileHandler('acquire.log', encoding='utf-8')
    output.setFormatter(formatter)
    l = logging.getLogger()
    l.addHandler(console)
    l.addHandler(output)
    l.setLevel(logging.DEBUG)

def log_events():
    sock = ctx.socket(zmq.SUB)
    sock.bind("inproc://raw_events")
    sock.setsockopt(zmq.SUBSCRIBE, "")
    packer = Packer()
    with open('tweets.%d.msgpack' % int(time.time()), 'wb') as f:
        # intentionally writing the raw bytes and not parsing it here
        while True:
            msg = sock.recv()
            LOG.debug('event received: %d bytes', len(msg))
            f.write(packer.pack({'time' : int(time.time()), 'event' : msg}))
            f.flush()

# this does not backfill from the REST API, but it probably should

ctx = zmq.Context()
def main():
    configure_logging()
    LOG.info("Startup")
    eventlet.spawn_n(log_events)
    eventlet.sleep(0.100)
    eventlet.spawn_n(consume_stream)
    while True:
        # we could maybe do something more interesting here
        # we don't run consume_stream because consume_stream uses spawn_after to reschedule itself
        # if it gets disconnected
        eventlet.sleep(300)
    
    

if __name__ == '__main__':
    main()
