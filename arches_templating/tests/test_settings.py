import os

import arches
from arches.settings import *

PACKAGE_NAME = "arches_templating"
APP_NAME = "arches_templating"

APP_ROOT = os.path.dirname(__file__)
TEST_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "..", "tests"))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "arches",
    "arches.app.models",
    "arches.management",
    "guardian",
    "arches_templating",
]

ROOT_URLCONF = "arches_templating.urls"

TEST_RUNNER = "arches_templating.tests.base_test.ArchesTestRunner"
SILENCED_SYSTEM_CHECKS.append(
    "arches.W001"
)  # Cache backend does not support rate-limiting


DOCKER = False

try:
    from arches.settings_local import *
except ImportError:
    pass

if DOCKER:
    try:
        from arches.settings_docker import *
    except ImportError:
        pass
