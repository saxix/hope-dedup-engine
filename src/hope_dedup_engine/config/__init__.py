from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Tuple, TypeAlias, Union
from urllib import parse

from environ import Env

if TYPE_CHECKING:
    ConfigItem: TypeAlias = Union[Tuple[type, Any, str, Any], Tuple[type, Any, str], Tuple[type, Any]]


DJANGO_HELP_BASE = "https://docs.djangoproject.com/en/5.0/ref/settings"


def setting(anchor: str) -> str:
    return f"@see {DJANGO_HELP_BASE}#{anchor}"


class Group(Enum):
    DJANGO = 1


NOT_SET = "<- not set ->"
EXPLICIT_SET = ["DATABASE_URL", "SECRET_KEY", "CACHE_URL", "CELERY_BROKER_URL", "MEDIA_ROOT", "STATIC_ROOT"]

CONFIG: "Dict[str, ConfigItem]" = {
    "ADMIN_EMAIL": (str, "", "Initial user created at first deploy"),
    "ADMIN_PASSWORD": (str, "", "Password for initial user created at first deploy"),
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"], setting("allowed-hosts")),
    "AUTHENTICATION_BACKENDS": (list, [], setting("authentication-backends")),
    "CACHE_URL": (str, "redis://localhost:6379/0"),
    "CATCH_ALL_EMAIL": (str, "If set all the emails will be sent to this address"),
    "CELERY_BROKER_URL": (str, NOT_SET, "https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html"),
    "CELERY_TASK_ALWAYS_EAGER": (
        bool,
        False,
        "https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_always_eager",
        True,
    ),
    "CELERY_TASK_EAGER_PROPAGATES": (
        bool,
        True,
        "https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates",
    ),
    "CELERY_VISIBILITY_TIMEOUT": (
        int,
        1800,
        "https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-transport-options",
    ),
    "CSRF_COOKIE_SECURE": (bool, True, setting("csrf-cookie-secure")),
    "DATABASE_URL": (
        str,
        "postgres://127.0.0.1:5432/dedupe",
        "https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url",
        "postgres://127.0.0.1:5432/dedupe",
    ),
    "DEBUG": (bool, False, setting("debug"), True),
    "EMAIL_BACKEND": (str, "django.core.mail.backends.smtp.EmailBackend", setting("email-backend"), True),
    "EMAIL_HOST": (str, "localhost", setting("email-host"), True),
    "EMAIL_HOST_USER": (str, "", setting("email-host-user"), True),
    "EMAIL_HOST_PASSWORD": (str, "", setting("email-host-password"), True),
    "EMAIL_PORT": (int, "25", setting("email-port"), True),
    "EMAIL_SUBJECT_PREFIX": (str, "[Hope-dedupe]", setting("email-subject-prefix"), True),
    "EMAIL_USE_LOCALTIME": (bool, False, setting("email-use-localtime"), True),
    "EMAIL_USE_TLS": (bool, False, setting("email-use-tls"), True),
    "EMAIL_USE_SSL": (bool, False, setting("email-use-ssl"), True),
    "EMAIL_TIMEOUT": (str, None, setting("email-timeout"), True),
    "LOGGING_LEVEL": (str, "CRITICAL", setting("logging-level")),
    "FILE_STORAGE_DEFAULT": (str, "django.core.files.storage.FileSystemStorage", setting("storages")),
    "FILE_STORAGE_MEDIA": (str, "django.core.files.storage.FileSystemStorage", setting("storages")),
    "FILE_STORAGE_STATIC": (str, "django.contrib.staticfiles.storage.StaticFilesStorage", setting("storages")),
    "FILE_STORAGE_HOPE": (str, "django.core.files.storage.FileSystemStorage", setting("storages")),
    "MEDIA_ROOT": (str, None, setting("media-root")),
    "MEDIA_URL": (str, "/media/", setting("media-url")),
    "ROOT_TOKEN": (str, "", ""),
    "SECRET_KEY": (str, NOT_SET, setting("secret-key")),
    "SECURE_HSTS_PRELOAD": (bool, True, setting("secure-hsts-preload"), False),
    "SECURE_HSTS_SECONDS": (int, 60, setting("secure-hsts-seconds")),
    "SECURE_SSL_REDIRECT": (bool, True, setting("secure-ssl-redirect"), False),
    "SENTRY_DSN": (str, "", "Sentry DSN"),
    "SENTRY_ENVIRONMENT": (str, "production", "Sentry Environment"),
    "SENTRY_URL": (str, "", "Sentry server url"),
    "SESSION_COOKIE_DOMAIN": (str, "", setting("std-setting-SESSION_COOKIE_DOMAIN"), "localhost"),
    "SESSION_COOKIE_HTTPONLY": (bool, True, setting("session-cookie-httponly"), False),
    "SESSION_COOKIE_NAME": (str, "dedupe_session", setting("session-cookie-name")),
    "SESSION_COOKIE_PATH": (str, "/", setting("session-cookie-path")),
    "SESSION_COOKIE_SECURE": (bool, True, setting("session-cookie-secure"), False),
    "SIGNING_BACKEND": (str, "django.core.signing.TimestampSigner", setting("signing-backend")),
    "SOCIAL_AUTH_LOGIN_URL": (str, "/login/", "", ""),
    "SOCIAL_AUTH_RAISE_EXCEPTIONS": (bool, False, "", True),
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": (bool, True, "", False),
    "STATIC_FILE_STORAGE": (str, "django.core.files.storage.FileSystemStorage", setting("storages")),
    "STATIC_ROOT": (str, None, setting("static-root")),
    "STATIC_URL": (str, "/static/", setting("static-url")),
    "TIME_ZONE": (str, "UTC", setting("std-setting-TIME_ZONE")),
    "AZURE_ACCOUNT_NAME": (str, ""),
    "AZURE_ACCOUNT_KEY": (str, ""),
    "AZURE_CUSTOM_DOMAIN": (str, ""),
    "AZURE_CONNECTION_STRING": (str, ""),
    "CV2DNN_PATH": (str, ""),
}


class SmartEnv(Env):
    def __init__(self, **scheme):  # type: ignore[no-untyped-def]
        self.raw = scheme
        values = {k: v[:2] for k, v in scheme.items()}
        super().__init__(**values)

    def get_help(self, key: str) -> str:
        entry: "ConfigItem" = self.raw.get(key, "")
        if len(entry) > 2:
            return entry[2]
        return ""

    def for_develop(self, key: str) -> Any:
        entry: ConfigItem = self.raw.get(key, "")
        if len(entry) > 3:
            value = entry[3]
        else:
            value = self.get_value(key)
        return value

    def storage(self, value: str) -> dict[str, str | dict[str, Any]] | None:
        raw_value = self.get_value(value, str)
        if not raw_value:
            return None
        options = {}
        if "?" in raw_value:
            value, options = raw_value.split("?", 1)
            options = dict(parse.parse_qsl(options))
        else:
            value = raw_value

        return {"BACKEND": value, "OPTIONS": options}

    def get_default(self, var: str) -> Any:
        var_name = f"{self.prefix}{var}"
        value = ""
        if var_name in self.scheme:
            var_info = self.scheme[var_name]
            value = var_info[1]
            try:
                cast = var_info[0]
                return cast(value)
            except TypeError as e:
                raise TypeError(f"Can't cast {var} to {cast}") from e
        return value


env = SmartEnv(**CONFIG)  # type: ignore[no-untyped-call]
