from rest_framework import mixins
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import GenericAPIView


class Item_Dashboard(GenericAPIView, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    pagination_class = LimitOffsetPagination

    def get(self, request):
        cache_key = "items_" + request.GET.urlencode()
        print(cache_key)

        if cache.get(cache_key):  # Cache hit
            print("from cache")
            return Response(cache.get(cache_key))

        # Cache miss

        name = request.GET.get("name", None)
        SKU = request.GET.get("SKU", None)
        category = request.GET.get("category", None)
        stock_status = request.GET.get("stock_status", None)
        tags = request.GET.getlist("tags", [])
        if name:
            self.queryset = self.queryset.filter(name__icontains=name)
        if SKU:
            self.queryset = self.queryset.filter(SKU__icontains=SKU)
        if category:
            self.queryset = self.queryset.filter(category__icontains=category)
        if stock_status:
            self.queryset = self.queryset.filter(stock_status__icontains=stock_status)
        if len(tags) > 0:
            self.queryset = self.queryset.filter(
                tags__name__iregex=r"(" + "|".join(tags) + ")"
            )

        # Paginate the queryset
        self.queryset = self.paginate_queryset(self.queryset)
        serializer = ItemSerializer(self.queryset, many=True)

        # Cache the response
        cached_data = self.get_paginated_response(serializer.data).data
        cache.set(cache_key, cached_data)
        return self.get_paginated_response(serializer.data)


# Invalidate cache on item change
@receiver(post_save, sender=Item)
@receiver(post_delete, sender=Item)
def invalidate_cache_on_item_change(sender, instance, **kwargs):
    print("clear")
    #  Invalidate all cached items
    cache.delete_many(keys=cache.keys("items_*"))
