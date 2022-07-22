# Set base image (host OS)
FROM python:3.10.4

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .
COPY surestart-key.json .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY flask_app.py .

# Specify the command to run on container start
CMD [ "python", "./flask_app.py" ]