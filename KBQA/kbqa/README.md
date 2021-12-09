# Documentation for the webservice

In order to run the webservice _nginx_ and _docker-compose_ have to be installed. The whole webservice is splitted into modules, which are running in their own containers, and composed by Docker.

# Build the webservice

For the first or if there were any changes on the files, the webservice has to be built:

```bash
docker-compose build
```

# Start the webservice

After building the webservice, the container for all modules can be started by the command:

```bash
docker-compose up
```

# Stop the webservice

The webservice is stopped by stopping all containers. This can be done by using the command:

```bash
docker stop $(docker ps -a -q)
```
