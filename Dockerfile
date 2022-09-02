FROM google/cloud-sdk:alpine
RUN gcloud components install kubectl
COPY . .
pip3 install requirements.txt
ENTRYPOINT [ "/deploy.sh" ]
