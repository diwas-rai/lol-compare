# --- Stage 1: Build the React app with Bun ---
FROM oven/bun:latest as build

WORKDIR /app

# Copy dependency files
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy the rest of the frontend source code
COPY . .

# Run the production build
RUN bun run build


# --- Stage 2: Serve the static files with Nginx ---
FROM nginx:1.29-alpine

# Remove the default Nginx config
RUN rm /etc/nginx/nginx.conf

# Copy our custom Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the built React app from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 (which Nginx listens on)
EXPOSE 80