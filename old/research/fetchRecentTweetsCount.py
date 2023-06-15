import tweepy

# API情報
BEARER_TOKEN        = "AAAAAAAAAAAAAAAAAAAAAK1tcwEAAAAAIB4QgUopSxqOrKTGsF2DOXFzMEg%3DSUmGqxQCsqOPUBAMx4rqqlGtq72VdooeUWqsY5FTCJbj6anxVG"
API_KEY             = "hk5CU83eucFZg9sDl3GvFE6qd"
API_SECRET          = "55LYVdlJwkCpXzbqK5Kp48GBaQd4oZXBvstSaBvLeOIGiczSGj"
ACCESS_TOKEN        = "3053396588-zi0u9IJauIyg8uhDcfzmS80toc6SHJKBysbR6Ed"
ACCESS_TOKEN_SECRET = "2DL5MQMThAXjT6x58A8uR202i54IlkWUHXEATk0HYDhoq" 

client = tweepy.Client(bearer_token    = BEARER_TOKEN,
                           consumer_key    = API_KEY,
                           consumer_secret = API_SECRET,
                           access_token    = ACCESS_TOKEN,
                           access_token_secret = ACCESS_TOKEN_SECRET,
                          )

# ★必要情報入力
searchWord = "#ワイルドリフト"  # 検索対象
tweets = client.get_recent_tweets_count(query = searchWord)
tweetCount = tweets.meta['total_tweet_count']
print(tweetCount)