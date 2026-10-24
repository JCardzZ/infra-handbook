"""Network topology: one GCP VPC with public and private subnets.

Internet traffic enters through a global external Application Load Balancer and
a serverless NEG to Cloud Run. Cloud Run reaches the private subnet with Direct
VPC egress. VMs without external IPs reach the internet through Cloud NAT.
"""

from diagrams.gcp.compute import GCE, Run
from diagrams.gcp.database import SQL
from diagrams.gcp.network import NAT, FirewallRules, LoadBalancing, Router
from diagrams.onprem.client import User, Users
from diagrams.onprem.network import Internet

from _style import config, diagram, flow, highlight, layer, legend

with diagram("gcp-network-topology", direction="LR"):
    # Left to right: Internet in, the project, Internet out. Nodes that share a
    # group sit on one straight row: the HTTPS path on top, the SSH path below.
    with layer("Internet (entrada)", "internet"):
        users = Users("Usuarios", group="https")
        admin = User("Admin", group="ssh")

    with layer("Proyecto de Google Cloud", "cloud", icon="gcp"):
        lb = LoadBalancing("Application LB\nexterno (global)", group="https")
        run = Run("Cloud Run\n(serverless NEG)", group="https")

        with layer("VPC: prod-vpc", "network", icon="gcp_vpc"):
            fw = FirewallRules("Firewall rules")

            with layer("Región us-central1", "network", dashed=True):
                with layer("Subnet pública\n10.0.1.0/24", "public", labelloc="b"):
                    bastion = GCE("VM con\nIP externa", group="ssh")

                with layer("Subnet privada\n10.0.2.0/24", "private", labelloc="b"):
                    app = GCE("VMs sin\nIP externa", group="https")

                nat = NAT("Cloud NAT")
                router = Router("Cloud Router")

        with layer("Datos (private services access)", "data", labelloc="b"):
            db = SQL("Cloud SQL\n(IP privada)")

    with layer("Internet (salida)", "internet", labelloc="b"):
        external = Internet("APIs y repos\nexternos")

    users >> highlight("HTTPS") >> lb
    lb >> highlight() >> run
    run >> flow("Direct VPC egress") >> app
    app >> flow("IP privada") >> db
    admin >> flow("SSH") >> bastion
    fw >> config("permite / niega") >> bastion
    app >> flow("salida") >> nat
    router >> config("configura") >> nat
    nat >> flow("IP pública de NAT") >> external

    legend(
        layers=("internet", "public", "private", "data"),
        edges=("highlight", "flow", "config"),
        anchor=external,  # bottom right, after the last column
    )
