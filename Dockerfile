FROM google/cloud-sdk:slim
ENV USE_GKE_GCLOUD_AUTH_PLUGIN=True
RUN apt-get -y -qq update && apt-get install -y ca-certificates curl google-cloud-sdk-gke-gcloud-auth-plugin --no-install-recommends
RUN curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt-get -y -qq update && apt-get install -y kubectl=1.25.0-00 python3=3.7.3-1 --no-install-recommends && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY src /infra-gitops-deploy
COPY requirements.txt .
RUN pip3 install -r requirements.txt
ENTRYPOINT [ "/infra-gitops-deploy/deploy.sh" ]
