from django.db.models.signals import post_save, post_delete

from django.contrib.auth.models import User
from .models import Profile

from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

def createProfile(sender, instance, created, **kwargs):
    '''Create Profile if Django User is created.'''

    if created:
        user = instance
        profile = Profile.objects.create(
                user=user,
                username=user.username,
                email=user.email,
                name=user.first_name
        )

        subject = 'Welcome to DevSearch'
        message = 'We are glad you are here!'

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=False
        )


def updateUser(sender, instance, created, **kwargs):
    '''Update Django's User when Profile is updated.'''

    profile = instance
    user = profile.user

    if not created:
        user.email = profile.email
        user.username = profile.username
        user.first_name = profile.name
        user.save()


# This causes an error if staff member tries to delete User instance
# on the admin page instead of Profile instance
@receiver(post_delete, sender=Profile)
def userDeleted(sender, instance, **kwargs):
    '''Delete Django User when user's Profile is deleted.'''

    # Instance is Profile object so we get User of it
    user = instance.user
    user.delete()


post_save.connect(createProfile, sender=User)
post_save.connect(updateUser, sender=Profile)
