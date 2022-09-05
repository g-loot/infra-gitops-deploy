FROM google/cloud-sdk:slim
RUN apt-get -y -qq update && apt-get install -y ca-certificates curl --no-install-recommends
RUN curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt-get -y -qq update && apt-get install -y kubectl python3=3.7.3-1 --no-install-recommends && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY src /src
COPY requirements.txt .
RUN pip3 install -r requirements.txt
WORKDIR /src
ENTRYPOINT [ "/src/deploy.sh" ]
