# AWS ECS Fargate Blue/Green Infrastructure (Infrastructure-as-Code)

This project provisions a highly-available network and application delivery layer for an ECS Fargate service with blue/green deployments behind an Application Load Balancer (ALB). It also includes container registry and CI/CD integration components.

What you get (at a glance):
- Networking: 1 VPC, 2 public subnets, 2 private subnets across 2 AZs, 1 Internet Gateway, and 2 NAT Gateways (one per AZ) with route tables configured for HA.
- Ingress: Internet-facing ALB across both public subnets.
- Compute: ECS Fargate cluster and service running tasks in private subnets.
- Container Registry: Amazon ECR repository with image scanning and basic lifecycle policy.
- CI/CD: CodeDeploy (ECS blue/green), CodePipeline using an S3 artifact bucket, and GitHub OIDC role for secure, keyless deployments.

Note on costs:
- NAT Gateways incur hourly and data processing charges. This architecture deploys 2 NAT Gateways (one per AZ) for high availability. Clean up when done to avoid unnecessary costs.

## Network Architecture Diagram (diagram-as-code)

The diagram below focuses on the network path and runtime placement of the service. It shows VPC segmentation, routing, and traffic flow from the internet through the ALB to ECS tasks in private subnets.
