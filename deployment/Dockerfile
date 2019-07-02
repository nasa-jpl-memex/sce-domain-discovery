
# Pull base image.

FROM ubuntu:bionic
WORKDIR /projects/sce-domain-discovery/
RUN apt-get update && \
    apt-get install -y software-properties-common wget maven emacs-nox python python-setuptools python-pip python-dev build-essential docker.io
#RUN \
#  echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
#  apt-add-repository universe && \
#  add-apt-repository -y ppa:webupd8team/java && \
#  apt-get update && \
#  apt-get install -y oracle-java8-installer && \
#  rm -rf /var/lib/apt/lists/* && \
#  rm -rf /var/cache/oracle-jdk8-installer

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle


COPY . /projects/sce-domain-discovery/

WORKDIR /projects/sce-domain-discovery/webui
RUN pip install -r requirements.txt

CMD ["python", "run.py"]

