var iterator=1;
text.forEach(function(sample){
  document.getElementById(iterator).innerHTML += "Randomly Selected Cell "+ iterator + ": <br>";
  document.getElementById(iterator).innerHTML += '<button type="button" class="btn btn-warning" onClick=submitCell(' + iterator + ')>Test Cell</button><br/><br/>';
  for (var key in sample){
    document.getElementById(iterator).innerHTML +=key + ": " +sample[key]+"<br>";
  }
  if(text[iterator-1]['class']=='0'){
    document.getElementById(iterator).style.backgroundColor = "#27ae60";
    document.getElementById(iterator).innerHTML += "<H2>BENIGN</H2>";}

  else{
    document.getElementById(iterator).style.backgroundColor = "#e74c3c";
    document.getElementById(iterator).innerHTML += "<H2>MALIGNANT</H2>";
  }

  iterator+=1;

});
function submitRecord(i){
  i=i-1
  console.log(i);
  console.log(text[i]);
}
function submitCell(i){
  i=i-1;
  document.getElementById("response").innerHTML= "<h2>Neural Network's Prediction:</h2>" + "<h2></h2><img class='loader' src=./loader.gif>"
  $.ajax({
    type: "POST",
    url: "./NN_query.py",
    data: {
      thickness: text[i]["thickness"],
      size: text[i]["size"],
      shape: text[i]["shape"],
      adhesion: text[i]["adhesion"],
      single_size: text[i]["single_size"],
      nuclei: text[i]["nuclei"],
      chromatin: text[i]["chromatin"],
      nucleoli: text[i]["nucleoli"],
      mitoses: text[i]["mitoses"],
      class: text[i]["class"],
    },
    success: function (data) {
         console.log(data);
         document.getElementById("response").innerHTML="<h2>Neural Network's Prediction:</h2>" + "<h2>" + data+"</h2><img class='loader'>";
     }
    }).done(function(o) {
    console.log(text[i]);
    console.log('submitted to server.');
    });
  }
