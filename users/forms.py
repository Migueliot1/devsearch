from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Skill, Message

class CustomUserCreationForm(UserCreationForm):
    '''Form for registering the user.'''

    class Meta:
        model = User
        fields = ['first_name', 'email', 'username', 'password1',
                'password2']
        labels = {
            'first_name': 'Name',
            
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class ProfileForm(ModelForm):
    '''
    Form for adding all info for the user's account such as 
    location, info, bio, etc.
    '''

    class Meta:
        model = Profile
        fields = ['email', 'name', 'username', 'location', 
        'short_info', 'bio', 'profile_image', 'social_github', 
        'social_twitter', 'social_linkedin', 'social_youtube', 
        'social_website']
    
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class SkillForm(ModelForm):
    '''
    Form for creating user's skill such as Python, Django, 
    and its description.
    '''

    class Meta:
        
        model = Skill
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super(SkillForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class MessageForm(ModelForm):
    '''Form for creating a message.'''

    class Meta:
        model = Message
        fields = ['name', 'email', 'subject', 'body']

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
