FROM ubuntu:18.04 as base
LABEL maintainer="docsearch@algolia.com"

WORKDIR /root

# Install selenium
ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN useradd -d /home/seleuser -m seleuser
RUN chown -R seleuser /home/seleuser
RUN chgrp -R seleuser /home/seleuser

RUN apt-get update -y && apt-get install -yq \
    curl \
    wget \
    sudo \
    gnupg \
    software-properties-common \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    default-jdk \
    chromium-browser \
    chromium-chromedriver \
    && curl -sL https://deb.nodesource.com/setup_16.x | sudo bash - \
    && apt-get update -y && apt-get install -yq nodejs

RUN apt-get update -y && apt-get install -yq \
    python3.8 \
    python3.8-dev \
    python3.8-distutils \
    python3.8-venv \
    libssl-dev \
    libffi-dev \
    && curl -sL https://bootstrap.pypa.io/get-pip.py | python3.8 \
    && python3.8 -m pip install pipenv
 
# Install DocSearch dependencies
COPY Pipfile .
COPY Pipfile.lock .

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PIPENV_HIDE_EMOJIS 1
RUN pipenv install --python 3.8

FROM base as prod
LABEL maintainer="docsearch@algolia.com"

WORKDIR /root
COPY scraper/src ./src

ENTRYPOINT ["pipenv", "run", "python", "-m", "src.index"]
