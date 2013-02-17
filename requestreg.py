import webapp2
from google.appengine.ext import db

class YelpSearchRequest(db.Model):
    term = db.StringProperty()
    location = db.StringProperty()
    related_partner = db.StringProperty()
    related_id = db.StringProperty()
    results = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class YelpSearchRequestHandler(webapp2.RequestHandler):
    def get(self):
       request = YelpSearchRequest()
       request.term = self.request.get('term')
       request.location = self.request.get('location')
       request.related_partner = self.request.get('partner')
       request.related_id = self.request.get('id')
       request.put()
       self.redirect('/search/api') 

app = webapp2.WSGIApplication([
     ('/search/request', YelpSearchRequestHandler)], debug=True)