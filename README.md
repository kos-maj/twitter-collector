# jsonNetwork creator

Create a folder in the directory of the clone titled 'data'. Populate this folder with the afghan data which you wish to convert into a neo4j network. If the json files must be formatted first then run `python jsonFormatter.py` first, then `python main.py`.  

### NEO4J details/authentication
Neo4j instance must be running on ports 7474 and 7687. Authentication details must either not be required or set to neo4j/testing123. To run page rank the GDS (Graph Data Science) library must be installed within the neo4j instance.    
  
Here is an example of how to include this library (GDS) upon container initialization:
```
docker run -p7474:7474 -p7687:7687 -d --name neo-graph -v neo-data:/data -v neo-logs:/logs --env NEO4J_AUTH=neo4j/testing123 --env NEO4JLABS_PLUGINS='["graph-data-science"]' neo4j:latest
```


### Note
The json formatter formats the json files in the data as the afghan data is invalid and not able to be parsed by default via python's json library. It likely will not work if another format of json is provided. 
