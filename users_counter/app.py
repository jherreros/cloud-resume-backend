import json
import time
import boto3
import decimal

# This is a workaround for: http://bugs.python.org/issue16535
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

myHeaders =  {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
            }

dynamodb = boto3.resource('dynamodb')

def getCount(event, context):

    userId = event['pathParameters']['userId']
    table = dynamodb.Table('usersTable')
    timestamp = str(time.time())
    
    userRecord = table.get_item( Key={ 'userId': userId } )

    if 'Item' in userRecord:
        result = table.update_item(
            Key={
                'userId': userId
            },
            ExpressionAttributeValues={
            ':timestamp': timestamp,
            ':one': 1,
            },
            UpdateExpression="SET userCount = userCount + :one,\
                            updatedAt = :timestamp",
            ReturnValues='ALL_NEW',
        )

        response = {
            "statusCode": 200,
            'headers': myHeaders,
            "body": json.dumps(result['Attributes'],
                                cls=DecimalEncoder)
        }

    else:
        item = {
            'userId': userId,
            'createdAt': timestamp,
            'userCount': 1,
        }

        table.put_item(Item=item)

        response = {
            "statusCode": 200,
            'headers': myHeaders,
            "body": json.dumps(item)
        }

    return response
