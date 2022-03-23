FROM google/cloud-sdk:alpine
RUN gcloud components install kubectl
COPY deploy.sh /deploy.sh
ENTRYPOINT [ "/deploy.sh" ]
