const form = document.getElementById("registrationForm");
const success = document.getElementById("success");

form.addEventListener("submit", function(e){

e.preventDefault();

let valid = true;

document.querySelectorAll(".error").forEach(error=>{
error.innerHTML="";
});

const fullname=document.getElementById("fullname").value.trim();
const email=document.getElementById("email").value.trim();
const phone=document.getElementById("phone").value.trim();
const course=document.getElementById("course").value;
const password=document.getElementById("password").value;
const confirmPassword=document.getElementById("confirmPassword").value;

const emailPattern=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phonePattern=/^[6-9]\d{9}$/;

if(fullname===""){
showError(0,"Full name is required");
valid=false;
}

if(email===""){
showError(1,"Email is required");
valid=false;
}
else if(!emailPattern.test(email)){
showError(1,"Invalid Email");
valid=false;
}

if(phone===""){
showError(2,"Phone number is required");
valid=false;
}
else if(!phonePattern.test(phone)){
showError(2,"Enter valid 10-digit phone number");
valid=false;
}

if(course===""){
showError(3,"Please select a course");
valid=false;
}

if(password===""){
showError(4,"Password is required");
valid=false;
}

if(confirmPassword===""){
showError(5,"Confirm password");
valid=false;
}
else if(password!==confirmPassword){
showError(5,"Passwords do not match");
valid=false;
}

if(valid){

const student={
fullname,
email,
phone,
course,
password
};

localStorage.setItem("studentData",JSON.stringify(student));

success.innerHTML="Registration Successful!";

form.reset();

}

});

function showError(index,message){

document.querySelectorAll(".error")[index].innerHTML=message;

}

const themeBtn=document.getElementById("themeBtn");

themeBtn.onclick=function(){

document.body.classList.toggle("dark");

if(document.body.classList.contains("dark")){
themeBtn.innerHTML="☀ Light Mode";
}
else{
themeBtn.innerHTML="🌙 Dark Mode";
}

}