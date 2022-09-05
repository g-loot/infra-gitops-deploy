FROM google/cloud-sdk:slim
RUN apt update
RUN apt-get -y -qq update && apt-get install -y python3=3.7.3-1 --no-install-recommends && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY src /src
COPY requirements.txt .
RUN pip3 install -r requirements.txt
WORKDIR /src
ENTRYPOINT [ "/src/deploy.sh" ]
