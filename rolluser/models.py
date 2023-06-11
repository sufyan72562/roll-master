from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings


# Create your models here.


def upload_to(instance, filename):
    return 'user/{filename}'.format(filename=filename)


class UserManager(BaseUserManager):
    def create_user(self, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, name, tc and password.
        """
        user = self.model(
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        # user = self.create_user(
        #     email,
        #     password=password,
        #     **extra_fields
        # )
        user = self.model(
            **extra_fields
        )
        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


#  Custom User Model
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
        null=True
    )
    username = models.CharField(max_length=200, unique=True, null=True)
    firstname = models.CharField(max_length=50, default="")
    lastname = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=20, unique=True, null=True)
    dob = models.CharField(max_length=12, default="")
    website = models.CharField(max_length=50, default="")
    bio = models.TextField(default="")
    image = models.ImageField(upload_to=upload_to, default='user/logo.jpg')
    followers = models.ManyToManyField('self',
                                       related_name="user_followers",
                                       blank=True,
                                       symmetrical=False)
    following = models.ManyToManyField('self',
                                       related_name="user_following",
                                       blank=True,
                                       symmetrical=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return str(self.email)

    def number_of_followers(self):

        if self.followers.count():
            return self.followers.count()
        else:
            return 0

    def number_of_following(self):
        if self.following.count():
            return self.following.count()
        else:
            return 0

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin
