echo "Starting Docker Build"
docker stop forecast;
docker rm forecast;
docker stop forecast; 
docker rm forecast;
docker build -t forecast .;
docker run -p 5000:5000 --restart=always -d --name=forecast -it forecast
