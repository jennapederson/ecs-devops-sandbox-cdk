import aws_cdk as cdk
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_iam as iam
import aws_cdk.aws_ecs_patterns as ecs_patterns

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

        # task_definition = ecs.FargateTaskDefinition(self,
        #     "ecs-devops-sandbox-task-definition",
        #     execution_role=execution_role,
        #     family="ecs-devops-sandbox-task-definition")

        # container = task_definition.add_container(
        #     "ecs-devops-sandbox",
        #     image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
        #     logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs-devops-sandbox-container")
        # )

        # service = ecs.FargateService(self,
        #     "ecs-devops-sandbox-service",
        #     cluster=cluster,
        #     task_definition=task_definition,
        #     service_name="ecs-devops-sandbox-service")

        task_image_options = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
            family="ecs-devops-sandbox-task-definition",
            execution_role=execution_role,
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            container_name="ecs-devops-sandbox",
            container_port=8080,
            log_driver=ecs.LogDrivers.aws_logs(stream_prefix="ecs-devops-sandbox-container")
        )

        ecs_patterns.ApplicationLoadBalancedFargateService(self, "ecs-devops-sandbox-service",
            cluster=cluster,
            service_name="ecs-devops-sandbox-service",
            # cpu=512,                    # Default is 256
            desired_count=2,            # Default is 1
            task_image_options=task_image_options,
            memory_limit_mib=512,      # Default is 512
            public_load_balancer=True # Default is False
        )
