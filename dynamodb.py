from typing import Literal, Tuple, Any
import json
import boto3


class DynamoDB:
    TableName = Literal['user', 'iotDevice', 'iotDeviceProducts', 'product']

    def __init__(
        self,
        region='us-east-2',
        lambda_name='DA_DynamoDB_Read',
        invocation_type='RequestResponse',
    ):
        self.client = boto3.client('lambda', region_name=region)
        self.lambda_name = lambda_name
        self.invocation_type = invocation_type

    def invoke_lambda(
        self, table: TableName, key_name: str, key_value: Any
    ) -> Tuple[bool, Any]:
        payload = {'table': table, 'key_name': key_name, 'key_value': key_value}

        lambda_response = self.client.invoke(
            FunctionName=self.lambda_name,
            InvocationType=self.invocation_type,
            Payload=json.dumps(payload),
        )

        resp_str = lambda_response['Payload'].read()
        resp = json.loads(resp_str)

        return resp[0], resp[1]

    # Método reutilizable para obtener datos de cualquier tabla.
    # ya que tods tienen la misma estructura.
    def get_data(
        self, table: TableName, key_name: str, key_value: Any
    ) -> Tuple[bool, Any]:
        return self.invoke_lambda(table, key_name, key_value)

    # Métodos específicos para obtener datos de tablas predeterminadas.
    def get_user(self, id: str) -> Tuple[bool, Any]:
        return self.get_data('user', 'id', id)

    def get_iot_device(self, id: str) -> Tuple[bool, Any]:
        return self.get_data('iotDevice', 'id', id)

    def get_iot_device_products(self, deviceId: str) -> Tuple[bool, Any]:
        return self.get_data('iotDeviceProducts', 'deviceId', deviceId)

    def get_product(self, id: str) -> Tuple[bool, Any]:
        return self.get_data('product', 'id', id)
