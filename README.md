# wwnz-ai-digital-twins-generator

Cloud Run service to generate digital twins

## Local setup

Nothing special to the setup, just create your virtualenv, install requirements and run `uvicorn web:app --reload` to run your development environment.

## Debugging dev

You can follow the guide here to [proxy cloud run](https://cloud.google.com/run/docs/authenticating/developers#gcloud), then you will be able to make requests as if cloud run were running on http://127.0.0.1:8080
