from re import U
from .neoconnection import NeoConnection
from .neomethods import create_follows_relation, create_tweet_relation

def buildTweetNetwork(client, tweet_ids, connection: NeoConnection):
    usernames = []
    for tweet_id in tweet_ids:
        tweet = client.get_tweet(id = tweet_id, tweet_fields=['author_id'])
        usernames.append(client.get_user(id=tweet.data['author_id']).data['username'])

    buildUsernameNetwork(client, usernames, connection)

def buildUsernameNetwork(client, usernames, connection: NeoConnection):
    for username in usernames:
        user      = client.get_user(
                        username=username, 
                        user_fields=['created_at', 'description', 'location', 'protected', 'public_metrics']
                    )
        
        if user.data is None:
            continue;

        # Import user into Neo4j
        connection.add_transactions(
            f'''CREATE (:User{{\
                    username: "{username}",\
                    id: "{user.data['id']}",\
                    description: "${user.data['description']}",\
                    name: "{user.data['name']}",\
                    followers: "{user.data['public_metrics']['followers_count']}",\
                    following: "{user.data['public_metrics']['following_count']}",\
                    tweet_count: "{user.data['public_metrics']['tweet_count']}",\
                    protected: "{user.data['protected']}",\
                    created_on: "{str(user.data['created_at'])[0:10]}"}})'''
        )

        # Import followers
        followers = client.get_users_followers(id=user.data['id'])
        for follower in followers.data:
            create_follows_relation(follower, username, connection)
    
        # Import recent tweets (if existent)
        recent_tweets = client.get_users_tweets(
            id=user.data['id'],
            tweet_fields=['author_id', 'created_at','public_metrics', 'entities']
        )

        if recent_tweets.data:
            for tweet in recent_tweets.data:
                # Add tweet and authored by relation in neo4j
                tweet_id = tweet['id']
                text     = str(tweet['text']).replace('"', "'")
                connection.add_transactions(
                    f'''MERGE (u:User{{username: "{username}"}})\
                        MERGE (t:Tweet{{
                            id: "{tweet_id}",\
                            author_id: "{tweet['author_id']}",\
                            created_at: "{tweet['created_at']}",\
                            likes: "{tweet['public_metrics']['like_count']}",\
                            retweets: "{tweet['public_metrics']['retweet_count']}",\
                            replies: "{tweet['public_metrics']['reply_count']}",\
                            text: "{text}"}})\
                        CREATE (u)-[:AUTHORED]->(t)'''
                )

                # Push data regarding mentioned users/people/places
                if 'entities' in tweet: 
                    if 'mentions' in tweet['entities']:
                        for user in tweet['entities']['mentions']:
                            connection.add_transactions(
                                f'''MERGE (u:User {{username: "{user['username']}", id: "{user['id']}"}}) \
                                    MERGE (t:Tweet {{id: "{tweet_id}"}}) \
                                    MERGE (t)-[:MENTIONS]->(u)'''
                            )
                    
                    if 'annotations' in tweet['entities']:
                        for annotation in tweet['entities']['annotations']:
                            connection.add_transactions(
                                f'''MERGE (a:{annotation['type']} {{description: "{annotation['normalized_text']}"}}) \
                                    MERGE (t:Tweet {{id: "{tweet_id}"}}) \
                                    MERGE (t)-[:ANNOTATES {{probability: "{annotation['probability']}"}}]->(a)'''
                            )  

                # Add likes/retweets in neo4j 
                # likes    = client.get_liking_users(id=tweet['id'])
                # retweets = client.get_retweeters(id=tweet['id'])
                # if likes.data: 
                    # for tmp_user in likes.data:
                        # create_tweet_relation(tmp_user, tweet_id, 'LIKED', connection)
                # if retweets.data:
                    # for tmp_user in retweets.data:
                        # create_tweet_relation(tmp_user, tweet_id, 'RETWEETED', connection)

        connection.exec_transactions()