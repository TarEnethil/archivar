#!/bin/sh

log() {
    echo "entrypoint: ${*}"
}

err() {
    echo "entrypoint: ${*}" 1>&2
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

    dirs="media/thumbnails logos/thumbnails map mapnodes"

    for d in ${dirs}; do
        mkdir -p /opt/data/"$d"

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

    flask db upgrade

    if [ $? -ne 0 ]; then
        err "db upgrade failed"
        restore_db
        exit 1
    fi
}

run() {
    log "starting server"

    exec gunicorn -b :5000 --access-logfile - --error-logfile - dmcp:app
}

set_env
init_config
init_datadir

backup_db
upgrade_db

run
