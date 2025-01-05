# Stage 1: Build the Angular app
FROM node:20-alpine AS build
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the application code and build the app
COPY . ./
RUN npm run build -- --configuration=production --base-href=/chat/

# Stage 2: Serve the app with NGINX
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/chatbot /usr/share/nginx/html

EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]