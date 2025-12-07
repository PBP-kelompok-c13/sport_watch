from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Berita, NewsReaction
from .serializers import BeritaSerializer, CommentSerializer

class BeritaListCreate(generics.ListCreateAPIView):
    queryset = Berita.objects.filter(is_published=True)
    serializer_class = BeritaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(penulis=self.request.user)

class BeritaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Berita.objects.all()
    serializer_class = BeritaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'id'

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def react_to_news(request, id):
    berita = get_object_or_404(Berita, id=id)
    reaction_type = request.data.get('reaction_type')
    
    if not reaction_type:
        return Response({'error': 'Reaction type is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    reaction, created = NewsReaction.objects.update_or_create(
        berita=berita,
        user=request.user,
        defaults={'reaction_type': reaction_type}
    )
    
    return Response({'status': 'success', 'created': created})
