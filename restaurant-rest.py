import json
import oauth2
import optparse
import urllib
import urllib2
from google.appengine.ext import webapp
from google.appengine.ext import db
from credentials import CJCredentials

class RestaurantRequest(db.Model):
    advertiser_ids= '867296'

class CJ_API(webapp.RequestHandler):
    parser = optparse.OptionParser()
    advertiser_ids = RestaurantRequest().advertiser_ids

    parser.add_option('-a', '--authorization', dest='authorization', default=CJCredentials().developer_key)
    parser.add_option('-b', '--website_id', dest='website-id', default=CJCredentials().website_id)
    parser.add_option('-c', '--host', dest='host', help='Host', default=CJCredentials().host)

    parser.add_option('-s', '--advertiser_ids', dest='advertiser-ids', default=RestaurantRequest().consumer_secret)

    options, args = parser.parse_args()

    # Required options
    if not options.authorization:
      parser.error('--authorization required')
    if not options.website_id:
      parser.error('--website_id required')

    url_params = {}
    if options.advertiser_ids:
      url_params['advertiser-ids'] = options.advertiser_ids


    def request(host, url_params, authorization, website_id):

      # Unsigned URL
      encoded_params = ''
      if url_params:
        encoded_params = urllib.urlencode(url_params)
      url = 'https://%s?%s' % (host, encoded_params)
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
    print json.dumps(response, sort_keys=True, indent=2)

def main():
    application = webapp.WSGIApplication([
        ('/search', CJ_API)], debug=True)