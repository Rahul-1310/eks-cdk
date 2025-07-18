from aws_cdk import (
    # Duration,
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_eks as eks,
    # aws_sqs as sqs,
)
import os
import aws_cdk
from constructs import Construct
#from aws_cdk.lambda_layer_kubectl_v33 import KubectlV33Layer
import importlib

class EksStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, _vpc, conf, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.conf = conf
        self.kube_version = conf.eks.get("version", "33")
        self.kubectl_layer_class = self.get_kubectl_layer(self.kube_version)
        self.kubernetes_version = self.get_kubernetes_version(f"1_{self.kube_version}")

        # Check if the VPC has NAT gateways configured.
        if not self._vpc_has_nat(_vpc):
            raise ValueError("VPC does not have NAT gateway(s), but PRIVATE_WITH_EGRESS subnets are used.")

        eks_master_role = iam.Role(self, 'EksMasterRole',
                                   role_name='EksMasterRole',
                                   assumed_by=iam.AccountRootPrincipal()
        )

        # Create the EKS cluster
        self.cluster = eks.Cluster(self, 'Cluster',
                              vpc=_vpc,
                              version=self.kubernetes_version,
                              cluster_name = f"{conf.environment.name}-eks",
                              kubectl_layer=self.kubectl_layer_class(self, "kubectl"),
                              masters_role=eks_master_role,
                              authentication_mode=eks.AuthenticationMode.API_AND_CONFIG_MAP,
                              endpoint_access =eks.EndpointAccess.PUBLIC_AND_PRIVATE,
                              default_capacity=0,
                              vpc_subnets=[ec2.SubnetSelection(
                                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
                                )],      
                              )
        
        if conf.eks.admin_access:
            self.admin_access = self.grant_admin_access(conf.eks.admin_access)
        # Create a managed node group
        self.cluster.add_nodegroup_capacity(
                f"{conf.environment.name}-ng",
                nodegroup_name=f"{conf.environment.name}-nodepool",
                capacity_type=eks.CapacityType.ON_DEMAND,
                min_size=conf.eks.node_group.managed.min,
                max_size=conf.eks.node_group.managed.max,
                desired_size=conf.eks.node_group.managed.desired,
                instance_types=self.get_instance_types(), 
                disk_size=conf.eks.node_group.managed.disk_size,
                subnets=ec2.SubnetSelection(
                                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
                                ), 
                #taints=[eks.TaintSpec()]
            )
        
        
        
        self.ekscluster = self.cluster
        CfnOutput(self, "EksClusterName", value=self.cluster.cluster_name, description="EKS Cluster Name")
        CfnOutput(self, "EksClusterArn", value=self.cluster.cluster_arn, description="EKS Cluster ARN")
        CfnOutput(self, "EksClusterEndpoint", value=self.cluster.cluster_endpoint, description="EKS Cluster Endpoint")

    
    # Function to dynamically import Kubectl layer based on version
    def get_kubectl_layer(self, version: str):
        module_name = f"aws_cdk.lambda_layer_kubectl_v{version.replace('.', '')}"
        try:
            kubectl_layer_module = importlib.import_module(module_name)
            kubectl_layer_class = getattr(kubectl_layer_module, f"KubectlV{version.replace('.', '')}Layer")
            return kubectl_layer_class
        except ModuleNotFoundError:
            raise Exception(f"Layer for Kubectl version {version} not found.")

    # Function to get the Kubernetes version based on the configuration. 
    # Add supported versions here for future uses.
    def get_kubernetes_version(self, version: str) -> eks.KubernetesVersion:
        version_mapping = {
            "1_33": eks.KubernetesVersion.V1_33,
            "1_32": eks.KubernetesVersion.V1_32,
            "1_31": eks.KubernetesVersion.V1_31,
        }
        kubernetes_version = version_mapping.get(version)
        if not kubernetes_version:
            raise ValueError(f"Unsupported Kubernetes version: {version}")
        return kubernetes_version
    
    # Check if the VPC has NAT gateways configured.
    def _vpc_has_nat(self, vpc: ec2.Vpc) -> bool:
        if hasattr(vpc, "nat_gateways"):
            if vpc.nat_gateways == 0:
                return False
        return True
    
    # Fucntion to Get the instance types based on the configuration. Add allowed instances here for future uses.
    def get_instance_types(self) -> list:
        ec2_class = {
            "t2": ec2.InstanceClass.BURSTABLE2,
            "t3": ec2.InstanceClass.BURSTABLE3,
            "t3a": ec2.InstanceClass.BURSTABLE3
        }
        ec2_size = {
            "micro": ec2.InstanceSize.MICRO,
            "small": ec2.InstanceSize.SMALL,
            "medium": ec2.InstanceSize.MEDIUM
        }
        i_types = []
        for instance_type in self.conf.eks.node_group.managed.type:
            try:
                this_type = ec2.InstanceType.of(
                    ec2_class[instance_type.i_class], 
                    ec2_size[instance_type.i_size]
                )
                i_types.append(this_type)
            except KeyError:
                raise ValueError(f"Invalid instance type configuration: {instance_type}. Allowed classes: {list(ec2_class.keys())}, sizes: {list(ec2_size.keys())}")
        return i_types

    def grant_admin_access(self, entities: list) -> None:
        accessPolicy = eks.AccessPolicy.from_access_policy_name("AmazonEKSClusterAdminPolicy",
                    access_scope_type=eks.AccessScopeType.CLUSTER
                )
        for entity in entities:
            if isinstance(entity, str):
                eks.AccessEntry(self, f"access-{entity}",
                    access_policies=[accessPolicy],
                    cluster=self.cluster,
                    principal=entity
                    )
            else:
                raise TypeError(f"Unsupported entity type: {type(entity)}. Only IAM Roles and Users are supported.")