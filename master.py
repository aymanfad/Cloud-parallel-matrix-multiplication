import boto3
import paramiko
import json
import numpy as np
import concurrent.futures
import time



ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='summa-queue')
queue_url = queue.url
sqs_client = boto3.client('sqs')


return_queue = sqs.get_queue_by_name(QueueName='summa-send')
return_queue_url = return_queue.url

def create_instance(groupid):
    print("creating EC2 instance")

    instance = ec2_resource.create_instances(
        ImageId="ami-0b5eea76982371e91",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="new-key1",
        SecurityGroupIds=[groupid]
    )
    return instance



def instance_ip(instance):
    instance[0].wait_until_running()
    instance[0].reload()
    public_ip = instance[0].public_ip_address
    print(public_ip)
    return public_ip

response = ec2_client.describe_security_groups(GroupIds=['sg-020b7d01c04e358d0'])
security_group = response['SecurityGroups'][0]
groupid = security_group["GroupId"]
print(groupid)

print("creating multiple EC2 instances")

public_ips = []
for i in range(4):
    instance = create_instance(groupid)
    
    print(instance)

    print('describing EC2 instance')
    
    instance_id=ec2_client.describe_instances()['Reservations'][0]['Instances'][0]['InstanceId']
    print(instance_id)

    instance[0].wait_until_running()

    instance[0].reload()

    public_ip_i = instance[0].public_ip_address

    print(f'The public IP of the instance is {public_ip_i}')

    public_ips.append(public_ip_i)

print(public_ips)



command = [
    "sudo pip3 install boto3",
    "sudo pip3 install numpy",
    "sudo python3 worker.py"
    ]

def paramiko_run(public_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    f = open('new-key1.pem', 'r')
    private_key = paramiko.RSAKey.from_private_key(f)

    ssh = paramiko.SSHClient() 
    print('calling paramiko')
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 

    ssh.connect(hostname=public_ip,username='ec2-user', pkey=private_key)
    print(private_key)
    print('trying to connect')
    sftp = ssh.open_sftp()
    sftp.put('worker.py', 'worker.py')
    sftp.close()

    for cmd in command:
        print("running command: {}".format(cmd))
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read())
        print(public_ip)
    ssh.close()

# Use the concurrent.futures.ThreadPoolExecutor to run the function on multiple instances
with concurrent.futures.ThreadPoolExecutor() as executor:

    matrix_a = np.random.randint(10, size=(1000, 1000))
    matrix_b = np.random.randint(10, size=(1000, 1000))

    matrix_a_split = np.split(matrix_a, 5)
    matrix_b_split = np.hsplit(matrix_b, 5)
    time_1 = time.time()
    matrix_c = np.matmul(matrix_a, matrix_b)
    print("Execution time : ", (time.time() - time_1))
    print('--------')
    for i in range(5):
        for j in range(5):
            a = json.dumps(matrix_a_split[i].tolist())
            b = json.dumps(matrix_b_split[j].tolist())
            message  = str((i, j)) + ',,' + a + ',,' + b
            sqs_client.send_message(QueueUrl=queue_url, MessageBody=message)
    results = list(executor.map(paramiko_run,public_ips))

            
            

            
messages2=[]
while True:
    # Receive a message from the queue
    message = sqs_client.receive_message(QueueUrl=return_queue_url)
    messages = message.get('Messages', [])
    if not messages:
        break
    receipt_handle2 = message.get('Messages',[{}])[0].get('ReceiptHandle')
    
    
    parts = message.get('Messages',[{}])[0].get('Body',None)
    part = parts.split(',,')
    print('parts ',part)
    sqs_client.delete_message(QueueUrl=return_queue_url,ReceiptHandle=receipt_handle2)
    messages22 = [(part[0]) , json.loads(part[1])] 
    print('parts 0', part[0])
    messages2 = messages2 + [messages22] 

print(messages2)
Y = []
X = []
for i in range(5):
    for j in range(5):
        for m in range(len(messages2)):
            if messages2[m][0] == str((i, j)):

                Y = Y + [messages2[m][1]]
    X = X + [np.concatenate(Y, axis=1)]
    Y = []
result = np.concatenate(X, axis=0)

#compares the result of the parallel multiplication with the normal multiplication
print((result == matrix_c).all())
sqs_client.delete_message(QueueUrl=return_queue_url,ReceiptHandle=receipt_handle2)

    