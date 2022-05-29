from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=False,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        if validated_data.get('password'):
            user.set_password(validated_data.get('password'))
            user.save()
        return user


class ExtendedUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = ExtendedUser
        fields = UserSerializer.Meta.fields + ['phone_number', 'photo']


class ClientSerializer(ExtendedUserSerializer):
    class Meta(ExtendedUserSerializer.Meta):
        model = Client
        fields = ['client_id'] + ExtendedUserSerializer.Meta.fields + ['address']


class DogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        fields = ['dog_id', 'name', 'breed', 'age', 'description', 'photo', 'owner']


class TrainerSerializer(ExtendedUserSerializer):
    class Meta(ExtendedUserSerializer.Meta):
        model = Trainer
        fields = ['trainer_id'] + ExtendedUserSerializer.Meta.fields + ['date_of_birth', 'experience']


class WalkSerializer(serializers.ModelSerializer):
    dog = DogSerializer(read_only=True)
    trainer = TrainerSerializer(read_only=True)
    class Meta:
        model = Walk
        fields = ['walk_id', 'dog', 'date', 'start_hour', 'end_hour', 'trainer']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['start_hour'] = instance.start_hour.strftime('%H:%M')
        representation['end_hour'] = instance.end_hour.strftime('%H:%M')
        return representation


class TrainerReviewSerializer(serializers.ModelSerializer):
    trainer = TrainerSerializer()
    client = ClientSerializer()
    class Meta:
        model = TrainerReview
        fields = ['review_id', 'trainer', 'client', 'rating', 'comment']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notification_id', 'title', 'message', 'date', 'client', 'read']


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ['id', 'latitude', 'longitude', 'walk']

