FROM dalenys/debian:wheezy

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -qq && \
    apt-get upgrade -qq -y && \
    apt-get install -qq -y \
      build-essential \
      python \
      python-pip \
      python-dev

# pgocli (https://github.com/tusbar/pgocli)
ADD . /opt/pgocli

# pip (https://pypi.python.org/pypi/pip)
RUN pip install --quiet --upgrade pip
RUN pip install --quiet --upgrade setuptools

# install requirements
RUN cd /opt/pgocli && pip install --requirement requirements.txt

# install pgocli
RUN cd /opt/pgocli && pip install -e .

# clean
RUN apt-clean

WORKDIR /opt/pgocli
# EOF
