"""Tri-cloud comparison: outbound internet from a private subnet.

GCP Cloud NAT vs AWS NAT Gateway vs Azure NAT Gateway, side by side, each with
its own official icons and group style, all exiting to one shared Internet node.
"""

from diagrams.aws.compute import EC2
from diagrams.aws.network import IGW, NATGateway, RouteTable
from diagrams.azure.compute import VM
from diagrams.azure.networking import Nat, PublicIpAddresses
from diagrams.gcp.compute import GCE
from diagrams.gcp.network import NAT, Router
from diagrams.onprem.network import Internet

from _style import config, diagram, flow, junction, layer, legend

with diagram("tricloud-private-egress", direction="TB", nodesep="0.6", ranksep="0.6"):
    with layer("Google Cloud", "cloud", icon="gcp"):
        with layer("VPC (subnets regionales)", "network", icon="gcp_vpc"):
            with layer("Subnet privada", "private"):
                gcp_vm = GCE("VM sin IP externa", group="gcp")
            gcp_router = Router("Cloud Router")
            gcp_nat = NAT("Cloud NAT\n(gestionado, sin\ninstancia en la ruta)", group="gcp")

    # AWS boxes use the AWS group style: colored border, no fill, group icon.
    with layer("AWS Cloud", "aws_cloud", icon="aws"):
        with layer("VPC (subnets por AZ)", "aws_vpc", icon="aws_vpc"):
            with layer("Subnet privada", "aws_private", icon="aws_private"):
                aws_vm = EC2("EC2")
                aws_rt = RouteTable("Route table\n0.0.0.0/0 →\nNAT GW")
            with layer("Subnet pública", "aws_public", icon="aws_public"):
                aws_nat = NATGateway("NAT Gateway\n+ Elastic IP")
            aws_igw = IGW("Internet Gateway")

    with layer("Azure", "cloud", icon="azure"):
        with layer("VNet", "azure_vnet", icon="azure_vnet"):
            with layer("Subnet privada", "azure_subnet", icon="azure_subnet"):
                az_vm = VM("VM sin IP pública", group="az")
            az_nat = Nat("NAT Gateway\n(asociado a la subnet)", group="az")
            az_ip = PublicIpAddresses("IP pública\ndel NAT Gateway", group="az")

    with layer("Internet", "internet", labelloc="b"):  # entered from above
        internet = Internet("Internet")

    gcp_vm >> flow() >> gcp_nat
    gcp_router >> config("configura") >> gcp_nat
    # GCP and Azure drop straight down to a bend point below their cloud box,
    # then turn toward Internet, so no line cuts through the AWS box.
    gcp_bend = junction("gcp")
    gcp_nat >> flow(arrowhead="none", minlen="2") >> gcp_bend
    gcp_bend >> flow() >> internet

    aws_vm >> flow() >> aws_nat
    aws_rt >> config("enruta") >> aws_nat
    aws_nat >> flow() >> aws_igw
    aws_igw >> flow(minlen="2") >> internet

    az_vm >> flow() >> az_nat
    az_nat >> config("usa") >> az_ip
    az_bend = junction("az")
    az_ip >> flow(arrowhead="none") >> az_bend
    az_bend >> flow() >> internet

    legend(edges=("flow", "config"), anchor=internet)
