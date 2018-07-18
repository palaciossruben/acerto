function set_circle_color(score, id_string){

    var color;
    if (score < 50){
        color = '#dd5133';
    }else if (score < 59){
        color = '#e8903d';
    }else if (score < 69){
        color = '#eea540';
    }else if (score < 74){
        color = '#f7c645';
    }else if (score < 79){
        color = '#fbd447';
    }else if (score < 84){
        color = '#ffe649';
    }else if (score < 89){
        color = '#e0e159';
    }else if (score < 94){
        color = '#accb54';
    }else if (score < 99){
        color = '#48ab58';
    }else{
        color = "#4ab4a6";
    }

    console.log(id_string);

    var me = document.getElementById(id_string);
    me.style["border-color"] = color;
    me.style["background"] = 'linear-gradient(to top, rgba(100, 235, 52, 0.7)' + score + '%, transparent ' + score + '% )';
}
