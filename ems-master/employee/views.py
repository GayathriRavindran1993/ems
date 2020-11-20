from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView
from django.urls import reverse
from django.urls import reverse_lazy
from employee.forms import UserForm
from datetime import date
from ems.decorators import admin_hr_required, admin_only
from .models import Task
import csv

from django.http import HttpResponse

def index(request):
    print("hai")
    return HttpResponseRedirect(reverse('employee_list'))
def user_login(request):
    print("haiii")
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(user)
        if user:
            login(request, user)
            if request.GET.get('next', None):
                print("reached")
                return HttpResponseRedirect(request.GET['next'])
            return HttpResponseRedirect(reverse('view_task'))
        else:
            context["error"] = "Provide valid credentials !!"
            return render(request, "auth/login.html", context)
    else:
        return render(request, "auth/login.html", context)

@login_required(login_url="/login/")
def success(request):
    context = {}
    context['user'] = request.user
    return render(request, "auth/success.html", context)

@login_required(login_url="/login/")
def view_task(request):
    context = {}
    #context['user'] = request.user
    tasks= Task.objects.filter(date=date.today())
    return render(request, "employee/index.html",{'tasks':tasks})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('user_login'))


@login_required(login_url="/login/")
def employee_list(request):
    print(request.role)
    context = {}
    context['users'] = User.objects.all()
    context['title'] = 'Employees'
    return render(request, 'employee/index.html', context)

@login_required(login_url="/login/")
def employee_details(request, id=None):
    context = {}
    context['user'] = get_object_or_404(User, id=id)
    return render(request, 'employee/details.html', context)

def file_load_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachement; filename="report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Employee Name', 'Task','Date','Time','Comment'])

    tasks = Task.objects.filter(date=date.today())

    # Note: we convert the students query set to a values_list as the writerow expects a list/tuple  

    for task in tasks:
        writer.writerow([task.employee_name,task.task_value,task.date,task.time,task.comment])

    return response
@login_required(login_url="/login/")
def add_task(request):
    context = {}
    print(request.method)
    if request.method == "POST":
        employeeName = request.POST['name']
        task = request.POST['task']
        time=request.POST['time']
        task=Task()
        task.employee_name=employeeName
        task.task_value=task
        task.time=time
        task.date=date.today()
        task.save()
        tasks= Task.objects.filter(date=date.today())
        return render(request, "employee/index.html", {'tasks':tasks})
@login_required(login_url="/login/")
@admin_only
def employee_add(request):
    context = {}
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        context['user_form'] = user_form
        if user_form.is_valid():
            u = user_form.save()    
            return HttpResponseRedirect(reverse('employee_list'))
        else:
            return render(request, 'employee/add.html', context)
    else:
        user_form = UserForm()
        context['user_form'] = user_form
        return render(request, 'employee/add.html', context)

@login_required(login_url="/login/")
def employee_edit(request, id=None):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()    
            return HttpResponseRedirect(reverse('employee_list'))
        else:
            return render(request, 'employee/edit.html', {"user_form": user_form})
    else:
        user_form = UserForm(instance=user)
        return render(request, 'employee/edit.html', {"user_form": user_form})

@login_required(login_url="/login/")
def employee_delete(request, id=None):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        user.delete()
        return HttpResponseRedirect(reverse('employee_list'))
    else:
        context = {}
        context['user'] = user
        return render(request, 'employee/delete.html', context)


class ProfileUpdate(UpdateView):
    fields = ['designation', 'salary', 'picture']
    template_name = 'auth/profile_update.html'
    success_url = reverse_lazy('my_profile')

    def get_object(self):
        return self.request.user.profile



class MyProfile(DetailView):
    template_name = 'auth/profile.html'

    def get_object(self):
        return self.request.user.profile


from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .serializers import LoginSerializer
from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import generics
from .serializers import EmployeeSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import FilterSet
from django_filters import rest_framework as filters


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=200)


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication, )

    def post(self, request):
        django_logout(request)
        return Response(status=204)

class EmployeeFilter(FilterSet):
    is_active = filters.CharFilter('is_active')
    designation = filters.CharFilter('profile__designation')
    min_salary = filters.CharFilter(method="filter_by_min_salary")
    max_salary = filters.CharFilter(method="filter_by_max_salary")

    class Meta:
        model = User
        fields = ('is_active', 'designation', 'username',)

    def filter_by_min_salary(self, queryset, name, value):
        queryset = queryset.filter(profile__salary__gt=value)
        return queryset

    def filter_by_max_salary(self, queryset, name, value):
        queryset = queryset.filter(profile__salary__lt=value)
        return queryset


class EmployeeListView(generics.ListAPIView):
    serializer_class = EmployeeSerializer
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    # filter_fields = ('is_active', 'profile__designation', )
    filter_class = EmployeeFilter

    ordering_fields = ('is_active', 'username')
    ordering = ('username',)
    search_fields = ('username', 'first_name')


class TaskListView(generics.ListAPIView):
    serializer_class = EmployeeSerializer
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    # filter_fields = ('is_active', 'profile__designation', )
    filter_class = EmployeeFilter

    ordering_fields = ('is_active', 'username')
    ordering = ('username',)
    search_fields = ('username', 'first_name')

    # def get_queryset(self):
    #     queryset = User.objects.all()
    #     active = self.request.query_params.get('is_active', '')
    #     if active:
    #         if active == "False":
    #             active = False
    #         elif active == "True":
    #             active = True
    #         else:
    #             return queryset
    #         return queryset.filter(is_active=active)
    #     return queryset
