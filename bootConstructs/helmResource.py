from aws_cdk import aws_eks as eks
from constructs import Construct

class HelmChartConstruct(Construct):

    def __init__(self, scope: Construct, id: str, ekscluster: eks.Cluster, helm_values, conf, **kwargs) -> None:
        super().__init__(scope, id)

        # if not isinstance(helm_values, dict):
        #     raise ValueError("helm_values must be a dictionary")

        if not isinstance(ekscluster, eks.Cluster):
            raise TypeError("ekscluster must be an instance of eks.Cluster")

        self.helm_chart = self._deploy_nginx_helm_chart(ekscluster, helm_values)

    def _deploy_nginx_helm_chart(self, cluster: eks.Cluster, values) -> eks.HelmChart:
        try:
            nginxChart = eks.HelmChart(self, "nginx",
                cluster=cluster,
                chart="ingress-nginx",
                repository="https://kubernetes.github.io/ingress-nginx",
                namespace="ingress-nginx",
                release="nginx",
                version="4.13.0",
                values=values)
            return nginxChart
        except Exception as e:
            raise RuntimeError(f"Failed to deploy Helm chart: {e}")
