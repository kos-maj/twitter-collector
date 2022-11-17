from .neoconnection import NeoConnection

def update_tweet(session, tweet_data):
    # Updates a tweet which already exists within the neo4j database
    session.run("MATCH (t:Tweet {id: $id})"
                "SET t.likes = $like_count"
                "t.retweets: $retweet_count"
                "t.replies: $reply_count",
                id=tweet_data['id'], 
                like_count=tweet_data['public_metrics']['like_count'],
                retweet_count=tweet_data['public_metrics']['retweet_count'],
                reply_count=tweet_data['public_metrics']['reply_count']
    )

def update_user(session, user_data):
    # Updates a user who already exists within the neo4j database
    session.run("MATCH (n:User{id: $id})"
                "SET n.followers = $followers, n.following = $following, n.tweet_count = $tweet_count",
                id=user_data['id'], 
                followers=user_data['public_metrics']['followers_count'], 
                following=user_data['public_metrics']['following_count'],
                tweet_count=user_data['public_metrics']['tweet_count']
    )

def get_users(connection: NeoConnection):
    return connection.exec_query("MATCH (n:User) RETURN (n.username) AS username", getResult=True)
    
def get_tweets(connection: NeoConnection):
    return connection.exec_query("MATCH (n:Tweet) RETURN (n.id) AS tweetId", getResult=True)

def tweet_exists(connection: NeoConnection, tweet_id):
    if len(connection.exec_query(
        f'MATCH (n:Tweet{{id: {tweet_id}}}) RETURN (n)',
        getResult=True
    )):
        return True
    return False

def user_exists(connection: NeoConnection, user_id):
    if len(connection.exec_query(
        f'MATCH (n:User{{id: {user_id}}}) RETURN (n)',
        getResult=True
    )):
        return True
    return False

# def create_tweet():

# def create_user():

def create_tweet_relation(user, tweet_id, relation, connection: NeoConnection):
    session = connection.get_session()
    username = str(user["username"]).replace('"', "")
    name = str(user["name"]).replace('"', "")

    session.run("MERGE (:Follower {username: $username, user_id: $id, name: $name)",
                username = username, id = user['id'], name = name
    )
    session.run("MATCH (p:Follower {username: $username}), t(Tweet {id: $id})"
                "CREATE (p)-[:$relation]->(t)",
                username = username, id = tweet_id, relation = relation
    )
    session.run("MATCH (p:User {username: $username}), (t:Tweet {id: $id})"
                "CREATE (p)-[:$relation]->(t)",
                username = username, id = tweet_id, relation = relation
    )

def create_follows_relation(user, main_username, connection: NeoConnection):
    session = connection.get_session()
    username = str(user["username"]).replace('"', "")
    name = str(user["name"]).replace('"', "")

    session.run("MERGE (:Follower {username: $username, id: $id, name: $name})",
                username = username, id = user['id'], name = name
    )
    session.run("MATCH (p1:Follower {username: $username}), (p2:User {username: $main_username})"
                "CREATE (p1)-[:FOLLOWS]->(p2)",
                username = username, main_username = main_username
    )
    session.run("MATCH (p1:User {username: $username}), (p2:User {username: $main_username})"
                "CREATE (p1)-[:FOLLOWS]->(p2)",
                username = username, main_username = main_username
    )

def extract_identifiers(*, path: str, data: list):
    # Extracts the id's provided at the given path. Assumes each id is seperated by a newline character.
    #
    # Args:     path - path to file containing user(s)
    #           data - list to which extracted users/ids will be pushed to
    from os.path import exists

    while True:
        if exists(path):
            # Read all id's from file
            with open(path) as fin:
                while True:
                    line = fin.readline()
                    if not line:
                        break
                    else:
                        data.append(line.rstrip())
            break
        else:
            print("[-] Error: input file does not exist.")
