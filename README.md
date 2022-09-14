# twitter-collector

**Use Case 1**: A set of tweets is provided - create a network consisting of the tweets' authors and their followers.  
  
**Use Case 2**: A list of usernames is provided. 

# Instructions
This repository's dependencies were created with conda in mind. To setup the dependencies, simply clone the repo and create a conda env with the following command:  
`conda create --name <env> --file conda-requirements.txt`  
  
A docker config file will be added later. For now, to setup a neo4j container assure you have the latest neo4j image installed within docker and run the following:  
`docker run -p7474:7474 -p7687:7687 -d --name <container_name> --env NEO4J_AUTH=neo4j/testing123 neo4j:latest`  
  
If you wish to have persistent storage (for container data and logs), then create two volumes within docker by using:  
`docker volume create <name>`  
where the name for the first container can be 'neo-data' and the second 'neo-logs', for neo4j data and logs, respectively.   
  
Once the volumes are created, simply run the neo4j image but assure to mount the volumes to the image:  
`docker run -p7474:7474 -p7687:7687 -d --name <container_name> -v data:/neo-data logs:/neo-logs --env NEO4J_AUTH=neo4j/testing123 neo4j:latest`

## Addition information
- All data which is pulled and used to create the networks will be stored in both neo4j and elasticsearch.
- Come up with 2 plans
  1. Build the network from scratch (i.e. deleting entire network and rebuilding it)
  2. Updating rather than deleting and constructing from nothing
