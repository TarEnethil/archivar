#!/bin/sh

log() {
    echo "entrypoint: ${*}"
}

err() {
    echo "entrypoint: ${*}" 1>&2
}

# override the userid of dungeonmaster with USER_ID if given
# requires a chown afterwards, so that dungeonmaster owns its
# home diretory again.
# this is (a, not the) solution for when the /opt/data mount is not owned
# by the user with uid 1000, as per default that is what dungeonmaster will get.
# a later step checks again if the uid of dungeonmaster matches that of the volume.
# see https://github.com/TarEnethil/archivar/issues/99
setup_user() {
    if [ -n "$USER_ID" ]; then
        log "setting userid for internal user to ${USER_ID}"
        usermod -u $USER_ID dungeonmaster
        if [ $? -ne 0 ]; then
            err "setting userid failed"
            exit 1
        fi

        chown -R dungeonmaster /home/dungeonmaster
        if [ $? -ne 0 ]; then
            err "chown to new userid failed"
            exit 1
        fi
    fi
}

set_env() {
    if [ "$FLASK_ENV" = "development" ]; then
        log "debug mode detected"
        DEBUG=1
    else
        DEBUG=0
    fi

    if [ -z "$SECRET_KEY" ]; then
        log "no SECRET_KEY found, setting one at random"
        SECRET_KEY=$(uuidgen)
        export SECRET_KEY
    fi
}

init_config() {
    log "initializing config"

    # point data_basedir to /opt/, so that datadir is /opt/data (external mount point)
    sed -i 's/data_basedir =.*/data_basedir = "\/opt\/"/' config/default_config.py

    if [ ! -f config/user_config.py ]; then
        cp config/user_config.template.py config/user_config.py
    fi

    if [ ! -f config/debug_config.py ]; then
        cp config/debug_config.template.py config/debug_config.py
    fi
}

init_datadir() {
    log "initializing data dir"

    if [ ! -d /opt/data ]; then
        err "could not find mount /opt/data"
        exit 1
    fi

    # check that the uid of the mount and our user match;
    # if not, the database and media dirs are not writetable.
    # see https://github.com/TarEnethil/archivar/issues/99
    OWNER=$(stat -c '%u' /opt/data)
    if [ "${OWNER}" -ne "$(id -u dungeonmaster)" ]; then
        err "internal user dungeonmaster is not the owner of /opt/data"
        err "change the owner of the volume or retry using USER_ID=${OWNER}"
        exit 1
    fi

    dirs="media/thumbnails logos/thumbnails map mapnodes"

    for d in ${dirs}; do
        su dungeonmaster -c "mkdir -p /opt/data/$d"

        if [ $? -ne 0 ]; then
            err "creating dir ${d} failed"
            exit 1
        fi
    done
}

backup_db() {
    if [ -z "$DATABASE_URL" ]; then
        if [ -f /opt/data/app.db ]; then
            log "backing up database"
            cp /opt/data/app.db /tmp/app.db.backup
        fi
    else
        log "using custom database, not backing up database"
    fi
}

restore_db() {
    if [ -z "$DATABASE_URL" ]; then
        if [ -f /tmp/app.db.backup ]; then
            log "restoring database from backup"
            cp /tmp/app.db.backup /opt/data/app.db
        fi
    else
        log "using custom database, not restoring database"
    fi
}

upgrade_db() {
    log "initializing or upgrading database"

    su dungeonmaster -c "flask db upgrade"

    if [ $? -ne 0 ]; then
        err "db upgrade failed"
        restore_db
        exit 1
    fi
}

run() {
    log "starting server"

    exec su dungeonmaster -c "gunicorn -b :5000 --access-logfile - --error-logfile - dmcp:app"
}

run_tests() {
    log "starting unittests"

    exec su dungeonmaster -c "python3 run_tests.py"
}

setup_user

set_env
init_config

# tests use tempfile / tempdirs and in-memory db and
# docker container for tests does not get a mount volume
# so they only need to be initialized on non-test runs
if [ -z "$RUN_TESTS" ]; then
init_datadir
backup_db
upgrade_db

run
else
run_tests
fi
