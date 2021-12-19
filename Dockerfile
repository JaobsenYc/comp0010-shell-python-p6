FROM python:3.8-buster

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH "${PYTHONPATH}:/comp0010/src"
RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils dialog 2>&1 \
    && apt-get -y install git procps lsb-release \
    && apt-get autoremove -y \
    && apt-get clean -y

COPY . /comp0010

RUN chmod u+x /comp0010/sh
RUN chmod -x $(find /comp0010/test/ -name '*.py')
RUN chmod u+x /comp0010/tools/test
RUN chmod u+x /comp0010/tools/coverage
RUN chmod u+x /comp0010/tools/analysis
RUN chmod u+x /comp0010/tools/pylint
RUN chmod u+x /comp0010/tools/scalene
RUN chmod u+x /comp0010/tools/mccabe
RUN chmod u+x /comp0010/tools/mutmut

RUN cd /comp0010 && python -m pip install -r requirements.txt

ENV DEBIAN_FRONTEND=

EXPOSE 8000

