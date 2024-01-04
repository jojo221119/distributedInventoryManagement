# Justfile

default: start

build:
    docker-compose up --build -d

start:
    docker-compose up -d
