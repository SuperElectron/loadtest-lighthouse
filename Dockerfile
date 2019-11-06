FROM python:3.7-alpine3.9

LABEL name="code-quality" \
      maintainer="Mat McCann <matmccann@gmail.com>" \
      version="1.0" \
      description="Loadtest and lighthouse analysis are performed based on exported environment variables."

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.7/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.7/community" >> /etc/apk/repositories

# make directory & copy project into it
RUN mkdir -p /code
COPY /code /code

# installations: https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management
RUN apk update
RUN apk add vim
RUN apk add chromium chromium-chromedriver
RUN apk add nodejs
RUN apk add nodejs-npm
RUN npm i -g lighthouse

# upgrade pip
RUN pip install --upgrade pip

# install selenium
RUN pip install -r code/requirements.txt
# enable bash
RUN /bin/sh -c "apk add --no-cache bash"
#keep container running after dockerfile is finished
CMD tail -f /dev/null