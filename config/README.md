# Archivar configuration

Some configuration must be done before starting up the application.
The way you set the options depends on if you're running archivar with or without Docker.

## When not running inside Docker

You can set the options using the file config/user_config.py.
The config follows a simple KEY = value format, although python data types apply.

## First Steps

* Copy or rename `config/user_config.template.py` to `config/user_config.py`
* Set the SECRET_KEY configuration (mandatory)
* Set other options

## When running inside Docker

The options must be defined as environment variables for the docker container, either via the [-e flag](https://docs.docker.com/engine/reference/run/#env-environment-variables) or via [environment:](https://docs.docker.com/compose/environment-variables/) in docker-compose.
All these environment variables are strings, which archivar tries to parse into the python datatypes.

## Mandatory Configuration

### SECRET_KEY (type: String)

A secret key that will be used for securely signing the session cookie
and can be used for any other security related needs by extensions or
your application. It should be a long random string of bytes,
although unicode is accepted too.

see also: https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY

Do not reveal the secret key when posting questions or committing code.

#### Default Value

`None`, **must** be provided

Note: The Docker container will set a random string as SECRET_KEY when it is booted.
That also means logins will be invalidated whenever the container is restarted.
The SECRET_KEY can be overwritten.


#### Examples
```python
    SECRET_KEY = "_4sdo%&AAdk7c6dd]"
```

## Optional Configuration

### MAX_CONTENT_LENGTH (type: Integer)

Maximum size of media files (in Bytes)


#### Default Value
`1024 * 1000 = 1 Megabyte`


#### Examples
```python
    # 100 Kbyte
    MAX_CONTENT_LENGTH = 1024 * 100

    # 10 MByte
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
```

Note for Docker: Do the math yourself.

### SERVE_LOCAL (type: Boolean)

Whether to use a CDNs to deliver external js/css files.
Using CDNs means slightly less load / traffic on your server.


#### Default Value
`True`


#### Examples
```python
    # Dont use CDNs
    SERVE_LOCAL = True

    # Use CDNs
    SERVE_LOCAL = False
```

Note for Docker: several strings will be interpreted as boolean true. Try stuff like "True", "true", "1", "yes".

### PAGE_TITLE_SUFFIX (type: String)

Suffix for the HTML title attribute.
A space will automatically be added in the front of the string.


#### Default Value
`:: Archivar`


#### Examples
```python
    PAGE_TITLE_SUFFIX = "- Worldbuilder5000"

    PAGE_TITLE_SUFFIX = ""
```