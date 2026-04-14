import threading
import time

from django.contrib.auth.models import User
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MyModel


_caller_context = threading.local()
SIGNAL_RESULTS = {}


def set_caller_context(caller_thread_id):
    _caller_context.caller_thread_id = caller_thread_id


@receiver(post_save, sender=User)
def assignment_signal_probe(sender, instance, created, **kwargs):
    if not created or not instance.username.startswith("signal_demo_"):
        return

    caller_thread_id = getattr(_caller_context, "caller_thread_id", None)
    signal_thread_id = threading.get_ident()
    in_atomic_block = connection.in_atomic_block

    if instance.username.startswith("signal_demo_sync_"):
        time.sleep(1)

    MyModel.objects.create(name=f"from-signal:{instance.username}")

    SIGNAL_RESULTS[instance.username] = {
        "caller_thread_id": caller_thread_id,
        "signal_thread_id": signal_thread_id,
        "in_atomic_block": in_atomic_block,
    }