from rest_framework import serializers
from retail.models import *


# Serializers define the API representation.
class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'price')


# Serializers define the API representation.
class ProviderSerializer(serializers.HyperlinkedModelSerializer):
    days_since_joined = serializers.SerializerMethodField()

    # 方法写法：get_ + 字段
    def get_days_since_joined(self, obj):
        return [1111,22,33,11]

    class Meta:
        model = Provider
        fields = ('name', 'gender', 'telephone','days_since_joined')


class RepositorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Repository
        fields = ('name', 'location')


class InLogSerializer(serializers.ModelSerializer):
    # repository = RepositorySerializer()

    class Meta:
        model = InLog
        fields = "__all__"
        depth = 1


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = "__all__"
        depth = 1


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"
        depth = 1
