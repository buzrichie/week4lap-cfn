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

with Diagram("ECS CI/CD Architecture", show=False, direction="LR"):  # <<-- force Left-to-Right

    user = User("End User")

    with Cluster("Developer Zone"):
        developer = User("Developer")
        github = Github("GitHub")
        developer >> Edge(label="git push") >> github

    with Cluster("GitHub Zone"):
        ghactions = GithubActions("GitHub Actions Workflow")
        github >> Edge(label="Triggers") >> ghactions
        ghactions >> Edge(label="Build & Push (OIDC)") >> ECR("Amazon ECR")

    with Cluster("AWS Environment"):

        s3_cf = S3("S3\nCloudFormation GitSync")
        s3_cp = S3("S3\nCodePipeline Artifacts")

        with Cluster("Custom VPC"):
            alb = ALB("Application Load Balancer")
            ecs = ECS("ECS Fargate\nJava App")
            alb >> Edge(label="HTTP/S Traffic") >> ecs

        with Cluster("CI/CD Services"):
            eb = Eventbridge("EventBridge\nECR Push")
            cp = Codepipeline("CodePipeline")
            cd = Codedeploy("CodeDeploy\nBlue/Green")

            eb >> cp
            cp >> Edge(label="Artifacts") >> s3_cp
            cp >> cd
            cd >> Edge(label="Deploys to") >> ecs

        with Cluster("Security & Management"):
            ecr = ECR("Amazon ECR")
            cw = Cloudwatch("CloudWatch\nLogs & Metrics")

        ecs >> Edge(label="Logs & Metrics") >> cw

    # External links
    user >> Edge(label="Access via ALB") >> alb
    ghactions - Edge(style="dotted", label="OIDC Federation") - ecr

    # CloudFormation GitSync
    github >> Edge(label="GitSync Template Upload") >> s3_cf
    s3_cf >> Edge(label="Template URL") >> Cloudformation("CloudFormation") >> alb
