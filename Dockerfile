FROM python:3.11.4-alpine3.18
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" > /etc/apk/repositories &&\
    echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories &&\
    apk update && apk upgrade &&\
    apk add chromium\
    && apk add chromium-chromedriver
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "./main.py"]
EXPOSE 443
EXPOSE 80
EXPOSE 8080
