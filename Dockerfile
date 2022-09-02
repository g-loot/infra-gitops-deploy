FROM google/cloud-sdk:alpine
RUN gcloud components install kubectl
COPY . .
RUN "pip3 install requirements.txt"
ENTRYPOINT [ "/deploy.sh" ]
