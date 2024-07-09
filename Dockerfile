FROM node:14 as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
RUN npm install bootstrap
COPY . .
RUN npm run build

FROM python:3.9-slim
WORKDIR /app
COPY --from=build-stage /app/dist /app/dist
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
