from django.db import models
import uuid
from users.models import Profile
# Create your models here.

class Project(models.Model):
    '''
    Model for each project.
    
    Consists of owner's foreign key, project's title, description, 
    demo link, source link, image, total amount of votes, and votes' ratio.

    Only owner, title are essential.
    '''

    owner = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    demo_link = models.CharField(max_length=2000, null=True, blank=True)
    source_link = models.CharField(max_length=2000, null=True, blank=True)
    featured_image = models.ImageField(null=True, blank=True, default='default.jpg')
    tags = models.ManyToManyField('Tag', blank=True)
    vote_total = models.IntegerField(default=0, null=True, blank=True)
    vote_ratio = models.IntegerField(default=0, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, 
                            primary_key=True, editable=False)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-vote_ratio', '-vote_total', 'title']

    @property
    def reviewers(self):
        '''Return reviewers for the project.'''

        queryset = self.review_set.all().values_list('owner__id', flat=True)
        return queryset

    @property
    def getVoteCount(self):
        '''Get count of votes for the project.'''

        reviews = self.review_set.all()
        upvotes = reviews.filter(value='up').count()
        totalVotes = reviews.count()

        ratio = (upvotes / totalVotes) * 100
        self.vote_total = totalVotes
        self.vote_ratio = ratio
        self.save()


class Review(models.Model):
    '''
    Model for the project's review.
    
    Consists of project owner's profile, project's foreign key, 
    body, and upvote/downvote.
    '''

    VOTE_TYPE = (
        ('up', 'Up Vote'),
        ('down', 'Down Vote')
    )
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    body = models.TextField(null=True, blank=True)
    value = models.CharField(max_length=200, choices=VOTE_TYPE)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, 
                            primary_key=True, editable=False)

    class Meta:
        unique_together = [['owner', 'project']]

    def __str__(self):
        return self.value

class Tag(models.Model):
    '''Model for each tag such as HTML, Python, and others for projects.'''

    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, 
                            primary_key=True, editable=False)

    def __str__(self):
        return self.name
