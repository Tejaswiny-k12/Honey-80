# Dockerfile
FROM ubuntu:20.04

# Avoid timezone prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python3 and some utilities
RUN apt-get update && \
    apt-get install -y python3 python3-pip net-tools iproute2 && \
    apt-get clean

# Set workdir
WORKDIR /app

# Copy server script into container
COPY server.py /app/server.py

# Run server.py on container start
CMD ["python3", "server.py"]