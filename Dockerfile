##########
# Builder (build wheels)
##########

FROM python:3.9-alpine as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# mostly dependencies for building Pillow
RUN apk update && \
    apk add --no-cache build-base gcc jpeg-dev libffi-dev python3-dev zlib-dev

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

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

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt ./
RUN pip install --no-cache /wheels/*

COPY --chown=dungeonmaster:dungeonmaster app ./app
COPY --chown=dungeonmaster:dungeonmaster config ./config
COPY --chown=dungeonmaster:dungeonmaster install ./install
COPY --chown=dungeonmaster:dungeonmaster migrations ./migrations
COPY --chown=dungeonmaster:dungeonmaster dmcp.py entrypoint.sh CHANGELOG.md ./

USER dungeonmaster

RUN chmod u+x entrypoint.sh

ENV FLASK_APP dmcp.py

EXPOSE 5000

VOLUME ["/opt/data"]

ENTRYPOINT ["./entrypoint.sh"]
