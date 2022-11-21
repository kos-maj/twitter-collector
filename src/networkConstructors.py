from tweepy import Paginator
from .neoconnection import NeoConnection
from .neomethods import *

def buildHashtagNetwork(connection: NeoConnection, client, hashtags, start_date, relation_options): 
    query = '';
    if isinstance(hashtags, list):              
        for hashtag in hashtags:
            query += "#{} ".format(hashtag)      # Add each hashtag to query
    else:
        query = "#{}".format(hashtags)          # Single hashtag
    query += 'lang:en -is:retweet' 

    for tweets in Paginator(
        client.search_all_tweets,
        query=query,
        start_time=start_date,
        max_results=100,
        tweet_fields=["created_at", "public_metrics", "entities"]
    ):
        if tweets.data:
            for tweet in tweets.data:
                create_tweet(connection, tweet)

def buildTweetNetwork(connection: NeoConnection, client, tweet_ids, start_date, relation_options):
    all_usernames = []
    session = connection.get_session()

    for tweet_id in tweet_ids:
        tweet = client.get_tweet(
            id=tweet_id,
            tweet_fields=["author_id", "created_at", "public_metrics", "entities"],
        )
        if tweet.data is None:
            continue

        author = client.get_user(id=tweet.data['author_id'])
        author_username = [author.data['username']]
        if author_username[0] not in all_usernames:
            all_usernames.append(author_username[0])
            buildUsernameNetwork(client, author_username, start_date, connection)

        if tweet_exists(connection, tweet_id):       # Tweet existent in graph
            update_tweet(session, tweet.data)  
        else:
            create_tweet(connection, tweet.data)
            create_author(connection, author.data['id'], tweet_id)

def buildUsernameNetwork(connection: NeoConnection, client, usernames, start_date, relation_options):
    for username in usernames:
        user = client.get_user(
            username=username,
            user_fields=[
                "created_at",
                "description",
                "location",
                "protected",
                "public_metrics",
            ],
        )
        if user.data is None:
            continue

        if user_exists(connection, user.data['id']):
            update_user(connection.get_session(), user.data);    
        else:
            create_user(connection, client, user.data, start_date)