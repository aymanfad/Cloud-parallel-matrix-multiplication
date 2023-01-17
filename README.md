# Parallel matrix multiplication



## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Boto3.

```bash
pip install boto3
```
Install the python library Paramiko to connect to SSH servers and use SFTP to transfer files, as well as execute commands on our EC2 instances. 
```bash
pip install paramiko
```
```python
ssh = paramiko.SSHClient() 
    print('calling paramiko')
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.connect(hostname=public_ip,username='ec2-user', pkey=private_key)

    print(private_key)
    print('trying to connect')

    sftp = ssh.open_sftp()
    sftp.put('worker.py', 'worker.py')
    sftp.close()
```
