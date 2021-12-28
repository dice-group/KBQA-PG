# Approach B

This is the implementation for querying embeddings of URIs.
Once running, the embedding server should be available at http://kbqa-pg.cs.upb.de/embedding_query/ via a POST request.
The POST request has to send a JSON file containing a list of URIs(str). The server then returns a JSON file containing the embeddings in corresponding list positions as a response.

```python
import requests
uri_dict = {"uris": ["http://foo/bar1","http://foo/bar2"]}
r = requests.post("http://kbqa-pg.cs.upb.de/embedding_query/", json=uri_dict)
#r.json() contains the embeddings
```

If no embedding is found for a URI, then an empty string is returned for that URI.

## Local Tests

In order to test the functionality of the embedding server, a local script can be executed to simulate a query by going through entities found in one of the QALD datasets.

Start the development server:

```bash
python3 embedding_server_wsgi.py
```

In another terminal execute the script **local_test.py**:

```bash
python3 local_test.py
```

Local test will then report on the coverage of requested URIs in the database. Note that the database for the embedding server is a slightly older DBPedia version, so some entities might not be found.
