FROM python:3-alpine

COPY . /app
WORKDIR /app
RUN apk add --no-cache libffi-dev build-base python3-dev git libgit2 \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del --no-cache --purge build-base