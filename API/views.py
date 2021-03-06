from rest_framework import mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from API.serializers import *
from .models import *
import base64
from django.core.files.base import ContentFile


def get_image_from_base64(request_string):
    format, imgstr = request_string.split(';base64,')
    data = ContentFile(base64.b64decode(imgstr), name='image.' + format.split('/')[-1])
    return data


def convert_to_number(string):
    for char in string:
        if char not in '0123456789.':
            string = string.replace(char, '')
    return float(string)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        client = Client.objects.filter(id=user.id)
        trainer = Trainer.objects.filter(id=user.id)
        response = {
            'token': token.key
        }
        if len(client):
            response.update({
                'client_id': Client.objects.get(id=user.id).client_id if len(client) else 0
            })
        if len(trainer):
            response.update({
                'trainer_id': Trainer.objects.get(id=user.id).trainer_id if len(trainer) else 0
            })
        if User.objects.get(id=user.id).is_superuser:
            response.update({
                'admin_id': 0
            })
        return Response(response)


class RegisterViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        account_type = request.data['account_type']
        data = dict(request.data)
        if 'photo 'in data:
            data['photo'] = get_image_from_base64(data['photo'])
        del data['account_type']
        for key, value in data.items():
            data[key] = value
            if key == 'password':
                data[key] = make_password(data[key])
        if account_type == 'Klient':
            client = Client.objects.create(**data)
            client.save()
        elif account_type == 'Trener':
            trainer = Trainer.objects.create(**data)
            if 'photo' in data.keys():
                trainer.photo = get_image_from_base64(data['photo'])
            trainer.save()
        return Response(status=201)


class ResetPasswordViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        for key, value in data.items():
            data[key] = value[0]
        user = User.objects.get(username=data['username'])
        if not user:
            return Response({"response": "User with that username does not exists."}, status=400)
        if not user.check_password(data['old_password']):
            return Response({"response": "Old password is incorrect."}, status=400)
        user.set_password(data['new_password'])
        user.save()
        return Response(status=200)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExtendedUserViewSet(viewsets.ModelViewSet):
    queryset = ExtendedUser.objects.all().order_by('-date_joined')
    serializer_class = ExtendedUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        request.data['photo'] = get_image_from_base64(request.data['photo'])
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if 'http' in request.data['photo']:
            del request.data['photo']
        elif 'base64' in request.data['photo']:
            request.data['photo'] = get_image_from_base64(request.data['photo'])
        serializer = ExtendedUserSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        extended = self.get_object()
        for key, value in serializer.validated_data.items():
            setattr(extended, key, value)
        extended.save()
        return Response(ExtendedUserSerializer(extended).data)


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
        if 'http' in request.data['photo']:
            del request.data['photo']
        elif 'base64' in request.data['photo']:
            request.data['photo'] = get_image_from_base64(request.data['photo'])
        if User.objects.get(username=request.data['username']):
            del request.data['username']
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

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Walk.objects.all()
        else:
            dogs_of_owner = Dog.objects.filter(owner=Client.objects.get(id=self.request.user.id).client_id)
            return Walk.objects.filter(dog__in=dogs_of_owner)

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
        if request.data['photo'] is not None:
            request.data['photo'] = get_image_from_base64(request.data['photo'])
        else:
            del request.data['photo']
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if 'base64' in request.data['photo']:
            request.data['photo'] = get_image_from_base64(request.data['photo'])
        else:
            del request.data['photo']
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

    def create(self, request, *args, **kwargs):
        walk = Walk.objects.get(walk_id=request.data['walk'])
        for key, value in request.data.items():
            if key != 'walk':
                value = convert_to_number(value)
            request.data[key] = value
        serializer = CoordinatesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        walk = Walk.objects.get(walk_id=request.data['walk'])
        for key, value in request.data.items():
            if key != 'walk':
                value = convert_to_number(value)
            request.data[key] = value
        serializer = CoordinatesSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        coords = self.get_object()
        for key, value in serializer.validated_data.items():
            setattr(coords, key, value)
        coords.save()
        return Response(CoordinatesSerializer(coords).data)


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
                'available_hours': [hour for hour, available in available_hours.items() if available],
                'unavailable_hours': [hour for hour, available in available_hours.items() if not available]
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


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        serializer = PositionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        position = self.get_object()
        for key, value in serializer.validated_data.items():
            setattr(position, key, value)
        position.save()
        return Response(PositionSerializer(position).data)
