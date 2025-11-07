from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from aws_cdk import aws_lambda as lambda_
from constructs import Construct
import os


class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table
        events_table = dynamodb.Table(
            self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For dev/testing only
        )

        # Lambda Function using PythonFunction
        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        
        api_lambda = PythonFunction(
            self, "EventsApiFunction",
            entry=backend_path,
            runtime=lambda_.Runtime.PYTHON_3_11,
            index="main.py",
            handler="handler",
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "EVENTS_TABLE_NAME": events_table.table_name,
            }
        )

        # Grant Lambda permissions to access DynamoDB
        events_table.grant_read_write_data(api_lambda)

        # API Gateway
        api = apigateway.LambdaRestApi(
            self, "EventsApi",
            handler=api_lambda,
            proxy=True,
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["*"],
            ),
        )

        # Outputs
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="API Gateway URL"
        )
        
        CfnOutput(
            self, "TableName",
            value=events_table.table_name,
            description="DynamoDB Table Name"
        )
