# twitter-collector

**Use Case 1**: A set of tweets is provided - create a network consisting of the tweets' authors and their followers.  
  
**Use Case 2**: A list of usernames is provided. 

## Addition information
- All data which is pulled and used to create the networks will be stored in both neo4j and elasticsearch.
- Come up with 2 plans
  1. Build the network from scratch (i.e. deleting entire network and rebuilding it)
  2. Updating rather than deleting and constructing from nothing
