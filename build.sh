#zsh

docker build -t jaszhou/python .


#docker tag jaszhou/python:latest asia-northeast1-docker.pkg.dev/master-vehicle-340623/docker-repository/python

#gcloud auth configure-docker asia-northeast1-docker.pkg.dev

docker push jaszhou/python


#gcloud container clusters get-credentials cluster-tokyo


#kubectl patch deployment binance --type='json' -p='[{"op": "replace", "path": "/spec/replicas", "value":0}]'

#sleep 30

#kubectl patch deployment binance --type='json' -p='[{"op": "replace", "path": "/spec/replicas", "value":1}]'


