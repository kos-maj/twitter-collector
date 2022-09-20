from .neoconnection import NeoConnection

def create_tweet_relation(user, tweet_id, relation, connection: NeoConnection):
    username = str(user['username']).replace('"', '')
    name     = str(user['name']).replace('"', '')
    cmd_1    = f'''MERGE (:Follower{{\
                    username: "{username}",\
                    user_id: "{user['id']}",\
                    name: "{name}"\
                }})'''
    cmd_2   = f'''MATCH (p:Follower{{username: "{username}"}}), (t:Tweet{{id: "{tweet_id}"}})\
                CREATE (p)-[:{relation}]->(t)'''
    cmd_3   = f'''MATCH (p:User{{username: "{username}"}}), (t:Tweet{{id: "{tweet_id}"}})\
                CREATE (p)-[:{relation}]->(t)'''
    
    connection.add_transactions([cmd_1, cmd_2, cmd_3])

def create_follows_relation(user, main_username, connection: NeoConnection):
    username = str(user['username']).replace('"', '')
    name     = str(user['name']).replace('"', '')
    cmd_1    = f'''MERGE (:Follower{{\
                    username: "{username}",\
                    user_id: "{user['id']}",\
                    name: "{name}"\
                }})'''            
    cmd_2   = f'''MATCH (p1:Follower{{username: "{username}"}}), (p2:User{{username: "{main_username}"}})\
                CREATE (p1)-[:FOLLOWS]->(p2)'''
    cmd_3   = f'''MATCH (p1:User{{username: "{username}"}}), (p2:User{{username: "{main_username}"}})\
                CREATE (p1)-[:FOLLOWS]->(p2)'''

    connection.add_transactions([cmd_1, cmd_2, cmd_3])

def extract_identifiers(*, path: str, data: list):
    # Extracts the id's provided at the given path. Assumes each id is seperated by a newline character.
    # 
    # Args:     path - path to file containing user(s)
    #           data - list to which extracted users/ids will be pushed to
    from os.path import exists

    while True:
        if(exists(path)):
            # Read all id's from file
            with open(path) as fin:
                while(1):
                    line = fin.readline()
                    if not line:
                        break
                    else:
                        data.append(line.rstrip())
            break
        else:
            print('[-] Error: input file does not exist.')