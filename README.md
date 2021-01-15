Idemia In-Person-Proofing Microservice
=================
## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
    - [Setting Up](#setting-up-your-environment)
- [Deploying the application](#deploying-the-application-to-cloud.gov)

## Overview
The Idemia microservice is a Python Django application that uses the Django Rest Framework to expose an API for in-person-proofing functions to GIVE.

## Installation

### Setting up a development environment
To set up your environment, follow these steps (or the equivalent steps if not using a bash-like terminal):
```sh
git clone https://github.com/18F/identity-give-ipp-idemia
cd identity-give-ipp-idemia
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

Installation of dependencies and commit hooks should be installed and ready to go now. To run the application locally:
```sh
cd idemia
python manage.py runserver
```

### Deploying the application to Cloud.gov
All deployments require having the correct Cloud.gov credentials in place. If you haven't already, visit [Cloud.gov](https://cloud.gov) and set up your account and CLI.

*manifest.yml* file contains the deployment configuration for cloud.gov, and expects a vars.yaml file that includes runtime variables referenced. For info, see [cloud foundry manifest files reference](https://docs.cloudfoundry.org/devguide/deploy-apps/manifest-attributes.html)

The application database must be deployed prior to the application, and can be deployed with the following commands:
```sh
cf create-service aws-rds <service-instance> ipp-idemia-db
```

*You must wait* until the database has completed provisioning to continue with the deployment. Wait for the status of `cf service ipp-idemia-db` to change to `create succeeded`
```sh
watch -n 15 cf service ipp-idemia-db
```

After the database has come up, running `cf push --vars-file vars.yaml` with an appropriately populated `vars.yaml` file should successfully deploy the application.
