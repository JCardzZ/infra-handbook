# Manual de Infra de Manuel

Notas sobre ingeniería de cloud, plataforma e infraestructura, escritas mientras construyo y opero sistemas reales.

## Propósito {#purpose}

Este manual registra lo que aprendo en la transición de backend engineering a cloud y platform engineering. La mayoría de los capítulos parte de un problema concreto: un error, una decisión de diseño o un concepto que necesité entender para sacar algo adelante. Escribirlo me obliga a que la explicación sea correcta y me deja una referencia a la que puedo volver.

!!! tip "Último capítulo"
    [gcloud ADC: el scope cloud-platform no fue consentido](troubleshooting/gcloud-adc-scope-not-consented.md): por qué `gcloud` funciona pero Terraform no, y cómo arreglar el consent de ADC.

## Secciones {#sections}

<div class="grid cards" markdown>

-   ![](assets/icons/linux.svg){ .hb-logo } **Fundamentos**

    ---

    Linux, redes, DNS y TLS, contenedores y Git: la base sobre la que corre todo lo demás.

    [![](assets/icons/linux.svg){ .hb-chip__logo } Linux](foundations/linux/index.md) · [Redes](foundations/networking/index.md) · [DNS y TLS](foundations/dns-tls/index.md) · [Contenedores](foundations/containers/index.md) · [![](assets/icons/git.svg){ .hb-chip__logo } Git](foundations/git/index.md)

    <span class="hb-badge hb-badge--planned">planeado</span>

-   ![](assets/icons/terraform.svg){ .hb-logo } **IaC**

    ---

    Infraestructura como código con Terraform: state, módulos, plan/apply y drift.

    [![](assets/icons/terraform.svg){ .hb-chip__logo } Terraform](iac/terraform/index.md)

    <span class="hb-badge hb-badge--planned">planeado</span>

-   ![](assets/icons/gcp.svg){ .hb-logo } ![](assets/icons/aws.svg){ .hb-logo } ![](assets/icons/azure.svg){ .hb-logo } **Nube**

    ---

    Servicios principales de cada proveedor, comparados contra GCP.

    [![](assets/icons/gcp.svg){ .hb-chip__logo } GCP](cloud/gcp/index.md) · [![](assets/icons/aws.svg){ .hb-chip__logo } AWS](cloud/aws/index.md) · [![](assets/icons/azure.svg){ .hb-chip__logo } Azure](cloud/azure/index.md)

    <span class="hb-badge hb-badge--planned">planeado</span>

-   ![](assets/icons/kubernetes.svg){ .hb-logo } **Kubernetes**

    ---

    Workloads, services, configuración y cómo depurar pods que no arrancan.

    [![](assets/icons/kubernetes.svg){ .hb-chip__logo } Kubernetes](kubernetes/index.md)

    <span class="hb-badge hb-badge--planned">planeado</span>

-   ![](assets/icons/githubactions.svg){ .hb-logo } **CI/CD**

    ---

    Pipelines con GitHub Actions: artefactos, promoción entre entornos y estrategias de deploy.

    [![](assets/icons/githubactions.svg){ .hb-chip__logo } CI/CD](cicd/index.md)

    <span class="hb-badge hb-badge--planned">planeado</span>

-   ![](assets/icons/prometheus.svg){ .hb-logo } **Observabilidad**

    ---

    Logs, métricas con Prometheus, traces y alertas para encontrar la causa de un incidente.

    [![](assets/icons/prometheus.svg){ .hb-chip__logo } Observabilidad](observability/index.md)

    <span class="hb-badge hb-badge--planned">planeado</span>

-   :material-shield-lock-outline:{ .lg .middle } **Seguridad**

    ---

    Identidad, mínimo privilegio, secrets y auditoría.

    [:octicons-arrow-right-24: Seguridad](security/index.md)

    <span class="hb-badge hb-badge--planned">planeado</span>

-   :material-cash-multiple:{ .lg .middle } **FinOps**

    ---

    Cómo se factura la nube y de dónde sale el gasto inesperado.

    [:octicons-arrow-right-24: FinOps](finops/index.md)

    <span class="hb-badge hb-badge--planned">planeado</span>

-   :material-bug-outline:{ .lg .middle } **Troubleshooting**

    ---

    Errores reales, con causa raíz, diagnóstico y solución.

    [:octicons-arrow-right-24: Troubleshooting](troubleshooting/index.md)

    <span class="hb-badge hb-badge--progress">en progreso</span>

</div>

## Ruta de estudio {#study-path}

El orden sugerido para recorrer el manual. Las etapas marcadas como completadas muestran mi avance actual.

<div class="hb-path" markdown>

<div class="hb-path__steps" markdown>

<div class="hb-step" data-step="foundations" markdown>

![](assets/icons/linux.svg){ .hb-logo } **Fundamentos** <span class="hb-badge hb-badge--planned">planeado</span>
{ .hb-step__title }

La base sobre la que corre todo lo demás: el sistema operativo, la red y el control de versiones.
{ .hb-step__desc }

[![](assets/icons/linux.svg){ .hb-chip__logo } Linux](foundations/linux/index.md){ .hb-chip } [Redes](foundations/networking/index.md){ .hb-chip } [DNS y TLS](foundations/dns-tls/index.md){ .hb-chip } [Contenedores](foundations/containers/index.md){ .hb-chip } [![](assets/icons/git.svg){ .hb-chip__logo } Git](foundations/git/index.md){ .hb-chip }
{ .hb-step__topics }

</div>

<div class="hb-step" data-step="iac" markdown>

![](assets/icons/terraform.svg){ .hb-logo } **IaC** <span class="hb-badge hb-badge--planned">planeado</span>
{ .hb-step__title }

Infraestructura como código con Terraform: state, módulos, plan/apply y drift.
{ .hb-step__desc }

[![](assets/icons/terraform.svg){ .hb-chip__logo } Terraform](iac/terraform/index.md){ .hb-chip }
{ .hb-step__topics }

</div>

<div class="hb-step" data-step="gcp" markdown>

![](assets/icons/gcp.svg){ .hb-logo } **GCP** <span class="hb-badge hb-badge--planned">planeado</span>
{ .hb-step__title }

Servicios principales de Google Cloud, la nube donde corre puente.
{ .hb-step__desc }

[![](assets/icons/gcp.svg){ .hb-chip__logo } GCP](cloud/gcp/index.md){ .hb-chip }
{ .hb-step__topics }

</div>

<div class="hb-step" data-step="kubernetes" markdown>

![](assets/icons/kubernetes.svg){ .hb-logo } **Kubernetes** <span class="hb-badge hb-badge--planned">planeado</span>
{ .hb-step__title }

Workloads, services, configuración y cómo depurar pods que no arrancan.
{ .hb-step__desc }

[![](assets/icons/kubernetes.svg){ .hb-chip__logo } Kubernetes](kubernetes/index.md){ .hb-chip }
{ .hb-step__topics }

</div>

<div class="hb-step" data-step="cicd" markdown>

![](assets/icons/githubactions.svg){ .hb-logo } **CI/CD** <span class="hb-badge hb-badge--planned">planeado</span>
{ .hb-step__title }

Pipelines con GitHub Actions: artefactos, promoción entre entornos y estrategias de deploy.
{ .hb-step__desc }

[![](assets/icons/githubactions.svg){ .hb-chip__logo } CI/CD](cicd/index.md){ .hb-chip }
{ .hb-step__topics }

</div>

<div class="hb-step" data-step="observability" markdown>

![](assets/icons/prometheus.svg){ .hb-logo } **Observabilidad** <span class="hb-badge hb-badge--planned">planeado</span>
{ .hb-step__title }

Logs, métricas con Prometheus, traces y alertas para encontrar la causa de un incidente.
{ .hb-step__desc }

[![](assets/icons/prometheus.svg){ .hb-chip__logo } Observabilidad](observability/index.md){ .hb-chip }
{ .hb-step__topics }

</div>

<div class="hb-step" data-step="security" markdown>

:material-shield-lock-outline:{ .hb-step__icon } **Seguridad** <span class="hb-badge hb-badge--planned">planeado</span>
{ .hb-step__title }

Identidad, mínimo privilegio, secrets y auditoría.
{ .hb-step__desc }

[Seguridad](security/index.md){ .hb-chip }
{ .hb-step__topics }

</div>

<div class="hb-step" data-step="finops" markdown>

:material-cash-multiple:{ .hb-step__icon } **FinOps** <span class="hb-badge hb-badge--planned">planeado</span>
{ .hb-step__title }

Cómo se factura la nube y de dónde sale el gasto inesperado.
{ .hb-step__desc }

[FinOps](finops/index.md){ .hb-chip }
{ .hb-step__topics }

</div>

<div class="hb-step" data-step="multicloud" markdown>

![](assets/icons/aws.svg){ .hb-logo } ![](assets/icons/azure.svg){ .hb-logo } **Multicloud** <span class="hb-badge hb-badge--planned">planeado</span>
{ .hb-step__title }

Los mismos servicios en AWS y Azure, comparados contra GCP.
{ .hb-step__desc }

[![](assets/icons/aws.svg){ .hb-chip__logo } AWS](cloud/aws/index.md){ .hb-chip } [![](assets/icons/azure.svg){ .hb-chip__logo } Azure](cloud/azure/index.md){ .hb-chip }
{ .hb-step__topics }

</div>

</div>

<div class="hb-path__aside" markdown>

:material-bug-outline:{ .hb-step__icon } **Troubleshooting** <span class="hb-badge hb-badge--progress">en progreso</span>
{ .hb-step__title }

Acompaña toda la ruta: cada error real se documenta en el momento en que aparece, con causa raíz, diagnóstico y solución.
{ .hb-step__desc }

[Ver todos](troubleshooting/index.md){ .hb-chip } [Último: gcloud ADC](troubleshooting/gcloud-adc-scope-not-consented.md){ .hb-chip }
{ .hb-step__topics }

</div>

</div>

## Cómo están estructurados los capítulos {#how-chapters-are-structured}

Cada capítulo sigue la misma [plantilla de capítulo](templates/chapter-template.md), en este orden:

1. **Ficha del capítulo**: tiempo de lectura, nivel, nubes relacionadas y estado.
2. **En 30 segundos**: el TL;DR en tres viñetas.
3. **Vista de alto y bajo nivel**: una pestaña con analogía y diagrama de arquitectura, otra con el mecanismo real (archivos, tokens, flags, diagrama de secuencia).
4. **GCP vs AWS vs Azure**: una pestaña por nube y una tabla resumen.
5. **Cómo se rompe**: un bloque por cada modo de falla real.
6. **Cómo diagnosticar**: checklist numerado con comandos anotados.
7. **Aplicado en puente**: un enlace al código o commit real.
8. **Preguntas de entrevista**: 3–5 preguntas con respuestas colapsables.
9. **Repaso rápido**: checklist de autoevaluación.
10. **Referencias**: solo documentación oficial.

## Cómo estudiar con este manual {#how-to-study}

- Pasa el cursor sobre términos como ADC, IAM o OAuth para ver su significado.
- Abre la búsqueda con ++s++ o ++slash++; ve a la página anterior o siguiente con ++p++ y ++n++.
- Usa el **Repaso rápido** al final de cada capítulo: si no puedes marcar un punto sin volver a leer, vuelve a esa sección.

## El proyecto puente {#the-puente-project}

Muchos ejemplos vienen de [puente](https://github.com/JCardzZ/puente), una plataforma de remesas transfronterizas API-first en Google Cloud. La sección "Aplicado en puente" de cada capítulo enlaza al código donde aparece el tema.
