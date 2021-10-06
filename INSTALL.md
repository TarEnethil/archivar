# Installing and running Archivar
Archivar can be run as a standalone python (Flask) application or inside a Docker container.
In both cases, you probably want to run archivar behind a (reverse) proxy configuration with standard webservers such as apache or nginx.
There is currently no packaged release, so you will need to check out the source first:

```
git clone https://github.com/TarEnethil/archivar.git
cd archivar
```

## Docker

### Build the Docker container
```bash
sudo docker build -t archivar:latest .
```

### Run the Docker container
Archivar needs a mount where it stores user data (and the database) under the mountpoint `/opt/data/`.
Other configuration can be done via environment variables, see [config/README.md](config/README.md).
If the volume directory is owned by a user with uid != 1000, you can override the uid of the internal user in the environment-block using USER_ID=$my-id.

Example docker-compose file:

```yaml
version: '3'

services:
  archivar:
    image: archivar:latest
    container_name: archivar
    restart: unless-stopped
    ports:
      - 8000:5000
    volumes:
      - ./data/:/opt/data/
    environment:
      - PAGE_TITLE_SUFFIX=HANS PETER
```

## Standalone

### Set up python virtual environment
Flask apps are usually run inside python virtual environments, which allows the installation of dependencies without needing global permissions.
Python >= 3.7 is required.

```bash
python3 -m venv venv
```

### enter venv and install dependencies
```bash
. venv/bin/activate
pip install -r requirements.txt
```

If the installation of Pillow gives you troubles, you might need to install the packages libjpeg8-dev, zlib1g-dev and python3-dev.

## Initial configuration and database init
```bash
flask db upgrade
```

The script will initialize the database, while providing the migration-files from this repository (allowing for incremental database structure changes).

## Test the installation
```bash
export FLASK_APP=dmcp.py
flask run -h localhost
```

This is not production-ready.
For the standalone case, you will need to run archivar as a WSGI application.
TODO: Example file

## Reverse Proxies
TODO

## First time steps
When running archivar for the first time, you will need to do some install steps:

* Visit https://your-archivar-server/ to be forwarded to the installation
* Installation also includes some default settings if wanted
* After installation, log in with the admin account and head to the (module) settings
