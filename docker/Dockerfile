FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DOCKYARD_PROJECT_DIR=/project
ENV DOCKYARD_USER=docker

RUN mkdir $DOCKYARD_PROJECT_DIR
RUN groupadd -r $DOCKYARD_USER -g 1000 \
	&& useradd -u 1000 -r -g $DOCKYARD_USER -d $DOCKYARD_PROJECT_DIR -s /sbin/nologin -c "Docker image user" $DOCKYARD_USER \
	&& chown -R $DOCKYARD_USER:$DOCKYARD_USER $DOCKYARD_PROJECT_DIR

ENV PATH $PATH:$DOCKYARD_PROJECT_DIR/.local/bin
COPY .bashrc /etc/bash.bashrc
COPY entrypoint.sh /docker/entrypoint.sh
COPY run-server.sh /docker/run-server.sh

# Install Python and Package Libraries
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get install -y \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    net-tools \
    nano \
    mc \
    gettext \
    libtiff-dev libjpeg62-turbo-dev zlib1g-dev \
	libfreetype6-dev python3-pil libtiff6 \
	libfreetype6 libwebp-dev jpegoptim \
	python3-dev default-libmysqlclient-dev build-essential \
    default-libmysqlclient-dev python3-mysqldb

RUN apt-get update \
	&& apt-get install -y \
	python3-setuptools python3-distutils python3-pip python3-ipython \
	build-essential git-core gcc \
	cmake musl-dev


RUN apt-get update \
	&& apt-get install -y \
	libwebp7 libopenjp2-7-dev \
	liblcms2-dev \
	tcl8.6-dev tk8.6-dev python3-tk \
	libharfbuzz-dev libfribidi-dev libxcb1-dev \
	libpq-dev libncurses5-dev

VOLUME $DOCKYARD_PROJECT_DIR
WORKDIR $DOCKYARD_PROJECT_DIR

USER $DOCKYARD_USER

EXPOSE 8000 8080 443

ENTRYPOINT ["/docker/entrypoint.sh"]
CMD ["/docker/run-server.sh local"]
