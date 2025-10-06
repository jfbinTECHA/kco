FROM node:20-alpine

WORKDIR /app

COPY frontend/package.json frontend/next.config.mjs /app/
RUN npm install --no-audit --no-fund

COPY frontend /app

EXPOSE 3000

CMD ["npm", "run", "dev"]