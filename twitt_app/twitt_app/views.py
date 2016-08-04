from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from twitt_app.forms import AuthenticateForm, UserCreateForm, TwitForm
from twitt_app.models import Twitt


def index(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        twit_form = TwitForm()
        user = request.user
        twitts_self = Twit.objects.filter(user=user.id)
        twitts_buddies = Twit.objects.filter(user__userprofile__in=user.profile.follows.all)
        twitts = twitts_self | twitts_buddies
 
        return render(request,
                      'buddies.html',
                      {'twitt_form': twit_form, 'user': user,
                       'twitts': twitts,
                       'next_url': '/', })
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()
 
        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, })



def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return index(request, auth_form=form)
    return redirect('/')
 
 
def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')


@login_required
def submit(request):
    if request.method == "POST":
        twit_form = TwitForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if twit_form.is_valid():
            twit = twit_form.save(commit=False)
            twit.user = request.user
            twit.save()
            return redirect(next_url)
        else:
            return public(request, twit_form)
    return redirect('/')


@login_required
def public(request, ribbit_form=None):
    ribbit_form = ribbit_form or RibbitForm()
    ribbits = Ribbit.objects.reverse()[:10]
    return render(request,
                  'public.html',
                  {'ribbit_form': ribbit_form, 'next_url': '/ribbits',
                   'ribbits': ribbits, 'username': request.user.username})
