# Deploying a Flask Application to AWS Lambda using Docker and Amazon ECR

## Prerequisites
- AWS CLI installed and configured
- Docker installed
- AWS Lambda and API Gateway set up
- AWS IAM Role with necessary permissions
- Amazon Elastic Container Registry (ECR) set up

## Step 1: Login to AWS CLI
Before proceeding, authenticate Docker with AWS ECR:

```sh
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <Amazon ID>.dkr.ecr.us-east-2.amazonaws.com
```

## Step 2: Create a `Dockerfile`
Create a `Dockerfile` in the root of your project:

```dockerfile
FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

CMD ["app.lambda_handler"]
```

## Step 3: Define the Lambda Function in `app.py`
Ensure that your `app.py` file includes a Lambda handler function:

```python
import json

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from AWS Lambda!')
    }
```

## Step 4: Build and Test Locally
Run the following command to build the Docker image:

```sh
docker build --platform linux/amd64 --no-cache --rm --tag resume-ready-container .
```

Save and reload the image:

```sh
docker save -o resume-ready-container.tar resume-ready-container

docker load -i resume-ready-container.tar
```

## Step 5: Tag and Push the Image to Amazon ECR
1. Tag the Docker image:

```sh
docker tag <RepoName>:latest <Amazon ID>.dkr.ecr.us-east-2.amazonaws.com/<RepoName>:latest
```

2. Push the image to ECR:

```sh
docker push <Amazon ID>.dkr.ecr.us-east-2.amazonaws.com/<RepoName>:latest
```

## Step 6: Deploy to AWS Lambda
1. Deploy the image from Amazon ECR to AWS Lambda through the AWS Management Console.
2. Navigate to AWS Lambda, create a new function, and choose "Container image" as the deployment package.
3. Select the image from Amazon ECR and configure the necessary permissions.
4. Save and deploy the function.

## Step 7: Set Up API Gateway
1. Create an API Gateway using REST API.
2. Configure a proxy integration with AWS Lambda.
3. Deploy the API and note the generated endpoint.
4. Test the API using Postman or `curl`:

```sh
curl -X GET <your-api-gateway-url>
```

## Conclusion
Your Flask application is now successfully deployed on AWS Lambda using Docker, Amazon ECR, and API Gateway!

