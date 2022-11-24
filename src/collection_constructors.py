from tweepy import Paginator, Client
from elasticsearch import Elasticsearch
from .neoconnection import NeoConnection
from .neomethods import *
from .elasticmethods import *

def build_hashtag_collection(neo_connection: NeoConnection, neo_client: Client, es_client: Elasticsearch, hashtags, start_date, relations, es_index_name): 
    query = '';
    if isinstance(hashtags, list):              
        for hashtag in hashtags:
            query += "#{} ".format(hashtag)      # Add each hashtag to query
    else:
        query = "#{}".format(hashtags)          # Single hashtag
    query += 'lang:en -is:retweet' 

    for tweets in Paginator(
        neo_client.search_all_tweets,
        query=query,
        start_time=start_date,
        max_results=100,
        tweet_fields=["created_at", "public_metrics", "entities"]
    ):
        if tweets.data:
            for tweet in tweets.data:
                create_tweet(neo_connection, tweet, relations, es_index_name)

                # Format data for ES ingestion
                doc = {
                    'id': tweet.data['id'],
                    'created_on': tweet.data['created_at'],
                    'likes': tweet.data['public_metrics']['like_count'],
                    'retweets': tweet.data['public_metrics']['retweet_count'],
                    'replies': tweet.data['public_metrics']['reply_count'],
                    'text': tweet.data['text']
                }

                # Merge into elastic search (handles both update or creation)
                merge_doc(
                    client=es_client, 
                    index_name=es_index_name, 
                    doc_id=doc['id'], 
                    doc_data=doc
                ) 

def build_tweet_collection(neo_connection: NeoConnection, neo_client: Client, es_client: Elasticsearch, tweet_ids, start_date, relations, es_index_name):
    all_usernames = []
    session = neo_connection.get_session()

    for tweet_id in tweet_ids:
        tweet = neo_client.get_tweet(
            id=tweet_id,
            tweet_fields=["author_id", "created_at", "public_metrics", "entities"],
        )
        if tweet.data is None:
            continue

        author = neo_client.get_user(id=tweet.data['author_id'])
        author_username = [author.data['username']]
        if author_username[0] not in all_usernames:
            all_usernames.append(author_username[0])
            build_username_collection(neo_connection, neo_client, author_username, start_date, relations, es_index_name)

        if tweet_exists(neo_connection, tweet_id):       # Tweet existent in graph
            update_tweet(session, tweet.data)                           
        else:
            create_tweet(neo_connection, tweet.data, relations, es_index_name)
            create_author(neo_connection, author.data['id'], tweet_id)

        # Format data for ES ingestion
        doc = {
            'type': 'tweet',
            'id': tweet.data['id'],
            'created_on': tweet.data['created_at'],
            'likes': tweet.data['public_metrics']['like_count'],
            'retweets': tweet.data['public_metrics']['retweet_count'],
            'replies': tweet.data['public_metrics']['reply_count'],
            'text': tweet.data['text']
        }

        # Merge into elastic search (handles both update or creation)
        merge_doc(
            client=es_client, 
            index_name=es_index_name, 
            doc_id=doc['id'], 
            doc_data=doc
        ) 

def build_username_collection(neo_connection: NeoConnection, neo_client: Client, es_client: Elasticsearch, usernames, start_date, relations, es_index_name):
    for username in usernames:
        user = neo_client.get_user(
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

        # Neo4j
        if user_exists(neo_connection, user.data['id']):
            update_user(neo_connection.get_session(), user.data);    
        else:
            create_user(neo_connection, neo_client, es_client, user.data, start_date, relations, es_index_name)

        # Elasticsearch 
        doc = {
            'type': 'user',
            'id': user.data['id'],
            'created_on': str(user.data['created_at'])[0:10],
            'username': user.data['username'],
            'name': user.data['name'],
            'description': user.data['description'],
            'followers': user.data['public_metrics']['followers_count'],
            'following': user.data['public_metrics']['following_count'],
            'tweet_count': user.data['public_metrics']['tweet_count']
        } 

        # Merge into elastic search (handles both update or creation)
        merge_doc(
            client=es_client, 
            index_name=es_index_name, 
            doc_id=doc['id'], 
            doc_data=doc
        ) 