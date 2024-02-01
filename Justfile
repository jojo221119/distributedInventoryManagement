# Justfile

default: start

build:
    docker-compose up --build -d
    docker-compose logs -f
    
start:
    docker-compose up -d
    docker-compose logs -f
