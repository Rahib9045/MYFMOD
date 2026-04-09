FROM node:20-alpine

WORKDIR /app

# Copy package files first for caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend source
COPY . .

EXPOSE 3000

# Use dev server for easy demo (no build step needed)
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
