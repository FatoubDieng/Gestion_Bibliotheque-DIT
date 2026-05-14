# STAGE 1 — Builder React
# Compile tout le code React en fichiers HTML/CSS/JS statiques

FROM node:18-slim AS builder

WORKDIR /app

# Installer les dépendances
COPY package.json .
RUN npm install --silent

# Copier le code et compiler
COPY . .
RUN npm run build
# Résultat : /app/build/ contient les fichiers statiques

# STAGE 2 — Runtime Nginx
# Sert les fichiers statiques 
FROM nginx:alpine AS runtime

# Utilisateur non-root 
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

#  Copier le build React depuis le builder 
COPY --from=builder /app/build /usr/share/nginx/html

# ── Config Nginx pour React Router (SPA) ─────────────────────
# Sans ça, les routes /catalogue, /emprunts etc. donnent 404
RUN echo 'server { \n\
    listen 3000; \n\
    root /usr/share/nginx/html; \n\
    index index.html; \n\
    \n\
    # Toutes les routes → index.html (React Router gère) \n\
    location / { \n\
        try_files $uri $uri/ /index.html; \n\
    } \n\
    \n\
    # Cache pour les assets statiques \n\
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \n\
        expires 1y; \n\
        add_header Cache-Control "public, immutable"; \n\
    } \n\
}' > /etc/nginx/conf.d/default.conf

#  Port exposé 
EXPOSE 3000

#  Lancement 
CMD ["nginx", "-g", "daemon off;"]