
# Jiranimo

Getting data out of JIRA needs automation.  Basic automation always begs for a CLI. This one should make it easy to store credentials and get data of out of jira with the press of a button. 

## Getting Started


### Prerequisites

`python 3.x` and ideally `virtualenv/virtualenvmanager`.  I haven't tested this on python 2 yet, so for now try to create an env with python3.

### Installing

```
git clone https://github.com/mspiegel31/jiranimo.git
cd jiranimo
pip3 install jiranimo/
```

And finally

```
jiranimo
```

should yield the docstring:
```
Usage: jiranimo [OPTIONS] COMMAND [ARGS]...

  Utilities for getting data out of JIRA

Options:
  --help  Show this message and exit.

Commands:
  get_data  Get you some jira data
  profile   Manage your login credentials
```

the first thing you will want to do is run `jiranimo profile create` to get your JIRA login credentials setup.

## Running the tests

Coming soon!

## Built With

* [Click](http://click.pocoo.org/5/)
* [python-jira](https://pythonhosted.org/jira/)
* [Keyring](http://pythonhosted.org/keyring/)
