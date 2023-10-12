from django.http import JsonResponse
from django.templatetags.static import static
import json


from .models import Product, Order, OrderItem


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


def register_order(request):
    # TODO это лишь заглушка
    try:
        data = json.loads(request.body.decode())
        Order.objects.create(
            firstname=data['firstname'],
            lastname=data['lastname'],
            phonenumber=data['phonenumber'],
            address=data['address']
        )
        order = Order.objects.get(firstname=data['firstname'])
        for product_data in data['products']:
            product_id = product_data['product'] - 1
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=product_data['quantity']
            )
        print(data)
        return JsonResponse({})
    except ValueError:
        return JsonResponse({
            'error': 'bla bla bla',
        })
