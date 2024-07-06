from rest_framework import serializers
from .models import User,Organisation
from rest_framework.validators import ValidationError
class SignupSerializers(serializers.ModelSerializer):
    
    class Meta:
        model= User
        fields= ("userId,email,firstName,lastName,phone")
        

    def validate(self, attrs):
        email_exists = User.objects.filter(email= attrs['email']).exists()

        if email_exists: 
            raise ValidationError("email has been used by another user")
        
        return super().validate(attrs)    
    
    def create(self, validated_data):
        password = validated_data.pop("password")

        user= super().create(validated_data)
         
        user.set_password(password)
        user.save()

        organistaion_name = f"{User.firstName}'s Organization"
        organistaion = Organisation.objects.create(name=organistaion_name)
        organistaion.save()

        return user
    
        '''
        not sure this code will work ooo 

        but insha'allah. lol 
        '''
    
    # def update(self, instance, validated_data):

    #     instance.set_password(validated_data['password'])
    #     instance.save()

    #     return instance

    '''the update function is to try and update the user models. might work or not.'''


class OrganisationSerializers(serializers.ModelSerializer):
    class Meta: 
        model = Organisation
        field = "__all__"