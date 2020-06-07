FROM python:3.8-alpine
LABEL maintainer="patrick@simpletechture.nl"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev libressl-dev \
      libffi-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN adduser -D user

# Setup directory structure
RUN mkdir /app && chown -R user:user /app
RUN mkdir /app/staticfiles && chown -R user:user /app/staticfiles
COPY --chown=user:user ./app/ /app
RUN chown user.user /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
RUN rm /app/app/.env || true
RUN rm /app/apnscert/AuthKey_FP92KAS2J7.p8 || true

WORKDIR /app

USER user