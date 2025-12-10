Secrets Management – AWS Secrets Manager + CSI Driver

This project uses AWS Secrets Manager together with the Kubernetes Secrets Store CSI Driver to securely deliver application secrets into pods.

This approach ensures:

No secrets in Git

No secrets in environment variables

No static credentials inside containers

Secrets always come directly from AWS at runtime

It is a clean, secure, and cloud-native solution for managing sensitive values.

1. Why Use Secrets Manager Instead of Kubernetes Secrets?

AWS Secrets Manager provides several advantages:

✔ Encryption handled automatically

Secrets are encrypted at rest and at transit.

✔ Centralized management

Rotate, update, or audit secrets without touching Kubernetes.

✔ IAM-based access

Pods access secrets using IRSA roles — no root access required.

✔ No duplication

Secrets stay in AWS, not stored inside Kubernetes objects.

2. Secrets Store CSI Driver

The CSI driver is a Kubernetes addon that mounts secrets from external providers (like AWS).

In this project:

Terraform provisions the required IAM role.

The CSI driver is installed in the cluster via Helm (or manifest).

Each microservice references a SecretProviderClass to load the secret.

The CSI driver reads the secret at pod startup and mounts it as a file.

3. IAM Requirements (Terraform)

The folder:

infra/terraform/secrets-store-csi/


contains IAM policies that allow the CSI driver to:

Read from AWS Secrets Manager

Decrypt KMS-encrypted secrets (if needed)

The permissions include:

secretsmanager:GetSecretValue
kms:Decrypt


These permissions are attached to the CSI driver via IRSA.

4. SecretProviderClass

Each service has a SecretProviderClass object that defines which AWS secret to pull.

Example (simplified):

apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: kontox-secrets
spec:
  provider: aws
  parameters:
    objects: |
      - objectName: "Kontox-secret"
        objectType: "secretsmanager"


This tells Kubernetes:

Use the AWS provider

Pull the secret named Kontox-secret

Mount it as a file inside the pod

5. How Pods Receive Secrets

Each deployment mounts a CSI volume:

volumes:
  - name: kontox-secrets
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: kontox-secrets


Then the containers mount it:

volumeMounts:
  - name: kontox-secrets
    mountPath: "/mnt/secrets-store"
    readOnly: true


Inside the pod, the secrets appear as files such as:

/mnt/secrets-store/<secret-key>


Your application can read these files at runtime.

6. Creating the Secrets in AWS

This is done manually via the AWS Console or CLI.

In AWS Console:

Open Secrets Manager

Click Store a new secret

Choose Other type of secret

Add your key/value pairs

Name the secret: Kontox-secret

Save

Once created, the CSI driver and IRSA role allow pods to retrieve it securely.