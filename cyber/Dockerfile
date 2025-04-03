FROM node:16 as build

WORKDIR /app

# Copy package files first
COPY package*.json ./

# Install dependencies with flag to handle peer dependency conflicts
RUN npm install --legacy-peer-deps

# Install all missing dependencies required by EUI
RUN npm install --legacy-peer-deps moment @elastic/eui-theme-borealis @elastic/eui-theme-common

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]



#
#FROM node:16 as build
#
#WORKDIR /app
#
## Copy package files and install dependencies first for better caching
#COPY package*.json ./
#
## Install all dependencies including dev dependencies
#RUN npm install --legacy-peer-deps
#
## Explicitly install required packages that might be missing
#RUN npm install --save typescript axios @elastic/eui
#
## Copy the rest of the application
#COPY . .
#
## Verify EUI theme files
#RUN echo "Checking available EUI theme files:"
#RUN find node_modules/@elastic/eui/dist -name "*.css"
#
## Build the application
#RUN npm run build
#
## Production stage
#FROM nginx:alpine
#COPY --from=build /app/build /usr/share/nginx/html
#COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
#EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]