# Frontend App: Breast Cancer Classifier

This is an example of a web application (created with the React.js framework) which interacts with the Perceptron API created for this project. It successfully queries the Perceptron API for random cell samples from the database, parsing the raw data into meaningful cards and interactive elements.

The user can select any random "measurement card" and query the API with those measurements, being then provided a real-time AI analysis of those features in an easy-to-digest manner.

The app provides clear output classifications from the API (Benign vs Malignant), as well as showing "Raw Network Outputs" corresponding to the AI confidence for each classification.

## Screenshots



## Deployment 
Since this project is designed as an ecosystem of micro-services, it would be easiest to run `docker-compose` from the project/repository root:

```
docker-compose build
docker-compose up
```

This will build and deploy all three components of the project: Backend DB, Backend API, Frontend React.js App.

## Advanced Deployment / Debugging

If you do not wish to run the stack with the default configuration, you can run custom deployments for each service.

For this React.js application, you can enter the `./frontend_cell_classifier` directory and build the micro-service via the `Dockerfile` or run the `npm start`/`npm run build` commands if you have Node.js and npm installed.
