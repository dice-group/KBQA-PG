# Documentation for the webservice

In order to structure the project, the logic of the webservice and all used resources are divided into two different directories. The directory **/webservice** contains the files for running the webservice (e.g. Dockerfiles, python files, ...) and the directory **/resources** contains all files, which are accessed by the webservice (e.g. models, embeddings, ...). Note that most of those files are too large to be pushed to the remote Github server. Therefore, those files have to be added to the VM manually.

In general, it is not necessary to build, start or stop the webservice, since we use an action-runner, which applies each merge to the branch develop to the running system on the VM. However, the webservice can be built, started or stopped by hand using some simple Docker commands.

## Build the webservice

Building the webservice can be done by the command:

```bash
docker-compose build
```

## Start the webservice

Starting the webservice can be done by the command:

```bash
docker-compose up
```

## Stop the webservice

Stopping the webservice can be done by the command:

```bash
docker-compose down
```
