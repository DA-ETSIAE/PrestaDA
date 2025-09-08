# PrestaDA
Aplicación web para la gestión de préstamos de material en un entorno universitario.

## Setup
El proyecto ha sido diseñado para usarse _exclusivamente_ con Docker. Aunque es posible ejecutarlo localmente (`python manage.py runserver`), esto no está soportado y seguramente lleve a errores. 

En cualquier caso, se ha de configurar una base de datos (Postgres) y un broker de mensajes (RabbitMQ). 
Se puede sustituir Postgres por otras bases de datos SQL (e.j. MariaDB) así como RabbitMQ por Redis ([pero no Valkey](https://github.com/celery/celery/issues/9092)), 
pero puede que no funcione.

En dockerhub: [`ticdaetsiae/prestamos`](https://hub.docker.com/r/ticdaetsiae/prestamos/).

Ver compose.yml y env.example para ejemplo de uso.

### Configuración OIDC (SIU-UPM)
La aplicación **no** soporta la creación de cuentas, descarga la autentificación a un provedor OpenID (como SIU-UPM). Se han de configurar las siguientes variables de entorno
- `OIDC_CLIENT_ID=` 
- `OIDC_CLIENT_SECRET=`
- `OIDC_AUTH_ENDPOINT=`
- `OIDC_CLIENT_ID=`
- `OIDC_CLIENT_SECRET=`
- `OIDC_AUTH_ENDPOINT=`
- `OIDC_TOKEN_ENDPOINT=`
- `OIDC_USERINFO_ENDPOINT=`
- `OIDC_LOGIN_REDIRECT_URL=`
- `OIDC_LOGOUT_REDIRECT_URL=`
- `OIDC_RP_SIGN_ALGO=`
- `OIDC_OP_JWKS_ENDPOINT=`
- `OIDC_SCOPES=`

Ver https://mozilla-django-oidc.readthedocs.io/en/stable/settings.html para una explicación detallada de cada variable.

> [!TIP]
> El callback es siempre `/oidc/callback` (p.ej. http://django:8000/oidc/callback/).

### Variables de Entorno
> [!CAUTION]
> `PRESTAMOS_LOCALMODE` y `PRESTAMOS_DEBUG` activadas en conjunto permite hacer bypass al login, creando una cuenta de administrador. Esta opción solo ha de usarse para desarrollo.

#### `PRESTAMOS_SECRET_KEY` 
https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-SECRET_KEY

#### `PRESTAMOS_DEBUG`
Establece el modo Debug (arroja errores). En producción, se recomienda ponerlo a `False`

#### `PRESTAMOS_LOCALMODE`
Establece el modo Local (permite hacer bypass al login y configura la cabecera). Se recomienda encarecidamente no activarlo nunca, indicar el valor explicítamente como `False`

#### `PRESTAMOS_ALLOWED_HOSTS`
https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts

#### `EMAIL_HOST`
#### `EMAIL_PORT`
#### `EMAIL_HOST_USER`
#### `EMAIL_HOST_PASSWORD`
#### `EMAIL_USE_TLS`
#### `EMAIL_USE_SSL`
#### `DATABASE_ENGINE`
#### `DATABASE_NAME`
#### `DATABASE_USERNAME`
#### `DATABASE_PASSWORD`
#### `DATABASE_HOST`
#### `DATABASE_PORT`
#### `CELERY_BROKER_URL`
#### `CELERY_RESULT_BACKEND`
#### `RABBITMQ_DEFAULT_USER`
#### `RABBITMQ_DEFAULT_PASS`


&copy; 2025 Iván Moya Ortiz
