import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import util, template
from google.appengine.ext import db
from google.appengine.api import mail
from appengine_utilities import sessions
import datetime
from restaurantcom import RestaurantcomCoupon
from search import YelpRestaurant
#from search import User

class EmailHandler(webapp2.RequestHandler):
    def get(self, page):        
        restaurant = YelpRestaurant.get_by_key_name(page)
        restcom_coupon = RestaurantcomCoupon.all().filter('yelpid =', page)
        email = 'baptiste.picard@gmail.com'
        template_values = {
          'restaurant': restaurant,
          'restcom_coupon': restcom_coupon,
          'email': email,
        }
        self.response.out.write(template.render('templates/Recommendation_Email.html', template_values))


app = webapp2.WSGIApplication([
     ('/email/(.+)', EmailHandler)], debug=True)
