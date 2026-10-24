"""Reference architecture: CLI user credentials vs Application Default Credentials.

Used in docs/troubleshooting/gcloud-adc-scope-not-consented.md.
"""

from diagrams.gcp.compute import Run
from diagrams.gcp.database import SQL
from diagrams.gcp.devtools import SDK
from diagrams.gcp.security import Iam
from diagrams.gcp.storage import GCS
from diagrams.generic.storage import Storage
from diagrams.onprem.client import User
from diagrams.onprem.iac import Terraform
from diagrams.programming.language import Java

from _style import config, diagram, flow, highlight, layer, legend

with diagram("adc-credentials", direction="LR", ranksep="0.8"):
    dev = User("Developer")

    # Left to right: developer, laptop, OAuth, APIs. Box titles sit at the bottom,
    # away from the lines that cross the boxes sideways.
    with layer("Laptop del developer", "network", labelloc="b", labeljust="r"):
        with layer("CLI", "private"):
            cli = SDK("gcloud CLI")
            cli_creds = Storage("credentials.db")

        with layer("ADC", "public", labeljust="r"):
            tf = Terraform("Terraform", group="adc")  # same row as the file it reads
            libs = Java("Client libraries")
            adc = Storage("application_default_\ncredentials.json", group="adc")

    oauth = Iam("Google\nOAuth 2.0")

    with layer("APIs de Google Cloud", "cloud", labelloc="b", icon="gcp"):
        apis = [Run("Cloud Run"), SQL("Cloud SQL"), GCS("Cloud Storage")]

    dev >> flow("gcloud auth login") >> cli
    cli >> config() >> cli_creds
    dev >> flow("terraform plan") >> tf
    [tf, libs] >> config("leen") >> adc

    cli_creds >> flow("app: Google Cloud SDK") >> oauth
    adc >> highlight("app: Google Auth Library\nrequiere scope cloud-platform") >> oauth
    oauth >> flow("access token") >> apis

    legend(edges=("flow", "config", "highlight"), anchor=dev)
