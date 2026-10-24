# Guía de diagramas

Cómo se dibujan los diagramas de este manual, para que todos los capítulos se vean consistentes y se lean igual que las guías de arquitectura oficiales de Google Cloud, AWS y Azure.

!!! concepto "Principios"
    - **Una idea por diagrama.** Si necesitas explicar dos cosas, haz dos diagramas.
    - **Íconos oficiales** de cada nube para servicios; íconos genéricos solo para lo que no es de un proveedor (usuarios, Internet, archivos).
    - **El color comunica capa, no decoración.** El rojo se reserva para fallas.
    - **Diagramas como código.** Los SVG se generan desde `diagrams/`; nunca se editan a mano.
    - **Accesibles.** Todo diagrama lleva texto alternativo y un caption; los de Mermaid llevan `accTitle` y `accDescr`.

## Qué diagrama usar {#which-diagram}

| Tipo | Herramienta | Úsalo para |
|---|---|---|
| [Arquitectura de referencia](#reference-architecture) | `diagrams` (Python) | Qué servicios hay y cómo se conectan |
| [Topología de red](#network-topology) | `diagrams` con clusters | VPC/VNet, regiones, zonas, subnets, firewalls, NAT, load balancers |
| [Comparación tri-cloud](#tri-cloud) | `diagrams` | El mismo patrón en GCP, AWS y Azure, lado a lado |
| [Secuencia](#sequence) | Mermaid `sequenceDiagram` | Flujos de request o de autenticación, paso a paso |
| [Flujo de datos / eventos](#data-flow) | Mermaid `flowchart` o `diagrams` | Cómo se mueven datos o eventos entre componentes |
| [Máquina de estados](#state-machine) | Mermaid `stateDiagram` | Ciclos de vida: estados y transiciones |
| [Árbol de decisión](#decision-tree) | Mermaid `flowchart` | "¿Cuándo usar X vs Y?" |
| [Antes / después](#before-after) | `diagrams` | "Cómo se rompe": el estado roto en rojo junto al arreglado |

Regla rápida: si el diagrama necesita **íconos de servicios**, usa `diagrams`. Si muestra **orden o lógica** (pasos, estados, decisiones), usa Mermaid.

## Convenciones visuales {#conventions}

Todos los diagramas de Python importan `diagrams/_style.py`, que fija fuente, espaciado, colores por capa, estilos de flecha y la leyenda.

| Capa | Color | Uso |
|---|---|---|
| Internet | <span class="hb-swatch" style="background:#f1f3f5;border-color:#adb5bd"></span> | Usuarios, Internet, destinos externos |
| Pública | <span class="hb-swatch" style="background:#e7f1fb;border-color:#5b9bd5"></span> | Subnets o recursos con IP pública |
| Privada | <span class="hb-swatch" style="background:#e8f5ec;border-color:#5aa872"></span> | Subnets y cómputo sin IP pública |
| Datos | <span class="hb-swatch" style="background:#fdf3e1;border-color:#d99a2b"></span> | Bases de datos y almacenamiento |
| Roto / arreglado | <span class="hb-swatch" style="background:#fdecec;border-color:#c62828"></span> <span class="hb-swatch" style="background:#eef7ee;border-color:#2e7d32"></span> | Solo en diagramas antes / después |

**Estilo por proveedor.** Cuando un diagrama muestra una nube concreta, sus cajas siguen el estilo de ese proveedor, con su ícono de grupo en el título (`layer(..., icon="...")`):

| Proveedor | Cajas | Fuente |
|---|---|---|
| AWS | <span class="hb-swatch" style="border-color:#232f3e"></span> AWS Cloud · <span class="hb-swatch" style="border-color:#8c4fff"></span> VPC · <span class="hb-swatch" style="border-color:#7aa116"></span> subnet pública · <span class="hb-swatch" style="border-color:#00a4a6"></span> subnet privada; sin relleno y con texto negro | [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) (colores tomados de [aws-icons-for-plantuml](https://github.com/awslabs/aws-icons-for-plantuml)) |
| Google Cloud | Logo de Google Cloud en el proyecto e ícono de VPC; capas con los colores de esta guía | [Íconos de Google Cloud](https://cloud.google.com/icons) (no publica colores de cajas) |
| Azure | <span class="hb-swatch" style="border-color:#0078d4"></span> VNet · <span class="hb-swatch" style="border-color:#50a7e8"></span> subnet, con sus íconos oficiales | [Azure architecture icons](https://learn.microsoft.com/azure/architecture/icons/) (no publica colores de cajas) |

En todos los casos los íconos de servicio se usan tal cual, sin recortar ni recolorear, y con el nombre del producto debajo.

| Flecha | Estilo | Helper |
|---|---|---|
| Flujo de request o datos | <span class="hb-line" style="border-color:#616e7c"></span> | `flow()` |
| Ruta principal | <span class="hb-line" style="border-color:#0f5f5a"></span> | `highlight()` |
| Configuración o lectura | <span class="hb-line hb-line--dashed" style="border-color:#616e7c"></span> | `config()` |
| Falla | <span class="hb-line" style="border-color:#c62828"></span> | `failure()` |

Las flechas son **ortogonales** (solo tramos rectos y ángulos de 90°), como en los diagramas oficiales de Google Cloud. Al renderizar, `scripts/postprocess_svg.py` pone cada etiqueta junto a su propia flecha, en el lugar que no choca con otros textos, y le da un fondo para que ninguna línea la tache.

Los clusters se crean con `layer("Etiqueta", "private")`, y `legend(...)` agrega la leyenda. Los SVG tienen fondo blanco y el sitio los muestra en una tarjeta blanca, así que se leen igual en modo claro y oscuro. Se ajustan al ancho de la pantalla. Toca o haz clic en cualquier diagrama, también en los de Mermaid (o en el ícono de expandir de su esquina), para abrir el visor de estudio a pantalla completa: la rueda o arrastrar mueven, <kbd>Ctrl</kbd> + rueda o pellizcar hacen zoom, y tiene **Ajustar**, **1:1** (tamaño real) y atajos de teclado (<kbd>+</kbd> <kbd>−</kbd> <kbd>0</kbd> <kbd>1</kbd> <kbd>Esc</kbd>). Al abrirlo, el diagrama se desliza desde su lugar en la página y crece hasta llenar la pantalla.

??? example "Código fuente: `diagrams/_style.py`"
    ```python
    --8<-- "diagrams/_style.py"
    ```

## Arquitectura de referencia {#reference-architecture}

**Cuándo usarlo:** para mostrar qué servicios participan y cómo se conectan, sin entrar en detalles de red. Es el diagrama de "alto nivel" de un capítulo.

<figure class="hb-diagram" markdown="span">
  ![Arquitectura de referencia. El developer usa gcloud CLI, que guarda credenciales en credentials.db y se autentica ante Google OAuth como la app Google Cloud SDK. Terraform y las client libraries leen application_default_credentials.json, que se autentica como la app Google Auth Library con el scope cloud-platform, resaltado como ruta principal. Google OAuth entrega access tokens para Cloud Run, Cloud SQL y Cloud Storage.](assets/diagrams/adc-credentials.svg)
  <figcaption>Ejemplo: credenciales del CLI vs ADC (usado en el capítulo de ADC). Toca o haz clic para abrir el visor con zoom.</figcaption>
</figure>

??? example "Código fuente: `diagrams/adc_credentials.py`"
    ```python
    --8<-- "diagrams/adc_credentials.py"
    ```

## Topología de red {#network-topology}

**Cuándo usarlo:** cuando importa *dónde* vive cada recurso: proyecto, VPC, región, subnet, y por dónde entra y sale el tráfico. Usa un cluster por nivel (proyecto → VPC → región → subnet) y colorea las subnets por capa.

<figure class="hb-diagram" markdown="span">
  ![Topología de red en Google Cloud. Los usuarios entran por HTTPS a un Application Load Balancer externo global, que enruta a Cloud Run mediante un serverless NEG. Cloud Run usa Direct VPC egress hacia la subnet privada 10.0.2.0/24 de la VPC prod-vpc en us-central1, donde hay VMs sin IP externa que acceden a Cloud SQL por IP privada. Un admin entra por SSH a una VM con IP externa en la subnet pública 10.0.1.0/24, controlada por firewall rules. Las VMs privadas salen a Internet a través de Cloud NAT, configurado por Cloud Router.](assets/diagrams/gcp-network-topology.svg)
  <figcaption>Ejemplo: una VPC en GCP con subnets pública y privada, Cloud NAT, load balancer externo y Cloud Run. Toca o haz clic para abrir el visor con zoom.</figcaption>
</figure>

!!! tip "En GCP, pública o privada depende de la VM, no de la subnet"
    Las subnets de GCP no son públicas ni privadas por sí mismas: una VM es "pública" si tiene IP externa. Los nombres del diagrama describen la intención de cada subnet.

??? example "Código fuente: `diagrams/gcp_network_topology.py`"
    ```python
    --8<-- "diagrams/gcp_network_topology.py"
    ```

## Comparación tri-cloud {#tri-cloud}

**Cuándo usarlo:** en la sección "GCP vs AWS vs Azure" de un capítulo, cuando el mismo patrón se implementa distinto en cada nube. Una columna por nube, mismo orden de arriba hacia abajo, y un destino compartido al final para que las diferencias salten a la vista.

<figure class="hb-diagram" markdown="span">
  ![Comparación de salida a Internet desde una subnet privada. En Google Cloud, una VM sin IP externa sale por Cloud NAT, configurado por Cloud Router y sin instancia en la ruta. En AWS, una EC2 en subnet privada usa una route table con 0.0.0.0/0 hacia un NAT Gateway con Elastic IP en una subnet pública, y de ahí al Internet Gateway. En Azure, una VM sin IP pública sale por un NAT Gateway asociado a la subnet, que usa una IP pública. Las tres terminan en Internet.](assets/diagrams/tricloud-private-egress.svg)
  <figcaption>Ejemplo: salida a Internet desde una subnet privada con Cloud NAT, AWS NAT Gateway y Azure NAT Gateway. Toca o haz clic para abrir el visor con zoom.</figcaption>
</figure>

??? example "Código fuente: `diagrams/tricloud_private_egress.py`"
    ```python
    --8<-- "diagrams/tricloud_private_egress.py"
    ```

## Secuencia {#sequence}

**Cuándo usarlo:** para flujos donde importa el **orden**: autenticación, llamadas entre servicios, handshakes. Numera los pasos (`autonumber`) y usa `alt` para mostrar el camino feliz y el de error.

=== "Diagrama"

    ```mermaid
    --8<-- "diagrams/mermaid/sequence-service-to-service.mmd"
    ```

=== "Código"

    ```text
    --8<-- "diagrams/mermaid/sequence-service-to-service.mmd"
    ```

## Flujo de datos / eventos {#data-flow}

**Cuándo usarlo:** para mostrar cómo viaja un dato o evento entre componentes. Usa Mermaid si lo que importa es el recorrido; usa `diagrams` si además importan los servicios concretos y su ubicación. Los caminos de error van punteados y en rojo.

=== "Diagrama"

    ```mermaid
    --8<-- "diagrams/mermaid/flow-events.mmd"
    ```

=== "Código"

    ```text
    --8<-- "diagrams/mermaid/flow-events.mmd"
    ```

## Máquina de estados {#state-machine}

**Cuándo usarlo:** para entidades con ciclo de vida, como una transferencia, un deploy o un certificado. Cada transición lleva la condición que la dispara. Este ejemplo es genérico; no describe el modelo de puente.

=== "Diagrama"

    ```mermaid
    --8<-- "diagrams/mermaid/state-transfer.mmd"
    ```

=== "Código"

    ```text
    --8<-- "diagrams/mermaid/state-transfer.mmd"
    ```

## Árbol de decisión {#decision-tree}

**Cuándo usarlo:** para preguntas del tipo "¿cuándo usar X vs Y?". Las preguntas van en rombos, las respuestas finales en verde, y cada rama lleva la condición en su etiqueta.

=== "Diagrama"

    ```mermaid
    --8<-- "diagrams/mermaid/decision-compute.mmd"
    ```

=== "Código"

    ```text
    --8<-- "diagrams/mermaid/decision-compute.mmd"
    ```

## Antes / después {#before-after}

**Cuándo usarlo:** en "Cómo se rompe", para mostrar el estado roto junto al arreglado. El cluster roto usa la capa `broken`, el arreglado usa `fixed`, y la ruta que falla se dibuja con `failure()`: roja, gruesa y terminada en una barra que indica bloqueo.

<figure class="hb-diagram" markdown="span">
  ![Antes y después. Antes, sin Cloud NAT: una VM sin IP externa en una subnet privada intenta salir a Internet para apt-get o para descargar una imagen, y la conexión expira; la ruta está en rojo y bloqueada. Después, con Cloud NAT: la misma VM sale por Cloud NAT, configurado por Cloud Router, y llega a Internet con la IP pública de NAT.](assets/diagrams/gcp-egress-before-after.svg)
  <figcaption>Ejemplo: una VM privada no puede salir a Internet hasta que existe Cloud NAT. Toca o haz clic para abrir el visor con zoom.</figcaption>
</figure>

??? example "Código fuente: `diagrams/gcp_egress_before_after.py`"
    ```python
    --8<-- "diagrams/gcp_egress_before_after.py"
    ```

## Cómo agregar un diagrama {#how-to-add}

1. **Python (`diagrams`):** crea `diagrams/<nombre>.py` y empieza con `from _style import diagram, layer, flow, ...`. Abre el diagrama con `with diagram("<nombre-del-svg>"):`.
2. **Mermaid:** escríbelo directo en el capítulo. En un `flowchart`, empieza con el frontmatter `config: flowchart: curve: step` (ver `diagrams/mermaid/flow-events.mmd`) para que las flechas también sean ortogonales. Si se reutiliza o se muestra su código, guárdalo en `diagrams/mermaid/<nombre>.mmd` e inclúyelo con un snippet `--8<--`.
3. Renderiza y valida:

    ```bash
    make diagrams   # renderiza diagrams/*.py a docs/assets/diagrams/*.svg
    make build      # diagramas + mkdocs build --strict
    make serve      # sitio local con live reload
    ```

4. Inserta el SVG como imagen (`![texto alternativo](...)`, sin envolverla en un enlace) dentro de `<figure class="hb-diagram" markdown="span">`, con texto alternativo que describa el flujo completo y un `<figcaption>`. El visor de estudio se agrega solo.
5. Elige la orientación según la forma del resultado: las pantallas son apaisadas, así que un diagrama más ancho que alto se ve más grande en el visor. Usa `direction="LR"` para recorridos y arquitecturas (ADC, topología, antes / después) y `direction="TB"` cuando comparas columnas lado a lado (tri-cloud). Los flowcharts de Mermaid van en `TD`: en `LR` quedan como tiras muy anchas y bajas. Para alinear nodos en una fila recta, dales el mismo `group="..."`.
   Si una flecha dobla por dentro de una caja ajena, hazla pasar por un punto de quiebre: `origen >> flow(arrowhead="none") >> junction("col") >> flow() >> destino`, con el mismo `group="col"` en los nodos de esa columna para que baje recta (ejemplo: `diagrams/tricloud_private_egress.py`).
6. Commitea el `.py` (o `.mmd`) junto con el SVG generado.

!!! cuidado "Antes de commitear, revisa el diagrama"
    Ábrelo en el sitio en modo claro y oscuro y verifica que los íconos se vean, que ninguna etiqueta toque una flecha y que la leyenda explique cada color usado.
