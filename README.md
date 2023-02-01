# wwnz-ai-digital-twins-generator

Cloud Run service to generate digital twins

# Service account requirements

* Must be able to access BQ with table creation/write access
*


## Local docker build

```bash
docker build digital-twins-generator:local . --build-arg BRANCH_NAME=local PROJECT_ID=my-project-id
docker run digital-twins-generator:local
```
