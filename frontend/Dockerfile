FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

COPY . .

# Komenda uruchamiająca serwer deweloperski
# UWAGA: Jeśli używacie Vite, "--host" jest wymagane, żeby Docker przepuścił ruch!
CMD ["npm", "run", "dev", "--", "--host"]
# Jeśli używacie starszego Create React App, odkomentuj linię niżej zamiast tej wyżej:
# CMD ["npm", "start"]