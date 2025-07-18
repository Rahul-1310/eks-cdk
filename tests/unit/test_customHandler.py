import json
import pytest
import boto3
from moto import mock_aws
from srccode.customlambda import customHandler  

# to build a cloudFormation event
def build_event(ssm_param_name, request_type):
    return {
        "RequestType": request_type,
        "ResourceProperties": {
            "SSMParamName": ssm_param_name
        }
    }


@mock_aws
@pytest.mark.parametrize("env_value,expected_replica", [
    ("development", 1),
    ("staging", 2),
    ("production", 2)
])
def test_create_event(env_value, expected_replica):
    ssm_client = boto3.client("ssm", region_name="eu-central-1")
    ssm_param_name = "/env/test"
    ssm_client.put_parameter(
        Name=ssm_param_name,
        Value=env_value,
        Type="String"
    )

    event = build_event(ssm_param_name, "Create")
    context = {}

    customHandler.ssm_client = ssm_client 
    customHandler.helper.Data.clear()

    customHandler.on_create_or_update(event, context)

    helm_values = customHandler.helper.Data["HelmValues"]
    assert helm_values == expected_replica

@mock_aws
@pytest.mark.parametrize("env_value,expected_replica", [
    ("development", 1),
    ("staging", 2),
    ("production", 2)
])
def test_update_event(env_value, expected_replica):
    ssm_client = boto3.client("ssm", region_name="eu-central-1")
    ssm_param_name = "/env/test"
    ssm_client.put_parameter(
        Name=ssm_param_name,
        Value=env_value,
        Type="String"
    )

    event = build_event(ssm_param_name, "Update")
    context = {}

    customHandler.ssm_client = ssm_client 
    customHandler.helper.Data.clear()

    customHandler.on_create_or_update(event, context)

    helm_values = customHandler.helper.Data["HelmValues"]
    assert helm_values == expected_replica

@mock_aws
def test_invalid_environment_raises_error():
    ssm_client = boto3.client("ssm", region_name="eu-central-1")
    ssm_param_name = "/env/test-invalid"
    ssm_client.put_parameter(
        Name=ssm_param_name,
        Value="qa",  # unsupported value
        Type="String"
    )

    event = build_event(ssm_param_name, "Create")
    context = {}

    customHandler.ssm_client = ssm_client
    customHandler.helper.Data.clear()

    with pytest.raises(ValueError, match="Unsupported SSM parameter value 'qa'. Supported values are 'development', 'staging', 'production'."):
        customHandler.on_create_or_update(event, context)


@mock_aws
def test_missing_ssm_param_key_raises_error():
    event = {"RequestType": "Create", "ResourceProperties": {}}
    context = {}

    with pytest.raises(ValueError, match="SSMParamKey property is required"):
        customHandler.on_create_or_update(event, context)


@mock_aws
def test_parameter_not_found_error():
    ssm_client = boto3.client("ssm", region_name="eu-central-1")
    customHandler.ssm_client = ssm_client

    event = build_event("nonexistent", "Create")
    context = {}

    with pytest.raises(ValueError, match="SSM parameter 'nonexistent' not found"):
        customHandler.on_create_or_update(event, context)

def test_delete_event_does_nothing():
    event = {
        "RequestType": "Delete",
        "ResourceProperties": {
            "SSMParamName": "dummy"
        }
    }
    context = {}
    customHandler.on_delete(event, context)
