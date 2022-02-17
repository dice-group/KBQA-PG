# Embedding server

This is the implementation for querying embeddings of URIs of both Entities and Relations.
Once running, the embedding server should be available at http://kbqa-pg.cs.upb.de/embedding_query/ via a POST request.
The POST request has to send a JSON file containing a list of entity URIs and a list of relation URIs. Both may be empty. The server then returns a JSON file containing the embeddings in corresponding list positions as a response.

```python
import requests
uri_dict = {"entities": ["http://foo/bar1","http://foo/bar2"], "relations" : ["http://foo/bar3"]}
r = requests.post("http://kbqa-pg.cs.upb.de/embedding_query/", json=uri_dict)
#r.json() contains the embeddings
```

The entity embeddings are send as tab seperated values.
The relation embeddings are send as a dict containing both the rhs and lhs embeddings with the respective real and imaginary parts.

If no embedding is found for an entity URI, then an empty string is returned.
If no embedding is found for a relation URI, then an empty dict is returned.

## Local Tests

In order to test the functionality of the embedding server locally, start the server in the kbqa folder:

```bash
sudo env RESOURCE_PATH="/location/to/entity_embedding_file" docker-compose up --build 
```

In another terminal execute the script **stress_test.py**:

```bash
python stress_test.py
```

The stress test will try to query the first **n** entities from the entity embedding file and will report all entities which can not be found by the server, which should be 0.
