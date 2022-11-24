from elasticsearch import Elasticsearch

def create_index(client: Elasticsearch, index_name):
    '''
    Attempts to create an index at the connection provided by client (ElasticSearch client).
    Returns:    1 if successful
                0 if not (e.g. index already exists)
    '''    
    if client is None or client.indices.exists(index=index_name):
        return 0
    
    try:
        client.indices.create(index='users')
    except Exception as e:
        print('[-] Error: ', e)

    return 1

def delete_index(client: Elasticsearch, index_name):
    '''
    Attempts to delete an index at the connection provided by client (ElasticSearch client).
    Returns:    1 if successful
                0 if not (e.g. index does not exist)
    '''
    if client is None or not client.indices.exists(index=index_name):
        return 0
    
    try:
        client.indices.delete(index=index_name)
    except Exception as e:
        print('[-] Error: ', e)
    
    return 1

def update_doc(client: Elasticsearch, index_name, doc_data):
    '''
    Attempts to update a document within the provided index.
    Returns:    1 if successful
                0 if not (e.g. document or index does not exist)
    '''
    if client is None or not client.exists(index=index_name, id=doc_data['id']):
        return 0
    
    try:
        client.update(index=index_name, id=doc_data['id'], doc=doc_data)
    except Exception as e:
        print('[-] Error: ', e)

def create_doc(client: Elasticsearch, index_name, doc_data):
    '''
    Attempts to create a document within the provided index.
    Returns:    1 if successful
                0 if not (e.g. index does not exist or client invalid)
    ''' 
    if client is None or not client.indices.exists(index=index_name):
        return 0
    
    try:
        client.create(index=index_name, id=doc_data['id'], document=doc_data)
    except Exception as e:
        print('[-] Error: ', e)
    
    return 1

'''
    es_client = Elasticsearch(
        "https://localhost:9200",
        ca_certs="./src/http_ca.crt",
        basic_auth=("elastic", config.ELASTIC_PASSWORD)
    )

    index = 'tweet-index'
    # DOES INDEX EXIST
    es_client.indices.exists(index=index)    # True

    # DOES TWEET EXIST
    es_client.exists(index='tweet-index', id=19213)      # True
    es_client.exists(index='tweet-index', id=19211)      # False

    tweet_data = {
        "likes": 333,
        "retweets": 333,
    }

    # CREATE A TWEET DOC
    try:
        es_client.create(index=index, id=101, document=tweet_data)
    except Exception as e:
        print('error: doc already exists')

    # UPDATE A TWEET DOC
    es_client.update(index=index, id=101, doc=tweet_data)

    es_client.close();
    return
    ''' 