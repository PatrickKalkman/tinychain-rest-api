#!/bin/bash
VERSION="0.3.13"
APP="pkalkman/tinychain"
docker buildx build -f ./Dockerfile -t $APP:$VERSION . --load
docker push $APP:$VERSION