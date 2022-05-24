import aws_cdk as cdk
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_iam as iam
# import aws_cdk.aws_ecs_patterns as ecs_patterns

class EcsDevopsSandboxCdkStack(cdk.Stack):

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecr_repository = ecr.Repository(self,
            "ecs-devops-sandbox-repository",
            repository_name="ecs-devops-sandbox-repository")

        vpc = ec2.Vpc(self,
            "ecs-devops-sandbox-vpc",
            max_azs=3)

        cluster = ecs.Cluster(self,
            "ecs-devops-sandbox-cluster",
            cluster_name="ecs-devops-sandbox-cluster",
            vpc=vpc)

        execution_role = iam.Role(self,
            "ecs-devops-sandbox-execution-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name="ecs-devops-sandbox-execution-role")

        execution_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
                ]
        ))

        #
        # Option 1: Creates service, container, and task definition without creating a load balancer
        #   and other costly resources. Containers will not be publicly accessible.
        #
        task_definition = ecs.FargateTaskDefinition(self,
            "ecs-devops-sandbox-task-definition",
            execution_role=execution_role,
            family="ecs-devops-sandbox-task-definition")

        container = task_definition.add_container(
            "ecs-devops-sandbox",
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs-devops-sandbox-container")
        )

        service = ecs.FargateService(self,
            "ecs-devops-sandbox-service",
            cluster=cluster,
            task_definition=task_definition,
            service_name="ecs-devops-sandbox-service")

        # END Option 1

        #
        # Option 2: Creates a load balancer and related AWS resources using the ApplicationLoadBalancedFargateService construct.
        #   These resources have non-trivial costs if left provisioned in your AWS account, even if you don't use them. Be sure to
        #   clean up (cdk destroy) after working through this exercise.
        #
        # Comment out option 1 and uncomment the code below. Uncomment the aws_cdk.aws_ecs_patterns import at top of file.
        #
        # task_image_options = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
        #     family="ecs-devops-sandbox-task-definition",
        #     execution_role=execution_role,
        #     image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
        #     container_name="ecs-devops-sandbox",
        #     container_port=8080,
        #     log_driver=ecs.LogDrivers.aws_logs(stream_prefix="ecs-devops-sandbox-container")
        # )
        #
        # ecs_patterns.ApplicationLoadBalancedFargateService(self, "ecs-devops-sandbox-service",
        #     cluster=cluster,
        #     service_name="ecs-devops-sandbox-service",
        #     desired_count=2,
        #     task_image_options=task_image_options,
        #     public_load_balancer=True
        # )
        #
        # END Option 2
