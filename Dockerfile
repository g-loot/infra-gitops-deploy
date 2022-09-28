FROM python:3.7.14-slim
COPY src /infra-gitops-deploy
COPY requirements.txt .
RUN pip3 install -r requirements.txt
ENTRYPOINT [ "/infra-gitops-deploy/deploy.sh" ]
