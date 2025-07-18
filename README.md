
# CDK project - AWS EKS

This is a CDK development project with Python.

# To Run Locally

1. **Configure environment YAML**  
   Update `conf/<envname>-config.yaml` with the necessary attributes.  
   This file acts like `*.tfvars` in Terraform — it keeps the code environment-agnostic.

2. **Prepare Lambda Layer**  
   Run the `preparedependency.sh` script to build the Lambda layer.  
   Add required Python packages to `requirements-lambdalayer.txt`.

3. **Assume AWS Role**  
   Use `aws sts assume-role` to authenticate locally.  
   The assumed role will be used by CDK to determine the account, region, and permissions.
---
# To Run in CI/CD
1. **Configure environment YAML**  
   Update `conf/<envname>-config.yaml` as with local execution.

2. **Handle Lambda Layer Build**  
   Ensure `preparedependency.sh` is executed as part of the CI pipeline to build the Lambda layer separately.

3. **Commit Synth Files**  
   Commit `cdk.json` and `cdk.context.json` to version control to prevent unintentional `cdk synth` changes.

4. **Assume Role for Deployment**  
   Use `sts assume-role` to authenticate.  
   For **deterministic deployments**, hardcode the AWS `account` and `region` either in:
   - `app.py`  
   - Or the CI/CD runner’s environment variables
---
# Assumptions

-  The SSM parameter `/platform/account/env` is **pre-created** outside of CDK as a prerequisite.
-  Basic VPC networking and EKS infrastructure is already created using CDK L2 constructs with reasonable defaults.
-  Only the Helm value `controller.replicaCount` is dynamically generated — all other Helm values are assumed to use standard chart defaults.
-  Although Helm resources **should ideally be decoupled** from the EKS stack for better lifecycle separation, they are handled in the same app here for simplicity.


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

- `app.py` - Entry point that initializes all three stacks
- `cdk.json` - CDK configuration
- `cdk.context.json` - Context values for lookups
- `requirements.txt` - CDK and construct dependencies
- `requirements-lambdadeploy.txt` - Dependencies for Lambda layers
- `network/`
  - `networkstack.py` - Defines the `NetworkStack` (VPC, subnets, etc.)
- `eks/`
  - `eksstack.py` - Defines the `EksStack` (EKS cluster)
- `bootstrap/`
  - `bootstrapstack.py` - Defines the `BootstrapStack`
- `bootConstructs/`
  - `customLambdaConstruct.py` - CDK construct for a custom resource backed by Lambda
  - `helmConstruct.py` - CDK construct for Helm chart for ingress nginx
- `srccode/`
  - `customlambda/`
    - `customHandler.py` - Lambda handler for the custom resource
  - `lambdadependencies/` - Additional Lambda-layer dependencies
- `utils/`
  - `config_loader.py` - Utility module for loading configuration
- `tests/`
  - `unit/`
    - `test_customHandler.py` - Unit tests for Lambda logic



## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
