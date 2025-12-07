from rest_framework import serializers
from .models import Berita, KategoriBerita, Comment, NewsReaction

class KategoriBeritaSerializer(serializers.ModelSerializer):
    class Meta:
        model = KategoriBerita
        fields = ['id', 'nama']

class BeritaSerializer(serializers.ModelSerializer):
    kategori = KategoriBeritaSerializer(read_only=True)
    penulis = serializers.ReadOnlyField(source='penulis.username')
    kategori_nama = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Berita
        fields = [
            'id', 'judul', 'konten', 'kategori', 'kategori_nama',
            'thumbnail', 'views', 'penulis', 'sumber', 
            'is_published', 'tanggal_dibuat', 'tanggal_diperbarui',
            'reaction_summary'
        ]
        read_only_fields = ['id', 'views', 'tanggal_dibuat', 'tanggal_diperbarui', 'reaction_summary']

    def create(self, validated_data):
        kategori_nama = validated_data.pop('kategori_nama', None)
        if kategori_nama:
            kategori, _ = KategoriBerita.objects.get_or_create(nama=kategori_nama)
            validated_data['kategori'] = kategori
        return super().create(validated_data)

    def update(self, instance, validated_data):
        kategori_nama = validated_data.pop('kategori_nama', None)
        if kategori_nama:
            kategori, _ = KategoriBerita.objects.get_or_create(nama=kategori_nama)
            instance.kategori = kategori
        return super().update(instance, validated_data)

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'berita', 'user', 'parent', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']
