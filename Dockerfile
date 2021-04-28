##########
# Builder (build wheels)
##########

FROM python:3.9-alpine as builder

WORKDIR /usr/src/archivar-build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# mostly dependencies for building Pillow
RUN apk update && \
    apk add --no-cache build-base gcc git jpeg-dev libffi-dev python3-dev zlib-dev

# lint with flake8
RUN pip install --upgrade pip
RUN pip install flake8
COPY . /usr/src/archivar-build/
RUN flake8 --config=.flake8

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/archivar-build/wheels -r requirements.txt

########
# Image
########

FROM python:3.9-alpine

RUN adduser -D dungeonmaster

WORKDIR /home/dungeonmaster

# util-linux for uuidgen, rest for Pillow
RUN apk update && \
    apk add --no-cache jpeg util-linux zlib

RUN pip install --upgrade pip && pip install gunicorn

COPY --from=builder /usr/src/archivar-build/wheels /wheels
COPY --from=builder /usr/src/archivar-build/requirements.txt ./
RUN pip install --no-cache /wheels/*

COPY --chown=dungeonmaster:dungeonmaster app ./app
COPY --chown=dungeonmaster:dungeonmaster config ./config
COPY --chown=dungeonmaster:dungeonmaster install ./install
COPY --chown=dungeonmaster:dungeonmaster migrations ./migrations
COPY --chown=dungeonmaster:dungeonmaster tests ./tests
COPY --chown=dungeonmaster:dungeonmaster dmcp.py entrypoint.sh CHANGELOG.md run_tests.py ./

USER dungeonmaster

RUN chmod u+x entrypoint.sh

ENV FLASK_APP dmcp.py

EXPOSE 5000

VOLUME ["/opt/data"]

ENTRYPOINT ["./entrypoint.sh"]
