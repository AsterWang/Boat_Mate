var input = document.getElementById("input");
var button = document.getElementById('button');
var ul = document.querySelector("ul");

function inputLength() {
	return input.value.length;
}

function createElementList() {
	var li = document.createElement("li");
	li.appendChild(document.createTextNode(input.value));
	ul.appendChild(li);
	input.value = "";
}

function addListAfterClick() {
	if (inputLength() > 0) {
		createElementList()
	}
}

function addListAfterKeypress(event) {
	if (input.value.length > 0 && event.keyCode === 13){
		createElementList()
	}
}


button.addEventListener("click", addListAfterClick)

input.addEventListener("keypress", addListAfterKeypress)
