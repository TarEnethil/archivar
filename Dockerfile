##########
# Builder (build wheels)
##########

FROM python:3.12-alpine as builder

WORKDIR /usr/src/archivar-build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# mostly dependencies for building Pillow
RUN apk update && \
    apk add --no-cache build-base gcc git jpeg-dev libffi-dev python3-dev zlib-dev

# lint with flake8
RUN pip install --upgrade pip
RUN pip install flake8

WORKDIR /usr/src/archivar-build

# don't just copy . here, because then the build takes longer when changing
# stuff like entrypoint.sh
COPY app ./app
COPY config ./config
COPY install ./install
COPY migrations ./migrations
COPY tests ./tests
COPY dmcp.py run_tests.py requirements.txt .flake8 ./

RUN flake8 --config=.flake8

RUN pip wheel --no-cache-dir --no-deps --wheel-dir ./wheels -r requirements.txt

########
# Image
########

FROM python:3.9-alpine

RUN adduser -D dungeonmaster

WORKDIR /home/dungeonmaster

# util-linux for uuidgen, rest for Pillow
RUN apk update && \
    apk add --no-cache gnupg jpeg su-exec util-linux shadow zlib

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

RUN chmod +x entrypoint.sh

ENV FLASK_APP dmcp.py

EXPOSE 5000

VOLUME ["/opt/data"]

ENTRYPOINT ["./entrypoint.sh"]
