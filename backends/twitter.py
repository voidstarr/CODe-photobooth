import tweepy

class Twitter(object):
    
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth)

    def post_photo(self, filename, status_text=""):
        self.api.update_with_media(filename, status_text)
