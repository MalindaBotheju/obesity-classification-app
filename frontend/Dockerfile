# Use the lightweight Nginx image
FROM nginx:alpine

# Copy your frontend files to Nginx's default public folder
COPY . /usr/share/nginx/html

# Expose port 80 (the default port for web traffic)
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]