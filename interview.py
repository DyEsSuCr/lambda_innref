import json
import boto3

"""
#########################
# Roles table           #
#########################
# Id    # Name          #
#########################
# 0     # ADMIN         #
# 1     # CLIENT        #
# 2     # TECHNICIAN    #
# 3     # REPLENISHER   #
#########################
"""


# Función que obtiene los datos de un usuario desde DynamoDB
def get_user_on_dynamoDB(id):
    # Se llama a AWS Lambda para acceder a la base de datos DynamoDB
    invokeLambda = boto3.client('lambda', region_name='us-east-2')

    # Invoca la función Lambda que consulta DynamoDB para el usuario con el ID proporcionado
    lambda_response = invokeLambda.invoke(
        FunctionName='DA_DynamoDB_Read',
        InvocationType='RequestResponse',
        Payload=json.dumps({'table': 'user', 'key_name': 'id', 'key_value': id}),
    )

    # Se lee la respuesta de Lambda y se convierte en un objeto JSON
    resp_str = lambda_response['Payload'].read()
    resp = json.loads(resp_str)

    # Devuelve dos elementos: el estado y los datos del usuario
    return resp[0], resp[1]


# Función que obtiene los datos de un dispositivo IoT desde DynamoDB
def get_iot_device_on_dynamoDB(id):
    invokeLambda = boto3.client('lambda', region_name='us-east-2')
    lambda_response = invokeLambda.invoke(
        FunctionName='DA_DynamoDB_Read',
        InvocationType='RequestResponse',
        Payload=json.dumps({'table': 'iotDevice', 'key_name': 'id', 'key_value': id}),
    )
    resp_str = lambda_response['Payload'].read()
    resp = json.loads(resp_str)
    return resp[0], resp[1]


# Error: Esta función está repetida en el código. El nombre y la lógica son exactamente los mismos que el de la función anterior
# Se debería eliminar esta duplicación

# def get_iot_device_on_dynamoDB(id):
#     invokeLambda = boto3.client("lambda", region_name="us-east-2")
#     lambda_response = invokeLambda.invoke(
#         FunctionName="DA_DynamoDB_Read",
#         InvocationType="RequestResponse",
#         Payload=json.dumps({"table": "iotDevice", "key_name": "id", "key_value": id}),
#     )
#     resp_str = lambda_response["Payload"].read()
#     resp = json.loads(resp_str)
#     return resp[0], resp[1]


# Función que obtiene los productos asociados a un dispositivo IoT desde DynamoDB
def get_iot_device_products_on_dynamoDB(deviceId):
    invokeLambda = boto3.client('lambda', region_name='us-east-2')
    lambda_response = invokeLambda.invoke(
        FunctionName='DA_DynamoDB_Read',
        InvocationType='RequestResponse',
        Payload=json.dumps(
            {
                'table': 'iotDeviceProducts',
                'key_name': 'deviceId',
                'key_value': deviceId,
            }
        ),
    )
    resp_str = lambda_response['Payload'].read()
    resp = json.loads(resp_str)
    return resp[0], resp[1]


# Función que obtiene un producto desde DynamoDB
def get_product_on_dynamoDB(id):
    invokeLambda = boto3.client('lambda', region_name='us-east-2')
    lambda_response = invokeLambda.invoke(
        FunctionName='DA_DynamoDB_Read',
        InvocationType='RequestResponse',
        Payload=json.dumps({'table': 'product', 'key_name': 'id', 'key_value': id}),
    )
    resp_str = lambda_response['Payload'].read()
    resp = json.loads(resp_str)
    return resp[0], resp[1]


# Función principal Lambda que maneja la lógica de negocio
def lambda_handler(event, context):
    # Se obtiene el usuario a partir de su ID
    flag, user_entity = get_user_on_dynamoDB(event['userId'])

    # Verificamos que el usuario exista y si tiene los roles necesarios
    if flag and user_entity:
        flag = False
        for role in user_entity['roles']:
            # Si el usuario tiene los roles de CLIENT o REPLENISHER, se permite el acceso
            if role == 1 or role == 3:
                flag = True

        # Si el usuario tiene uno de los roles requeridos
        if flag:
            # Se obtiene el dispositivo IoT a partir de su ID
            flag_device, device = get_iot_device_on_dynamoDB(event['deviceId'])

            # Si el dispositivo IoT existe, obtenemos los productos asociados
            if flag_device and device:
                flag_device_products, device_products = (
                    get_iot_device_products_on_dynamoDB(event['deviceId'])
                )

                # Si existen productos asociados al dispositivo
                if flag_device_products and device_products:
                    products = []

                    # Obtenemos la información de cada producto asociado al dispositivo
                    for i in range(len(device_products)):
                        flagProduct, product = get_product_on_dynamoDB(
                            device_products[i]['productId']
                        )

                        # Si el producto existe, lo agregamos a la lista
                        if flagProduct and product:
                            products.append(product)
                        else:
                            # Si no se puede obtener el producto, retornamos error
                            return {
                                'statusCode': 500,
                                'body': {'msg': 'Unable to get whole products'},
                            }

                    # Se actualiza la lista de productos con la cantidad de cada uno
                    for i in range(len(products)):
                        product = products[i]
                        for j in range(len(device_products)):
                            if device_products[j]['productId'] == product['id']:
                                product['amount'] = device_products[j]['amount']
                        products[i] = product

                    # Se crea una lista con el ancho de cada producto
                    products_width = []
                    for i in range(len(products)):
                        # products_width[i] = products[i]["width"] # Error: debe usarse append() en lugar de la asignación directa
                        products_width.append(products[i]['width'])

                    # Se retorna la respuesta con los productos y sus anchos
                    return {
                        'statusCode': 200,
                        'body': {
                            # "products": list_products,  # Error: Se hace referencia a "list_products" que no existe. Debe ser "products"
                            'products': products,
                            'widths': products_width,
                        },
                    }
                else:
                    return {
                        'statusCode': 500,
                        'body': {'msg': 'Unable to get device products'},
                    }
            else:
                return {'statusCode': 500, 'body': {'msg': 'Unable to get device'}}

        # Si el usuario no tiene acceso autorizado
        if not flag:
            return {'statusCode': 500, 'body': {'msg': 'Unauthorized access'}}
    else:
        # Si no se puede recuperar el usuario desde DynamoDB
        return {'statusCode': 500, 'body': {'msg': 'Unable to retrieve user'}}

    # Error: Esta línea nunca se ejecutará debido a los retornos previos
    return {'statusCode': 500, 'body': {'msg': 'Unable to retrieve user'}}
