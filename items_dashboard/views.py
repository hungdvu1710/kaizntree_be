from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_items(request):
    name = request.GET.get("name", None)
    SKU = request.GET.get("SKU", None)
    category = request.GET.get("category", None)
    stock_status = request.GET.get("stock_status", None)
    tags = request.GET.getlist("tags", [])
    items = Item.objects.all()
    if name:
        items = items.filter(name__icontains=name)
    if SKU:
        items = items.filter(SKU__icontains=SKU)
    if category:
        items = items.filter(category__icontains=category)
    if stock_status:
        items = items.filter(stock_status__icontains=stock_status)
    if len(tags) > 0:
        items = items.filter(tags__name__iregex=r"(" + "|".join(tags) + ")")
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)
