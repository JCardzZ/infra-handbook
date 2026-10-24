# Plantilla de capítulo

<div class="hb-meta" markdown="span">
<span class="hb-meta__item">:material-clock-outline: **Lectura:** X min</span>
<span class="hb-meta__item">:material-signal-cellular-2: **Nivel:** básico | intermedio | avanzado</span>
<span class="hb-meta__item">**Nubes:** :simple-googlecloud: GCP · :material-aws: AWS · :material-microsoft-azure: Azure</span>
<span class="hb-meta__item">**Estado:** <span class="hb-badge hb-badge--planned">planeado</span></span>
</div>

???+ info "Cómo usar esta plantilla"
    - Copia este archivo en la carpeta de la sección correspondiente, reemplaza el texto guía y agrega la página a `nav` en `mkdocs.yml`.
    - Mantén todas las secciones en este orden y conserva los anchors (`{#tldr}`, `{#concept}`, etc.) para que los enlaces sigan funcionando.
    - **Ficha:** estado con `hb-badge--planned` (planeado), `hb-badge--progress` (en progreso) o `hb-badge--done` (completado).
    - **Diagramas:** sigue la [guía de diagramas](../diagrams-guide.md) para elegir el tipo (arquitectura, topología de red, tri-cloud, secuencia, estados, decisión, antes/después). Los de Python van en `diagrams/` y se renderizan con `make diagrams`.
    - **Admonitions disponibles:** `concepto`, `tip`, `cuidado`, `rompe-y-arregla`, además de `danger` para modos de falla y `question` para preguntas de entrevista.
    - Los términos del glosario (`docs/includes/glossary.md`) muestran su significado al pasar el cursor en cualquier página.

## En 30 segundos {#tldr}

!!! tldr "TL;DR"
    - Una oración: qué es.
    - Una oración: por qué importa o qué sale mal.
    - Una oración: la solución o la ==idea clave==.

## Vista de alto y bajo nivel {#concept}

=== "Alto nivel"

    !!! concepto "Analogía"
        Explica la idea con una analogía cotidiana, como se la explicarías a un backend engineer que nunca la ha usado.

    Uno o dos párrafos cortos con la idea general. Define cada término la primera vez que aparece.

    Inserta aquí el diagrama de arquitectura generado con `diagrams`, envuelto en `<figure class="hb-diagram" markdown="span">` con un `<figcaption>`.

=== "Bajo nivel"

    El mecanismo real: archivos, tokens, flags, variables de entorno.

    `ruta/o/flag`
    :   Qué es y para qué sirve.

    `OTRA_VARIABLE`
    :   Qué es y para qué sirve.

    ```mermaid
    sequenceDiagram
        participant A as Cliente
        participant B as Servicio
        A->>B: Solicitud
        B-->>A: Respuesta
    ```

## GCP vs AWS vs Azure {#gcp-vs-aws-vs-azure}

=== ":simple-googlecloud: GCP"

    Cómo funciona en Google Cloud, con los comandos principales.

=== ":material-aws: AWS"

    Cómo funciona en AWS, con los comandos principales.

=== ":material-microsoft-azure: Azure"

    Cómo funciona en Azure, con los comandos principales.

### Resumen {#comparison-summary}

| Aspecto | GCP | AWS | Azure |
|---|---|---|---|
| Servicio o mecanismo | | | |
| Cómo se configura | | | |
| Diferencia notable | | | |

## Cómo se rompe {#how-it-breaks}

Un bloque por modo de falla real, con el síntoma (texto exacto del error cuando exista), la causa y el arreglo.

!!! danger "Nombre corto del modo de falla"
    **Síntoma:** `texto exacto del error`

    **Causa:** ...

    **Arreglo:** ...

## Cómo diagnosticar {#how-to-diagnose}

Checklist numerado. Cada flag se explica con una anotación de código (`# (1)!`).

1. **Qué verificar primero.**

    ```bash
    comando --flag valor # (1)!
    ```

    1.  Qué hace `--flag` y por qué se usa aquí.

    - Saludable: cómo se ve la salida cuando todo está bien.
    - Roto: cómo se ve cuando no.

2. **Qué verificar después.**

### Soluciones {#fixes}

!!! rompe-y-arregla "Solución 1: nombre corto"
    Pasos concretos para arreglarlo.

!!! cuidado "Advertencia"
    Riesgos al aplicar la solución (credenciales, datos, costos).

## Aplicado en puente {#applied-in-puente}

!!! todo "TODO"
    Enlaza al archivo, pull request o commit de [puente](https://github.com/JCardzZ/puente) donde aparece este tema.

## Preguntas de entrevista {#interview-questions}

??? question "Pregunta 1"
    Respuesta.

??? question "Pregunta 2"
    Respuesta.

??? question "Pregunta 3"
    Respuesta.

## Repaso rápido {#quick-review}

Marca cada punto solo si puedes explicarlo sin volver a leer.

- [ ] Puedo explicar ...
- [ ] Puedo explicar ...
- [ ] Puedo diagnosticar ...

## Referencias {#references}

Solo documentación oficial (docs de proveedores cloud, docs del proyecto, RFCs).

<!-- Add official documentation links -->
