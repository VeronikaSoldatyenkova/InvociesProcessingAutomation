# automation_app/views.py
from datetime import datetime, timedelta
import requests
import pyautogui
import time
import psutil
import subprocess
import logging
from django.http import JsonResponse, HttpResponse


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Automation, UserAutomation, User
from .forms import UserRegistrationForm, UserProfileForm, UserPasswordForm


@login_required
def home(request):
    user_automations = UserAutomation.objects.filter(user=request.user)
    return render(request, 'automation_app/home.html', {'user_automations': user_automations})


@login_required
def add_automation(request):
    if request.method == 'POST':
        automation_id = request.POST.get('automation_id')
        automation = get_object_or_404(Automation, id=automation_id)
        if (request.user.role == 'order_processing' and automation.automation_type.name == 'Orders') or \
                (request.user.role == 'invoice_processing' and automation.automation_type.name == 'Invoices'):
            if not UserAutomation.objects.filter(user=request.user, automation=automation).exists():
                UserAutomation.objects.create(user=request.user, automation=automation)
                return redirect('home')
            else:
                return render(request, 'automation_app/add_automation.html',
                              {'error': 'You have already added this automation.'})
        else:
            return render(request, 'automation_app/add_automation.html',
                          {'error': 'You do not have rights to add this automation.'})

    available_automations = Automation.objects.all()
    return render(request, 'automation_app/add_automation.html', {'available_automations': available_automations})


@login_required
def delete_automation(request, automation_id):
    user_automation = get_object_or_404(UserAutomation, user=request.user, automation_id=automation_id)
    user_automation.delete()
    return redirect('home')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'automation_app/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'automation_app/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('home')
    else:
        user_form = UserProfileForm(instance=request.user)
    return render(request, 'automation_app/profile.html', {'user_form': user_form})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        password_form = UserPasswordForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            return redirect('home')
    else:
        password_form = UserPasswordForm(request.user)
    return render(request, 'automation_app/change_password.html', {'password_form': password_form})


@login_required
def run_automation(request, automation_id):
    automation = get_object_or_404(Automation, id=automation_id)
    shortcut_mapping = {
        'Invoices_Legrand': 'alt+j',
        'Invoices_Pawbol': 'alt+k',
        'Orders_Depo': 'alt+l',
        'Orders_Kursi': 'alt+m'
    }
    shortcut = shortcut_mapping.get(automation.name)

    if shortcut:
        # Replace these variables with your own
        user_key = 'v3laDPGhYrQErXa1NyHKlmvSE5guj-qfDT7cNA9aD6DQK'
        client_id = '8DEv1AMNXczW3y4U15LL3jYf62jK93n5'
        account_logical_name = 'transportandtelecommunicationinstitute'
        service_instance_logical_name = 'DefaultTenant'
        auth_url = 'https://account.uipath.com/oauth/token'

        headers = {
            "Content-Type": "application/json",
            "X-UIPATH-TenantName": "DefaultTenant"
        }

        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": user_key
        }

        response = requests.post(auth_url, json=data, headers=headers)
        if response.status_code == 200:
            access_token = response.json()['access_token']
            api_headers = {
                "Authorization": f"Bearer {access_token}",
                "X-UIPATH-TenantName": "DefaultTenant",
                "Content-Type": "application/json"
            }

            jobs_url = f'https://cloud.uipath.com/{account_logical_name}/{service_instance_logical_name}/odata/Jobs?$filter=State eq \'Running\''

            jobs_response = requests.get(jobs_url, headers=api_headers)
            if jobs_response.status_code == 200:
                running_jobs = jobs_response.json()['value']
                for job in running_jobs:
                    start_time_str = job['StartTime']
                    if '.' in start_time_str:
                        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    else:
                        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%SZ')
                    if datetime.utcnow() - start_time > timedelta(minutes=40):
                        job_id = job['Id']
                        terminate_url = f'https://cloud.uipath.com/{account_logical_name}/{service_instance_logical_name}/odata/Jobs/UiPath.Server.Configuration.OData.StopJobs'
                        terminate_data = {
                            "jobIds": [job_id],
                            "strategy": "Kill"
                        }
                        api_headers.update({"X-UIPATH-OrganizationUnitId": "5392416"})
                        terminate_response = requests.post(terminate_url, json=terminate_data, headers=api_headers)
                        if terminate_response.status_code not in [200, 204]:
                            return JsonResponse(
                                {'error': f"Failed to terminate job {job['Key']}: {terminate_response.text}"},
                                status=500)
        else:
            return JsonResponse({'error': f"Failed to obtain access token: {response.text}"}, status=500)

        process_name = "UiPath.Assistant.exe"
        process_path = r"C:\Users\veron\AppData\Local\Programs\UiPath\Studio\UiPathAssistant\UiPath.Assistant.exe"

        if not is_process_running(process_name):
            start_process(process_path)

        time.sleep(10)
        pyautogui.hotkey(*shortcut.split('+'))

        logging.info("Script execution completed.")
        return JsonResponse({'message': "Automation triggered successfully."}, status=200)
    else:
        return JsonResponse({'error': "Invalid automation name."}, status=400)


def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if process_name.lower() in proc.info['name'].lower():
            return True
    return False


def start_process(process_path):
    try:
        subprocess.Popen(process_path)
    except Exception as e:
        logging.error(f"Failed to start process {process_path}: {e}")