import boto3
import urllib.parse
import os
import json

def handler(event, context):

    # リクエストが正当か確認する
    verification_token = os.environ['VERIFICATION_TOKEN']
    body = map_to_dict(event["body"])
    print(event)
    print(body.keys())

    if body.get("token", "") != verification_token:
        print("token is invalid")

        return {
            'statusCode': 200,
            'body': "",
            'isBase64Encoded': False
        }

    command = body.get("command", "")
    # スラッシュコマンド「/today」だったらlambdaを呼ぶ
    try:
        if command == '/today':
            client = boto3.client('lambda')
            response = client.invoke(
                FunctionName=os.environ['MAIN_FUNCTION_ARN'],
                InvocationType='Event',
                Payload=json.dumps(body)
            )
            print(response)
        elif command == '/summary':
            client = boto3.client('lambda')
            response = client.invoke(
                FunctionName=os.environ['MAIN_FUNCTION_ARN'],
                InvocationType='Event',
                Payload=json.dumps(body)
            )
            print(response)
    except:
        import traceback
        print("[Error]")
        traceback.print_exc()

    return {
        'statusCode': 200,
        'body': "",
        'isBase64Encoded': False
    }

# スラッシュコマンドのbodyをurldecodeして辞書にする
def map_to_dict(data):
    param = {}

    for item in data.split('&'):
        key, value = item.split('=')
        param[key] = urllib.parse.unquote(value)

    return param
