from aws_cdk import Stack
import os
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import CfnOutput

class NetworkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, conf, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.privatesubnets = self._build_private_subnets(conf)
        self.publicsubnets = self._build_public_subnets(conf)

        combined_subnet_config = self.publicsubnets + self.privatesubnets
        nat_subnet_selection = self._get_nat_gateway_subnet_selection(conf)

        self._vpc = self._create_vpc(conf, combined_subnet_config, nat_subnet_selection)

        CfnOutput(self, "eksvpc", value=self._vpc.vpc_id, description="EKS VPC ID")
        
    
    def _build_private_subnets(self, conf):
        private_subnets = []

        if not conf.vpc.private_subnets.enabled:
            return []

        try:
            for i, mask in enumerate(conf.vpc.private_subnets.primary_cidr_masks):
                private_subnets.append(ec2.SubnetConfiguration(
                    name=f"primary-private-{i}",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=mask
                ))
        except Exception as e:
            raise ValueError(f"Error building private subnets: {e}")

        return private_subnets

    def _build_public_subnets(self, conf):
        public_subnets = []

        if not conf.vpc.public_subnets.enabled:
            return []

        try:
            for i, mask in enumerate(conf.vpc.public_subnets.primary_cidr_masks):
                public_subnets.append(ec2.SubnetConfiguration(
                    name=f"primary-public-{i}",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=mask
                ))
        except Exception as e:
            raise ValueError(f"Error building public subnets: {e}")

        return public_subnets

    def _get_nat_gateway_subnet_selection(self, conf):
        if conf.vpc.nat_gateways.enabled:
            return ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        return None

    def _create_vpc(self, conf, subnet_config, nat_subnet_selection) -> ec2.Vpc:
        try:
            return ec2.Vpc(self, "VPC",
                cidr=conf.vpc.cidr,
                max_azs=conf.vpc.azs,
                nat_gateways=1 if bool(conf.vpc.nat_gateways.enabled) else 0,
                nat_gateway_subnets=nat_subnet_selection,
                subnet_configuration=subnet_config
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create VPC: {e}")
        


