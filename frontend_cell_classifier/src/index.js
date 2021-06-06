import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import configData from "./app-config.json"
import {AppInfoP1, AppInfoP2} from "./appInfo";

function getPerceptronEndpoint() {
    return configData.PERCEPTRON_API_PROTOCOL.concat(`${window.location.hostname}`).concat(configData.PERCEPTRON_API_ENDPOINT);
}

function getRandomSamplesFromAPI(count) {
    return fetch(getPerceptronEndpoint().concat('/records/random'), {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"max": count, "training_record": "False"})
    }).then(response => {
        return response.json()
    });
}

function getClassificationFromAPI(features) {
    return fetch(getPerceptronEndpoint().concat('/query'), {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"name": configData.NEURAL_NETWORK_NAME, "features": features.join(",")})
    }).then(response => {
        return response.json()
    });
}

function loadSamplesToState(props) {
    if (props.state.loadingSamples) {
        setTimeout(() => {
            getRandomSamplesFromAPI(configData.SAMPLES_RETRIEVED).then(data => {
                let parsedSampleArray = data.records.map((sample) => {
                        let sampleArray = Array(configData.FEATURES.length + 1);
                        for (let i = 0; i < configData.FEATURES.length; i++) {
                            sampleArray[i] = sample[i]
                        }
                        sampleArray[configData.FEATURES.length] = sample['target_class']
                        return sampleArray;
                    }
                );
                props.setState({
                    loadingSamples: false,
                    loadingResponse: false,
                    cellSamples: parsedSampleArray,
                    revealedSamples: Array(configData.SAMPLES_RETRIEVED).fill(false),
                    responseIsCorrect: Array(configData.SAMPLES_RETRIEVED).fill(null),
                    finished: false,
                    selectedSample: null,
                    targetResponse: null,
                    featuresRequest: Array(configData.FEATURES.length).fill(0.0)
                });
            });
        }, configData.EASE_IN_TIME);

    }
}

function AppHeader(props) {
    return (
        <div className="row">
            <div className="app-heading">
                <b>{props.value}</b>
            </div>
        </div>
    );
}

function AppInfo(props) {
    return (
        <div className="row">
            <div className="app-info">
               <p>{props.value}</p>
            </div>
        </div>
    );
}

function LoadingCells(props) {
    let placeholderSamples = Array(configData.SAMPLES_RETRIEVED).fill(Array(configData.FEATURES.length + 1).fill(-1));
    let loaders = placeholderSamples.map(function (sample, index) {
        return (
            <Sample sample={sample} index={index} key={index} state={props.state} onClick={props.onClick}/>
        );
    });

    return (
        <div className="row">
            {loaders}
        </div>
    );
}

function NeuralNetworkResponse(props) {
    let networkResponse = Array(2).fill("");
    let responseText;
    let benignConf;
    let malignantConf;
    networkResponse[0] = "network-response";
    if (props.state.loadingSamples || !props.state.finished) {
        networkResponse[1] = "loading";
        responseText = "\xa0";
    } else if (props.state.targetResponse !== null) {
        networkResponse[1] = props.state.targetResponse === 1 ? "malignant" : "benign";
        responseText = networkResponse[1];
    }
    if (props.state.loadingResponse) {
        responseText = String.fromCharCode(8226, 8226, 8226);
    }
    if (props.state.lastResponseData !== null) {
        let raw_outputs = props.state.lastResponseData['raw_network_output'];
        benignConf = "Benign Conf. \u2192 ".concat(raw_outputs[0][0].toFixed(2))
        malignantConf = "Malignant Conf. \u2192 ".concat(raw_outputs[0][1].toFixed(2))
    }

    return (
        <div className="row">
            <div className="network-response-header">
                AI Classification
                <p className={networkResponse.join(" ")}>
                    {responseText}
                </p>
                <p>Raw Network Outputs</p>
                <p>{benignConf}</p>
                <p>{malignantConf}</p>
            </div>
        </div>
    );
}

class Sample extends React.Component {
    render() {
        let sampleClass = Array(3).fill("");

        sampleClass[0] = 'sample';
        // sampleClass[1] = this.props.sample[configData.FEATURES.length] === "1" ? "malignant" : (this.props.sample[configData.FEATURES.length] === "0" ? "benign" : "loading");
        let sampleTarget = this.props.sample[configData.FEATURES.length] === "1" ? "malignant" : (this.props.sample[configData.FEATURES.length] === "0" ? "benign" : "loading");
        let sampleHeadingClass;
        let sampleCorrect;
        let sampleCorrectClass;
        if (this.props.state.selectedSample !== null) {
            if (this.props.state.selectedSample === this.props.index) {
                sampleClass[1] = "selected-sample";
                if (this.props.state.targetResponse !== null) {
                    sampleClass[2] = "selection-done";
                    this.props.state.responseIsCorrect[this.props.index] = (parseInt(this.props.state.targetResponse) === parseInt(this.props.sample[configData.FEATURES.length]));
                }
            }
        }

        let featuresList = configData.FEATURES.map(function (feature, index) {
            let featureVal = (this.props.sample[index] < 0) ? "" : this.props.sample[index];
            return (
                <div className="sample-feature-value" key={index}>{feature}: {featureVal}</div>
            );
        }, this);

        if (this.props.state.revealedSamples[this.props.index]){
            sampleHeadingClass = sampleTarget;
        }
        else{
            sampleTarget = (sampleTarget === "loading") ? sampleTarget : "? ? ? "
        }
        sampleCorrect = (this.props.state.responseIsCorrect[this.props.index] !==null) ? ( (this.props.state.responseIsCorrect[this.props.index]) ? " \u2713 " : " \u2716 ") : " \xa0 ";
        sampleCorrectClass = (this.props.state.responseIsCorrect[this.props.index] !==null) ? ( (this.props.state.responseIsCorrect[this.props.index]) ? "benign" : "malignant") : "";
        console.log(this.props.state.responseIsCorrect[this.props.index]);
        return (
            <button className={sampleClass.join(' ')} onClick={() => this.props.onClick(this.props.index)}>
                <div className={"sample-heading ".concat(sampleHeadingClass)}>
                    <b>{sampleTarget}</b>
                </div>
                <div className={"check-box ".concat(sampleCorrectClass)}>
                    <b>{sampleCorrect}</b>
                </div>
                {featuresList}
            </button>
        );
    }
}

class SampleBoard extends React.Component {
    render() {
        if (this.props.state.loadingSamples) {
            return (
                <LoadingCells state={this.props.state} onClick={this.props.onClick} />
            );
        }
        let samplesList = this.props.state.cellSamples.map(function (sample, index) {
            return (
                <Sample sample={sample} index={index} key={index} state={this.props.state} onClick={this.props.onClick} />
            );

        }, this);

        return (
            <div className="row">
                {samplesList}
            </div>
        );
    }
}

class SubmitButton extends React.Component {
    render() {
        let submitButtonStatus = Array(2).fill("");
        submitButtonStatus[0] = "button";
        if (this.props.state.finished || this.props.state.selectedSample === null || this.props.state.loadingSamples || this.props.state.loadingResponse) {
            submitButtonStatus[1] = "disabled";
        }
        return (
            <div className="row">
                <button className={submitButtonStatus.join(' ')} onClick={this.props.onClick}>
                    <b>Submit</b>
                </button>
            </div>
        );
    }
}

class RefreshButton extends React.Component {
    render() {
        return (
            <div className="row">
                <div className="button refresh" onClick={this.props.onClick}>
                    &#x21bb;
                </div>
            </div>
        );
    }
}

class StatusMessage extends React.Component{
    render(){
        let message;
        if(this.props.state.loadingSamples || this.props.state.loadingResponse){
            message = "Loading ...";
        }
        else if (this.props.state.targetResponse !== null){
            message = "Neural Network classification complete !";
        }
        else if(this.props.state.selectedSample === null){
            message = "Select a sample for testing ...";
        }
        else{
            message = "Submit your sample ";
        }

        return(
            <div className="row">
                <code>
                    <p>{message}</p>
                </code>
            </div>
        );
    }
}

class MachineLearningApp extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loadingSamples: true,
            loadingResponse: true,
            lastResponseData: null,
            cellSamples: null,
            selectedSample: null,
            featuresRequest: Array(configData.FEATURES.length).fill(0.0),
            revealedSamples: Array(configData.SAMPLES_RETRIEVED).fill(false),
            targetResponse: null,
            responseIsCorrect: Array(configData.SAMPLES_RETRIEVED).fill(null),
            finished: false
        };
    }

    submitClick() {
        // Given a valid selection/load state, ping the API with the selected data and receive a response
        if (!this.state.loadingSamples && !this.state.loadingResponse && this.state.selectedSample !== null && !this.state.finished) {
            this.setState({loadingResponse: true});
            setTimeout(() => {
                getClassificationFromAPI(this.state.featuresRequest).then(data => {
                    this.state.revealedSamples[this.state.selectedSample] = true;
                    this.setState({
                        lastResponseData: data,
                        targetResponse: data['identified_class'],
                        loadingResponse: false,
                        finished: true
                    });
                });
            }, configData.EASE_IN_TIME);
        }
    }

    sampleClick(i) {
        let features;
        if (this.state.loadingSamples || this.state.loadingResponse){
            return null; // App is in a loading state, do nothing
        }
        else{
            features = this.state.cellSamples[i].slice(0, this.state.cellSamples[i].length - 1).map(function (f) {
                return parseFloat(f);
            });
        }
        if (!this.state.finished) {
            // Stage API request with selected features
            this.setState({
                selectedSample: this.state.selectedSample === i ? null : i,
                featuresRequest: features,
                targetResponse: null
            });
        } else {
            // Soft reset the board state, allowing for another sample to the be tested
            this.setState({selectedSample: i, featuresRequest: features, targetResponse: null,  lastResponseData: null, finished: false});
        }
    }

    refreshSampleList() {
        if(this.state.loadingResponse || this.state.loadingSamples ){
            return null;
        }
        // Set the App into a loading state and request a new random sample set from the database via an API call
        this.setState({loadingSamples: true, loadingResponse: true, selectedSample: null, lastResponseData: null, responseIsCorrect: Array(configData.SAMPLES_RETRIEVED).fill(null)});
        loadSamplesToState(this);
    }

    render() {
        loadSamplesToState(this);
        return (
            <div>
                <AppHeader value="Machine Learning Cell Classifier"/>
                <div className="ml-app">
                    <div className="sample-board">
                        <AppInfo value={AppInfoP1}/>
                        <img alt="Perceptron Network" src={process.env.PUBLIC_URL + "logo192.png"} className="app-logo"/>
                        <AppInfo value={AppInfoP2}/>
                        <SampleBoard state={this.state} onClick={(i) => this.sampleClick(i)}/>
                        <RefreshButton onClick={() => this.refreshSampleList()}/>
                        <SubmitButton state={this.state} onClick={() => this.submitClick()}/>
                        <StatusMessage state={this.state}/>
                        <NeuralNetworkResponse state={this.state}/>
                    </div>
                </div>
            </div>
        );
    }
}

ReactDOM.render(
    <MachineLearningApp/>,
    document.getElementById('root')
);
