from django.contrib.auth.models import UserManager as DefaultUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class UserManager(DefaultUserManager):
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError(_('The Username must be set'))
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        user = self.create_user(username, email, password, **extra_fields)
        user.role = 'superadmin'  
        user.save(using=self._db)
        return user


class User(AbstractUser):
    objects = UserManager() 

    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('superadmin', 'SuperAdmin'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    managed_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_users')    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    
    def is_admin(self):
        return self.role == 'admin' or self.role == 'superadmin'
    
    def is_superadmin(self):
        return self.role == 'superadmin'
    
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'superadmin'
        super(User, self).save(*args, **kwargs)
