import tweepy
from pprint import pprint

# API情報
BEARER_TOKEN        = "AAAAAAAAAAAAAAAAAAAAAK1tcwEAAAAAIB4QgUopSxqOrKTGsF2DOXFzMEg%3DSUmGqxQCsqOPUBAMx4rqqlGtq72VdooeUWqsY5FTCJbj6anxVG"
API_KEY             = "hk5CU83eucFZg9sDl3GvFE6qd"
API_SECRET          = "55LYVdlJwkCpXzbqK5Kp48GBaQd4oZXBvstSaBvLeOIGiczSGj"
ACCESS_TOKEN        = "3053396588-zi0u9IJauIyg8uhDcfzmS80toc6SHJKBysbR6Ed"
ACCESS_TOKEN_SECRET = "2DL5MQMThAXjT6x58A8uR202i54IlkWUHXEATk0HYDhoq" 

# クライアント関数を作成
def ClientInfo():
    client = tweepy.Client(bearer_token    = BEARER_TOKEN,
                           consumer_key    = API_KEY,
                           consumer_secret = API_SECRET,
                           access_token    = ACCESS_TOKEN,
                           access_token_secret = ACCESS_TOKEN_SECRET,
                          )
    
    return client

# ★必要情報入力
search    = "#モバレ"  # 検索対象
tweet_max = 100           # 取得したいツイート数(10〜100で設定可能)

# 関数
def SearchTweets(search,tweet_max):    
    # 直近のツイート取得
    tweets = ClientInfo().search_recent_tweets(query = search, max_results = tweet_max)

    # 取得したデータ加工
    results     = []
    tweets_data = tweets.data

    # tweet検索結果取得
    if tweets_data != None:
        for tweet in tweets_data:
            obj = {}
            obj["tweet_id"] = tweet.id      # Tweet_ID
            obj["text"] = tweet.text  # Tweet Content
            results.append(obj)
    else:
        results.append('')
        
    # 結果出力
    return results

# 関数実行・出力
print(len(SearchTweets(search,tweet_max)))
#pprint(SearchTweets(search,tweet_max))