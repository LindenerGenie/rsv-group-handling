# Use node:14 as the base image for the build stage
FROM node:14 AS build-stage
WORKDIR /app
# Copy package.json and package-lock.json
COPY package*.json ./
# Install dependencies including bootstrap, xlsx, and express
RUN npm install && npm install bootstrap xlsx express
# Copy the rest of the application code
COPY . .
# Build the application
RUN npm run build

# Use python:3.9-slim for the runtime stage
FROM python:3.9-slim
WORKDIR /app
# Copy the built application from the build stage
COPY --from=build-stage /app/dist /app/dist
# Copy the Python requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the main Python application file
COPY app.py .
# Expose port 5000 for the application
EXPOSE 5000
# Command to run the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
