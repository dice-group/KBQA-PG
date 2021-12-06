# Knowledge Base Question Answering

dummy_webserver

# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) in order to install all needed dependencies:

```bash
pip install -r requirements.txt
```

# Start the dummy_webserver

Depending on which system you are using, you first have to set the **FLASK_APP** variable:

(Linux, Mac)

```bash
$ export FLASK_APP=dummy_webserver
$ python dummy_webserver.py
```

Windows CMD:

```bash
> set FLASK_APP=dummy_webserver
> python dummy_webserver.py
```

Windows Powershell:

```bash
> $env:FLASK_APP="dummy_webserver"
> python dummy_webserver.py
```
