from dynamodb import DynamoDB
from error_handler import (
    UnauthorizedAccessError,
    NotFoundError,
    handle_error,
)


def lambda_handler(event, context):
    dynamo = DynamoDB(region='us-east-2')

    try:
        flag, user_entity = dynamo.get_data('user', 'id', event['userId'])
        if not (flag and user_entity):
            raise NotFoundError('user')

        if not any(role in user_entity['roles'] for role in [1, 3]):
            raise UnauthorizedAccessError()

        flag_device, device = dynamo.get_data('iotDevice', 'id', event['deviceId'])
        if not (flag_device and device):
            raise NotFoundError('iotDevice')

        flag_device_products, device_products = dynamo.get_data(
            'iotDeviceProducts', 'deviceId', event['deviceId']
        )
        if not (flag_device_products and device_products):
            raise NotFoundError('iotDeviceProducts')

        products = []
        for device_product in device_products:
            flag_product, product = dynamo.get_data(
                'product', 'id', device_product['productId']
            )
            if not (flag_product and product):
                raise NotFoundError('product')

            product['amount'] = device_product['amount']
            products.append(product)

        products_width = [product['width'] for product in products]

        return {
            'statusCode': 200,
            'body': {
                'products': products,
                'widths': products_width,
            },
        }

    except Exception as e:
        return handle_error(e)
