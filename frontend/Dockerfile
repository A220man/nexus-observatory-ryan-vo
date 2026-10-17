# Stage 1: build
FROM node:24-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Stage 2: runtime (nginx)
FROM nginx:1.27-alpine
LABEL maintainer="Ryan Vo <ryandtvo@gmail.com>"
# Create nonroot user
RUN addgroup -S app && adduser -S -G app app
# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist /usr/share/nginx/html
# nginx.conf to set ownership + listen on 80
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Fix permissions for nonroot
RUN chown -R app:app /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /usr/share/nginx/html
USER app
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1
CMD ["nginx", "-g", "daemon off;"]