function on_signup() {
    $("#overlay-signup").css("display", "block");
    $("#hide1").css("display", "none");
    $("#hide2").css("display", "none");
    $("#register-form").css("display", "block");
    $("html").css("background-size", "cover");
    $("#option1").css("color", "white");
    $("#option2").css("color", "white");
    $("#register-form").animate({"marginLeft": '60%'}, 650,"swing");
    $("#form-image").animate({"backgroundPosition": '86%'}, 690,"swing");
    $("html").css("overflow", "hidden");
    $("nav").css("margin-bottom", "40px");
}

function off_signup() {
    document.getElementById("overlay-signup").style.display = "none";
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

function on_login() {
    document.getElementById("overlay-login").style.display = "block";
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

function off_login() {
    document.getElementById("overlay-login").style.display = "none";
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
