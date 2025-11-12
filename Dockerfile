# Stage 1: Build
FROM node:20-alpine AS builder

# Install Yarn globally
RUN corepack enable && corepack prepare yarn@1.22.22 --activate

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install all dependencies (including devDependencies for build)
# Skip scripts to prevent prepare hook from running before source is copied
RUN yarn install --frozen-lockfile --ignore-scripts

# Copy source code
COPY . .

# Build the application (compile TypeScript + copy static assets)
RUN yarn build

# Stage 2: Production
FROM node:20-alpine

# Install Yarn globally
RUN corepack enable && corepack prepare yarn@1.22.22 --activate

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install only production dependencies
# Skip scripts since we're only copying pre-built artifacts
RUN yarn install --frozen-lockfile --production --ignore-scripts

# Copy built application from builder stage
COPY --from=builder /app/dist ./dist

# Copy config directory structure (for config.json mount point)
# Note: example.config.json is already in dist/config/ from the build process
# This ensures the directory structure exists for the volume mount
COPY --from=builder /app/dist/config/example.config.json ./dist/config/

# Create proto_samples directory
RUN mkdir -p proto_samples

# Expose the default port
EXPOSE 8081

# Set NODE_ENV to production
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8081/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the application
CMD ["node", "dist/index.js"]
