from aws_cdk import (
    aws_lambda as _lambda,
    custom_resources as cr,
    CustomResource,
    RemovalPolicy,
    aws_iam as iam,
    aws_logs as logs,
    Duration,
    Stack
)
from datetime import datetime
import aws_cdk
import os
from constructs import Construct

class HelmValuesProvider(Construct):

    def __init__(self, scope: Construct, id: str, ssmParameterName: str, conf, **kwargs) -> None:
        super().__init__(scope, id)

        if not ssmParameterName:
            raise ValueError("ssm_parameter_name must be provided")
        self.ssm_parameter_name = ssmParameterName

        self.lambda_layer = self._create_lambda_layer()
        self.custom_lambda = self._create_custom_lambda()
        self.helm_values = self._create_custom_resource()
        print(type(self.helm_values))
    def _create_lambda_layer(self) -> _lambda.LayerVersion:
        try:
            layer = _lambda.LayerVersion(
                self,
                "LambdaLayer",
                code=_lambda.Code.from_asset(os.path.join("srccode", "lambda_dependencies")),
                compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
                description="Layer with shared dependencies for Lambda functions"
            )
            #layer.apply_removal_policy(RemovalPolicy.RETAIN)
            return layer
        except Exception as e:
            raise RuntimeError(f"Failed to create Lambda Layer: {e}")

    def _create_custom_lambda(self) -> _lambda.Function:
        try:
            func = _lambda.Function(
                self, "CustomResourceHandler",
                runtime=_lambda.Runtime.PYTHON_3_12,
                handler="customHandler.handler",
                code=_lambda.Code.from_asset(os.path.join("srccode", "customlambda")),
                timeout=Duration.seconds(120),
                log_retention=logs.RetentionDays.ONE_WEEK
            )
            func.add_layers(self.lambda_layer)
            #func.apply_removal_policy(RemovalPolicy.RETAIN)

            func.add_to_role_policy(
                iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[f"arn:aws:ssm:{Stack.of(self).region}:{Stack.of(self).account}:parameter{self.ssm_parameter_name}"]
                )
                )
            return func
        except Exception as e:
            raise RuntimeError(f"Failed to create Lambda Function: {e}")

    def _create_custom_resource(self):
        try:
            resource = CustomResource(
                self,
                "HelmValuesCustomResource",
                service_token=self.custom_lambda.function_arn,
                removal_policy=RemovalPolicy.DESTROY,
                properties={
                    "SSMParamName": self.ssm_parameter_name,
                    "deploytrigger": datetime.now().isoformat() # Trigger to ensure the resource is recreated on every deployment.
                }
            )

            return resource.get_att("HelmValues").to_string()
        except Exception as e:
            raise RuntimeError(f"Failed to create custom resource: {e}")