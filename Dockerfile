# Run a python script using FB Prophet in a Docker container 
# Build image: docker build -f Dockerfile-Debian -t forecast:R1 .

FROM ubuntu:latest
MAINTAINER Stefan Proell <stefan.proell@cropster.com>

RUN apt-get -y update  && apt-get install -y \
  python3-dev \
  libpng-dev \
  apt-utils \
  python3-psycopg2 \
  postgresql-client \
  python3 \
  python3-pip \
&& rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade setuptools
RUN pip install cython
RUN pip install numpy
RUN pip install matplotlib
RUN pip install pyparsing==2.4.7
RUN pip install pystan==2.19.1.1 
RUN pip install prophet
RUN pip install psycopg2
RUN pip install sqlalchemy
RUN pip install jupyterlab
RUN pip install notebook
RUN pip install plotly

WORKDIR /forecast
COPY . /forecast/
#CMD ["/bin/bash"]
#EXPOSE 8888:8888
COPY start-notebook.sh /usr/local/bin/  
RUN chmod +x /usr/local/bin/start-notebook.sh
CMD ["start-notebook.sh"]
#CMD [ "python", "./run_forecast.py" ]
