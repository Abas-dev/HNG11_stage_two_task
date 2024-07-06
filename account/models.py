
from django.db import models

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
    

class CustomUserManager(BaseUserManager):
    def create_user(self,email,password,**extra_fields):
        email = self.normalize_email(email)

        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser has to have is_staff as true")
        
        if extra_fields.get("is_superuser") is not True: 
            raise ValueError("superuser has to have is_superuser set to true")
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    userId = models.CharField(max_length= 100,blank= False,null= False)
    email = models.EmailField(max_length= 80, unique= True)
    firstName = models.CharField(max_length= 150, blank= False,null=False)
    lastName = models.CharField(max_length= 150, blank= False,null=False) 
    phone = models.CharField(max_length= 100, default= '')

    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']


    def __str__(self):
        return self.first_name+" "+ self.last_name
