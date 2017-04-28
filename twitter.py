import tweepy

consumer_key = "u3ZGuIoi1eQQUJjU0fdQDKJEa"
consumer_secret = "vbmq7oo68MteWO2eixC5HpoTHox5R1LfRhhGY91E2HD1HNTs9W"

access_token = "856995340901269504-7l5FQctovxaqxQ4P0EdOWX6d6c4I2b5"
access_token_secret = "qycoys4nMhTBtfKioQNNTDoU1TF8XpbUHpPKF8sa5bzCZ"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print tweet.text

api.update_with_media("/home/pi/photos/photos-0000/1488162063.jpg", "This is a test.")
