# api_profile/serializers.py
from rest_framework import serializers
from .models import Profile, Skill, Career, Link


class SkillSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(
        source='get_category_display', read_only=True
    )

    class Meta:
        model  = Skill
        fields = [
            'id', 'category', 'category_label',
            'name', 'level', 'description', 'order',
        ]


class CareerSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Career
        fields = [
            'id', 'company', 'title', 'description',
            'start_date', 'end_date', 'is_current', 'order',
        ]


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Link
        fields = ['id', 'platform', 'url', 'label', 'order']


class ProfileSerializer(serializers.ModelSerializer):
    skills   = SkillSerializer(many=True, read_only=True)
    careers  = CareerSerializer(many=True, read_only=True)
    links    = LinkSerializer(many=True, read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = Profile
        fields = [
            'id', 'name', 'nickname', 'location', 'bio',
            'avatar_url', 'skills', 'careers', 'links',
            'updated_at',
        ]

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None
