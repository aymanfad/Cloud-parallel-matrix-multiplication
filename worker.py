import boto3
import numpy as np
import json
import time

session = boto3.Session(
aws_access_key_id='',
aws_secret_access_key='',
aws_session_token='',
region_name='us-east-1')
sqs = session.resource('sqs')

#recieve queue

sqs_client = session.client('sqs')
queue = sqs.get_queue_by_name(QueueName='summa-queue')
queue_url = queue.url


# Return queue: 
return_queue = sqs.get_queue_by_name(QueueName='summa-send')
return_queue_url = return_queue.url




while True:
    # Receive a message from the queue
    message = sqs_client.receive_message(QueueUrl=queue_url)
    messages = message.get('Messages', [])
    if not messages:
        break
    

  
    receipt_handle = message.get('Messages',[{}])[0].get('ReceiptHandle',None)

    parts = message.get('Messages',[{}])[0].get('Body',None)
    part = parts.split(',,')
    
    sqs_client.delete_message(QueueUrl=queue_url,ReceiptHandle=receipt_handle)   
    A = np.array(json.loads(part[1]))
    B = np.array(json.loads(part[2]))
    C = np.matmul(A, B)
    C_str = json.dumps(C.tolist())
    message2 = part[0] + ',,' + C_str
    print('message2',message2)
        
    
    

    # Sending result sub_matrix C to the return queue
    sqs_client.send_message(QueueUrl=return_queue_url, MessageBody=message2)
    
   

