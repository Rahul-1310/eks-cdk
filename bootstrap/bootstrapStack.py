from aws_cdk import (
    # Duration,
    Stack, Fn
)
import os, json, aws_cdk
from constructs import Construct
from bootConstructs.customLambdaResource import HelmValuesProvider
from bootConstructs.helmResource import HelmChartConstruct
from aws_cdk import aws_eks as eks

class bootstrapStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, ekscluster, conf, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Custom Resource
        self.helm_values_provider = HelmValuesProvider(
            self, "HelmValuesProvider",
            ssmParameterName=conf.environment.ssmParameterName,
            conf=conf
        )
        print(self.helm_values_provider.helm_values)
        # nginx ingress controller resource
        HelmChartConstruct(
            self, "HelmChart",
            ekscluster=ekscluster,
            helm_values=self.helm_values_provider.helm_values,
            #helm_values=helm_values_provider.helm_values,
            conf=conf
        )
        
        