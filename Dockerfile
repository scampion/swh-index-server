FROM python:alpine
MAINTAINER sebastien.campion@protonmail.com
RUN apk add curl g++ make autoconf automake
RUN curl https://codeload.github.com/pelotoncycle/bsort/zip/master | unzip -
WORKDIR bsort-master
RUN ls
RUN autoreconf -i
RUN ./configure
RUN make
RUN make install
ADD . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app:app"]