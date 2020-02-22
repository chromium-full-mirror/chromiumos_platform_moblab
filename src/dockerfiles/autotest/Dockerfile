FROM alpine/git as copy

WORKDIR /

#RUN git clone https://chromium.googlesource.com/chromiumos/platform/moblab
COPY ./src /moblab/src
COPY ./third_party /moblab/third_party
COPY ./scripts /moblab/scripts
COPY ./setup.py /moblab/

RUN rm -rf /moblab/third_party/autotest/site-packages
RUN mkdir -p /moblab/third_party/autotest/site-packages

# This seems pointless ( we set the user in the run enviroment )
# however if this is not done copies from this overlay to the run_env
# have messed up permission on the directories ?????????.  Don't remove.
RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 --disabled-password --gecos "" moblab
RUN chown -R moblab:moblab /moblab

######################################################################

FROM alpine/git as source

WORKDIR /

RUN git clone https://chromium.googlesource.com/chromiumos/infra/lucifer
RUN git clone https://chromium.googlesource.com/chromiumos/chromite

WORKDIR /infra
RUN git clone https://chromium.googlesource.com/chromiumos/infra_virtualenv

######################################################################
FROM alpine/git as downloads

WORKDIR /
RUN wget https://dl.google.com/go/go1.11.2.linux-amd64.tar.gz
RUN wget https://storage.googleapis.com/gwt-releases/gwt-2.8.2.zip
RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v3.10.0/protoc-3.10.0-linux-x86_64.zip


######################################################################

FROM debian:buster as goinstall

COPY --from=downloads /*.gz /

RUN apt-get update && apt-get install --no-install-recommends -yq \
	wget unzip git ca-certificates sed

#Install Go, complile lucifer
RUN tar -xvf go1.11.2.linux-amd64.tar.gz
RUN mv go /usr/local

######################################################################

FROM goinstall as lucifer

COPY --from=source /lucifer /lucifer

WORKDIR /lucifer/src
ENV GOROOT=/usr/local/go
ENV GOPATH=/lucifer
ENV PATH=$GOPATH/bin:$GOROOT/bin:$PATH
RUN sed -i 's#go.opencensus.io/exporter/stackdriver#contrib.go.opencensus.io/exporter/stackdriver#g' lucifer/metrics/metrics.go
RUN sed -i 's#trace.SetDefaultSampler(trace.AlwaysSample())#//trace.SetDefaultSampler(trace.AlwaysSample())#g' lucifer/metrics/metrics.go
RUN go get -v go.chromium.org/chromiumos/infra/proto/go/test_platform/side_effects
RUN go get -v lucifer/cmd/lucifer
RUN go build -i -o /usr/bin/lucifer lucifer/cmd/lucifer

######################################################################

FROM debian:buster as protobuild

RUN apt-get update && apt-get install --no-install-recommends -yq \
	unzip

COPY --from=copy /moblab/third_party/autotest/tko/tko.proto /moblab/third_party/autotest/tko/tko.proto
COPY --from=copy /moblab/third_party/autotest/site_utils/cloud_console.proto /moblab/third_party/autotest/site_utils/cloud_console.proto
COPY --from=lucifer /lucifer/src/go.chromium.org/chromiumos/infra/proto/src/test_platform/side_effects /
COPY --from=downloads /protoc-3.10.0-linux-x86_64.zip /


# install protoc
RUN unzip protoc-3.10.0-linux-x86_64.zip
RUN cp bin/protoc /usr/local/bin

RUN protoc --proto_path /moblab/third_party/autotest/tko --python_out=/moblab/third_party/autotest/tko /moblab/third_party/autotest/tko/tko.proto
RUN protoc --proto_path /moblab/third_party/autotest/site_utils --python_out=/moblab/third_party/autotest/site_utils /moblab/third_party/autotest/site_utils/cloud_console.proto
RUN protoc --proto_path / --python_out=/ config.proto

######################################################################

FROM debian:buster as build_env
RUN apt-get update && apt-get install --no-install-recommends -yq \
	curl unzip python2.7 cmake \
	default-jdk gcc virtualenv \
	default-libmysqlclient-dev python-dev

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip install --upgrade pip
RUN pip install setuptools six

######################################################################
FROM build_env as build

COPY --from=source /chromite /chromite
COPY --from=copy /moblab /moblab
COPY --from=downloads /*.zip /
COPY --from=source /infra /infra

RUN ln -s /moblab/third_party/autotest /usr/local/autotest

ENV DEBIAN_FRONTEND noninteractive

# Fake moblab
COPY src/dockerfiles/autotest/lsb-release /etc/
RUN chmod uog+r /etc/lsb-release

#Add new mysql virtual env package
WORKDIR /infra/infra_virtualenv
RUN /infra/infra_virtualenv/bin/python_venv -m pip wheel -w pip_packages mysqlclient==1.4.6
WORKDIR /

# GWT compile
RUN unzip gwt-2.8.2.zip
RUN mkdir -p /usr/local/autotest
RUN mv gwt-2.8.2/ /usr/local/autotest/site-packages/gwt
RUN ln -s /chromite /usr/local/autotest/site-packages/chromite
RUN /usr/local/autotest/utils/compile_gwt_clients.py -a -e"-Djava.util.prefs.userRoot=/tmp"

WORKDIR /
COPY src/dockerfiles/autotest/setup_chromite.py /
RUN python /setup_chromite.py install

COPY src/dockerfiles/autotest/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /moblab
RUN python2.7 ./setup.py install

###################################################################

FROM debian:buster as run_env
# Install packages
RUN apt-get update && apt-get install --no-install-recommends -yq \
	curl unzip python2.7 lxc pbzip2 xz-utils \
	sudo libpython2.7-dev \
	default-libmysqlclient-dev ssh \
	apache2 apache2-utils libapache2-mod-wsgi \
	virtualenv rsync bzip2 vim docker.io mariadb-client

# Apache setup
RUN a2enmod headers
RUN a2enmod rewrite
RUN a2dismod mpm_event
RUN a2enmod mpm_prefork

#setcap to bind to privileged ports as non-root
RUN setcap 'cap_net_bind_service=+ep' /usr/sbin/apache2
RUN getcap /usr/sbin/apache2

RUN sed -i 's/www-data/moblab/g' /etc/apache2/envvars

###################################################################
FROM run_env as run

COPY --from=build /chromite /chromite
COPY --from=build /moblab /moblab
COPY --from=build /usr/local/lib/python2.7/dist-packages /usr/local/lib/python2.7/dist-packages
COPY --from=build /infra /infra
COPY --from=lucifer /usr/bin/lucifer /usr/bin/lucifer
COPY --from=protobuild /moblab/third_party/autotest/tko/*_pb* /moblab/third_party/autotest/tko/
COPY --from=protobuild /moblab/third_party/autotest/site_utils/*_pb* /moblab/third_party/autotest/site_utils/
COPY --from=protobuild /*_pb* /moblab/third_party/autotest/utils/side_effects/proto/

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 --disabled-password --gecos "" moblab
RUN echo "moblab     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN chown -R moblab:moblab /moblab

RUN ln -s /infra/* /opt
RUN ln -s /moblab/third_party/autotest /usr/local/autotest

RUN chmod a+x /moblab/third_party/autotest/tko/*.cgi

# Fake moblab
COPY src/dockerfiles/autotest/lsb-release /etc/
RUN chmod uog+r /etc/lsb-release

COPY src/dockerfiles/autotest/shadow_config.ini /usr/local/autotest
RUN chmod uog+rw /usr/local/autotest/shadow_config.ini

COPY src/dockerfiles/autotest/autotest_init /
RUN chmod uog+rx /autotest_init

RUN rm /etc/apache2/ports.conf
RUN touch /etc/apache2/ports.conf
RUN rm /etc/apache2/sites-enabled/*
COPY src/dockerfiles/autotest/apache-docker.conf /etc/apache2/mods-available
RUN cp /moblab/third_party/autotest/apache/conf/* /etc/apache2/mods-available
RUN rm -f /etc/apache2/mods-enabled/apache-docker.conf
RUN ln -s /etc/apache2/mods-available/apache-docker.conf /etc/apache2/mods-enabled/apache-docker.conf

RUN cp /moblab/third_party/autotest/apache/conf/* /etc/apache2/mods-available
RUN cp /moblab/third_party/autotest/apache/conf/* /etc/apache2/mods-enabled

RUN sed -i 's/#MySQL-python==1.2.5/MySQL-python==1.2.5/g' /moblab/third_party/autotest/venv/requirements.txt


RUN chown -R moblab:moblab /run
RUN chown -R moblab:moblab /var/log
RUN mkdir -p /home/moblab
RUN mkdir -p /home/moblab/.ssh
COPY --from=source /chromite/ssh_keys/* /home/moblab/.ssh/
RUN chmod -R 600 /home/moblab/.ssh/*
RUN touch /home/moblab/.boto
COPY src/dockerfiles/autotest/ssh_config /home/moblab/.ssh/config
RUN chown -R moblab:moblab /home/moblab
RUN chown -R moblab:moblab /etc/apache2/mods-enabled/*

ENV CROS_VENV_CACHE=/usr/local/.cros-venv-cache
RUN mkdir /usr/local/.cros-venv-cache
RUN chown -R moblab /usr/local/.cros-venv-cache

RUN sudo -u moblab /usr/local/autotest/bin/job_reporter || true
RUN mkdir /moblab/third_party/autotest/logs
RUN mkdir /moblab/third_party/autotest/results
RUN chown -R moblab:moblab /moblab/third_party/autotest
RUN chown -R moblab:moblab /usr/local/autotest
RUN chown -R moblab:moblab /etc/apache2/mods-enabled/
RUN chown -R moblab:moblab /etc/apache2/mods-available/
RUN setcap cap_net_raw=ep /bin/ping

USER moblab
ENV USER=moblab

EXPOSE 8888

CMD ["/autotest_init"]
