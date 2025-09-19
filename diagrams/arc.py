from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.aws.devtools import Codepipeline, Codedeploy
from diagrams.aws.compute import ECS
from diagrams.aws.network import ALB
from diagrams.aws.management import Cloudwatch, Cloudformation
from diagrams.aws.integration import Eventbridge
from diagrams.aws.storage import S3
from diagrams.onprem.client import User

# Handle ECR import across versions
try:
    from diagrams.aws.compute import ECR
except ImportError:
    from diagrams.aws.storage import ECR

with Diagram("Highly Available Java Web App on ECS Fargate", show=False, direction="TB"):
    
    # ===== EXTERNAL ENTITIES =====
    user = User("End User")
    
    # ===== DEVELOPMENT & SOURCE CONTROL =====
    with Cluster("Development & Source Control"):
        developer = User("Developer")
        github_app = Github("GitHub Repo\n(Application Code)")
        github_infra = Github("GitHub Repo\n(Infrastructure Code)")
        
        developer >> Edge(label="git push") >> github_app
        developer >> Edge(label="git push") >> github_infra

    # ===== CI/CD PIPELINE =====
    with Cluster("CI/CD Pipeline", direction="LR"):
        # Build Phase
        with Cluster("Build Phase (GitHub Actions)"):
            ghactions = GithubActions("GitHub Actions Workflow\n(OIDC Authentication)")
            github_app >> Edge(label="Triggers on push") >> ghactions
            ghactions >> Edge(label="Builds & pushes Docker image") >> ECR("Amazon ECR\n(Container Registry)")
        
        # Deployment Phase
        with Cluster("Deployment Phase (AWS Services)"):
            eb = Eventbridge("EventBridge Rule\n(Detects ECR Push)")
            cp = Codepipeline("CodePipeline\n(Orchestration)")
            cd = Codedeploy("CodeDeploy\n(Blue/Green Deployment)")
            
            s3_artifacts = S3("S3 Artifact Store\n(Deployment Packages)")
            
            # Deployment flow
            ECR("Amazon ECR") >> Edge(label="Image push event") >> eb
            eb >> Edge(label="Triggers pipeline") >> cp
            cp >> Edge(label="Stores deployment artifacts") >> s3_artifacts
            cp >> Edge(label="Initiates deployment") >> cd

    # ===== AWS PRODUCTION ENVIRONMENT =====
    with Cluster("AWS Production Environment", direction="LR"):
        # Networking
        with Cluster("VPC Architecture", direction="TB"):
            with Cluster("Public Subnets (AZ1 & AZ2)"):
                alb = ALB("Application Load Balancer\n(Public Endpoint)")
            
            with Cluster("Private Subnets (AZ1 & AZ2)"):
                ecs = ECS("ECS Fargate Service\n(Java Application)")
            
            alb >> Edge(label="Routes traffic\n(HTTP/HTTPS)") >> ecs
        
        # Infrastructure Management
        with Cluster("Infrastructure as Code"):
            s3_templates = S3("S3 Bucket\n(CloudFormation Templates)")
            cf = Cloudformation("CloudFormation\n(Infrastructure Provisioning)")
            github_infra >> Edge(label="GitSync template upload") >> s3_templates
            s3_templates >> Edge(label="References template URL") >> cf
            cf >> Edge(label="Creates/Updates") >> alb
            cf >> Edge(label="Creates/Updates") >> ecs
        
        # Observability
        with Cluster("Monitoring & Observability"):
            cw = Cloudwatch("Amazon CloudWatch\n(Logs, Metrics, Alarms)")
            ecs >> Edge(label="Streams logs & metrics") >> cw

    # ===== EXTERNAL CONNECTIONS & CROSS-SERVICE LINKS =====
    user >> Edge(label="Accesses application via", color="black") >> alb
    ghactions - Edge(style="dashed", label="OIDC Federation", color="blue") - ECR("Amazon ECR")
    cd >> Edge(label="Deploys new version", color="green") >> ecs