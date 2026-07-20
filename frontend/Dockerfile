# Build da SPA (Vite)
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# A URL da API é embutida no bundle em tempo de build (variável do Vite)
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Servir os arquivos estáticos com Nginx
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

# Cloud Run injeta a porta via $PORT, mas espera o container escutando nela;
# como o Nginx não lê variáveis de ambiente nativamente, fixamos 8080
# (padrão do Cloud Run) e configuramos o serviço para usar essa porta.
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
