# Perceptron API: Machine Learning Cancer Cell Classifier

A full-stack microservice demo: a machine learning neural network wrapped in a RESTful API and accessed through a React.js frontend.

The backend is a custom Python module implementing the Perceptron model, exposed through endpoints on a Flask server. The React.js frontend is a testing "sandbox" which lets users query the neural network and receive a classification (Benign vs Malignant).

In the sample deployment (Breast Cancer Classifier), the network is trained on ~700 records of cell measurements to distinguish malignant from benign cells with ~95% accuracy. On startup the system re-trains the network several times (default=10) and keeps the most accurate version.

The project is split into three Docker containers: a MongoDB database, the Flask API and the React frontend.

### Key Features
 * "Raw Python" implementation of the Perceptron learning model (no ML frameworks used)
 * RESTful API endpoints for managing individual models: create, train, query, update, delete
 * Custom internal caching system (similar to an LRU cache) limiting disk reads/writes and database calls
 * Containerized ecosystem for easy deployment/development
 * Sample data and a pre-trained model for Breast Cancer classification
 * Sample interactive React.js frontend for testing pre-trained ML models
 * MongoDB for managing training records, testing records and metadata for pre-trained networks

### Planned Features
 * Improve training optimization
 * Add functionality for custom user-spaces & authentication
 * Implement additional machine learning models
 * Enable bulk training via frontend interface

-----
## Quick Start (Docker Compose)

This works the same on Linux, macOS and Windows.

### Requirements
 * [Docker Engine](https://docs.docker.com/engine/install/) or Docker Desktop, with **Docker Compose v2** (the `docker compose` command, included with current Docker installs). Check with `docker compose version`.
 * Internet access on the first build (to pull base images and install dependencies).
 * Ports `3000`, `5000` and `27017` free on the host (or change the left-hand side of the `ports:` mappings in `docker-compose.yml`).
 * A CPU supported by MongoDB 8 (x86-64 with AVX, or ARM64 with ARMv8.2-A). On older hardware, pick an older tag in `db/Dockerfile` (e.g. `mongo:4.4`).

### Run

From the repository root:

```
docker compose up --build
```

Add `-d` to run in the background. Re-run with `--build` whenever you change source code or Docker configuration.

On the first start the API loads the sample records into MongoDB and trains the sample network. Wait until the API log prints a line like:

```
[Breast Cancer Classifier] After 10 training iterations on 667 records, deploying Sample Network with 100.00% Accuracy...
```

The frontend dev server also needs a short moment to compile on its first start. Then open:

| Service | URL |
|---|---|
| React.js frontend | http://localhost:3000 |
| REST API | http://localhost:5000/api/v1/perceptron |
| MongoDB | `mongodb://localhost:27017` |

Check that the API is up (it should return `{"status": "OK"}`):

```
curl http://localhost:5000/api/v1/perceptron
```

### Stop / Reset
```
docker compose down       # stop and remove containers (keeps the database and trained networks)
docker compose down -v    # also delete the stored database, trained networks and node_modules volumes
```

### Deploying on another machine or a server
The frontend runs in your browser and calls the API at **the same hostname it was loaded from, on port 5000** (`http://<hostname>:5000`, see `frontend_cell_classifier/src/app-config.json`). So to deploy remotely:
 1. Clone the repository on the server and run `docker compose up -d --build`.
 2. Make ports `3000` and `5000` reachable from the browsers that will use the app (firewall/security group). Port `27017` does not need to be exposed; remove its `ports:` entry in `docker-compose.yml` to keep the database private.
 3. Browse to `http://<server-address>:3000`.

If you serve the API on a different port or behind a reverse proxy, update `PERCEPTRON_API_ENDPOINT` (and `PERCEPTRON_API_PROTOCOL`) in `frontend_cell_classifier/src/app-config.json`, then rebuild.

_Note: the services run the React and Flask development servers, which are intended for demos and development. Put a hardened reverse proxy in front of them (or swap in production servers) before exposing them to the public internet. The API currently has no authentication._

-----
## Configuration

**API** (`api/config.json`):

| Key | Purpose |
|---|---|
| `flask_host`, `flask_port` | Address the Flask server binds to |
| `flask_cache_max_size` | Number of networks held in the in-memory cache |
| `flask_enable_debug_endpoints` | Enables the raw database read/write/delete debug endpoints (keep `false` outside of development) |
| `mongo_host`, `mongo_port`, `mongo_database` | MongoDB connection |
| `data_collection`, `metadata_collection` | Mongo collections for records and network metadata |
| `trained_networks_directory` | Where serialized networks are written |
| `load_sample_network_on_start` | Load the sample data and train the sample network at startup |
| `sample_*` | Sample network name, file, layer sizes, learning rate, CSV data files and training iterations |

The defaults assume the static addresses set in `docker-compose.yml` (`172.15.0.2` for MongoDB, `172.15.0.3` for the API). If you change those, update `flask_host` and `mongo_host` to match.

**Frontend** (`frontend_cell_classifier/src/app-config.json`): API protocol/endpoint, the name of the network to query and the number of samples displayed.

### API Endpoints
All endpoints live under `/api/v1/perceptron` and accept `GET` or `POST`.

| Endpoint | Description |
|---|---|
| `/` | Health check |
| `/records`, `/records/random` | Query stored records (`random` also requires `max`) |
| `/metadata` | List the stored networks |
| `/create`, `/update` | Create or replace a network (`name`, `input`, `hidden`, `output`, `learningrate` as query args) |
| `/query` | Classify a feature list (JSON body: `name`, `features`) |
| `/train` | Train a network on one record (JSON body: `name`, `features`, `target`) |
| `/commit` | Write a cached network's training to disk (`name`) |
| `/delete` | Delete a network (`name`) |

-----
## Running Without Docker Compose

### Individual Docker containers
Use this if you want to start the containers by hand. The default `config.json` expects the static addresses below.

1) Create a custom network with a user defined subnet:
```
docker network create --subnet=172.15.0.0/16 api-net
```

2) Build and run MongoDB first, and give it a few seconds to start (the API exits if the database is unreachable when it starts):
```
docker build -t perceptron-db-mongo ./db/
docker run -d -p 27017:27017 --network api-net --ip 172.15.0.2 perceptron-db-mongo
```

3) Build and run the API:
```
docker build -t perceptron-api-flask ./api/
docker run -d -p 5000:5000 --network api-net --ip 172.15.0.3 perceptron-api-flask
```

4) Build and run the frontend:
```
docker build -t perceptron-react-frontend ./frontend_cell_classifier/
docker run -d -p 3000:3000 --network api-net --ip 172.15.0.4 perceptron-react-frontend
```

_The `--ip` of the database must match `mongo_host` in `api/config.json`, otherwise the API cannot reach MongoDB._

### Local development (no containers for the app)
Requires Python 3.13+, Node.js 22+ and a MongoDB instance (e.g. `docker run -d -p 27017:27017 mongo:8.0`).

API:
```
cd api
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdir -p bin
```
Edit `api/config.json` so `flask_host` is `127.0.0.1` and `mongo_host` is `localhost`, then:
```
python perceptron_api.py
```

Frontend (in another terminal):
```
cd frontend_cell_classifier
npm install
npm start
```
The app opens at http://localhost:3000.

### Tests
The API unit tests (cache system) need no database:
```
cd api
python -m unittest unittests.cache_tests
```
Or inside the running stack: `docker compose exec perceptron-api-flask python3 -m unittest unittests.cache_tests`.

-----
## Sample Data References

### Breast Cancer Cell Data

Note: While the original attribute information is provided below, the records provided under `./api/sample_data` are normalized, and the target class is instead mapped as `0 -> benign` and `1 -> malignant`. Additionally, the sample code number was dropped.

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
Total: 699 points (as of the donated database on 15 July 1992) 
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
