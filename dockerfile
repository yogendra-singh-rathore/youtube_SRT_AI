FROM python:3.9-slim
WORKDIR /app
COPY . /app
# Upgrade pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Install ImageMagick
RUN apt-get update && apt-get install -y imagemagick
# Update ImageMagick policy for PNG32
RUN sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<policy domain="path" rights="read|write" pattern="@\*"/' /etc/ImageMagick-6/policy.xml

EXPOSE 3000
CMD python ./main.py 


# Command to Build Your Own Docker

# Create Image
# 1) docker build -t <Your Docker Name>/flsk-srt-genai:0.1.RELEASE .

# Test Your Docker Image Before Publish
# 2) docker container run -d -p 3000:3000 <Your Docker Name>/flsk-srt-genai:0.1.RELEASE

# To Stop or Close Docker
# 3) docker container ls
# docker container stop xxxx #fist 4 leter of container ID

# Publish Your Docker Image
# 4) docker push <Your Docker Name>/flsk-srt-genai:0.1.RELEASE