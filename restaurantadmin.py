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
from google.appengine.ext import db
from restaurantcom import RestaurantcomCoupon


class AdminHandler(webapp2.RequestHandler):
    def get(self):
        match_filter = self.request.get('matched')
        group = self.request.get('group')
        total_coupons = RestaurantcomCoupon.all().count()
        if match_filter:
            if match_filter == 'True':
                coupons = RestaurantcomCoupon.all().filter('yelpid_matched =', True).order('search_name')
            if match_filter == 'False':
                coupons = RestaurantcomCoupon.all().filter('yelpid_matched =', False).order('search_name')
        else:
            coupons = RestaurantcomCoupon.all().order('search_name')
        if group:
            if group < 'a':
                coupons = coupons.filter('search_name <', '9'+u"\ufffd")
            else:
                coupons = coupons.filter('search_name >=', group)
                coupons = coupons.filter('search_name <', group+u"\ufffd")
        template_values = {
          'coupons': coupons,
          'group': group,
          'total_coupons': total_coupons,
          'match_filter': match_filter,
        }
        self.response.out.write(template.render('templates/admin-restaurantcom.html', locals()))

class LinkHandler(webapp2.RequestHandler):
    def post(self):
        coupon = RestaurantcomCoupon.get_by_key_name(self.request.get('coupon_id'))
        coupon.yelpid = self.request.get('yelp_id')
        coupon.yelpid_matched = True
        coupon.put()

        sameid_coupons = RestaurantcomCoupon.all().filter('restaurant_name =', coupon.restaurant_name)
        if sameid_coupons:
            for sameid_coupon in sameid_coupons:
                if sameid_coupon.address_street == coupon.address_street:
                    sameid_coupon.yelpid = self.request.get('yelp_id')
                    sameid_coupon.yelpid_matched = True
                    sameid_coupon.put()
                else:
                    pass

        self.redirect('/admin/overview')



app = webapp2.WSGIApplication([
    ('/admin/overview', AdminHandler),
    ('/admin/link', LinkHandler)], debug=True)