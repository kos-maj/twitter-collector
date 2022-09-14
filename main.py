import src.config as config
import sys

from src.neoconnection import NeoConnection
from src.data_extraction import push_data

'''
TO DO: Create network out of json data file (entities, relationships, etc.) -- DONE
TO DO: test centrality algorithms on the aforementioned networks
TO DO: implement run pageRank algorithm
TO DO: read multiple files/directories -- DONE
TO DO: Incorporate referenced tweets -- DONE
'''

# Global variable which will be instantiated to neo4j connection
g_conn = None

def main():

    skipDataPush = False
    g_conn = NeoConnection(uri = "bolt://127.0.0.1:7687", user = "neo4j", pwd = "testing123")
    
    for arg in sys.argv:
        if(arg == '-s'):
            skipDataPush = True
            break
            
    if not skipDataPush:
        push_data(g_conn, folderpath='data')

    g_conn.run_pageRank(name='annotatedOrganizations', entities=['Organization','Tweet'], rel='ANNOTATES', attribute='description')
    g_conn.run_pageRank(name='mentionedUsers', entities=['User','Tweet'], rel='MENTIONS', attribute='username')
    g_conn.close()
    return 0
    

if __name__ == "__main__":
    main();