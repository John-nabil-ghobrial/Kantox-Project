import os
import logging
from typing import List, Dict, Any

import boto3
import botocore.exceptions
from fastapi import FastAPI, HTTPException

# --------------------------------------------------------------------
# Basic configuration
# --------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aux-service")

AUX_VERSION = os.getenv("APP_VERSION", "dev")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Use IAM role (IRSA) – no keys in code.
s3_client = boto3.client("s3", region_name=AWS_REGION)
ssm_client = boto3.client("ssm", region_name=AWS_REGION)

app = FastAPI(
    title="Aux Service",
    description="Auxiliary service handling AWS interactions (S3, SSM).",
    version=AUX_VERSION,
)


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def _aws_error_to_http(exc: Exception, service: str) -> HTTPException:
    logger.exception("Error calling AWS %s", service)
    return HTTPException(
        status_code=502,
        detail=f"Error calling AWS {service}: {str(exc)}",
    )


# --------------------------------------------------------------------
# Health & version
# --------------------------------------------------------------------
@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "aux-service", "version": AUX_VERSION}


@app.get("/version")
def version() -> Dict[str, str]:
    return {"service": "aux-service", "version": AUX_VERSION}


# --------------------------------------------------------------------
# S3: list buckets
# --------------------------------------------------------------------
@app.get("/aws/buckets")
def list_buckets() -> Dict[str, List[Dict[str, Any]]]:
    """
    List all S3 buckets in the AWS account.
    """
    try:
        response = s3_client.list_buckets()
        buckets = [
            {
                "name": bucket["Name"],
                "creationDate": bucket["CreationDate"].isoformat(),
            }
            for bucket in response.get("Buckets", [])
        ]
        return {"buckets": buckets}
    except botocore.exceptions.BotoCoreError as e:
        raise _aws_error_to_http(e, "S3")


# --------------------------------------------------------------------
# SSM Parameter Store
# --------------------------------------------------------------------
@app.get("/aws/parameters")
def list_parameters() -> Dict[str, List[Dict[str, Any]]]:
    """
    List all parameters in AWS Systems Manager Parameter Store (names & basic metadata).
    """
    try:
        params: List[Dict[str, Any]] = []
        paginator = ssm_client.get_paginator("describe_parameters")

        for page in paginator.paginate():
            for p in page.get("Parameters", []):
                params.append(
                    {
                        "name": p.get("Name"),
                        "type": p.get("Type"),
                        "lastModifiedDate": p.get("LastModifiedDate").isoformat()
                        if p.get("LastModifiedDate")
                        else None,
                        "version": p.get("Version"),
                    }
                )

        return {"parameters": params}
    except botocore.exceptions.BotoCoreError as e:
        raise _aws_error_to_http(e, "SSM")


@app.get("/aws/parameters/{name}")
def get_parameter(name: str) -> Dict[str, Any]:
    """
    Retrieve the value of a specific parameter from AWS Parameter Store.
    Uses WithDecryption=True to support SecureString parameters.
    """
    try:
        response = ssm_client.get_parameter(Name=name, WithDecryption=True)
        p = response.get("Parameter", {})
        return {
            "name": p.get("Name"),
            "value": p.get("Value"),
            "type": p.get("Type"),
            "version": p.get("Version"),
            "lastModifiedDate": p.get("LastModifiedDate").isoformat()
            if p.get("LastModifiedDate")
            else None,
        }
    except ssm_client.exceptions.ParameterNotFound:
        raise HTTPException(status_code=404, detail=f"Parameter '{name}' not found")
    except botocore.exceptions.BotoCoreError as e:
        raise _aws_error_to_http(e, "SSM")


# --------------------------------------------------------------------
# Uvicorn entrypoint
# --------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
