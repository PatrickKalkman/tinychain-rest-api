#!/bin/bash
VERSION="0.2.0"
APP="pkalkman/tinychain"
docker buildx build -f ./Dockerfile -t $APP:$VERSION . --load
docker push $APP:$VERSION