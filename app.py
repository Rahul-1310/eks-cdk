#!/usr/bin/env python3
import os
from boto3 import client, session
import aws_cdk as cdk
from utils.config_loader import load_config
from network.networkstack import NetworkStack
from eks.eksstack import EksStack
from bootstrap.bootstrapStack import bootstrapStack

# Load config
conf, env_name = load_config()

# Get AWS account and regio
account = client('sts').get_caller_identity()['Account']
region = session.Session().region_name

# Initialize the CDK application
app = cdk.App()
env = cdk.Environment(account=account, region=region)

NetworkStackObj = NetworkStack(app, f"{env_name}-VpcStack", env=env, conf=conf)
EksStackObj = EksStack(app, f"{env_name}-ClusterStack", env=env, _vpc=NetworkStackObj._vpc,conf=conf)
BootstrapStackObj = bootstrapStack(app, f"{env_name}-BootstrapStack", env=env,ekscluster=EksStackObj.ekscluster,conf=conf)

# add application level tags
for k,v in enumerate(conf.environment.tags):
    cdk.Tags.of(NetworkStackObj).add(v.key, v.value)
    cdk.Tags.of(EksStackObj).add(v.key, v.value)
    cdk.Tags.of(BootstrapStackObj).add(v.key, v.value)

app.synth()
