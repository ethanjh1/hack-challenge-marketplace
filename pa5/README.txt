Name:Ethan Huang
NetID:ejh249

Challenges Attempted (Tier I/II/III):
Working Endpoint: GET /api/courses/
Your Docker Hub Repository Link: https://hub.docker.com/repository/docker/ehuang2/pa5/general

Questions:
Explain the concept of containerization in your own words.
Containerization is putting the messy code into a neat container and also makes it faster

What is the difference between a Docker image and a Docker container?
An image is a blueprint of what the app looks like and the container is the actual running of the app. 

What is the command to list all Docker images?
docker images

What is the command to list all Docker containers?
docker ps

What is a Docker tag and what is it used for?
Differentiates between specific versions of a docker image if the image gets changed.

What is Docker Hub and what is it used for?
Similar to github. Docker Hub is a cloud based service that stores images in repositories.
Lets remote servers access already built images that are shared in docker hub

What is Docker compose used for?
It is used to define and run multi-container Docker apps

What is the difference between the RUN and CMD commands?
The RUN command executes commands to install required packages (requirements.txt) while the CMD command is used on what you want to run in the 
container (the code of the app, app.py)