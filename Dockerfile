# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.9-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.9

ENV AzureWebJobsScriptRoot=. \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY . .

RUN pip install -r /requirements.txt

CMD ["python", "./main.py"] 
