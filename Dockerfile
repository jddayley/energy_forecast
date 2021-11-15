# Run a python script using FB Prophet in a Docker container 
# Build image: docker build -f Dockerfile-Debian -t forecast:R1 .

FROM python:3
MAINTAINER Stefan Proell <stefan.proell@cropster.com>

RUN apt-get -y update  && apt-get install -y \
  python3-dev \
  libpng-dev \
  apt-utils \
  python3-psycopg2 \
  python-dev \
  postgresql-client \
&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade setuptools
RUN pip install cython
RUN pip install numpy
RUN pip install matplotlib
RUN pip install pystan
RUN pip install fbprophet
RUN pip install psycopg2
RUN pip install sqlalchemy

WORKDIR /forecast
COPY . /forecast/

CMD [ "python", "./run_forecast.py" ]
