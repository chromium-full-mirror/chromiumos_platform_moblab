# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#############
### build ###
#############

# base image
FROM node:12 as build

# install chrome for protractor tests
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update && apt-get install -yq google-chrome-stable

# install protoc
RUN apt-get install -yq unzip
ENV PROTOBUF_URL https://github.com/protocolbuffers/protobuf/releases/download/v3.10.0/protoc-3.10.0-linux-x86_64.zip
RUN curl -L -o /tmp/protobuf.zip $PROTOBUF_URL
WORKDIR /tmp/
RUN unzip protobuf.zip
RUN cp bin/protoc /usr/local/bin

RUN curl -L -o /usr/local/bin/protoc-gen-grpc-web https://github.com/grpc/grpc-web/releases/download/1.0.6/protoc-gen-grpc-web-1.0.6-linux-x86_64
RUN chmod uog+x /usr/local/bin/protoc-gen-grpc-web

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH


# install and cache app dependencies
# add app
COPY ./moblab-ui /app
COPY ./moblab-rpcserver/moblabrpc.proto /app
RUN npm install
RUN protoc -I=/app --js_out=import_style=commonjs:/app/src/app/services --grpc-web_out=import_style=commonjs+dts,mode=grpcwebtext:/app/src/app/services /app/moblabrpc.proto

# run tests
#RUN ng test --watch=false
#RUN ng e2e --port 4202

# generate build
RUN ng build --output-path=dist

############
### prod ###
############

# base image
FROM nginx:alpine

# copy artifact build from the 'build environment'
COPY --from=build /app/dist /etc/nginx/html/

COPY moblab-ui/nginx.conf /etc/nginx
RUN rm -f /etc/nginx/conf.d/*

EXPOSE 6010

# run nginx
CMD ["nginx", "-g", "daemon off;"]
