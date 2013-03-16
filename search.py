"""Command line interface to the Yelp Search API."""
import json
import oauth2
import optparse
import urllib
import urllib2
import webapp2
import datetime
from google.appengine.ext.webapp import util, template
from StringIO import StringIO
from google.appengine.ext import db
from credentials import YelpCredentials
from requestreg import YelpSearchRequest
from restaurantcom import RestaurantcomCoupon

class YelpRestaurant(db.Model):
    name = db.StringProperty()
    categories = db.StringListProperty()
    category_codes = db.StringListProperty()
    phone = db.StringProperty()
    display_phone = db.StringProperty()
    image_url = db.LinkProperty()
    address_city = db.StringProperty()
    address_street = db.StringProperty()
    address_postalcode = db.StringProperty()
    address_country = db.StringProperty()
    address_state = db.StringProperty()
    address_crossstreets = db.StringProperty()
    address_neighborhoods = db.StringListProperty()
    address_latitude = db.FloatProperty()
    address_longitude = db.FloatProperty()
    address_geo_accuracy = db.IntegerProperty()
    address_area = db.StringProperty()
    rating = db.FloatProperty()
    review_count = db.IntegerProperty()
    url = db.LinkProperty()
    mobile_url = db.LinkProperty()
    quote = db.TextProperty()
    quote_img = db.LinkProperty()
    restaurant_url = db.LinkProperty(required=False)
    checked = db.BooleanProperty()
    last_update = db.DateTimeProperty(auto_now_add=True)


class YelpSearchAPI(webapp2.RequestHandler):
    yelp_unchecked = YelpRestaurant.all().filter('checked =', False)
    for yelp in yelp_unchecked:
      yelp.checked = True
      yelp.put()

    yelprequest = YelpSearchRequest.all().order('-date')[0]
    term = yelprequest.term
    location = yelprequest.location
    parser = optparse.OptionParser()

    parser.add_option('-c', '--consumer_key', dest='consumer_key', help='OAuth consumer key (REQUIRED)', default=YelpCredentials().consumer_key)
    parser.add_option('-s', '--consumer_secret', dest='consumer_secret', help='OAuth consumer secret (REQUIRED)', default=YelpCredentials().consumer_secret)
    parser.add_option('-t', '--token', dest='token', help='OAuth token (REQUIRED)', default=YelpCredentials().token)
    parser.add_option('-e', '--token_secret', dest='token_secret', help='OAuth token secret (REQUIRED)', default=YelpCredentials().token_secret)
    parser.add_option('-a', '--host', dest='host', help='Host', default=YelpCredentials().host)

    parser.add_option('-q', '--term', dest='term', help='Search term', default=term)
    parser.add_option('-l', '--location', dest='location', help='Location (address)', default=location)
    parser.add_option('-b', '--bounds', dest='bounds', help='Bounds (sw_latitude,sw_longitude|ne_latitude,ne_longitude)')
    parser.add_option('-p', '--point', dest='point', help='Latitude,longitude')
    # Not sure if current location hints are currently working
    parser.add_option('-i', '--current_location', dest='current_location', help='Current location latitude,longitude for location disambiguation')

    parser.add_option('-o', '--offset', dest='offset', help='Offset (starting position)')
    parser.add_option('-r', '--limit', dest='limit', help='Limit (number of results to return)')
    parser.add_option('-u', '--cc', dest='cc', help='Country code')
    parser.add_option('-n', '--lang', dest='lang', help='Language code')

    parser.add_option('-d', '--radius', dest='radius', help='Radius filter (in meters)')
    parser.add_option('-g', '--category', dest='category', help='Category filter')
    parser.add_option('-z', '--deals', dest='deals', help='Deals filter')
    parser.add_option('-m', '--sort', dest='sort', help='Sort')

    options, args = parser.parse_args()

    # Required options
    if not options.consumer_key:
      parser.error('--consumer_key required')
    if not options.consumer_secret:
      parser.error('--consumer_secret required')
    if not options.token:
      parser.error('--token required')
    if not options.token_secret:
      parser.error('--token_secret required')

    if not options.location and not options.bounds and not options.point:
      parser.error('--location, --bounds, or --point required')

    # Setup URL params from options
    url_params = {}
    if options.term:
      url_params['term'] = options.term
    if options.location:
      url_params['location'] = options.location
    if options.bounds:
      url_params['bounds'] = options.bounds
    if options.point:
      url_params['ll'] = options.point
    if options.offset:
      url_params['offset'] = options.offset
    if options.limit:
      url_params['limit'] = options.limit
    if options.cc:
      url_params['cc'] = options.cc
    if options.lang:
      url_params['lang'] = options.lang
    if options.current_location:
      url_params['cll'] = options.current_location
    if options.radius:
      url_params['radius_filter'] = options.radius
    if options.category:
      url_params['category_filter'] = options.category
    if options.deals:
      url_params['deals_filter'] = options.deals
    if options.sort:
      url_params['sort'] = options.sort


    def request(host, path, url_params, consumer_key, consumer_secret, token, token_secret):
      """Returns response for API request."""
      # Unsigned URL
      encoded_params = ''
      if url_params:
        encoded_params = urllib.urlencode(url_params)
      url = 'http://%s%s?%s' % (host, path, encoded_params)
      print 'URL: %s' % (url,)

      # Sign the URL
      consumer = oauth2.Consumer(consumer_key, consumer_secret)
      oauth_request = oauth2.Request('GET', url, {})
      oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                            'oauth_timestamp': oauth2.generate_timestamp(),
                            'oauth_token': token,
                            'oauth_consumer_key': consumer_key})

      token = oauth2.Token(token, token_secret)
      oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
      signed_url = oauth_request.to_url()
      print 'Signed URL: %s\n' % (signed_url,)

      # Connect
      try:
        conn = urllib2.urlopen(signed_url, None)
        try:
          response = json.loads(conn.read())
        finally:
          conn.close()
      except urllib2.HTTPError, error:
        response = json.loads(error.read())

      return response

    response = request(options.host, '/v2/search', url_params, options.consumer_key, options.consumer_secret, options.token, options.token_secret)

    yelprequest.results = int(response['total'])
    yelprequest.put()

    d = response['businesses']

    for item in d:
      restaurant = YelpRestaurant(key_name=item['id'])
      restaurant.name = item['name']
      for category in item['categories']:
         restaurant.categories += category
      try:
        restaurant.phone = item['phone']
      except:
        pass
      try:
        restaurant.display_phone = item['display_phone']
      except:
        pass
      try:
        restaurant.image_url = item['image_url']
      except:
        pass
      try:
        restaurant.address_city = item['location']['city']
      except:
        pass
      try:
        restaurant.address_street = item['location']['address'][0]
      except:
        pass
      try:
        restaurant.address_postalcode = item['location']['postal_code']
      except:
        pass
      try:
        restaurant.address_country = item['location']['country_code']
      except:
        pass
      try:
        restaurant.address_state = item['location']['state_code']
      except:
        pass
      try:
        restaurant.address_crossstreets = item['location']['cross_streets']
      except:
        pass
      try:
        restaurant.address_neighborhoods = item['location']['neighborhoods']
      except:
        pass
      try:
        restaurant.address_latitude = float(item['location']['coordinate']['latitude'])
      except:
        pass
      try:
        restaurant.address_longitude = float(item['location']['coordinate']['longitude'])
      except:
        pass
      try:
        restaurant.address_geo_accuracy = int(item['location']['geo_accuracy'])
      except:
        pass
      try:
        restaurant.rating = float(item['rating'])
      except:
        pass
      try:
        restaurant.review_count = int(item['review_count'])
      except:
        pass
      try:
        restaurant.url = item['url']
      except:
        pass
      try:
        restaurant.mobile_url = item['mobile_url']
      except:
        pass
      try:
        restaurant.quote = item['snippet_text']
      except:
        pass
      try:
        restaurant.quote_img = item['snippet_image_url']
      except:
        pass
      restaurant.checked = False
      restaurant.last_update = datetime.datetime.now()
      restaurant.put()

    def get(self):
      yelprequest = YelpSearchRequest.all().order('-date')[0]
      partner = yelprequest.related_partner
      partner_id = yelprequest.related_id
      self.redirect('/search/results?partner=' + str(partner) + '&partner_id=' + str(partner_id))


class CheckResults(webapp2.RequestHandler):
    def get(self):
      restaurants = YelpRestaurant.all().filter("checked =", False)
      related_partner = self.request.get('partner')
      #related_id = self.request.get('partner_id')
      coupon = []
      if related_partner == 'restaurantcom':
        coupon = RestaurantcomCoupon.get_by_key_name(self.request.get('partner_id'))
      template_values = {
          'restaurants': restaurants,
          'related_partner': related_partner,
          'coupon': coupon
        }
      self.response.out.write(template.render('templates/yelpresults.html', template_values))


app = webapp2.WSGIApplication([
     ('/search/api', YelpSearchAPI),
     ('/search/results', CheckResults)], debug=True)