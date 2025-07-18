
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
# Project Structure — AWS CDK (Python)

This CDK app defines and deploys infrastructure in **three separate stacks**: `NetworkStack`, `EksStack`, and `BootstrapStack`.

# File Tree

- `app.py` — Entry point that initializes all three stacks
- `cdk.json` — CDK configuration
- `cdk.context.json` — Context values for lookups
- `requirements.txt` — CDK and construct dependencies
- `requirements-lambdadeploy.txt` — Dependencies for Lambda deployment
- `network/`
  - `networkstack.py` — Defines the `NetworkStack` (VPC, subnets, etc.)
- `eks/`
  - `eksstack.py` — Defines the `EksStack` (EKS cluster)
- `bootstrap/`
  - `bootstrapstack.py` — Defines the `BootstrapStack`
- `bootConstructs/`
  - `customLambdaConstruct.py` — CDK construct for a custom Lambda
  - `helmConstruct.py` — CDK construct for Helm value management
- `srccode/`
  - `customlambda/`
    - `customHandler.py` — Lambda handler for the custom resource
  - `lambdadependencies/` — Additional Lambda-layer dependencies
- `utils/`
  - `config_loader.py` — Utility module for loading configuration
- `tests/`
  - `unit/`
    - `test_customHandler.py` — Unit tests for Lambda logic



## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
