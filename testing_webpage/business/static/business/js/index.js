function on() {
    document.getElementById("overlay").style.display = "block";
    document.getElementById("hide1").style.display = "none";
    document.getElementById("hide2").style.display = "none";
    document.getElementById("register-form").style.display = "block";
    $("html").css("background-size", "cover");
    $("#option1").css("color", "white");
    $("#option2").css("color", "white");
    $("nav").css("margin-bottom", "40px");
    $("#register-form").animate({"marginLeft": '60%'}, 650,"swing");
    $("#form-image").animate({"backgroundPosition": '86%'}, 650,"swing");
    $("html").css("overflow", "hidden");
}

function off() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("hide1").style.display = "block";
    document.getElementById("hide2").style.display = "block";
    document.getElementById("register-form").style.display = "none";
    $("html").css("background-size", "contain");
    $("#option1").css("color", "#3d4753");
    $("#option2").css("color", "#3d4753");
    $("nav").css("margin-bottom", "");
    $("#register-form").animate({marginLeft: '160%'});
    $("#form-image").animate({"backgroundPosition": '186%'}, 650,"swing");
    $("html").css("overflow-y", "scroll");
}

function on2() {
    document.getElementById("overlay2").style.display = "block";
    document.getElementById("hide1").style.display = "none";
    document.getElementById("hide2").style.display = "none";
    document.getElementById("login-form").style.display = "block";
    $("html").css("background-size", "cover");
    $("#option1").css("color", "white");
    $("#option2").css("color", "white");
    $("nav").css("margin-bottom", "40px");
    $("#login-form").animate({"marginLeft": '60%'}, 650,"swing");
    $("#form-image2").animate({"backgroundPosition": '86%'}, 650,"swing");
    $("html").css("overflow", "hidden");
}

function off2() {
    document.getElementById("overlay2").style.display = "none";
    document.getElementById("hide1").style.display = "block";
    document.getElementById("hide2").style.display = "block";
    document.getElementById("login-form").style.display = "none";
    $("html").css("background-size", "contain");
    $("#option1").css("color", "#3d4753");
    $("#option2").css("color", "#3d4753");
    $("nav").css("margin-bottom", "");
    $("#login-form").animate({marginLeft: '160%'});
    $("#form-image2").animate({"backgroundPosition": '186%'}, 650,"swing");
    $("html").css("overflow-y", "scroll");
}

function myFunction() {
    var x = document.getElementById("myTopnav");
    if (x.className === "row") {
        x.className += " responsive";
    }
    else {
        x.className = "row";
    }
}
