FROM python:3.6-slim-stretch
COPY . /demo
RUN pip3 install cherrypy mako networkx PyYAML
ENTRYPOINT ["python3", "/demo/demo.py"]
