# Preparation

```
python3 -m venv venv
# Windows
.\venv\bin\activate.bat
# Linux, *BSD or MacOS
. venv/bin/activate

pip install requirements.txt
```

# Run tests

```
# Type check
mypy --strict gb_chat
# Tests
python -m pytest
```

# Server run

```
Usage: server.py [OPTIONS]

Options:
  -a, --address TEXT        [default: localhost]
  -p, --port INTEGER RANGE  [default: 7777]
  -v, --verbose             [default: False]
  --help                    Show this message and exit.
```

# Client run

```
Usage: client.py [OPTIONS] USERNAME PASSWORD

Options:
  -a, --address TEXT        [default: localhost]
  -p, --port INTEGER RANGE  [default: 7777]
  -v, --verbose             [default: False]
  --help                    Show this message and exit.
```
