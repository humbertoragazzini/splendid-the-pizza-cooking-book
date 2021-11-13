var btn = document.getElementById('stepsadder');

btn.addEventListener('click', addStep);

function addStep(){

    var fatherelement = document.getElementById('steps');
    var childelement = document.createElement('div');
    childelement.classList = "input-group";
    var spanelement = document.createElement('span');
    spanelement.classList='input-group-text';
    spanelement.innerText='Step N';
    var textelement = document.createElement('textarea');
    textelement.classList='form-control';
    textelement.ariaLabel='Whith textarea';
    childelement.appendChild(spanelement);
    childelement.appendChild(textelement);
    fatherelement.appendChild(childelement);
    console.log(childelement);
    console.log("hola");

}

