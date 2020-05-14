FROM docker:latest as docker

###########################################################

FROM linuxserver/openssh-server:latest

COPY ./testing_rsa.pub /
COPY --from=docker /usr/local/bin/docker /usr/local/bin/docker

#RUN echo "LogLevel DEBUG3" >> /etc/ssh/sshd_config