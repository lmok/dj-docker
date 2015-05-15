# dj-docker: (Docker-Jenkins)-Docker

A template Docker image to be used as a Jenkins slave with the Docker Plugin for Jenkins. It is thusly named due to its included toolset that lets Jenkins build Docker images as a part of its job definition -- from inside the slave container. This is a different approach to running a [Docker-in-Docker wrapper](https://github.com/tehranian/dind-jenkins-slave) inside the container.

This takes rough inspiration from [evarga/jenkins-slave](https://registry.hub.docker.com/u/evarga/jenkins-slave/), [docker-py](http://docker-py.readthedocs.org/), and [ochopod](https://github.com/autodesk-cloud/ochopod). 

Contact me at lillio.mok@mail.mcgill.ca.
