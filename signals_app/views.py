from django.shortcuts import render
from django.contrib.auth.models import User
from django.db import transaction
import threading
import time
import uuid

from .rectangle import Rectangle
from .models import MyModel
from .signals import SIGNAL_RESULTS, set_caller_context


def rectangle_demo(request):
	length = request.GET.get("length", 10)
	width = request.GET.get("width", 5)

	try:
		length = int(length)
		width = int(width)
		rectangle = Rectangle(length=length, width=width)
		items = list(rectangle)
		error = None
	except ValueError:
		items = []
		error = "Length and width must be integers."

	return render(
		request,
		"signals_app/rectangle_demo.html",
		{
			"length": length,
			"width": width,
			"items": items,
			"error": error,
		},
	)


def signals_assignment_demo(request):
	# Q1 + Q2 proof run
	username_sync = f"signal_demo_sync_{uuid.uuid4().hex[:8]}"
	caller_thread_id = threading.get_ident()
	set_caller_context(caller_thread_id)

	start = time.perf_counter()
	User.objects.create_user(username=username_sync, password="pass12345")
	elapsed = time.perf_counter() - start
	sync_data = SIGNAL_RESULTS.get(username_sync, {})

	q1_is_sync = elapsed >= 1.0 and bool(sync_data)
	q2_same_thread = sync_data.get("caller_thread_id") == sync_data.get("signal_thread_id")

	# Q3 proof run
	username_tx = f"signal_demo_tx_{uuid.uuid4().hex[:8]}"
	set_caller_context(threading.get_ident())

	try:
		with transaction.atomic():
			User.objects.create_user(username=username_tx, password="pass12345")
			raise RuntimeError("Force rollback")
	except RuntimeError:
		pass

	tx_user_exists = User.objects.filter(username=username_tx).exists()
	tx_model_exists = MyModel.objects.filter(name=f"from-signal:{username_tx}").exists()
	tx_signal_data = SIGNAL_RESULTS.get(username_tx, {})
	q3_same_transaction = (not tx_user_exists) and (not tx_model_exists)

	context = {
		"q1_result": q1_is_sync,
		"q1_elapsed": f"{elapsed:.2f}",
		"q2_result": q2_same_thread,
		"q2_caller_thread": sync_data.get("caller_thread_id"),
		"q2_signal_thread": sync_data.get("signal_thread_id"),
		"q3_result": q3_same_transaction,
		"q3_user_exists": tx_user_exists,
		"q3_model_exists": tx_model_exists,
		"q3_signal_in_atomic": tx_signal_data.get("in_atomic_block"),
	}

	return render(request, "signals_app/signals_assignment_demo.html", context)
