from django.shortcuts import render, redirect
from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages

from .models import Project
from .forms import ProjectForm, ReviewForm
from .utils import searchProjects, paginateProjects
# Create your views here.

def projects(request):
    '''Show all created projects.'''

    projects, search_query = searchProjects(request)

    # Make so only 10 pages show up
    # E.g.: you're on page 14, so you see pages from 9 to 19
    custom_range, projects = paginateProjects(request, projects, 6)

    context = {
        'projects' : projects, 'search_query': search_query, 
        'custom_range': custom_range,
        }
    return render(request, 'projects/projects.html', context)


def project(request, pk):
    '''Show a specific project.'''

    projectObj = Project.objects.get(id=pk)
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.project = projectObj
            review.owner = request.user.profile
            review.save()

            # Update project votecount
            projectObj.getVoteCount

            messages.success(request, 'Your reivew was successfully submitted!')
            return redirect('project', pk=projectObj.id)

    return render(request, 'projects/single-project.html', {'project' : projectObj, 'form': form})


@login_required(login_url='login')
def createProject(request):
    '''Page for creating a project.'''

    profile = request.user.profile
    form = ProjectForm()

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project.save()

            return redirect('projects')

    context = {'form' : form}
    return render(request, 'projects/project-form.html', context)


@login_required(login_url='login')
def updateProject(request, pk):
    '''Page for updating a project.'''


    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance=project)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('account')

    context = {'form' : form}
    return render(request, 'projects/project-form.html', context)


@login_required(login_url='login')
def deleteProject(request, pk):
    '''Function for deleting a project when user presses 'delete' button.'''

    profile = request.user.profile
    project = profile.project_set.get(id=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('projects')
        
    context = {'object' : project}
    return render(request, 'delete-template.html', context)
    