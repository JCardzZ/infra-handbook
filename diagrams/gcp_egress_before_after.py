"""Before / after: a private VM cannot reach the internet until Cloud NAT exists.

Example of the "cómo se rompe" diagram type: the broken path is red. Each state
is one left-to-right row, "antes" above "después", so the two paths line up.
"""

from diagrams import Edge
from diagrams.gcp.compute import GCE
from diagrams.gcp.network import NAT, Router
from diagrams.onprem.network import Internet

from _style import config, diagram, failure, flow, layer, legend

with diagram("gcp-egress-before-after", direction="LR", nodesep="0.45"):
    # In LR, Graphviz stacks unconnected clusters bottom-up in declaration
    # order, so "después" is declared first to land below "antes".
    with layer("Después: con Cloud NAT", "fixed"):
        with layer("Subnet privada ", "private"):
            vm_after = GCE("VM sin IP externa")
        router = Router("Cloud Router")
        nat = NAT("Cloud NAT")
        net_after = Internet("Internet")

    with layer("Antes: sin Cloud NAT", "broken"):
        with layer("Subnet privada", "private"):
            vm_before = GCE("VM sin IP externa")
        net_before = Internet("Internet")

    vm_before >> failure("apt-get / pull de imagen:\nla conexión expira") >> net_before

    vm_after >> flow("salida") >> nat
    # Router sits in Cloud NAT's column, so "configura" is a short vertical line
    # instead of one that crosses the subnet.
    vm_after >> Edge(style="invis") >> router
    router >> config(constraint="false", xlabel="  configura  ") >> nat  # plain labels are dropped on non-constraint edges
    nat >> flow("IP pública de NAT") >> net_after

    legend(layers=("broken", "fixed"), edges=("failure", "flow", "config"), anchor=net_after)
