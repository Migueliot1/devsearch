from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Profile, Skill


def paginateProfiles(request, profiles, results):
    '''
    Creates pagination for the Profiles url.
     
    In values: request - request object,
               profiles - given profiles from the search,
               results - how many results to display on the page.
    '''

    page = request.GET.get('page')
    results_to_display = results
    paginator = Paginator(profiles, results_to_display)

    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        profiles = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        profiles = paginator.page(page)

    custom_range = createCustomRange(page, paginator.num_pages, 5)

    return custom_range, profiles 


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


def searchProfiles(request):
    '''Helper function for searching profiles.'''

    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    skills = Skill.objects.filter(name__icontains=search_query)

    profiles = Profile.objects.distinct().filter(
        Q(name__icontains=search_query) | 
        Q(short_info__icontains=search_query) | 
        Q(skill__in=skills)
        )

    return profiles, search_query
