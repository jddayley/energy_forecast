#!/bin/bash
exec jupyter notebook --allow-root --ip 0.0.0.0 --no-browser --NotebookApp.token='' --NotebookApp.password=''  &> /dev/null &
docker run -i -t -p 8888:8888 energyforecast /bin/bash
docker build -t energyforecast . 