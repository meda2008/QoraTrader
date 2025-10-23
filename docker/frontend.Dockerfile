# Use an official Node runtime as a parent image
FROM node:18-alpine

# Set environment variables
ENV NODE_ENV=production

# Set work directory
WORKDIR /app

# Copy package.json first to leverage Docker cache
COPY ./frontend/package.json /app/package.json
COPY ./frontend/package-lock.json /app/package-lock.json

# Install node dependencies
RUN npm ci --only=production

# Copy project
COPY ./frontend /app

# Build the application
RUN npm run build

# Install a simple server to serve the static files
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Run the application
CMD ["serve", "-s", "build", "-l", "3000"]