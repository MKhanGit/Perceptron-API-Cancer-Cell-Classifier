FROM node:current-alpine
WORKDIR /perceptron-react-app
ENV PATH /perceptron-react-app/node_modules/.bin:$PATH
COPY package.json .
COPY package-lock.json .
RUN npm install
COPY . .
CMD ["npm", "start"]
