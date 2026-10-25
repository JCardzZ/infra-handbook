# Manual de Infra de Manuel

Un manual técnico público sobre ingeniería de cloud, plataforma e infraestructura, escrito por Manuel Cardoza ([@JCardzZ](https://github.com/JCardzZ)).

Cada capítulo cubre un tema o una falla real, lo explica en palabras simples, compara GCP, AWS y Azure, y muestra cómo diagnosticarlo. Cuando es posible, los capítulos enlazan a código real de [puente](https://github.com/JCardzZ/puente), una plataforma de remesas transfronterizas API-first en Google Cloud.

El sitio está construido con [MkDocs](https://www.mkdocs.org/) y [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Ejecutar localmente

Requiere Python 3. Para regenerar diagramas también necesitas [Graphviz](https://graphviz.org/) (`brew install graphviz`).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Abre <http://127.0.0.1:8000>. El sitio se recarga cuando cambian archivos dentro de `docs/`.

Para validar el build de la misma forma en que se validará antes de publicar:

```bash
mkdocs build --strict
```

## Estructura

```text
docs/                    contenido del sitio (Markdown)
docs/templates/          plantilla obligatoria de capítulo
docs/includes/           glosario (se agrega a todas las páginas, no se publica solo)
docs/stylesheets/        paleta, admonitions y componentes propios
docs/assets/diagrams/    SVGs generados (se commitean)
diagrams/                un archivo .py por diagrama; _style.py compartido; mermaid/*.mmd
scripts/                 build-diagrams.sh y utilidades
Makefile                 make serve | diagrams | build
```

## Diagramas

- **Mermaid** solo para flujos y secuencias (`flowchart`, `sequenceDiagram`), escrito directamente en el Markdown.
- **[diagrams](https://diagrams.mingrammer.com/)** para arquitectura cloud con íconos oficiales: un archivo por diagrama en `diagrams/`.

La [guía de diagramas](docs/diagrams-guide.md) explica qué tipo usar en cada caso y las convenciones visuales. Todos los diagramas de Python importan `diagrams/_style.py`.

```bash
make diagrams   # renderiza diagrams/*.py a SVG
make build      # diagramas + mkdocs build --strict
make serve      # sitio local con live reload
```

`make` usa el venv `.venv` sin necesidad de activarlo. El script renderiza cada `diagrams/*.py` como SVG en `docs/assets/diagrams/` e incrusta los íconos en el SVG, para que funcione en cualquier máquina. Commitea los SVG generados junto con el `.py`.

## Progreso de la ruta de estudio

La ruta de estudio de la página de inicio muestra qué etapas completé. El progreso se guarda en Firestore, en el proyecto de Firebase `infra-handbook-progress`, con dos documentos:

- `progress/{uid}`: mi documento, que solo yo leo y escribo.
- `progress/public`: una copia de solo lectura que ve cualquier visitante.

Ambos tienen la forma `{ steps: { <stepId>: { done, updatedAt } } }`.

- **Sin sesión:** la página lee `progress/public` y muestra cada etapa como "Completada" o "Pendiente", sin poder cambiarla.
- **Con sesión del dueño:** con el botón "Iniciar sesión" (Google) y la cuenta `cardozamanuel96@gmail.com`, "Marcar como completada" escribe en los dos documentos a la vez.
- **Sin conexión o con errores:** se muestra el último estado conocido, guardado en el navegador, y un aviso. Los cambios hechos sin conexión se envían al reconectar.

El código está en `docs/javascripts/progress-firebase.js` y la configuración en `docs/javascripts/firebase-config.js`.

### Reglas de seguridad

`firestore.rules` define quién puede leer y escribir:

- `progress/public`: lectura para todos; escritura solo si `request.auth.token.email` es `cardozamanuel96@gmail.com` y `email_verified` es `true`.
- `progress/{uid}`: lectura y escritura solo si `request.auth.uid == uid` y se cumple la misma condición de email.
- Todo lo demás se rechaza.

Para desplegarlas (requiere [Firebase CLI](https://firebase.google.com/docs/cli): `npm install -g firebase-tools`):

```bash
firebase login
firebase use infra-handbook-progress
firebase deploy --only firestore:rules
```

`firebase.json` apunta a `firestore.rules` y `.firebaserc` fija el proyecto por defecto.

### Por qué la `apiKey` no es un secreto

La `apiKey` de una app web de Firebase identifica el proyecto, no da acceso a los datos: cualquier visitante la recibe en el JavaScript del sitio. Lo que protege los datos son las reglas de Firestore y la autenticación. Por eso `firebase-config.js` se commitea. Una medida adicional opcional es restringir la key a los dominios del sitio en Google Cloud Console (APIs y servicios → Credenciales).

## Escribir un capítulo

Copia `docs/templates/chapter-template.md` en la carpeta de la sección correspondiente, mantén todas las secciones en el mismo orden y agrega la página a `nav` en `mkdocs.yml`. Para agregar un término al glosario (tooltip al pasar el cursor), edita `docs/includes/glossary.md`.

## Publicación

Por ahora el sitio solo se ejecuta localmente. La publicación (por ejemplo, en GitHub Pages) está planeada.
