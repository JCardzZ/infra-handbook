"""Shared style for every python diagram in the handbook.

Every script in diagrams/ builds its figure through these helpers so all
diagrams share the same font, spacing, layer colors, edge styles and legend.
See docs/diagrams-guide.md for when to use each diagram type.
"""

import itertools
import os
from html import escape
from pathlib import Path

import diagrams

from diagrams import Cluster, Diagram, Edge, Node

OUT_DIR = os.environ.get("DIAGRAMS_OUT", "docs/assets/diagrams")

FONT = "Helvetica"
INK = "#1f2933"
MUTED = "#52606d"
FLOW = "#616e7c"
ACCENT = "#0f5f5a"
FAILURE = "#c62828"

# Cluster colors per layer. Background is light so the SVG stays readable on
# the white card the site wraps it in (light and dark mode).
LAYERS = {
    "cloud": {"bgcolor": "#ffffff", "pencolor": "#9aa5b1", "label": "Nube / proyecto"},
    "network": {"bgcolor": "#f8fafb", "pencolor": "#7b8794", "label": "Red (VPC / VNet / región)"},
    "internet": {"bgcolor": "#f1f3f5", "pencolor": "#adb5bd", "label": "Internet"},
    "public": {"bgcolor": "#e7f1fb", "pencolor": "#5b9bd5", "label": "Capa pública"},
    "private": {"bgcolor": "#e8f5ec", "pencolor": "#5aa872", "label": "Capa privada"},
    "data": {"bgcolor": "#fdf3e1", "pencolor": "#d99a2b", "label": "Datos"},
    "broken": {"bgcolor": "#fdecec", "pencolor": FAILURE, "label": "Estado roto"},
    "fixed": {"bgcolor": "#eef7ee", "pencolor": "#2e7d32", "label": "Estado arreglado"},
    # AWS groups follow the AWS Architecture Icons spec (2023+): no fill, colored
    # border, black text, group icon. Colors from awslabs/aws-icons-for-plantuml.
    "aws_cloud": {"bgcolor": "#ffffff", "pencolor": "#232f3e", "label": "AWS Cloud"},
    "aws_vpc": {"bgcolor": "#ffffff", "pencolor": "#8c4fff", "label": "VPC"},
    "aws_public": {"bgcolor": "#ffffff", "pencolor": "#7aa116", "label": "Subnet pública (AWS)"},
    "aws_private": {"bgcolor": "#ffffff", "pencolor": "#00a4a6", "label": "Subnet privada (AWS)"},
    # Azure publishes no group colors; these use Azure blue with the official
    # VNet and subnet icons.
    "azure_vnet": {"bgcolor": "#ffffff", "pencolor": "#0078d4", "label": "VNet"},
    "azure_subnet": {"bgcolor": "#ffffff", "pencolor": "#50a7e8", "label": "Subnet (Azure)"},
}

# Group icons shown before a layer's title: provider logos and the official
# network group icons that ship with the diagrams package.
_RESOURCES = Path(diagrams.__file__).resolve().parent.parent / "resources"
GROUP_ICONS = {
    "gcp": "gcp/gcp.png",
    "gcp_vpc": "gcp/network/virtual-private-cloud.png",
    "aws": "aws/aws.png",
    "aws_vpc": "aws/network/vpc.png",
    "aws_public": "aws/network/public-subnet.png",
    "aws_private": "aws/network/private-subnet.png",
    "azure": "azure/azure.png",
    "azure_vnet": "azure/network/virtual-networks.png",
    "azure_subnet": "azure/network/subnets.png",
}

_GRAPH_ATTR = {
    "bgcolor": "white",
    "pad": "0.3",
    "nodesep": "0.5",
    "ranksep": "0.55",
    # Right-angle edges, like the official Google Cloud architecture diagrams.
    "splines": "ortho",
    "fontname": FONT,
    "fontsize": "16",
    "fontcolor": INK,
    "labelloc": "t",
}

# Icons are much smaller than the diagrams default (1.4in): a whole diagram
# should fit on one screen while its labels stay readable.
_NODE_ATTR = {
    "width": "0.85",
    # Icon pinned to the top of the node so the label below never overlaps it.
    "imagepos": "tc",
    "fontname": FONT,
    "fontsize": "13",
    "fontcolor": INK,
}

_EDGE_FONT = {"fontname": FONT, "fontsize": "12"}

_ids = itertools.count()

_ICON = 0.85  # matches _NODE_ATTR["width"]
_LABEL_GAP = 0.06
# One 13pt label line. diagrams adds 0.4in per line, which leaves a tall empty
# band under every multi-line label.
_LINE_HEIGHT = 0.21
Node._height = _ICON + _LABEL_GAP + _LINE_HEIGHT

# diagrams draws an icon node's label flush with the bottom of the node, where
# edges can attach, so lines would run through the text. A trailing blank line
# lifts the label clear of them, and the icon is pinned to the top (imagepos
# "tc") so the label never overlaps it. Orthogonal edges may still leave a node
# at the height of its name; scripts/postprocess_svg.py then puts the name on a
# background so the line passes under it.
_node_init = Node.__init__


def _node_init_with_label_gap(self, label: str = "", **kwargs):
    if self._icon and label:
        label += "\n "  # a bare trailing "\n" ends the line; the space makes a real blank line
    _node_init(self, label, **kwargs)
    if self._icon and label and "height" not in kwargs:
        self._attrs["height"] = str(_ICON + _LABEL_GAP + _LINE_HEIGHT * (self.label.count("\n") + 1))
        # Re-declaring the node id in Graphviz overrides the height diagrams set.
        (self._cluster or self._diagram).node(self._id, self.label, **self._attrs)


Node.__init__ = _node_init_with_label_gap


def diagram(name: str, *, title: str = "", direction: str = "LR", **graph_overrides) -> Diagram:
    """Open a diagram that renders to <OUT_DIR>/<name>.svg."""
    return Diagram(
        title,
        filename=os.path.join(OUT_DIR, name),
        outformat="svg",
        direction=direction,
        show=False,
        graph_attr={**_GRAPH_ATTR, **graph_overrides},
        node_attr=_NODE_ATTR,
    )


def _icon_label(label: str, icon: str) -> str:
    """HTML-like cluster title: a 20px group icon, then the text (\\n for new lines)."""
    path = _RESOURCES / GROUP_ICONS[icon]
    text = "<BR ALIGN=\"LEFT\"/>".join(escape(line) for line in label.split("\n"))
    return (
        '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0"><TR>'
        f'<TD FIXEDSIZE="TRUE" WIDTH="20" HEIGHT="20"><IMG SRC="{path}" SCALE="TRUE"/></TD>'
        f'<TD ALIGN="LEFT" BALIGN="LEFT">  {text}</TD></TR></TABLE>>'
    )


def layer(label: str, kind: str, *, dashed: bool = False, icon: str = "", **graph_overrides) -> Cluster:
    """A cluster colored by layer (see LAYERS), optionally titled with a group icon (see GROUP_ICONS)."""
    colors = LAYERS[kind]
    cluster = Cluster(
        label,
        graph_attr={
            "bgcolor": colors["bgcolor"],
            "pencolor": colors["pencolor"],
            "penwidth": "1.4",
            "style": "rounded,dashed" if dashed else "rounded",
            "fontname": FONT,
            "fontsize": "14",
            "fontcolor": INK,
            "margin": "14",
            **graph_overrides,
        },
    )
    if icon:
        cluster.dot.graph_attr["label"] = _icon_label(label, icon)
    # diagrams names subgraphs after their label; identical labels would merge.
    cluster.name = cluster.dot.name = f"cluster_{next(_ids)}"
    return cluster


def _label(label: str) -> dict:
    # Side spaces keep the text off the line. scripts/postprocess_svg.py puts a
    # background behind every label, so a line that crosses one passes under it.
    if not label:
        return {}
    return {"label": "\n".join(f"  {line}  " for line in label.split("\n"))}


def flow(label: str = "", **attrs) -> Edge:
    """Normal request or data path."""
    return Edge(**_label(label), color=FLOW, fontcolor=MUTED, penwidth="1.4", **_EDGE_FONT, **attrs)


def config(label: str = "", **attrs) -> Edge:
    """Configuration, association or read dependency (not a request path)."""
    return Edge(**_label(label), color=FLOW, fontcolor=MUTED, style="dashed", **_EDGE_FONT, **attrs)


def highlight(label: str = "", **attrs) -> Edge:
    """The path the reader should focus on."""
    return Edge(**_label(label), color=ACCENT, fontcolor=ACCENT, penwidth="2.2", **_EDGE_FONT, **attrs)


def failure(label: str = "", **attrs) -> Edge:
    """Broken path: drawn red and bold, with a blocked arrowhead."""
    return Edge(
        **_label(label),
        color=FAILURE,
        fontcolor=FAILURE,
        penwidth="2.4",
        arrowhead="tee",
        **_EDGE_FONT,
        **attrs,
    )


def junction(group: str = "") -> Node:
    """Invisible bend point. Route an edge through it (tail >> flow(arrowhead="none")
    >> junction >> flow() >> head) to choose where an orthogonal line turns; give it
    the same group as the nodes above it to keep that run straight."""
    attrs = {"group": group} if group else {}
    return Node("", shape="point", style="invis", width="0.01", height="0.01", fixedsize="true", **attrs)


def legend(layers=(), edges=("flow",), anchor: Node = None) -> Node:
    """Legend box. Pass anchor to pin it next to a node via an invisible edge."""
    edge_rows = {
        "flow": (FLOW, "solid", "Flujo de request o datos"),
        "config": (FLOW, "dashed", "Configuración o lectura"),
        "highlight": (ACCENT, "solid", "Ruta principal"),
        "failure": (FAILURE, "solid", "Falla"),
    }
    rows = ['<TR><TD COLSPAN="2" ALIGN="LEFT"><B>Leyenda</B></TD></TR>']
    for kind in layers:
        c = LAYERS[kind]
        rows.append(
            f'<TR><TD WIDTH="26" HEIGHT="14" FIXEDSIZE="TRUE" BGCOLOR="{c["bgcolor"]}" COLOR="{c["pencolor"]}" BORDER="1"></TD>'
            f'<TD ALIGN="LEFT">{escape(c["label"])}</TD></TR>'
        )
    for kind in edges:
        color, style, text = edge_rows[kind]
        swatch = (
            f'<FONT COLOR="{color}">- - -</FONT>'
            if style == "dashed"
            else f'<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0"><TR><TD WIDTH="26" HEIGHT="3" FIXEDSIZE="TRUE" BGCOLOR="{color}"></TD></TR></TABLE>'
        )
        rows.append(f'<TR><TD WIDTH="26">{swatch}</TD><TD ALIGN="LEFT">{escape(text)}</TD></TR>')

    label = (
        '<<TABLE BORDER="1" COLOR="#cbd2d9" CELLBORDER="0" CELLSPACING="4" CELLPADDING="2" BGCOLOR="white">'
        + "".join(rows)
        + "</TABLE>>"
    )
    node = Node(label, shape="plaintext", fixedsize="false", width="0", height="0", labelloc="c", fontsize="11")
    if anchor is not None:
        anchor >> Edge(style="invis") >> node
    return node
