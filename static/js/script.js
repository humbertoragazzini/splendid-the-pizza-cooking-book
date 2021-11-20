
var locker = document.getElementsByClassName("add-space");
$('.toast').toast().show();

function closeToast(id){
    $('.toast').toast().hide();
    space = document.getElementById(id);
    space.classList.toggle('hidden-space');
}

function resetSpaces(){
    for(i=0;i<locker.length();i++)
        {
            locker[i].classList.toggle('hidden-space');
        }
}

function messageToWhatsapp(){
    Qual.errord("Oh no !","Our whatsapp service is not working at the moment, sorry for the inconveniences");
}

