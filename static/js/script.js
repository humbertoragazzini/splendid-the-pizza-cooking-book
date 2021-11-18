var toast = $('.toast').toast(
    animation = true,
    autohide = true,
    delay=500,
);

toast.show();

var toast = $('.toast').toast(
    animation = true,
    autohide = true,
    delay=500,
);

toast.show();

function hideTheToast(thetoast){
    thetoast.hide();
}

toast.show();
setTimeout(hideTheToast, 800000, toast);


