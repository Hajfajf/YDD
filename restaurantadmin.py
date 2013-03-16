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
from search import YelpRestaurant


class AdminHandler(webapp2.RequestHandler):
    def get(self):
        match_filter = self.request.get('matched')
        group = self.request.get('group')
        area = self.request.get('area')
        total_coupons = RestaurantcomCoupon.all().count()
        coupons = []
        restaurants = []
        duplicate_restaurant = 0

        if match_filter or group:         
            if match_filter:
                if match_filter == 'True':
                    if area:
                        coupons = RestaurantcomCoupon.all().filter('yelpid_matched =', True).filter('area =', area).order('search_name')
                    else:
                        coupons = RestaurantcomCoupon.all().filter('yelpid_matched =', True).order('search_name')
                    for coupon in coupons:
                        duplicate_restaurant = 0
                        restaurant = YelpRestaurant.get_by_key_name(coupon.yelpid)
                        for item in restaurants:
                            if item.key().name() == coupon.yelpid:
                              duplicate_restaurant = 1
                            else:
                              pass
                        if duplicate_restaurant == 0:
                            restaurants.append(restaurant)
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
          'restaurants': restaurants,
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

class UpdateAreas(webapp2.RequestHandler):
     def get(self):
        restaurants = YelpRestaurant.all()
        area1 = ["Harlem","Morningside Heights","East Harlem"]
        area2 = ["Upper West Side","Manhattan Valley"]
        area3 = ["Upper East Side","Yorkville","Roosevelt Island"]
        area4 = ["Theater District","Hell's Kitchen","Koreatown","Midtown East","Midtown West","Murray Hill"]
        area5 = ["Chelsea","Greenwich Village","Nolita","SoHo","South Village","West Village"]
        area6 = ["Alphabet City","East Village","Flatiron","Gramercy","Kips Bay","Lower East Side","NoHo","Stuyvesant Town","Union Square"]
        area7 = ["Battery Park","Chinatown","Civic Center","Financial District","Little Italy","South Street Seaport","TriBeCa","Two Bridges"]
        areanr = 0
        for restaurant in restaurants:
            areanr = 0
            for area in area1:
                if area in restaurant.address_neighborhoods:
                    areanr = 1
            for area in area2:
                if area in restaurant.address_neighborhoods:
                    areanr = 2
            for area in area3:
                if area in restaurant.address_neighborhoods:
                    areanr = 3
            for area in area4:
                if area in restaurant.address_neighborhoods:
                    areanr = 4
            for area in area5:
                if area in restaurant.address_neighborhoods:
                    areanr = 5
            for area in area6:
                if area in restaurant.address_neighborhoods:
                    areanr = 6
            for area in area7:
                if area in restaurant.address_neighborhoods:
                    areanr = 7
            if areanr != 0:
                restaurant.address_area = 'NYC' + str(areanr)
            else:
                restaurant.address_area = 'NYC'
            restaurant.put()
        
        coupons = RestaurantcomCoupon.all()
        for coupon in coupons:
            try:
                restaurant = YelpRestaurant.get_by_key_name(coupon.yelpid)
                coupon.area = restaurant.address_area
                coupon.put()
            except:
                pass

            

app = webapp2.WSGIApplication([
    ('/admin/overview', AdminHandler),
    ('/admin/link', LinkHandler),
    ('/admin/areas', UpdateAreas)], debug=True)