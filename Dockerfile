# Dockerfile for dftlib
#######################
# The Docker image can be built by executing:
# docker build -t yourusername/dftlib .
# A different stormpy base image can be set from the commandline with:
# --build-arg STORMPY_BASE=<new_base_image>

# Set stormpy base image
ARG STORMPY_BASE=movesrwth/stormpy:stable
FROM $STORMPY_BASE
LABEL org.opencontainers.image.authors="m.volk@tue.nl"


# Configuration arguments
#########################
# The arguments can be set from the commandline with:
# --build-arg <arg_name>=<value>

# Optional support to install for dftlib, such as '[test,stormpy]'
ARG options=""


# Set-up virtual environment
############################
ENV VIRTUAL_ENV=/opt/venv
# Uncomment if no virtual environment is present in STORMPY_BASE
#RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# Build dftlib
###############
RUN mkdir /opt/dftlib
WORKDIR /opt/dftlib

# Copy the content of the current local repository into the Docker image
COPY . .

# Build dftlib
RUN pip install -v .$options
