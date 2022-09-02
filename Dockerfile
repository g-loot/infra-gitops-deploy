FROM google/cloud-sdk:alpine
RUN gcloud components install kubectl
COPY deploy.sh /deploy.sh
COPY canary.py canary.py
ENTRYPOINT [ "/deploy.sh" ]
