import tweepy

# API情報 
BEARER_TOKEN        = "AAAAAAAAAAAAAAAAAAAAAK1tcwEAAAAAIB4QgUopSxqOrKTGsF2DOXFzMEg%3DSUmGqxQCsqOPUBAMx4rqqlGtq72VdooeUWqsY5FTCJbj6anxVG"
API_KEY             = "hk5CU83eucFZg9sDl3GvFE6qd"
API_SECRET          = "55LYVdlJwkCpXzbqK5Kp48GBaQd4oZXBvstSaBvLeOIGiczSGj"
ACCESS_TOKEN        = "3053396588-zi0u9IJauIyg8uhDcfzmS80toc6SHJKBysbR6Ed"
ACCESS_TOKEN_SECRET = "2DL5MQMThAXjT6x58A8uR202i54IlkWUHXEATk0HYDhoq" 

# 認証 v2では対応してない。Essentialだとv2のみ。使うのであればElevatedにアップデートしないといけない
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# キーワードからツイートを取得
api = tweepy.API(auth)
tweets = api.search_tweets(q=['Python'], count=10)

for tweet in tweets:
    print('-----------------')
    print(tweet.text)