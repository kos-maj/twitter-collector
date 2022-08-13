# jsonNetwork creator

Create a folder in the directory of the clone titled 'data'. Populate this folder with the afghan data which you wish to convert into a neo4j network. If the json files must be formatted first then run `python jsonFormatter.py` first, then `python main.py`.  

### NEO4J details/authentication
Neo4j instance must be running on ports 7474 and 7687. Authentication details must either not be required or neo4j + testing123.

### Note
The json formatter formats the json files in the data as the afghan data is invalid and not able to be parsed by default via python's json library. It likely will not work if another format of json is provided. 
