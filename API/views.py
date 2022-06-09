from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from API.serializers import *
from datetime import timedelta
from .models import *


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        client_id = Client.objects.filter(id=user.id)
        return Response({
            'token': token.key,
            'client_id': Client.objects.get(id=user.id).client_id if len(client_id) else 0
        })


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

    def partial_update(self, request, *args, **kwargs):
        serializer = ClientSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        client = self.get_object()
        for key, value in serializer.validated_data.items():
            setattr(client, key, value)
        client.save()
        return Response(ClientSerializer(client).data)


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

    def partial_update(self, request, *args, **kwargs):
        serializer = WalkSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        walk = self.get_object()
        for key, value in serializer.validated_data.items():
            setattr(walk, key, value)
        walk.save()
        return Response(WalkSerializer(walk).data)


class DogViewSet(viewsets.ModelViewSet):
    queryset = Dog.objects.all()
    serializer_class = DogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Dog.objects.all()
        else:
            return Dog.objects.filter(owner=Client.objects.get(id=self.request.user.id).client_id)

    def create(self, request, *args, **kwargs):
        request.data['owner'] = Client.objects.get(client_id=request.data['owner']).client_id
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        serializer = DogSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        dog = self.get_object()
        for key, value in serializer.validated_data.items():
            setattr(dog, key, value)
        dog.save()
        return Response(DogSerializer(dog).data)


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

    def partial_update(self, request, *args, **kwargs):
        serializer = TrainerSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        trainer = self.get_object()
        for key, value in serializer.validated_data.items():
            setattr(trainer, key, value)
        trainer.save()
        return Response(TrainerSerializer(trainer).data)


class TrainerReviewViewSet(viewsets.ModelViewSet):
    queryset = TrainerReview.objects.all()
    serializer_class = TrainerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def ratings(self, request):
        trainers = Trainer.objects.all()
        response = []
        for trainer in trainers:
            reviews = TrainerReview.objects.filter(trainer=trainer)
            reviews_rating = {
                'trainer_id': trainer.trainer_id,
                '1': 0,
                '2': 0,
                '3': 0,
                '4': 0,
                '5': 0
            }
            for review in reviews:
                reviews_rating[str(review.rating)] += 1
            response.append(reviews_rating)

        return Response(response)


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


class TrainerAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = TrainerAvailability.objects.all()
    serializer_class = TrainerAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_availability(self, request):
        trainer_id = request.query_params.get('trainer_id')
        date = request.query_params.get('date')
        if trainer_id:
            trainer = Trainer.objects.get(trainer_id=trainer_id)
            availability = TrainerAvailability.objects.filter(trainer=trainer, date=date)
            walks = Walk.objects.filter(trainer=trainer, date=date).order_by('start_hour')
            available_hours = {}
            for availability_item in availability:
                start_hour = int(availability_item.start_hour.strftime('%H'))
                end_hour = int(availability_item.end_hour.strftime('%H'))
                hours = {f"{hour}:00": True for hour in range(start_hour, end_hour)}
                available_hours.update(hours)

            for walk in walks:
                if walk.active:
                    start_hour = int(walk.start_hour.strftime('%H'))
                    end_hour = int(walk.end_hour.strftime('%H'))
                    hours = {f"{hour}:00": False for hour in range(start_hour, end_hour)}
                    available_hours.update(hours)

            response = {
                'trainer_id': trainer.trainer_id,
                'date': date,
                'available_hours': available_hours
            }
        return Response(response)

    def partial_update(self, request, *args, **kwargs):
        serializer = TrainerAvailabilitySerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        availability = self.get_object()
        for key, value in serializer.validated_data.items():
            setattr(availability, key, value)
        availability.save()
        return Response(TrainerAvailabilitySerializer(availability).data)
