FROM python:3.9

WORKDIR /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Make ports available to the world outside this container
EXPOSE 80
EXPOSE 5678

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "helloworld.py"]