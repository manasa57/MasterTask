from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Task
from django.shortcuts import render, get_object_or_404, redirect




def homepage(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Retrieve username from the form
        password = request.POST.get('password')  # Retrieve password from the form

        # Authenticate user with username and password
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Log in the user
            messages.success(request, "Login successful!")
            return redirect('dashboard')  # Redirect to the dashboard view
        else:
            messages.error(request, "Invalid username or password. Please try again.")  # Add error message

    return render(request, 'login.html')  # Render the login page




def register_view(request):
    if request.method == 'POST':  # When the form is submitted
        username = request.POST.get('username', '').strip()  # Get the username
        email = request.POST.get('email', '').strip()        # Get the email
        password = request.POST.get('password', '').strip()  # Get the password

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please log in.")
        else:
            # Create a new user
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')  # Redirect to the login view by its name

    return render(request, 'register.html')  # Render the registration page


@login_required
def dashboard_view(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'tasks': tasks})


@login_required
def add_task_view(request):
    if request.method == 'POST':
        name = request.POST.get('task')
        description = request.POST.get('description')
        category = request.POST.get('category')
        priority = request.POST.get('priority')

        if not name:
            messages.error(request, "Task name is required.")
        elif not category:
            messages.error(request, "Please select a category.")
        elif not priority:
            messages.error(request, "Please select a priority.")
        else:
            # Save the task to the database
            Task.objects.create(
                user=request.user,
                name=name,
                description=description,
                category=category,
                priority=priority
            )
            messages.success(request, "Task added successfully!")
            return redirect('dashboard')  # Redirect to the dashboard after adding the task

    return render(request, 'add-task.html')


@login_required
def edit_task_view(request, task_id):
    # Fetch the task for the logged-in user
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == 'POST':
        task.name = request.POST.get('task', task.name)
        task.description = request.POST.get('description', task.description)
        task.category = request.POST.get('category', task.category)
        task.priority = request.POST.get('priority', task.priority)
        task.save()

        messages.success(request, "Task updated successfully!")
        return redirect('dashboard')

    return render(request, 'edit-task.html', {'task': task})

@login_required
def delete_task_view(request, task_id):
    # Fetch the task for the logged-in user
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted successfully!")
        return redirect('dashboard')

    messages.error(request, "Invalid request.")
    return redirect('dashboard')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def update_status(request, task_id):
    if request.method == "POST":
        try:
            task = Task.objects.get(id=task_id, user=request.user)
            data = json.loads(request.body)
            task.status = data.get("status", "Pending")
            task.save()
            return JsonResponse({"success": True, "status": task.status})
        except Task.DoesNotExist:
            return JsonResponse({"success": False, "error": "Task not found"}, status=404)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages

@login_required
def profile_settings_view(request):
    # Clear old messages
    storage = get_messages(request)
    list(storage)  # This consumes and clears existing messages

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password', None)

        # Update user information
        user = request.user
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)  # Keeps the user logged in after password change

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')  # Replace 'profile' with the name of your profile page URL

    return render(request, 'profile.html')
@login_required
def reports_view(request):
    # Fetch task reports
    completed_tasks = Task.objects.filter(user=request.user, status="Completed").count()
    pending_tasks = Task.objects.filter(user=request.user, status="Pending").count()
    in_progress_tasks = Task.objects.filter(user=request.user, status="In Progress").count()

    context = {
        'completed': completed_tasks,
        'pending': pending_tasks,
        'in_progress': in_progress_tasks,
    }

    return render(request, 'reports.html', context)