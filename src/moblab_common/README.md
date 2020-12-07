# Moblab Common

Moblab Common is a library that is used by other projects in this repo. It is
compiled into moblab-common wheel package and pushed as a docker container to
the docker registry.


## Development

The project contains protofiles for multiple services in the repo under /protos
directory.

For development you might want to generate python code for protofiles. To do so
simple run the protogen script:
`./protos/protogen.sh`
