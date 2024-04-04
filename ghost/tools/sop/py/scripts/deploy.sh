# create a docker image and run the container
docker build -t app_image .
docker run -d --name app_container app_image

