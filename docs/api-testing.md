API Testing Guide – Kontaxa Platform

This guide explains how to test both microservices after deployment.
The goal is to verify:

Service connectivity

AWS integration through aux-service

Version metadata in every response

Internal communication between services

Health and readiness of deployments

These tests can be executed on any environment where the services are running (local via port-forward or inside the cluster).

1. Port-Forward the main-api Service

If main-api is deployed in the cluster, expose it locally:

kubectl port-forward -n main-api deploy/main-api 8080:8000


You can now access the API on:

http://localhost:8080

2. Basic Health Check
Command
curl http://localhost:8080/health | jq

Expected Behavior

Service should return status: ok

You should see both version values:

mainApiVersion

auxServiceVersion

Example Output
{
  "data": {
    "status": "ok",
    "service": "main-api"
  },
  "mainApiVersion": "v1.0.5",
  "auxServiceVersion": "v1.0.3"
}


This confirms basic connectivity and versioning logic.

3. Get Version Information
Command
curl http://localhost:8080/version | jq

Expected Result

The API returns its own version, plus the aux-service version it fetches internally.

{
  "data": {
    "service": "main-api"
  },
  "mainApiVersion": "v1.0.5",
  "auxServiceVersion": "v1.0.3"
}

4. List S3 Buckets

This test validates that:

main-api correctly calls aux-service

aux-service can access AWS S3 using IRSA

Command
curl http://localhost:8080/buckets | jq

Expected Output Shape
{
  "data": {
    "buckets": [
      {
        "name": "example-bucket",
        "creationDate": "2024-11-01T10:00:00Z"
      }
    ]
  },
  "mainApiVersion": "v1.0.5",
  "auxServiceVersion": "v1.0.3"
}


If permissions are missing, you may see a 502 with an AWS error message.

5. List SSM Parameters

This verifies SSM access works correctly.

Command
curl http://localhost:8080/parameters | jq

Expected Output Example
{
  "data": {
    "parameters": [
      {
        "name": "/app/env",
        "type": "String",
        "lastModifiedDate": "2024-12-05T12:00:00Z",
        "version": 1
      }
    ]
  },
  "mainApiVersion": "v1.0.5",
  "auxServiceVersion": "v1.0.3"
}

6. Retrieve a Specific Parameter
Command
curl http://localhost:8080/parameters/%2Fapp%2Fenv | jq


(Use URL encoding for names containing slashes.)

Expected Output
{
  "data": {
    "name": "/app/env",
    "value": "production",
    "type": "String",
    "version": 1,
    "lastModifiedDate": "2024-12-05T12:00:00Z"
  },
  "mainApiVersion": "v1.0.5",
  "auxServiceVersion": "v1.0.3"
}

Parameter Not Found Case
{
  "detail": "Parameter '/does/not/exist' not found"
}


This verifies error handling works correctly across both services.

7. Internal Communication Check

To confirm main-api → aux-service communication:

Command
curl http://localhost:8080/buckets


If aux-service is unreachable, main-api will return:

{
  "detail": "Error calling aux-service: ..."
}


This helps validate DNS, namespace configuration, and service names.