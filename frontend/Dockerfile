# Use official Node.js lightweight image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the app explicitly
RUN npm run build

# Install a simple static server
RUN npm install -g serve

# Expose port 80
EXPOSE 80

# Serve the static files on port 80
CMD ["serve", "-s", "dist", "-l", "80"]
