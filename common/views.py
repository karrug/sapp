import uuid
import os
import hashlib
from urllib.parse import parse_qs, quote, urlencode
import requests
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from common.models import User



@login_required
def index(request):
    return render(request, "index.html")


def signup(request):
    next = request.GET.get('next', reverse('index'))
    if request.POST:
        name = request.POST['name']
        email = request.POST['email']
        phone_number = request.POST['phonenumber']
        password = request.POST['password']
        username = uuid.uuid4().hex
        print(phone_number, password)
        u = User.objects.create_user(name=name, email=email, phone_number=phone_number, username=username, password=password)
        login(request, u)
        url = request.GET.get('next', reverse('index'))
        return HttpResponseRedirect(url)
    return render(request, 'signup.html', {'next': next})


def signin(request):
    if request.POST:
        pn = request.POST['phonenumber']
        paswd = request.POST['password']
        print(pn, paswd)
        u = authenticate(username=pn, password=paswd)
        if u:
            login(request, u)
            return HttpResponseRedirect(reverse("index"))
    return render(request, 'signin.html')


def all_users(request):
    users = User.objects.all()
    return render(request, 'allusers.html', {'users': users})


@login_required
def user_details(request, pk):
    return render(request, 'userdetails.html')


@login_required
def set_password(request):
    errors = {}
    if request.POST:
        old_passwd = request.POST['oldpassword']
        u = request.user
        if u.check_password(old_passwd):
            new_passwd = request.POST['newpassword']
            u.set_password(new_passwd)
            u.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            errors = {'msg': "current password is wrong"}
    return render(request, "changepassword.html", {'errors': errors})


def user_search(request):
    if request.POST:
        pn = request.POST['phonenumber']
        result = {'pn': pn}
        try:
            result['user'] = User.objects.get(phone_number=pn)
        except User.DoesNotExist:
            result['msg'] = 'user does not exist'
        return render(request, 'search.html', {'result': result})
    return render(request, 'search.html')


@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def auth(request):
    qnext = quote(reverse('index'), safe="")
    url = "%s?next=%s" % (reverse("op_auth"), qnext)
    return HttpResponseRedirect(url)


def op_auth(request):
    qnext = quote(request.GET["next"], safe="")
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    state = "security_token=%s&next=%s" % (state, qnext)
    qstate = quote(state, safe="")
    url = "%s?client_id=%s&redirect_uri=%s&state=%s&scope=%s" % (
        'https://github.com/login/oauth/authorize',
        '9856aaffaf08603a0f4e',
        'http://149.56.24.69:9988/auth/complete',
        qstate,
        "user:email",
    )
    return HttpResponseRedirect(url)


def complete_op_auth(request):
    print(request.GET)
    code = request.GET['code']
    state = request.GET["state"]
    h = {"content-type": "application/x-www-form-urlencoded", 'Accept': 'application/json'}
    d = {
        "client_id": '9856aaffaf08603a0f4e',
        "client_secret": '47c8f7dd0daa98690d4cc967121d651e50c8d5f2',
        "code": code,
        "redirect_uri": 'http://149.56.24.69:9988/auth/complete',
        "state": state,
    }
    r = requests.post('https://github.com/login/oauth/access_token', headers=h, data=d)
    t = r.json()['access_token']

    h = {'Authorization': 'token %s' % t, 'Accept': 'application/json'}
    r = requests.get('https://api.github.com/user', headers=h)
    r = r.json()
    try:
        u = User.objects.get(email=r['email'])
    except User.DoesNotExist:
        url = '%s?next=%s' % (reverse('signup'), quote(reverse(auth), safe=""))
        print(url)
        return HttpResponseRedirect(url)
    else:
        d = {'github': r}
        u.meta.update(d)
        u.save()
        login(request, u)
    return HttpResponseRedirect(reverse('index'))
