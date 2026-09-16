async function submitIssue(){

let issue=document.getElementById("issue").value.trim();

let photo=document.getElementById("photo").files[0];

if(issue==="" && !photo){

alert("Please enter a problem or upload a photo.");

return;

}

let formData=new FormData();

formData.append("issue",issue);

if(photo){

formData.append("photo",photo);

}

const response=await fetch("/classify",{

method:"POST",

body:formData

});

const data=await response.json();

document.getElementById("result").innerHTML=`

<div class="card">

${data.image ? `<img src="${data.image}">` : ""}

<p><b>Detected Issue:</b> ${data.detected_issue}</p>

<h2>${data.category}</h2>

<p><b>Department:</b> ${data.department}</p>

<p><b>Priority:</b> ${data.priority}</p>

<p><b>Suggested Action:</b> ${data.action}</p>

</div>

`;

}