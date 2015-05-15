#
# Dockerised Jenkins Slave with a proxy to the overarching Docker daemon, inspired by evarga/jenkins-slave
#
# On my host, I have DOCKER_OPTS="-H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock" in /etc/default/docker... 
# if this is changed, make sure it is passed into docker-workflow.py or change your tools to reflect port changes
#

# Based on ubuntu 14.04
FROM ubuntu:14.04

# Make sure the package repository is up to date.
RUN apt-get update
RUN apt-get -y upgrade

# Install a basic SSH server
RUN apt-get install -y openssh-server
RUN sed -i 's|session    required     pam_loginuid.so|session    optional     pam_loginuid.so|g' /etc/pam.d/sshd
RUN mkdir -p /var/run/sshd

# Install JDK 7 (latest edition)
RUN apt-get install -y openjdk-7-jdk

# Add user jenkins to the image
RUN adduser --quiet jenkins
# Set password for the jenkins user (you may want to alter this).
RUN echo "jenkins:jenkins" | chpasswd

# Standard SSH port
EXPOSE 22

# Other usefuls for our proxy
RUN apt-get install -y curl tar python-pip python-dev git vim
ADD resources/tools /opt/resources/tools

# Add dockercfg to jenkins home -- used by auth.py
ADD .dockercfg /home/jenkins/.dockercfg
RUN chown jenkins:jenkins /home/jenkins/.dockercfg

# Server execution
CMD ["/usr/sbin/sshd", "-D"]