# 🐕 Perretes

Red social de mensajes cortos ("ladridos") construida con **Django 5**, **Django REST Framework**, **Celery** y **Redis**. Feed paginado, likes, edición de posts, búsqueda en tiempo real y suite de tests profesional.

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Django 5 + DRF |
| Async tasks | Celery + Redis |
| DB | SQLite (estructurado para PostgreSQL) |
| Tests | pytest + pytest-django + factory-boy |

---

## Instalación local

```bash
# 1. Clonar y entorno virtual
git clone <repo>
cd perretes
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Base de datos
python manage.py migrate

# 3. Redis (broker Celery)
redis-server
# o: docker run -d -p 6379:6379 --name redis-perretes redis:alpine

# 4. Celery worker (terminal aparte)
celery -A perretes worker -l info

# 5. Servidor de desarrollo
python manage.py runserver
```

Abre [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Arquitectura

El proyecto usa **Service Layer + Selectors** para mantener las views delgadas y el código testeable:

- **Services** (`apps/*/services/`): lógica de negocio (crear usuario, publicar ladrido, toggle like).
- **Selectors** (`apps/*/selectors/`): queries encapsuladas. Centralizan `select_related`, `annotate`, `prefetch_related`.
- **Views** (`views.py`): solo orquestan. Validan input, llaman al service/selector y devuelven response.

Beneficio: los services se testean unitariamente con mocks (sin base de datos). Los selectors se testean contra SQLite in-memory.

---

## API Endpoints

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/users/register/` | No | Registro + auto-login |
| POST | `/api/users/login/` | No | Login |
| POST | `/api/users/logout/` | Sí | Logout |
| GET | `/api/users/me/` | Sí | Usuario autenticado |
| GET | `/api/users/<username>/profile/` | No | Perfil público |
| GET | `/api/barkposts/` | No | Feed global (paginado) |
| GET | `/api/barkposts/search/?q=` | No | Búsqueda en tiempo real |
| POST | `/api/barkposts/create/` | Sí | Crear ladrido (+ imagen) |
| PATCH | `/api/barkposts/<id>/update/` | Sí | Editar propio |
| DELETE | `/api/barkposts/<id>/delete/` | Sí | Eliminar propio |
| POST | `/api/barkposts/<id>/like/` | Sí | Dar / quitar like |
| GET | `/api/barkposts/user/<username>/` | No | Ladridos de un usuario |

---

## Tests

```bash
pytest                          # Todo el suite (71 tests)
pytest -m unit -v               # Solo unitarios (sin DB, ~0.2s)
pytest -m integration -v        # Selectors con DB
pytest -m api -v                # API HTTP end-to-end
pytest --cov=apps --cov-report=html   # Coverage
```

**Coverage actual: 96%**

| Módulo | Tests | Cobertura |
|--------|-------|-----------|
| `users/services` | 8 unitarios | 100% |
| `barkposts/services` | 16 unitarios | 96% |
| `users/selectors` | 6 integración | 100% |
| `barkposts/selectors` | 12 integración | 100% |
| `users/api` | 12 HTTP | 90% |
| `barkposts/api` | 19 HTTP | 87% |
| `barkposts/tasks` | 2 Celery | 100% |

---

## Decisiones técnicas

### ¿Por qué Service Layer + Selectors?

Separa lógica de negocio de queries. Si mañana cambiamos un `filter()` por caching o raw SQL, solo tocamos el selector. Los services son testeables sin requests HTTP ni base de datos.

### ¿Por qué pytest + factory-boy?

- **Markers** (`@pytest.mark.unit`, `@pytest.mark.integration`) permiten ejecutar subsets según contexto.
- **Fixtures reutilizables** en `conftest.py`: `api_client`, `authenticated_client`, `user`.
- **Factory Boy** genera datos dinámicos con `Sequence`, `SubFactory` y `Trait` (ej. `inactive`, `long_content`). Evita fixtures YAML frágiles.

### ¿Por qué Celery para logging?

La tarea `log_barkpost_activity` se encola al crear un ladrido. Desacopla I/O (métricas, notificaciones futuras) del thread HTTP. Si Redis falla, el ladrido igual se crea; el error se loggea sin romper el flujo.

---

## Estructura del proyecto

```
perretes/
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services/user_service.py
│   │   ├── selectors/user_selector.py
│   │   └── tests/           # factories, test_services, test_selectors, test_api
│   └── barkposts/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── views_search.py
│       ├── urls.py
│       ├── tasks.py         # Celery
│       ├── services/bark_service.py
│       ├── selectors/
│       │   ├── bark_selector.py
│       │   └── search_selector.py
│       └── tests/           # factories, test_services, test_selectors, test_api, test_tasks
├── perretes/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── conftest.py              # Fixtures globales de pytest
├── pytest.ini               # Configuración de pytest
├── requirements.txt
└── manage.py
```

---

## Mejoras futuras

- [ ] **Sistema de follows**: feed personalizado en lugar de global.
- [ ] **PostgreSQL**: `tsvector` para búsqueda full-text, `CONN_MAX_AGE`.
- [ ] **Caching**: `django-redis` para feeds y perfiles.
- [ ] **WebSockets**: Django Channels para likes y posts en tiempo real.
- [ ] **Docker**: `docker-compose.yml` con Django, PostgreSQL, Redis, Celery.
- [ ] **CI/CD**: GitHub Actions con tests, linting (ruff/black) y deploy automático.

---

## Licencia

MIT
