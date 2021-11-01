# Knowledge Base Question Answering

Webservice for answering simple questions

# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) in order to install all needed dependencies:

```bash
pip install -r requirements.txt
```

# Start the WebService

Depending on which system you are using, you first have to set the **FLASK_APP** variable:

(Linux, Mac)
```bash
$ export FLASK_APP=kbqa
$ python kbqa.py
```

Windows CMD:
```bash
> set FLASK_APP=kbqa
> python kbqa.py
```

Windows Powershell:
```bash
> $env:FLASK_APP="kbqa"
> python kbqa.py
```

# Start Stanford CoreNLP server

The Webservice uses [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) in the background for annotating questions and extract information. In order to use this service, you have to start a running instance of a server locally. This can be done by following [these](https://stanfordnlp.github.io/CoreNLP/corenlp-server.html) instructions.

# Open the Website

After starting the Webservice and the Stanford CoreNLP you can visit the website **http://127.0.0.1:5000/** or **http://localhost:5000/** in order to ask questions.
