#!/usr/bin/env python

pos = (25, 121)
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
import settings as settings


def getgeohash(pos):

    import datetime
    import urllib
    from hashlib import md5
    from math import sqrt
    import struct

    if pos[1] < -30:
        td30 = 0
    else:
        td30 = 1
    if pos[0] < 0:
        south = -1
    else:
        south = 1
    if pos[1] < 0:
        west = -1
    else:
        west = 1

    date = datetime.date.today()
    dow = urllib.urlopen((date - datetime.timedelta(td30)).strftime("http://irc.peeron.com/xkcd/map/data/%Y/%m/%d")).read()
    if '404 Not Found' in dow:
        dow = 10000.0

    sum = md5("%s-%s" % (date, dow)).digest()
    n, w = [str(d*(abs(a)+f)) for d, f, a in zip((south, west),
              [x/2.**64 for x in struct.unpack_from(">QQ", sum)], pos)]
    # hashee = "%s-%.2f" %(date, float(dow))
    # hashed = md5(hashee).hexdigest()
    # p = (hashed[0:16], hashed[16:])
    # hashpos = [float.fromhex("0.%s" %x) for x in p]
    return (n, w)

def gowallahash(pos):
    from gowalla import Gowalla
    gowalla = Gowalla(api_key=settings.GOWALLA_API)
    radius = 50
    spots = gowalla.spots(lat=pos[0], lng=pos[1], radius=radius)
    if (len(spots['spots']) == 0):
        result = (None, None, None, pos)
    else:
        nearest = spots['spots'][0]
        urlbase = "http://gowalla.com"
        url = urlbase + nearest['url']
        imgurl = nearest['_image_url_50']
        name = nearest['name']
        result = (url, imgurl, name, pos)
    return result

class MainPage(webapp.RequestHandler):
    def get(self):
        url, imgurl, name, position = gowallahash(getgeohash(pos))
        if url is None:
            message = "No nearby Gowalla spot >.<"
        else:
            message = None

        template_values = {
            'posnorth': position[0],
            'poswest': position[1],
            'message': message,
            'url': url,
            'imgurl': imgurl,
            }
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication([('/', MainPage)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
