FROM alpine/git as copy

WORKDIR /

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 --disabled-password --gecos "" moblab
COPY --chown=moblab ./src/moblab_common /moblab/src/moblab_common
COPY --chown=moblab ./src/dockerfiles /moblab/src/dockerfiles
COPY --chown=moblab ./src/host_services /moblab/src/host_services
COPY --chown=moblab ./src/tools /moblab/src/tools
COPY --chown=moblab ./third_party/autotest /moblab/third_party/autotest
COPY --chown=moblab ./setup.py /moblab/

RUN rm -rf /moblab/third_party/autotest/site-packages
RUN mkdir -p /moblab/third_party/autotest/site-packages

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
RUN wget https://dl.google.com/go/go1.14.2.linux-amd64.tar.gz
RUN wget https://storage.googleapis.com/gwt-releases/gwt-2.8.2.zip
RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v3.10.0/protoc-3.10.0-linux-x86_64.zip


######################################################################

FROM debian:buster as goinstall

COPY --from=downloads /*.gz /

RUN apt-get update && apt-get install --no-install-recommends -yq \
	wget unzip git ca-certificates sed

#Install Go, complile lucifer
RUN tar -xvf go1.14.2.linux-amd64.tar.gz
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

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 --disabled-password --gecos "" moblab

COPY --chown=moblab --from=copy /moblab/third_party/autotest/tko/tko.proto /moblab/third_party/autotest/tko/tko.proto
COPY --chown=moblab --from=lucifer /lucifer/src/go.chromium.org/chromiumos/infra/proto/src/test_platform/side_effects /
COPY --from=downloads /protoc-3.10.0-linux-x86_64.zip /


# install protoc
RUN unzip protoc-3.10.0-linux-x86_64.zip
RUN cp bin/protoc /usr/local/bin

RUN protoc --proto_path /moblab/third_party/autotest/tko --python_out=/moblab/third_party/autotest/tko /moblab/third_party/autotest/tko/tko.proto
RUN protoc --proto_path / --python_out=/ config.proto

######################################################################

FROM debian:buster as build

RUN apt-get update && apt-get install --no-install-recommends -yq \
        curl unzip python2.7 cmake \
        default-jdk gcc \
        default-libmysqlclient-dev python-dev

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 --disabled-password --gecos "" moblab

COPY --chown=moblab --from=source /chromite /chromite
COPY --chown=moblab --from=copy /moblab /moblab
COPY --chown=moblab --from=downloads /*.zip /
COPY --chown=moblab --from=source /infra /infra

RUN ln -s /moblab/third_party/autotest /usr/local/autotest

ENV DEBIAN_FRONTEND noninteractive

# Fake moblab
COPY src/dockerfiles/autotest/lsb-release /etc/
RUN chmod uog+r /etc/lsb-release

#Add new mysql virtual env package
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip install --upgrade pip
RUN pip install setuptools six virtualenv==16.7.10
WORKDIR /infra/infra_virtualenv
RUN /infra/infra_virtualenv/bin/python_venv -m pip wheel -w pip_packages mysqlclient==1.4.6
WORKDIR /

# GWT compile
RUN unzip gwt-2.8.2.zip
RUN mkdir -p /usr/local/autotest
RUN mv gwt-2.8.2/ /usr/local/autotest/site-packages/gwt
RUN ln -s /chromite /usr/local/autotest/site-packages/chromite
RUN /usr/local/autotest/utils/compile_gwt_clients.py -a -e"-Djava.util.prefs.userRoot=/tmp"
RUN rm -rf /usr/local/autotest/site-packages/gwt

###################################################################

FROM debian:buster as run_env
# Install packages
RUN addgroup --gid 412 docker
RUN apt-get update && apt-get install --no-install-recommends -yq \
	curl unzip python2.7 pbzip2 xz-utils \
	sudo libpython2.7-dev \
	default-libmysqlclient-dev ssh gcc \
	apache2 apache2-utils libapache2-mod-wsgi \
	virtualenv rsync bzip2 vim iputils-ping \
	mariadb-client apt-transport-https ca-certificates gnupg

# Apache setup
RUN a2enmod headers
RUN a2enmod rewrite
RUN a2dismod mpm_event
RUN a2enmod mpm_prefork

RUN sed -i 's/www-data/moblab/g' /etc/apache2/envvars

###################################################################
FROM run_env as run

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 --disabled-password --gecos "" moblab

COPY --chown=moblab --from=build /chromite /chromite
COPY --chown=moblab --from=build /moblab /moblab
COPY --chown=moblab --from=build /infra /infra
COPY --chown=moblab --from=lucifer /usr/bin/lucifer /usr/bin/lucifer
COPY --chown=moblab --from=protobuild /moblab/third_party/autotest/tko/*_pb* /moblab/third_party/autotest/tko/
COPY --chown=moblab --from=protobuild /*_pb* /moblab/third_party/autotest/utils/side_effects/proto/

RUN echo "moblab     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip install --upgrade pip
RUN pip install setuptools six
COPY src/dockerfiles/autotest/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /
COPY src/dockerfiles/autotest/setup_chromite.py /
RUN python /setup_chromite.py install
WORKDIR /moblab
RUN python2.7 ./setup.py install

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


RUN chown -R moblab:moblab /etc/apache2/mods-enabled/*

RUN mkdir /usr/local/.cros-venv-cache
RUN chown -R moblab /usr/local/.cros-venv-cache

RUN mkdir -p /var/log/apache2/
RUN chmod uog+rw /var/log/apache2
RUN chmod uog+rw /run
RUN chown -R moblab /var/log/apache2
RUN chown -R root /etc/sudoers.d

# Install the google cloud sdk
RUN echo \
    "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
    http://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg  \
    add - && apt-get update -y && apt-get install google-cloud-sdk -y

RUN apt purge -yq gcc

USER moblab
ENV USER=moblab
RUN mkdir /moblab/third_party/autotest/logs
RUN mkdir /moblab/third_party/autotest/results
RUN mkdir /moblab/third_party/autotest/leases

ENV CROS_VENV_CACHE=/usr/local/.cros-venv-cache
RUN mkdir -p /home/moblab
RUN mkdir -p /home/moblab/.ssh
COPY --chown=moblab --from=source /chromite/ssh_keys/* /home/moblab/.ssh/
RUN chmod -R 600 /home/moblab/.ssh/*
COPY src/dockerfiles/autotest/ssh_config /home/moblab/.ssh/config
RUN touch /home/moblab/.boto

RUN sudo usermod -aG docker $USER

EXPOSE 8888

CMD ["/autotest_init"]
