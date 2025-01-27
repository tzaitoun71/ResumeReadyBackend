# Use the AWS Lambda Python 3.10 base image
FROM public.ecr.aws/lambda/python:3.10

# Copy only requirements.txt first (for caching)
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN pip install -r requirements.txt

# Copy the entire project
COPY . .

# Lambda requires a handler function, assuming Flask app
CMD ["app.lambda_handler"]
