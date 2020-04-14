
# Pull base image.

FROM ubuntu:bionic
WORKDIR /projects/sce-domain-discovery/
RUN apt-get update && \
    apt-get install -y software-properties-common wget python python-setuptools python-pip python-dev

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle

COPY . /projects/sce-domain-discovery/

WORKDIR /projects/sce-domain-discovery/webui
RUN pip install -r requirements.txt && mkdir /models && mkdir /images

CMD ["python", "run.py"]

