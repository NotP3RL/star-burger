import datetime

from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum


from .models import Product, Order, OrderItem
from .serializer import OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validate_international_phonenumber(serializer.validated_data['phonenumber'])
        offset = datetime.timedelta(hours=-8)
        timezone = datetime.timezone(offset, name='UTC')
        order_time = datetime.datetime.now(tz=timezone)
        Order.objects.create(
            firstname=serializer.validated_data['firstname'],
            lastname=serializer.validated_data['lastname'],
            phonenumber=serializer.validated_data['phonenumber'],
            address=serializer.validated_data['address'],
            time=order_time
        )
        order = Order.objects.get(time=order_time)
        for product_data in request.data['products']:
            product_id = product_data['product']
            product = Product.objects.get(id=product_id)
            price = product.price * product_data['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=product_data['quantity'],
                price=price
            )
        return Response(serializer.data)
    except ValueError:
        return JsonResponse({
            'error': 'ValueError',
        })
