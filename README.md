# twitter-collector

**Use Case 1**: A set of tweets is provided - create a network consisting of the tweets' authors and their followers.  
  
**Use Case 2**: A list of usernames is provided. 

# Instructions  
  
## NEO4J Setup
Docker is required to setup the neo4j instance in which the network(s) will be constructed.  
  
You can run the following commands from the root directory of the repository:  
- `docker compose up -d`  to create the necessary images and start containers
- `docker compose stop`   to stop the containers (but not remove them or newly created images)
- `docker compose start`  to start the containers if they were previously stopped but not deleted
- `docker compose down`   to stop and remove containers, networks, images, and volumes. Note that you will have to run `docker compose up -d` again to restart services as opposed to `docker compose start`.  
  
The `/data` folder within the `/docker` directory is set as the default storage of the newly created neo4j container. It will populate as data is pushed to the database and will persist after containers are stopped and/or removed.  

## Building a Network
Note: this repository's dependencies were created with conda in mind.  

1. To setup the dependencies clone the repo and create a conda env by running `conda create --name <env> --file conda-requirements.txt`  
2. Once neo4j is setup (instructions can be found [above](#neo4j-setup)) populate the `usernames.txt` and/or the `tweets.txt` file within the `/data` directory with the twitter handles or tweet ID's (respectively) from which the network will be constructed  
3. Activate the newly created environment from step 1 by running `conda activate <name>` 
4. Run the application by executing `python3 main.py` in the command prompt
  
## Addition information
- All data which is pulled and used to create the networks will be stored in both neo4j and elasticsearch (latter not yet implemented).
- Come up with 2 plans
  1. Build the network from scratch (i.e. deleting entire network and rebuilding it)
  2. Updating rather than deleting and constructing from nothing
