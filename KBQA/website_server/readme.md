# Knowledge Base Question Answering

Website-Server

# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) in order to install all needed dependencies:

```bash
pip install -r requirements.txt
```

# Start the Website-Server

Depending on which system you are using, you first have to set the **FLASK_APP** variable:

(Linux, Mac)

```bash
$ export FLASK_APP=website_server
$ python website_server.py
```

Windows CMD:

```bash
> set FLASK_APP=website_server
> python website_server.py
```

Windows Powershell:

```bash
> $env:FLASK_APP="website_server"
> python website_server.py
```

# Open the Website

After starting the server you can visit the website **http://127.0.0.1:24803/** or **http://localhost:24803/** in order to ask questions.
