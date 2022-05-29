from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from API.serializers import *

from .models import *


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExtendedUserViewSet(viewsets.ModelViewSet):
    queryset = ExtendedUser.objects.all().order_by('-date_joined')
    serializer_class = ExtendedUserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('-date_joined')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def dogs(self, request, pk=None):
        client = self.get_object()
        dogs = Dog.objects.filter(owner=client)
        serializer = DogSerializer(dogs, many=True)
        return Response(serializer.data)


class WalksViewSet(viewsets.ModelViewSet):
    queryset = Walk.objects.all().order_by('-date')
    serializer_class = WalkSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def resign(self, request, pk=None):
        walk = self.get_object()
        walk.active = False
        walk.save()
        return Response(status=200)


class DogViewSet(viewsets.ModelViewSet):
    queryset = Dog.objects.all()
    serializer_class = DogSerializer
    permission_classes = [permissions.IsAuthenticated]


class TrainerViewSet(viewsets.ModelViewSet):
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        trainer = self.get_object()
        reviews = TrainerReview.objects.filter(trainer=trainer)
        serializer = TrainerReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reviews_rating(self, request):
        trainers = Trainer.objects.all()
        response = {}
        for trainer in trainers:
            reviews = TrainerReview.objects.filter(trainer=trainer)
            reviews_rating = {
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0,
                '5': 0
            }
            for review in reviews:
                reviews_rating[str(review.rating)] += 1
            response[trainer.trainer_id] = reviews_rating

        return Response(response)


class TrainerReviewViewSet(viewsets.ModelViewSet):
    queryset = TrainerReview.objects.all()
    serializer_class = TrainerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response(status=200)


class CoordsViewSet(viewsets.ModelViewSet):
    queryset = Coordinates.objects.all()
    serializer_class = CoordinatesSerializer
    permission_classes = [permissions.IsAuthenticated]

