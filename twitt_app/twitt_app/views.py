from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from twitt_app.forms import AuthenticateForm, UserCreateForm, TwitForm
from twitt_app.models import Twit


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
def public(request, twit_form=None):
    twit_form = twit_form or TwitForm()
    twits = twit.objects.reverse()[:10]
    return render(request,
                  'public.html',
                  {'twit_form': twit_form, 'next_url': '/twits',
                   'twits': twits, 'username': request.user.username})



from django.db.models import Count
from django.http import Http404
 
 
def get_latest(user):
    try:
        return user.twit_set.order_by('-id')[0]
    except IndexError:
        return ""
 
 
@login_required
def users(request, username="", twit_form=None):
    if username:
        # Show a profile
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        twits = twit.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self Profile or buddies' profile
            return render(request, 'user.html', {'user': user, 'twits': twits, })
        return render(request, 'user.html', {'user': user, 'twits': twits, 'follow': True, })
    users = User.objects.all().annotate(twit_count=Count('twit'))
    twits = map(get_latest, users)
    obj = zip(users, twits)
    twit_form = twit_form or twitForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/',
                   'twit_form': twit_form,


@login_required
def follow(request):
    if request.method == "POST":
        follow_id = request.POST.get('follow', False)
        if follow_id:
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile)
            except ObjectDoesNotExist:
                return redirect('/users/')
    return redirect('/users/')
                   'username': request.user.username, })
