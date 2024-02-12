from items_dashboard.views import invalidate_cache_on_item_change
from items_dashboard.models import Item
from django.core.cache import cache


import pytest

pytestmark = pytest.mark.django_db


# Returns a 403 unauthorized when user is not authenticated
def test_returns_403_unauthorized_when_user_not_authenticated(client):

    response = client.get("/items/")

    assert response.status_code == 403


def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client


# Returns a list of all items when no query parameters are provided
def test_returns_all_items_when_no_query_parameters(admin_client):
    response = admin_client.get("/items/")

    assert response.status_code == 200
    assert len(response.data["results"]) == Item.objects.count()


def test_cache_miss(admin_client):
    cache_key = "items_name=test_cache_miss"
    assert cache.has_key(cache_key) == False

    response = admin_client.get("/items/", data={"name": "test_cache_miss"})

    # Cache the response
    assert response.status_code == 200
    assert cache.has_key(cache_key) == True
    cache.delete(cache_key)


def test_invalidate_cache_on_item_change_save():
    # Create a new Item
    item = Item.objects.create(
        name="Test Item",
        category="Test Category",
        stock_status="In Stock",
        available_stock=10,
    )

    # Call the function to invalidate cache on item save
    invalidate_cache_on_item_change(sender=Item, instance=item)

    # Assert that the cache for all items is invalidated
    assert cache.keys("items_*") == []


def test_invalidate_cache_on_item_change_delete():
    # Create a new Item
    item = Item.objects.create(
        name="Test Item",
        category="Test Category",
        stock_status="In Stock",
        available_stock=10,
    )

    # Call the function to invalidate cache on item delete
    invalidate_cache_on_item_change(sender=Item, instance=item)

    # Assert that the cache for all items is invalidated
    assert cache.keys("items_*") == []


# Filters items by name when 'name' query parameter is provided
def test_filters_items_by_name_when_name_query_parameter_provided(admin_client):
    name = "item_test"
    response = admin_client.get("/items/", {"name": name})

    assert response.status_code == 200
    assert all(
        item["name"].lower().find(name.lower()) != -1
        for item in response.data["results"]
    )


# Filters items by SKU when 'SKU' query parameter is provided
def test_filters_items_by_SKU_when_SKU_query_parameter_provided(admin_client):
    SKU = "test_SKU"
    response = admin_client.get("/items/", {"SKU": SKU})
    print(response.data, "here")

    assert response.status_code == 200
    assert all(
        item["SKU"].lower().find(SKU.lower()) != -1 for item in response.data["results"]
    )


# Returns empty list when no items match query parameters
def test_returns_empty_list_when_no_items_match_query_parameters(admin_client):
    name = "item_test_not_in_database"
    response = admin_client.get("/items/", {"name": name})

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


# Filters items case insensitively when 'name' query parameter is provided
def test_filters_items_case_insensitively_when_name_query_parameter_provided(
    admin_client,
):
    name = "ITEM_TEST"
    response = admin_client.get("/items/", {"name": name})

    assert response.status_code == 200
    assert all(
        item["name"].lower().find(name.lower()) != -1
        for item in response.data["results"]
    )


# Filters items case insensitively when 'category' query parameter is provided
def test_filters_items_case_insensitively_when_category_query_parameter_provided(
    admin_client,
):
    category = "CATEGORY_TEST"
    response = admin_client.get("/items/", {"category": category})

    assert response.status_code == 200
    assert all(
        item["category"].lower().find(category.lower()) != -1
        for item in response.data["results"]
    )


def test_filters_items_by_stock_status_when_stock_status_query_parameter_provided(
    admin_client,
):
    stock_status = "test_stock_status"
    response = admin_client.get("/items/", {"stock_status": stock_status})

    assert response.status_code == 200
    assert all(
        item["stock_status"].lower().find(stock_status.lower()) != -1
        for item in response.data["results"]
    )


def test_filters_items_by_tags_when_tags_query_parameter_provided(admin_client):
    # Arrange
    tags = ["test_tag1", "test_tag2"]
    response = admin_client.get("/items/", {"tags": tags})

    # Assert
    assert response.status_code == 200
    assert all(
        any(tag.lower() in item["tags"] for tag in tags)
        for item in response.data["results"]
    )
