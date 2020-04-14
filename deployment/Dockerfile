FROM python:2-buster
RUN apt update && apt install -y docker.io

WORKDIR /projects/sce-domain-discovery/webui

COPY webui/requirements.txt /projects/sce-domain-discovery/webui/

RUN pip install -r requirements.txt && mkdir /models && mkdir /images

COPY . /projects/sce-domain-discovery/


CMD ["python", "run.py"]

