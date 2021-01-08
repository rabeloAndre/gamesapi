"""
Book: Building RESTful Python Web Services
Chapter 2: Working with class based views and hyperlinked APIs in Django
Author: Gaston C. Hillar - Twitter.com/gastonhillar
Publisher: Packt Publishing Ltd. - http://www.packtpub.com
"""
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Game
from .serializers import GameSerializer
from datetime import datetime


@api_view(['GET','POST'])
def game_list(request):
	if request.method == 'GET':
		games = Game.objects.all()
		games_serializer = GameSerializer(games, many=True)
		return Response(games_serializer.data)
	elif request.method == 'POST':
		games_serializer = GameSerializer(data=request.data)
		if games_serializer.is_valid():
			data = games_serializer.validated_data
			name = Game.objects.filter(name=data['name'])

			if not(name.exists()):
				games_serializer.save()
				return Response(games_serializer.data, status=status.HTTP_201_CREATED)

			return Response({'detail':'There is a game registered with that name'}, status=status.HTTP_400_BAD_REQUEST)

		return Response(games_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PUT','DELETE'])
def game_detail(request, pk):
	try:
		game = Game.objects.get(pk=pk)
	except Game.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		games_serializer = GameSerializer(game)
		return Response(games_serializer.data)

	elif request.method == 'PUT':
		games_serializer = GameSerializer(game, data=request.data)		
		if games_serializer.is_valid():
			data = games_serializer.validated_data
			name = Game.objects.filter(name=data['name']).exclude(id=game.id)
			
			if not(name.exists()):				
				games_serializer.save()
				return Response(games_serializer.data)

			return Response({'detail':'There is a game registered with that name'}, status=status.HTTP_400_BAD_REQUEST)
		
		return Response(games_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	elif request.method == 'DELETE':
		current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
		release = game.release_date.strftime('%d/%m/%Y %H:%M:%S')

		if release < current_time:
			return Response({'detail':{'This game cannot be deleted. Because it was already released in {}'.format(release)}}, status=status.HTTP_400_BAD_REQUEST)
		
		game.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
		