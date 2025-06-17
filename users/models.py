from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy

#To automatically create One To One objects
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class MyUserManager(BaseUserManager):
    def _createuser(self, email, password, **extrafields):
        if not email:
            raise ValueError("Email Must be Set!")

        email = self.normalize_email(email)
        user = self.model(email=email, **extrafields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extrafields):
        extrafields.setdefault('is_staff', True)
        extrafields.setdefault('is_superuser', True)
        extrafields.setdefault('is_active', True)

        if extrafields.get('is_staff') is not True:
            raise ValueError("Super User Must be Staff!")
        if extrafields.get('is_superuser') is not True:
            raise ValueError("Must be active Super User!")

        return self._createuser(email, password, **extrafields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False)
    username = models.CharField(max_length=100)
    is_admin = models.BooleanField(ugettext_lazy('Admin Status'), default=False, help_text=ugettext_lazy('Whether User is an Admin'))
    is_staff = models.BooleanField(ugettext_lazy('Staff Status'), default=False, help_text=ugettext_lazy('Whether user should have Staff Priveleges'))
    is_active = models.BooleanField(ugettext_lazy('Active'), default=True, help_text=ugettext_lazy('Whether user should be treated as active'))
    learner = models.BooleanField(ugettext_lazy('Learner'), default=False, help_text=ugettext_lazy('Whether user is a learner'))
    tutor = models.BooleanField(ugettext_lazy('Tutor'), default=False, help_text=ugettext_lazy('Whether user is a tutor'))

    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    about = models.TextField(blank=True)
    user_image = models.ImageField(upload_to='userimages', blank=True)
    learning_level = models.CharField(max_length=50, null=True, blank=True)
    progress_percentage = models.FloatField(default=0.0)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + "'s Profile"

    def isfullyfilled(self):
        fieldsname = [f.name for f in self._meta.get_fields()]
        for fieldname in fieldsname:
            value = getattr(self, fieldname)
            if value is None or value=='':
                return False
        return True

@receiver(post_save, sender=User)
def createprofile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def saveprofile(sender, instance, **kwargs):
    instance.profile.save()
