import sys

from neoconnection import NeoConnection

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

def extract_users(users: list):
    # Extracts the usernames provided at the given path. Assumes each username is seperated by a newline character.
    # 
    # Args:     path - path to file containing user(s)
    #           users - list in which to store the extracted user(s)
   
    #           exits() application if unsuccessful
    from os.path import exists

    if(len(sys.argv) != 2):
        print('Error: must provide a file of base username network as input.')
        exit()

    path = str(sys.argv[1])
    if(exists(path)):
        # Read all usernames from file
        with open(path) as fin:
            while(1):
                line = fin.readline()
                if not line:
                    break
                else:
                    users.append(line.rstrip())
    else:
        print('Error: input file does not exist.');
        exit();