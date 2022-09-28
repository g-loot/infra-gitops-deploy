FROM python:3.7.14-slim
RUN apt-get -y -qq update && apt-get install -y ca-certificates curl --no-install-recommends
RUN curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt-get -y -qq update && apt-get install -y kubectl=1.25.0-00 --no-install-recommends && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY src /infra-gitops-deploy
COPY requirements.txt .
RUN pip3 install -r requirements.txt
ENTRYPOINT [ "/infra-gitops-deploy/deploy.sh" ]
