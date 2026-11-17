# Frontend App: Breast Cancer Classifier

This is an example of a web application (created with the React.js framework) which interacts with the Perceptron API created for this project. It successfully queries the Perceptron API for random cell samples from the database, parsing the raw data into meaningful cards and interactive elements.

The user can select any random "measurement card" and query the API with those measurements, being then provided a real-time AI analysis of those features in an easy-to-digest manner.

The app provides clear output classifications from the API (Benign vs Malignant), as well as showing "Raw Network Outputs" corresponding to the AI confidence for each classification.

## Deployment
This app is one part of a three-service stack. The easiest way to run it is `docker compose up --build` from the repository root; see the main [README](../README.md) for requirements, ports and configuration.

To run only the frontend (the API must be reachable at `http://<this hostname>:5000`, see `src/app-config.json`):

```
npm install
npm start        # development server on http://localhost:3000
npm run build    # production build into ./build
```
