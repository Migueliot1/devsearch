import re
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .utils import searchProfiles, paginateProfiles
from .models import Profile, Message
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from django.contrib import messages
 
# Create your views here.

def loginUser(request):
    '''Login the user.'''

    page = 'login'
    context  = {'page': page}

    # Redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        # Get username and password from the POST method
        username = request.POST['username']
        password = request.POST['password']

        # Try to get the user in db with given username
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        # Redirect user on 'profiles' page if login is successfull
        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request, 'Username OR password is incorrect')

    return render(request, 'users/login_register.html', context)


def logoutUser(request):
    '''Logout the user.'''

    logout(request)
    messages.info(request, 'Username logout successful')
    return redirect('login')


def registerUser(request):
    '''Register the user.'''

    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        # Fill in custom register form and save it if it's valid
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            # There appears an error if email host is wrong
            login(request, user)
            messages.success(request, 'User account was created!')
            return redirect('profiles')

        else:
            # Show a flash message if smth went wrong
            messages.error(
                    request, 'An error has occured during registration')
    
    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)


def profiles(request):
    '''Show all the user's profiles.'''

    profiles, search_query = searchProfiles(request)

    # Make so only 10 pages show up
    # E.g.: you're on page 14, so you see pages from 9 to 19
    custom_range, profiles = paginateProfiles(request, profiles, 6)

    context = {
        'profiles': profiles, 'search_query': search_query, 
        'custom_range': custom_range
        }
    return render(request, 'users/profiles.html', context)


def userProfile(request, pk):
    '''Show specific user's profile.'''

    profile = Profile.objects.get(id=pk)

    # Get skills of the user
    topSkills = profile.skill_set.exclude(description__exact='')
    otherSkills = profile.skill_set.filter(description='')

    context = {'profile': profile, 'topSkills': topSkills, 'otherSkills': otherSkills}
    return render(request, 'users/user-profile.html', context)


@login_required(login_url='login')
def userAccount(request):
    '''Show user's profile if user is logged in where they can edit their page.'''

    profile = request.user.profile

    # Get user's skills and projects
    skills = profile.skill_set.all()
    projects = profile.project_set.all()

    context = {'profile': profile, 'skills': skills, 
    'projects': projects}
    return render(request, 'users/account.html', context)


@login_required(login_url='login')
def editAccount(request):
    '''Show user's edit page.'''

    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        # Fill in the edit profile form and check if it's valid
        # then redirect to the account 
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid() and profile is not None:
            form.save()

            return redirect('account')
    
    context = {'form': form, 'profile': profile}
    return render(request, 'users/profile_form.html', context)


@login_required(login_url='login')
def createSkill(request):
    '''Create user's skill such as Python, HTML, etc.'''

    profile = request.user.profile
    form = SkillForm()


    if request.method == 'POST':

        # Fill in the form for saving skill and check if it's valid
        # then show a flash success message and redirect to user's account
        form = SkillForm(request.POST)

        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Skill was added successfully!')

            return redirect('account')


    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def updateSkill(request, pk):
    '''Send a form to update a skill.'''

    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)

    if request.method == 'POST':

        # Fill in the form for updating skill and check if it's valid
        # then show a flash success message and redirect to user's account
        form = SkillForm(request.POST, instance=skill)

        if form.is_valid():
            form.save()
            messages.success(request, 'Skill was updated successfully!')

            return redirect('account')


    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def deleteSkill(request, pk):
    '''Send a request to delete the skill on user's page.'''

    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)

    if request.method == 'POST':
        # Delete the skill, show success message, and redirect to user's account
        skill.delete()
        messages.success(request, 'Skill was deleted successfully!')
        return redirect('account')
        
    context = {'object' : skill}
    return render(request, 'delete-template.html', context)


@login_required(login_url='login')
def inbox(request):
    '''Render user's inbox with all messages and unread count.'''

    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context = {'messageRequests': messageRequests, 'unreadCount': unreadCount}
    
    return render(request, 'users/inbox.html', context)


@login_required(login_url='login')
def showMessage(request, pk):
    '''Show a specific message in user's inbox.'''

    profile = request.user.profile
    message = profile.messages.get(id=pk)

    # Update is_read boolean to True when user clicks it
    if message.is_read == False:
        message.is_read = True
        message.save()

    context = {'message': message}

    return render(request, 'users/message.html', context)


@login_required(login_url='login')
def createMessage(request, pk):
    '''Render form for sending a message.'''

    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    try:
        sender = request.user.profile
    except:
        sender = None
    
    if request.method == 'POST':

        # Check sent message form and create it in the database
        # then show success flash message and redirect to recipient's account
        form = MessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email

            message.save()
            messages.success(request, 'Your message was successfully sent!')

            return redirect('user-profile', pk=recipient.id)

    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/message_form.html', context)
