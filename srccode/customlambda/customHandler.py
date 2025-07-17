import boto3
import json
import logging
from crhelper import CfnResource

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize crhelper
helper = CfnResource(json_logging=True, log_level="INFO", boto_level="CRITICAL")
ssm_client = boto3.client("ssm")

@helper.create
@helper.update
def on_create_or_update(event, context):

    logger.info("Received event: %s", json.dumps(event))

    ssm_param_key = event['ResourceProperties'].get('SSMParamName')
    if not ssm_param_key:
        logger.error("SSMParamKey is missing from ResourceProperties")
        raise ValueError("SSMParamKey property is required")

    try:
        response = ssm_client.get_parameter(
            Name=ssm_param_key,
            WithDecryption=True
        )
        ssm_value = response['Parameter']['Value']
        logger.info("Fetched SSM parameter '%s' with value: %s", ssm_param_key, ssm_value)
    except ssm_client.exceptions.ParameterNotFound:
        logger.error("SSM parameter '%s' not found", ssm_param_key)
        raise ValueError(f"SSM parameter '{ssm_param_key}' not found")
    except Exception as e:
        logger.error("Error fetching SSM parameter: %s", str(e))
        raise RuntimeError(f"Error fetching SSM parameter: {str(e)}")

    # Determine replicaCount based on SSM value
    if ssm_value.strip().lower() == "development":
        replica_count = 1
    elif ssm_value.strip().lower() in ("staging", "production"):
        replica_count = 2
    else:
        logger.error("Unsupported SSM parameter value: '%s'", ssm_value)
        raise ValueError(f"Unsupported SSM parameter value '{ssm_value}'")

    # Build helm values
    helm_values = {
        "controller": {
            "replicaCount": replica_count
        }
    }

    logger.info("Generated Helm values: %s", json.dumps(helm_values))

    # Return helm values
    helper.Data["HelmValues"] = json.dumps(helm_values)

    # Return a physical resource id
    return f"HelmValues-{ssm_param_key}"

@helper.delete
def on_delete(event, context):

    #No cleanup required since nothnig is created.
    logger.info("Delete event received. No action needed.")
    return

def handler(event, context):
    logger.info("Handler invoked")
    helper(event, context)
