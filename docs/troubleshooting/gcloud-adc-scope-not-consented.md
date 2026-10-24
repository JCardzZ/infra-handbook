# gcloud ADC: el scope cloud-platform no fue consentido

<div class="hb-meta" markdown="span">
<span class="hb-meta__item">:material-clock-outline: **Lectura:** 15 min</span>
<span class="hb-meta__item">:material-signal-cellular-2: **Nivel:** intermedio</span>
<span class="hb-meta__item">**Nubes:** :simple-googlecloud: GCP · :material-aws: AWS · :material-microsoft-azure: Azure</span>
<span class="hb-meta__item">**Estado:** <span class="hb-badge hb-badge--progress">en progreso</span></span>
</div>

```text
ERROR: (gcloud.auth.application-default.login) https://www.googleapis.com/auth/cloud-platform scope is required but not consented.
```

A menudo seguido, al reintentar, por:

```text
ERROR: gcloud crashed (Warning): Scope has changed from "openid https://www.googleapis.com/auth/sqlservice.login https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/cloud-platform" to "openid https://www.googleapis.com/auth/userinfo.email".
```

## En 30 segundos {#tldr}

!!! tldr "TL;DR"
    - `gcloud auth login` autoriza el **CLI de gcloud**; `gcloud auth application-default login` crea **Application Default Credentials (ADC)**, que usan Terraform y las client libraries de Google Cloud. ==Son credenciales distintas, con consent distinto.==
    - El error significa que ==no se marcó la casilla de `cloud-platform`== en el consent screen granular de Google, así que Google devolvió un token solo con `openid` y `userinfo.email`. Un perfil de navegador con sesión iniciada en otra cuenta (por ejemplo, la del trabajo) hace que sea fácil equivocarse.
    - Solución: ejecuta el login con `--no-launch-browser`, abre la URL en una ventana de incógnito, inicia sesión con la cuenta correcta y ==marca todas las casillas==. Si sigue fallando, revoca "Google Auth Library" en tu cuenta de Google y vuelve a intentar.

## Vista de alto y bajo nivel {#concept}

=== "Alto nivel"

    !!! concepto "Analogía: dos llaves distintas"
        Piensa en un edificio de oficinas. `gcloud auth login` te da **tu credencial personal** para entrar y moverte por el edificio con la terminal. `gcloud auth application-default login` crea **una llave que les prestas a tus herramientas** (Terraform, client libraries) para que entren en tu nombre. El consent screen es el formulario donde decides a qué puertas abre esa llave. Si no marcas la puerta `cloud-platform`, la llave existe pero no abre nada útil, y gcloud se niega a guardarla.

    En una máquina de desarrollo hay dos credenciales distintas, y es fácil confundirlas. La del CLI solo la usan `gcloud`, `gsutil` y `bq`. La de ADC la busca automáticamente todo lo que usa las librerías de autenticación de Google: el provider `google` de Terraform, las client libraries de Java/Python/Go/Node.js, Spring Cloud GCP, etc.

    Tener sesión con el primero no te da el segundo: ==Terraform va a fallar aunque todos los comandos `gcloud` funcionen.==

    <figure class="hb-diagram" markdown="span">
      ![Diagrama de arquitectura. A la izquierda, el developer ejecuta gcloud auth login sobre gcloud CLI, que guarda credenciales de usuario en credentials.db, y ejecuta terraform plan sobre Terraform. Terraform y las client libraries leen application_default_credentials.json. credentials.db se autentica ante Google OAuth 2.0 como la app Google Cloud SDK; el archivo ADC se autentica como la app Google Auth Library y requiere el scope cloud-platform. Google OAuth entrega access tokens para llamar a APIs de Google Cloud como Cloud Run, Cloud SQL y Cloud Storage.](../assets/diagrams/adc-credentials.svg)
      <figcaption>Credenciales del CLI vs ADC en una laptop de desarrollo. Toca o haz clic para abrir el visor con zoom.</figcaption>
    </figure>

=== "Bajo nivel"

    **Archivos y variables**

    `~/.config/gcloud/credentials.db`
    :   Donde `gcloud auth login` guarda las credenciales de usuario del CLI. El consent screen muestra la app "Google Cloud SDK".

    `~/.config/gcloud/application_default_credentials.json`
    :   El archivo ADC en Linux y macOS, escrito por `gcloud auth application-default login`. Contiene un refresh token de tu usuario. El consent screen muestra la app "Google Auth Library".

    `GOOGLE_APPLICATION_CREDENTIALS`
    :   Si está definida, las client libraries usan el archivo al que apunta en lugar del archivo ADC de gcloud.

    `GOOGLE_OAUTH_ACCESS_TOKEN`
    :   Leída por el provider `google` de Terraform: un access token ya emitido, que se usa tal cual y no se refresca.

    `--no-launch-browser`
    :   Hace que gcloud imprima la URL de consent en lugar de abrir el navegador por defecto; luego pegas el authorization code en la terminal.

    **Scopes y consent granular**

    Un scope de OAuth es un string de permiso que la app solicita. En el error de arriba, ADC solicitó `openid`, `https://www.googleapis.com/auth/sqlservice.login`, `https://www.googleapis.com/auth/userinfo.email` y `https://www.googleapis.com/auth/cloud-platform`. El consent screen de Google puede mostrar cada permiso solicitado como una casilla separada, y el usuario puede otorgar algunos y dejar otros sin marcar.

    Si `cloud-platform` no se marca, Google igual completa el flujo, pero el token que devuelve solo trae los scopes otorgados. gcloud revisa los scopes devueltos, ve que falta `cloud-platform` y se detiene. El mensaje "Scope has changed" es la librería de OAuth reportando lo mismo: los scopes de la respuesta difieren de los solicitados.

    **Por qué el perfil de navegador equivocado lo empeora.** gcloud abre el navegador por defecto. Si ese perfil tiene sesión iniciada en una cuenta del trabajo, una cuenta administrada por una organización o varias cuentas a la vez, puedes terminar en el consent screen de la cuenta equivocada, o de una cuenta cuyo administrador restringe qué scopes pueden recibir las apps de terceros. El resultado se ve igual: `cloud-platform` no queda otorgado.

    ```mermaid
    sequenceDiagram
        participant Dev as Developer
        participant G as gcloud
        participant B as Navegador
        participant Acc as Google OAuth
        participant TF as Terraform / client library

        Dev->>G: gcloud auth application-default login
        G->>B: Abre la URL de consent (openid, userinfo.email, cloud-platform, ...)
        B->>Acc: Inicio de sesión, consent screen
        Note over B,Acc: El usuario debe marcar la casilla de cloud-platform
        alt cloud-platform otorgado
            Acc-->>G: El código se canjea por un refresh token con todos los scopes
            G->>G: Escribe application_default_credentials.json
            TF->>G: Lee el archivo ADC, solicita un access token
            TF-->>Dev: Las llamadas a la API funcionan
        else cloud-platform no otorgado
            Acc-->>G: Token solo con openid + userinfo.email
            G-->>Dev: ERROR: cloud-platform scope is required but not consented
        end
    ```

## GCP vs AWS vs Azure {#gcp-vs-aws-vs-azure}

Cada nube tiene un login del CLI y una "credential chain" que los SDKs y Terraform recorren para encontrar credenciales en una máquina de desarrollo.

=== ":simple-googlecloud: GCP"

    Dos logins separados: uno para el CLI y otro para ADC.

    ```bash
    gcloud auth login                       # credenciales del CLI
    gcloud auth application-default login   # ADC para Terraform y client libraries
    ```

    - **Búsqueda de ADC:** `GOOGLE_APPLICATION_CREDENTIALS`, luego el archivo ADC de gcloud, luego el metadata server.
    - **Dónde vive:** `~/.config/gcloud/application_default_credentials.json`.
    - **Falla típica:** scope no consentido; falta ADC aunque `gcloud` funcione.

=== ":material-aws: AWS"

    Un solo login SSO que sirve tanto al CLI como a los SDKs, a través de un profile.

    ```bash
    aws configure sso                 # crea el profile SSO en ~/.aws/config
    aws sso login --profile dev       # abre el navegador y guarda el token SSO
    aws sts get-caller-identity --profile dev
    ```

    - **Búsqueda:** default credential provider chain: variables de entorno, archivos compartidos `config`/`credentials` (incluidos profiles SSO), metadata de contenedor e instancia.
    - **Dónde vive:** `~/.aws/config`, `~/.aws/credentials`, `~/.aws/sso/cache/`.
    - **Falla típica:** token SSO expirado; se toma el profile equivocado del entorno (`AWS_PROFILE`).

=== ":material-microsoft-azure: Azure"

    `az login` inicia sesión en el CLI, y los SDKs reutilizan esa sesión a través de `DefaultAzureCredential`.

    ```bash
    az login
    az account set --subscription "<subscription>"
    az account show
    ```

    - **Búsqueda:** `DefaultAzureCredential`: variables de entorno, workload identity, managed identity y luego herramientas de desarrollo como Azure CLI.
    - **Dónde vive:** `~/.azure/`.
    - **Falla típica:** CLI con sesión en el tenant o subscription equivocado.

### Resumen {#comparison-summary}

| Aspecto | :simple-googlecloud: GCP | :material-aws: AWS | :material-microsoft-azure: Azure |
|---|---|---|---|
| Login del CLI | `gcloud auth login` | `aws sso login` | `az login` |
| Credenciales para SDKs y Terraform | `gcloud auth application-default login` (ADC) | La misma sesión SSO, vía profile | La misma sesión de `az login`, vía Azure CLI credential |
| Mecanismo de búsqueda | ADC | Default credential provider chain | `DefaultAzureCredential` |
| Cómo se elige la identidad | Cuenta elegida en el navegador | `AWS_PROFILE` o `--profile` | `az account set`, `AZURE_TENANT_ID` |
| Verificar quién eres | `gcloud auth list`, tokeninfo | `aws sts get-caller-identity` | `az account show` |

!!! tip "La diferencia clave"
    En AWS y Azure, el login del CLI y las credenciales del SDK normalmente salen de la misma sesión. En GCP son dos logins separados, así que un CLI que funciona no te dice nada sobre ADC.

## Cómo se rompe {#how-it-breaks}

!!! danger "Scope no consentido"
    **Síntoma:** `cloud-platform scope is required but not consented`

    **Causa:** la casilla de `cloud-platform` quedó sin marcar en el consent screen, o la organización de la cuenta no permite ese scope.

    **Arreglo:** [Solución 1](#fixes): login en incógnito marcando todas las casillas.

!!! danger "El scope cambió en la respuesta"
    **Síntoma:** `ERROR: gcloud crashed (Warning): Scope has changed from "..." to "openid https://www.googleapis.com/auth/userinfo.email".`

    **Causa:** la misma de arriba, reportada por la librería de OAuth. La respuesta del token trajo menos scopes de los solicitados.

    **Arreglo:** [Solución 1](#fixes); si se repite, Solución 2.

!!! danger "El error se repite y la casilla ya no aparece"
    **Síntoma:** el mismo error en cada intento; el consent screen ya no muestra la casilla de `cloud-platform`.

    **Causa:** Google recuerda el grant parcial de la app "Google Auth Library".

    **Arreglo:** Solución 2: revocar el acceso de la app y volver a intentar.

!!! danger "Identidad inesperada"
    **Síntoma:** el login "funciona", pero Terraform recibe `403` o actúa como una identidad inesperada.

    **Causa:** el navegador completó el consent con una cuenta distinta a la deseada (por ejemplo, una cuenta del trabajo en el perfil por defecto del navegador).

    **Arreglo:** verificar el `email` con tokeninfo (paso 3 del diagnóstico) y repetir la Solución 1 en incógnito.

!!! danger "ADC nunca se creó"
    **Síntoma:** los comandos `gcloud` funcionan, pero Terraform reporta que no pudo encontrar default credentials.

    **Causa:** solo se ejecutó `gcloud auth login`; nunca se creó ADC.

    **Arreglo:** ejecutar `gcloud auth application-default login` (Solución 1).

!!! danger "El token temporal expiró"
    **Síntoma:** Terraform funciona un rato y luego falla con `401` después de usar el workaround.

    **Causa:** el access token en `GOOGLE_OAUTH_ACCESS_TOKEN` expiró (aproximadamente una hora) y no se refresca.

    **Arreglo:** volver a exportar el token, o arreglar ADC y hacer `unset GOOGLE_OAUTH_ACCESS_TOKEN`.

## Cómo diagnosticar {#how-to-diagnose}

Sigue los pasos en orden. Haz clic en los marcadores :material-plus-circle: de cada bloque de código para ver qué hace cada parte del comando.

1. **¿Qué cuentas conoce gcloud?**

    ```bash
    gcloud auth list # (1)!
    gcloud config list account # (2)!
    ```

    1.  Lista las cuentas con las que hiciste `gcloud auth login` y marca la activa con `*`.
    2.  Muestra la cuenta activa de la configuración actual de gcloud.

    Esto muestra solo la cuenta del CLI. No dice nada sobre ADC.

2. **¿Existe un archivo ADC, y hay algo que lo esté sobrescribiendo?**

    ```bash
    echo "${GOOGLE_APPLICATION_CREDENTIALS:-not set}" # (1)!
    ls -l ~/.config/gcloud/application_default_credentials.json # (2)!
    ```

    1.  `${VAR:-not set}` imprime el valor de la variable, o `not set` si no está definida. Si tiene valor, las client libraries usan ese archivo en lugar del archivo ADC de gcloud.
    2.  `-l` muestra tamaño y fecha de modificación: confirma que el archivo existe y cuándo se escribió por última vez.

    No hagas `cat` del archivo ADC en una terminal que estés compartiendo: contiene un refresh token.

3. **¿ADC puede generar un token, y qué scopes y cuenta trae?**

    ```bash
    curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$(gcloud auth application-default print-access-token)" # (1)!
    ```

    1.  `-s` oculta la barra de progreso de curl. `$(...)` ejecuta `print-access-token`, que genera un access token a partir de ADC, y lo pasa al endpoint `tokeninfo` de Google, que responde con los scopes y el email asociados a ese token.

    Revisa los campos `scope` y `email` de la respuesta.

    - **Saludable:** `scope` contiene `https://www.googleapis.com/auth/cloud-platform` y `email` es la cuenta que esperas.
    - **Roto:** `scope` solo tiene `openid` y `userinfo.email`, `email` es la cuenta equivocada, o `print-access-token` falla porque no hay archivo ADC.

4. **Revisa el lado del navegador.** Fíjate qué perfil de navegador se abrió durante el login y con qué cuenta tenía sesión. Si era un perfil del trabajo o tenía varias cuentas con sesión, usa la Solución 1.

### Soluciones {#fixes}

!!! rompe-y-arregla "Solución 1: login en incógnito con `--no-launch-browser`"
    ```bash
    gcloud auth application-default login --no-launch-browser # (1)!
    ```

    1.  gcloud no abre el navegador por defecto: imprime la URL de consent y espera que pegues el authorization code.

    Pasos:

    1. gcloud imprime una URL. Cópiala y ábrela en una ventana privada/de incógnito, para que no haya otra cuenta con sesión iniciada.
    2. Inicia sesión con la cuenta que quieres que use ADC.
    3. En el consent screen, marca **todas** las casillas, incluida la de ver y administrar tus datos de Google Cloud (`cloud-platform`). Usa "Seleccionar todo" si aparece.
    4. Copia el authorization code que muestra Google y pégalo en la terminal con ++cmd+v++ (macOS) o ++ctrl+shift+v++ (Linux).

    Después vuelve a ejecutar la verificación con tokeninfo del paso 3.

!!! rompe-y-arregla "Solución 2: revocar el grant anterior y volver a intentar"
    1. Entra a [myaccount.google.com/connections](https://myaccount.google.com/connections) con la misma cuenta.
    2. Busca **Google Auth Library** y quítale el acceso.
    3. Opcionalmente, elimina el archivo local: `gcloud auth application-default revoke`.
    4. Ejecuta de nuevo la Solución 1. El consent screen ahora debería mostrar todas las casillas.

!!! tip "Workaround temporal: pasarle a Terraform un token desde el login del CLI"
    Si `gcloud auth login` funciona y necesitas ejecutar Terraform ya, el provider `google` acepta un access token desde una variable de entorno:

    ```bash
    export GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token) # (1)!
    terraform plan
    ```

    1.  `print-access-token` (sin `application-default`) usa las credenciales del CLI, que ya tienen `cloud-platform`. `export` deja la variable disponible para los procesos que lances desde este shell.

    Limitaciones:

    - El token expira después de aproximadamente una hora y no se refresca. Vuelve a ejecutar el `export` cuando pase.
    - Solo aplica a la sesión de shell actual.
    - Lo lee el provider `google` de Terraform; otras client libraries lo ignoran.
    - Ejecuta `unset GOOGLE_OAUTH_ACCESS_TOKEN` cuando ADC esté arreglado, para no quedarte con un token vencido.

!!! cuidado "Nunca compartas authorization codes ni tokens"
    El authorization code que pegas en la terminal, la salida de `print-access-token` y el contenido de `application_default_credentials.json` dan acceso a tus recursos de Google Cloud. No los pegues en chats, issues, capturas de pantalla ni herramientas de IA. Si alguno se filtra, revoca el acceso en myaccount.google.com/connections y ejecuta `gcloud auth application-default revoke`.

## Aplicado en puente {#applied-in-puente}

!!! todo "TODO"
    Enlazar al commit o al setup de Terraform en [puente](https://github.com/JCardzZ/puente) donde se necesita ADC para ejecutar `terraform plan`/`apply` localmente.

## Preguntas de entrevista {#interview-questions}

??? question "¿Cuál es la diferencia entre `gcloud auth login` y `gcloud auth application-default login`?"
    `gcloud auth login` guarda credenciales de usuario que solo usan el CLI de gcloud y sus herramientas complementarias. `gcloud auth application-default login` escribe Application Default Credentials en un archivo conocido que las client libraries de Google y el provider `google` de Terraform buscan automáticamente. Son logins separados con consent separado, así que uno puede funcionar mientras el otro falta.

??? question "¿Cómo encuentra credenciales una client library de Google cuando no configuras ninguna?"
    Sigue el orden de búsqueda de ADC: primero el archivo al que apunta `GOOGLE_APPLICATION_CREDENTIALS`, luego el archivo ADC creado por `gcloud auth application-default login`, y luego el metadata server del entorno donde corre (Compute Engine, Cloud Run, GKE, etc.), que entrega las credenciales de la service account asociada.

??? question "Un login termina sin errores, pero el token no puede llamar a las APIs de Google Cloud. ¿Cómo averiguas por qué?"
    Inspecciona el token en lugar de adivinar. Envíalo al endpoint de tokeninfo y lee los campos `scope` y `email`. Si falta el scope `cloud-platform`, apunta a un consent parcial; si el `email` es inesperado, apunta a que se usó la cuenta equivocada en el navegador. Se arregla volviendo a dar consent en una sesión de navegador limpia, revocando antes el grant anterior si hace falta.

??? question "¿Cuáles son los equivalentes de ADC en AWS y Azure para desarrollo local?"
    En AWS, `aws sso login` crea una sesión SSO y la default credential provider chain del SDK la toma a través del profile configurado (seleccionado con `AWS_PROFILE`). En Azure, `az login` inicia sesión en el CLI y `DefaultAzureCredential` usa esa sesión a través de su credencial de Azure CLI, después de revisar variables de entorno, workload identity y managed identity.

??? question "¿Por qué los workloads de producción no deberían usar ADC creado con `gcloud auth application-default login`?"
    Esas credenciales pertenecen a una persona, tienen los permisos de esa persona y dependen de un refresh token en una sola máquina. Los workloads de producción deberían usar una service account asociada a través del metadata server, o WIF cuando corren fuera de Google Cloud, para que los permisos estén limitados al workload y no haya secrets de usuario de larga duración que se puedan filtrar.

## Repaso rápido {#quick-review}

Marca cada punto solo si puedes explicarlo sin volver a leer.

- [ ] Puedo explicar la diferencia entre `gcloud auth login` y `gcloud auth application-default login`, y qué herramientas usa cada una.
- [ ] Puedo explicar qué es un scope de OAuth y cómo funciona el consent screen granular.
- [ ] Puedo leer el error "Scope has changed" e identificar qué scope faltó.
- [ ] Puedo verificar con tokeninfo qué scopes y qué cuenta tiene un token de ADC.
- [ ] Puedo aplicar las dos soluciones y el workaround, y explicar los límites del workaround.
- [ ] Puedo nombrar el equivalente de ADC en AWS y en Azure.
- [ ] Puedo explicar por qué nunca se comparten authorization codes ni tokens.

## Referencias {#references}

- [How Application Default Credentials works](https://cloud.google.com/docs/authentication/application-default-credentials) (Google Cloud)
- [Set up ADC for a local development environment](https://cloud.google.com/docs/authentication/provide-credentials-adc) (Google Cloud)
- [`gcloud auth application-default login`](https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login) (referencia de Google Cloud SDK)
- [`gcloud auth login`](https://cloud.google.com/sdk/gcloud/reference/auth/login) (referencia de Google Cloud SDK)
- [`gcloud auth print-access-token`](https://cloud.google.com/sdk/gcloud/reference/auth/print-access-token) (referencia de Google Cloud SDK)
- [How to handle granular permissions](https://developers.google.com/identity/protocols/oauth2/resources/granular-permissions) (Google Identity)
- [Google provider configuration reference](https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/provider_reference) (HashiCorp Terraform)
- [Configuring IAM Identity Center authentication with the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) (AWS)
- [Standardized credential providers](https://docs.aws.amazon.com/sdkref/latest/guide/standardized-credentials.html) (AWS SDKs and Tools)
- [Authenticate to Azure using Azure CLI](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli) (Microsoft Learn)
- [Credential chains in the Azure Identity library](https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/credential-chains) (Microsoft Learn)
