# Perceptron API: Machine Learning Cancer Cell Classifier

This application is a full-stack microservice solution demonstrating the deployment of a machine learning neural network wrapped into a RESTful API service, accessed with a React.js frontend app. 

The backend is a custom python module which implements the Perceptron Model for machine learning, providing access to the data class via API endpoints on a flask server. The application is accessed through a React.js frontend implementing a testing "sandbox" application, allowing users to query the backend neural network and receive classification outputs (i.e. Benign vs Malignant).

In this sample deployment of the API (Breast Cancer Classifier), the Perceptron Network is trained on ~700 records of cell measurements to produce a classifier which can distinguish between malignant and benign cancer cells with ~95% accuracy. Prior to deployment, the system also re-trains the network over several iterations (default=10) to maximize the accuracy against a set of optimizaiton records.

The entire project is dockerized into three discrete containers and can be deployed using the below steps under *"Build / Deploy Instructions"*

### Key  Features
 * "Raw Python" implementation of the Perpcetron learning model (i.e. no ML frameworks used)
 * RESTful API endpoints for managing individual models: create, train, query, update, delete
 * Custom internal caching system (similar to LRU cache) for limiting disk reads/writes and database calls
 * Containerized ecosystem for easy deployment/development
 * Sample Data/Models for Breast Cancer Classification
 * Sample Interactive React.js frontend for testing pre-trained ML models
 * MongoDB for managing training records, testing records and metadata for pre-trained networks


#### Planned Features
 * Improve training optimization
 * Add functionality for custom user-spaces & authentications
 * Implement additional machine learning models
 * Enable bulk training via frontend interface

-----
## Build / Deploy Instructions

### Requirements
 * Docker Engine
 * Docker-Compose (usually included with engine)
 * Ports `3000`, `27017`, and `5000` are available/unbound (or choose custom ports in `docker-compose.yml`)

If you wish to deploy the project with all default settings/values, you can simply run `docker-compose` with the provided yaml file in the repository root:

```
docker-compose build
docker-compose up
```
Note: `build` command is only required when you make changes to the source code or docker configs

After the images are built, and the containers are running, you can access the containers with the following endpoints: 
 - React.js Frontend App: `http://localhost:3000`
 - MonoDB database: `mongodb://localhost:27017`
 - RESTful API backend: `http://localhost:5000/api/v1/perceptron`


-----
## Advanced/Custom Build Instructions
**It is recommended to start with the `docker-compose.yml` deployment provided in the project.**

If you instead wish to manually set up the containers or do other advanced/custom settings for deployment, see below.

_Before Starting:
Creating a custom docker network is optional, but highly recommended as otherwise you will need to manually ensure that your endpoint routing between containers is properly setup for all containers (by editing each component's config)_

The following instructions will allow you to deploy the service using the default values provided in `config.json`:


1) Create a custom docker network with a user defined subnet, which all contianers will be attached to when run.
```
docker network create --subnet=172.15.0.0/16 api-net
```

2) Build the Monogo DB Server using the Dockerfile under `./db/` and Run it on the custom network:

```
docker build -t perceptron-db-mongo ./db/
docker run -p 27017:27017 --network="api-net" --ip="172.15.0.2" perceptron-db-mongo
```
_**Note**: Make sure the ip you bind this container to matches the `mongo_host` field in the `config.json`, otherwise the REST API container will **not be able to access** the monogo DB container._

3) Build the REST API Server using the Dockerfile under `./api/` and Run it on the custom network:
```
docker build -t perceptron-api-flask ./api/
docker run -p 5000:5000 --network="api-net" --ip="172.15.0.3" perceptron-api-flask
```

4) Build the React Frontend using the Dockerfile under `./frontend/` and Run it on the custom network:
```
docker build -t perceptron-react-frontend ./frontend_cell_classifier/
docker run -p 3000:3000 --network="api-net" --ip="172.16.0.4" perceptron-react-frontend
```

-----
## Sample Data References

### Breast Cancer Cell Data

Note: While the original attribute information is provided below, the records provided under `./api/sample_data` are normalized, and the target class is instead mappped as `0 -> benigign` and `1 -> malignant`. Additionally, the sample code number was dropped.

#### Attribute Information
```
1. Sample code number: id number 
2. Clump Thickness: 1 - 10 
3. Uniformity of Cell Size: 1 - 10 
4. Uniformity of Cell Shape: 1 - 10 
5. Marginal Adhesion: 1 - 10 
6. Single Epithelial Cell Size: 1 - 10 
7. Bare Nuclei: 1 - 10 
8. Bland Chromatin: 1 - 10 
9. Normal Nucleoli: 1 - 10 
10. Mitoses: 1 - 10 
11. Class: (2 for benign, 4 for malignant)
```

#### Data Set Information

Samples arrive periodically as Dr. Wolberg reports his clinical cases. The database therefore reflects this chronological grouping of the data. This grouping information appears immediately below, having been removed from the data itself: 
```
Group 1: 367 instances (January 1989) 
Group 2: 70 instances (October 1989) 
Group 3: 31 instances (February 1990) 
Group 4: 17 instances (April 1990) 
Group 5: 48 instances (August 1990) 
Group 6: 49 instances (Updated January 1991) 
Group 7: 31 instances (June 1991) 
Group 8: 86 instances (November 1991) 
----------------------------------------- 
Total: 699 points (as of the donated datbase on 15 July 1992) 
```
Note that the results summarized above in Past Usage refer to a dataset of size 369, while Group 1 has only 367 instances. This is because it originally contained 369 instances; 2 were removed. The following statements summarizes changes to the original Group 1's set of data: 

```
 Group 1 : 367 points: 200B 167M (January 1989) 
 Revised Jan 10, 1991: Replaced zero bare nuclei in 1080185 & 1187805 
 Revised Nov 22,1991: Removed 765878,4,5,9,7,10,10,10,3,8,1 no record 
 : Removed 484201,2,7,8,8,4,3,10,3,4,1 zero epithelial 
 : Changed 0 to 1 in field 6 of sample 1219406 
 : Changed 0 to 1 in field 8 of following sample: 
 : 1182404,2,3,1,1,1,2,0,1,1,1
```

##### Relevant Papers
```
Wolberg, W.H., & Mangasarian, O.L. (1990). Multisurface method of pattern separation for medical diagnosis applied to breast cytology. In Proceedings of the National Academy of Sciences, 87, 9193--9196. 

Zhang, J. (1992). Selecting typical instances in instance-based learning. In Proceedings of the Ninth International Machine Learning Conference (pp. 470--479). Aberdeen, Scotland: Morgan Kaufmann.
```
