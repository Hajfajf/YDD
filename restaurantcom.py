#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api.urlfetch import fetch
from google.appengine.ext.webapp import util, template
import gzip
import base64
import StringIO
import datetime
from credentials import CJCredentials
from lxml import etree
from google.appengine.ext import db

class RestaurantcomCoupon(db.Model):
    restaurant_name = db.StringProperty()
    search_name = db.StringProperty()
    address_street = db.StringProperty()
    address_city = db.StringProperty()
    address_state = db.StringProperty()
    address_zip = db.StringProperty()
    value = db.StringProperty()
    restrictions = db.StringProperty()
    url = db.StringProperty()
    active = db.BooleanProperty()
    last_update_prov = db.DateTimeProperty()
    yelpid_matched = db.BooleanProperty()
    yelpid = db.StringProperty()
    last_update = db.DateTimeProperty(auto_now_add=True)

class GetProductCatalog(webapp2.RequestHandler):
    def get(self):
        user = CJCredentials.user
        password = CJCredentials.password
        url = 'http://datatransfer.cj.com/datatransfer/files/3813599/outgoing/productcatalog/127262/Restaurant_com-Product_Catalog.xml.gz'

        # fetch gziped fil
        catalogResponse = fetch(url, headers={
            "Authorization": "Basic %s" % base64.b64encode(user + ':' + password)
        }, deadline=10000000)

        # the response content is in catalogResponse.content
        # un gzip the file
        f = StringIO.StringIO(catalogResponse.content)
        c = gzip.GzipFile(fileobj=f)
        content = c.read()

        # create something readable by lxml
        xml = StringIO.StringIO(content)
        del f
        del c
        del content

        # parse the file
        tree = etree.iterparse(xml, tag='product')

        for event, element in tree:
            if element.findtext('manufacturer') == 'New York':
                if RestaurantcomCoupon.get_by_key_name(element.findtext('sku')):
                        coupon = RestaurantcomCoupon.get_by_key_name(element.findtext('sku'))
                        if coupon.last_update_prov != datetime.datetime.strptime(element.findtext('lastupdated'), "%d/%m/%Y"):
                            name = element.findtext('name')
                            coupon.restaurant_name = name
                            coupon.search_name = name.lower()
                            coupon.restaurant_id = ''
                            coupon.address_street = element.findtext('keywords').split(',')[0]
                            coupon.address_city = element.findtext('manufacturer')
                            coupon.address_state = element.findtext('publisher')
                            coupon.address_zip = element.findtext('manufacturerid')
                            coupon.value = '$' + element.findtext('price') + ' for $' + element.findtext('retailprice')
                            coupon.restrictions = element.findtext('warranty')
                            coupon.url = element.findtext('buyurl')
                            if element.findtext('instock') == 'YES':
                                coupon.active = True
                            else:
                                coupon.active = False
                            coupon.last_update_prov = datetime.datetime.strptime(element.findtext('lastupdated'), "%d/%m/%Y")
                            coupon.put()
                        else:
                            pass
                else:
                        coupon = RestaurantcomCoupon(key_name = element.findtext('sku'))
                        coupon.restaurant_name = element.findtext('name')
                        coupon.restaurant_id = ''
                        coupon.address_street = element.findtext('keywords').split(',')[0]
                        coupon.address_city = element.findtext('manufacturer')
                        coupon.address_state = element.findtext('publisher')
                        coupon.address_zip = element.findtext('manufacturerid')
                        coupon.value = '$' + element.findtext('price') + ' for $' + element.findtext('retailprice')
                        coupon.restrictions = element.findtext('warranty')
                        coupon.url = element.findtext('buyurl')
                        if element.findtext('instock') == 'YES':
                            coupon.active = True
                        else:
                            coupon.active = False
                        coupon.yelpid_matched = False
                        
                        coupon.last_update_prov = datetime.datetime.strptime(element.findtext('lastupdated'), "%d/%m/%Y")
                        coupon.put()
            else:
                pass

            element.clear()



app = webapp2.WSGIApplication([
    ('/update/restaurantcom', GetProductCatalog),
], debug=True)