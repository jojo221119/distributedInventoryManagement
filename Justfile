# Justfile

default: start

build:
    docker-compose up --build 
    
start:
    docker-compose up -d
