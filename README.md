
# CDK Python project - AWS EKS

This is a CDK development project with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```
```
$ source .venv/bin/activate
```


Follow the below steps to run locally:

Install all required dependencies.
```
$ pip install -r requirements.txt
```
This creates a package for custom resource lambda's layer.
```
$ ./preparedependency.sh
```
At this point you can now synthesize the CloudFormation template for this code.
```
$ cdk synth
$ cdk deploy
```
Repository structure:

app.py # Entry point — initializes all 3 stacks
cdk.json # CDK configuration
cdk.context.json # Context values (e.g., lookups)

requirements.txt # CDK and construct library dependencies
requirements-lambdadeploy.txt # Dependencies for Lambda layer/deployment

network/
└── networkstack.py # Defines VPC, subnets, etc. for EKS

eks/
└── eksstack.py # Defines the EKS cluster and associated resources

bootstrap/
└── bootstrapstack.py # Stack for supporting resources like Lambda, Helm, etc.

bootConstructs/
├── customLambdaConstruct.py # CDK construct for deploying a custom Lambda function
└── helmConstruct.py # CDK construct for managing Helm chart values or deployments

srccode/
├── customlambda/
│ └── customHandler.py # Lambda function handler for custom resources
└── lambdadependencies/ # Dependencies/code packaged with Lambda layer

utils/
└── config_loader.py # Utility functions (e.g., config parsing)

tests/
└── unit/
└── test_customHandler.py # Unit tests for Lambda functionality

markdown
Copy
Edit


## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
