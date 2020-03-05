#!/bin/bash

if [ ! -e rvt2 ]; then
    echo "Please, clone the rvt2 repository in this directory"
    exit 1
fi

docker build -t incide/rvt2-base:latest -f Dockerfile.base .
docker build -t incide/rvt2-tools:latest -f Dockerfile.tools .
docker build -t incide/rvt2:latest -f Dockerfile .

docker login -u incide
docker push incide/rvt2:latest
