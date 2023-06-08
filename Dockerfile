# Base Dockerfile for using dftlib
##################################
# The Docker image can be built by executing:
# docker build -t yourusername/dftlib .
# A different base image can be set from the commandline with:
# --build-arg BASE_IMAGE=<new_base_image>

# Set stormpy base image
ARG BASE_IMAGE=movesrwth/stormpy:ci-release
FROM $BASE_IMAGE
MAINTAINER Matthias Volk <m.volk@utwente.nl>


# Set-up virtual environment
############################
ENV VIRTUAL_ENV=/opt/venv
# Uncomment if no virtual environment is present in BASE_IMAGE
#RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# Build dftlib
###############
RUN mkdir /opt/dftlib
WORKDIR /opt/dftlib

# Copy the content of the current local repository into the Docker image
COPY . .

# Build dftlib
RUN python setup.py develop
