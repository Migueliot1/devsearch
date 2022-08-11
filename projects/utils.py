from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Project, Tag


def paginateProjects(request, projects, results):
    '''
    Creates pagination for the Projects url.
     
    In values: request - request object,
               projects - given projects from the search,
               results - how many results to display on the page.
    '''

    page = request.GET.get('page')
    results_to_display = results
    paginator = Paginator(projects, results_to_display)

    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        projects = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        projects = paginator.page(page)

    custom_range = createCustomRange(page, paginator.num_pages, 5)

    return custom_range, projects 


def createCustomRange(pageCurrent, pageTotal, value):
    '''
    Creates a range of pages which shows up to user.
    
    E.g.: the range (value) is 10 = user on the page 14 
    so they see pages from 9 to 19.
    '''

    leftIndex = (int(pageCurrent) - (int(value) - 1))
    if leftIndex < 1:
        leftIndex = 1

    rightIndex = (int(pageCurrent) + int(value))
    if rightIndex > pageTotal:
        rightIndex = pageTotal + 1

    custom_range = range(leftIndex, rightIndex)

    return custom_range


def searchProjects(request):
    '''Helper function for searching projects.'''

    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    tags = Tag.objects.filter(name__icontains=search_query)

    projects = Project.objects.distinct().filter(
        Q(owner__name__icontains=search_query) | 
        Q(title__icontains=search_query) | 
        Q(description__icontains=search_query) | 
        Q(tags__in=tags)
        )

    return projects, search_query
