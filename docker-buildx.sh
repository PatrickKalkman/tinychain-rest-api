#!/bin/bash
VERSION="0.3.2"
APP="pkalkman/tinychain"
docker buildx build -f ./Dockerfile -t $APP:$VERSION . --load
docker push $APP:$VERSION