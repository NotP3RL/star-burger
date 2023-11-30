import datetime

from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

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


def check_str_keys(order_info):
    not_presented_str_keys = []
    empty_str_keys = []
    not_str_keys = []
    supposed_str_keys = ['firstname', 'lastname', 'phonenumber', 'address']
    for supposed_str_key in supposed_str_keys:
        if not supposed_str_key in order_info:
            not_presented_str_keys.append(supposed_str_key)
        elif not order_info[supposed_str_key]:
            empty_str_keys.append(supposed_str_key)
        elif not isinstance(order_info[supposed_str_key], str):
            not_str_keys.append(supposed_str_key)
    return not_presented_str_keys, empty_str_keys, not_str_keys


@api_view(['POST'])
def register_order(request):
    try:
        order_info = request.data
        checked_str_keys = check_str_keys(order_info)

        if checked_str_keys[0]:
            content = {'error': f'{", ".join(checked_str_keys[0])} keys not present'}
            return Response(content, status=status.HTTP_200_OK)
        elif checked_str_keys[1]:
            content = {'error': f'{", ".join(checked_str_keys[1])} keys cannot be null'}
            return Response(content, status=status.HTTP_200_OK)
        elif checked_str_keys[2]:
            content = {'error': f'{", ".join(checked_str_keys[2])} keys are not string'}
            return Response(content, status=status.HTTP_200_OK)
        elif not 'products' in order_info:
            content = {'error': 'products key not present'}
            return Response(content, status=status.HTTP_200_OK)
        elif not order_info['products']:
            content = {'error': 'products key cannot be null'}
            return Response(content, status=status.HTTP_200_OK)
        elif not isinstance(order_info['products'], list):
            content = {'error': 'products key is not list'}
            return Response(content, status=status.HTTP_200_OK)
        else:
            validate_international_phonenumber(order_info['phonenumber'])
            offset = datetime.timedelta(hours=-8)
            timezone = datetime.timezone(offset, name='UTC')
            order_time = datetime.datetime.now(tz=timezone)
            Order.objects.create(
                firstname=order_info['firstname'],
                lastname=order_info['lastname'],
                phonenumber=order_info['phonenumber'],
                address=order_info['address'],
                time=order_time
            )
            order = Order.objects.get(time=order_time)
            for product_data in order_info['products']:
                product_id = product_data['product']
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=product_data['quantity']
                )
            return JsonResponse({})
    except ValueError:
        return JsonResponse({
            'error': 'ValueError',
        })
    except ObjectDoesNotExist:
        content = {'error': 'products id does not exist'}
        return Response(content, status=status.HTTP_200_OK)
    except ValidationError:
        content = {'error': 'phonenumber is not correct'}
        return Response(content, status=status.HTTP_200_OK)

