# Proyectos del portafolio — vista general (e2e: frontend + backend + infra)

| | **Puente** (GCP) | **Vitrina** (AWS) | **Ruta** (Azure) | **Faro** (Multicloud) |
|---|---|---|---|---|
| **Qué es** | Plataforma API-first de remesas y pagos transfronterizos (USA → SV/GT/HN) | SaaS multi-tenant de comercio para pymes: tienda, checkout, inventario y ventas flash | Plataforma B2B de logística de última milla para distribuidoras | Plataforma de FinOps y confiabilidad que unifica costos y SLOs de las 3 nubes |
| **Quién paga** | Fintechs y casas de remesas | Pymes que venden en línea | Distribuidoras, farmacéuticas, retail con flota | Equipos de plataforma / CTOs |
| **Modelo de negocio** | Fee por transacción + spread cambiario | Suscripción mensual + % por venta | Licencia por vehículo/mes + SLA premium | Suscripción según gasto cloud gestionado |
| **Por qué es vendible** | Las remesas sostienen la economía de la región; el partner integra por API en días en lugar de meses | Las ventas flash tumban las tiendas pequeñas; Vitrina aguanta el pico y nunca sobrevende | Las empresas pierden dinero por entregas fallidas y sin prueba; Ruta da tracking, prueba de entrega y métricas de SLA | Las empresas desperdician gasto cloud sin verlo; Faro lo muestra por equipo y servicio y alerta anomalías |
| **Frontend** | Next.js + TS: portal de partners (API keys, transferencias, webhooks) + backoffice de compliance | Next.js + TS: storefront SSR/ISR en CDN + panel del comerciante | Angular: portal empresarial + PWA offline para repartidores (foto/firma) | Next.js + TS: dashboards de costo, SLOs y anomalías |
| **Backend (Spring Boot)** | quote, transfer (saga), compliance, ledger, payout, webhook | catalog, cart, checkout/order (saga), inventory, payment, notification, tenant | orders, dispatch/routing, tracking, proof-of-delivery, sla, integration (ERP) | ingest (por nube), normalizer, cost-api, slo-api, anomaly-detector |
| **Datos y eventos** | Postgres (ledger doble partida), Firestore, Pub/Sub, BigQuery | DynamoDB (inventario, escrituras condicionales), Aurora/Postgres, SQS/SNS/EventBridge, Step Functions | Azure SQL / PostgreSQL Flexible, Service Bus (sesiones FIFO), Event Grid, Blob Storage | BigQuery (warehouse central), exports de Cloud Billing, AWS CUR + Athena, Azure Cost exports |
| **Servicios clave** | Apigee, Cloud Run → GKE, Cloud Armor, Identity Platform, Secret Manager, Cloud KMS | CloudFront + S3, Cognito, ECS Fargate → EKS, WAF, API Gateway, multi-región | Container Apps → AKS, API Management, Entra ID / External ID, Front Door, Key Vault, hub-and-spoke | WIF entre nubes, Terraform multi-provider, OpenTelemetry, Argo CD central |
| **Lo difícil (lo que impresiona)** | Cero dinero duplicado con reintentos, ledger con RPO 0, screening de sanciones, webhooks firmados con DLQ | Cero sobreventa con 10k requests/s en una venta flash, aislamiento entre tenants, checkout como saga | Ubicación en tiempo real, mensajes en orden por envío, identidad federada con el Entra ID del cliente | Normalizar 3 modelos de costo distintos, identidad sin llaves entre nubes, análisis honesto de cuándo NO usar multicloud |
| **Auth** | OAuth2 client-credentials (partners) vía Apigee + OIDC (portal) | Cognito (compradores y comerciantes) | Entra ID B2B (empresas) + External ID (repartidores) | SSO OIDC + WIF entre nubes |
| **Cómo queda en $0** | Créditos para los labs de red de la Fase 0 → luego free tier: Cloud Run, Firestore, Pub/Sub, VM e2-micro gratis con Postgres propio, trial de Spanner, Apigee Emulator | Créditos del Free Plan ($100–200, 6 meses) para Fargate/Aurora/EKS en sesiones cortas; el resto en free tier (Lambda, DynamoDB, CloudFront, Cognito, SQS) | $200 en 30 días para AKS/Front Door en un sprint; 12 meses de servicios gratis (PostgreSQL Flexible B1ms, Container Apps, APIM Consumption, Static Web Apps) | Free tiers de BigQuery, Cloud Run, Lambda y Azure Functions + datos de costo sintéticos |
| **Certificación** | ACE → PCA | SAA → DevOps Pro | AZ-104 → AZ-305 | PCDE / SAP (opcional) |
| **Cuándo (aprox.)** | Oct-2026 → Mar-2028 (incluye Fase 0 y K8s) | 2028 | 2029 | 2029–2030 |

## Límites honestos del "$0"
- **GKE y multi-región de Puente (v3–v4)** caen después de que vencen los créditos. Los nodos de GKE no son gratis: el free tier de $74.40/mes solo cubre la tarifa del cluster. Plan: Kubernetes y GitOps 100 % local (kind/k3d), más 2–3 sesiones cortas en GKE con nodos Spot. Costo real estimado: menos de $5 en total.
- **AWS Free Plan:** la cuenta se cierra a los 6 meses o al agotar los créditos. Todo va como código para poder recrearlo.
- **Azure:** los $200 duran 30 días. Lo caro (AKS, Front Door) se concentra en ese mes.
- **Apigee:** Emulator local siempre; org de evaluación solo en un sprint corto.
- Los **exámenes** no son costo de nube: ACE $125, el resto entre $150 y $300 aprox.
- **No abras cuentas nuevas para repetir créditos:** viola los términos y te pueden cerrar todo.
