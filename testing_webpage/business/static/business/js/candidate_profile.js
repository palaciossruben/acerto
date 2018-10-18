function set_circle_color(score, id_string){

    var color;

    if (score < 50){
        color = 'rgba(221, 81, 51,';
    }else if (score < 59){
        color = 'rgba(232, 144, 61,';
    }else if (score < 69){
        color = 'rgba(238, 165, 64,';
    }else if (score < 74){
        color = 'rgba(247, 212, 71,';
    }else if (score < 79){
        color = 'rgba(251, 212, 71,';
    }else if (score < 84){
        color = 'rgba(255, 230, 73,';
    }else if (score < 89){
        color = 'rgba(224, 225, 89,';
    }else if (score < 94){
        color = 'rgba(172, 203, 84,';
    }else if (score < 99){
        color = 'rgba(72, 171, 88,';
    }else{
        color = 'rgba(74, 180, 166,';
    }

    if (score === null){
    }else{
        var me = document.getElementById(id_string);
        if(me == null){
        }else{

            me.style["border-color"] = color + '1)';
            me.style["background"] = 'linear-gradient(to top,' + color + '0.7)' + score + '%, transparent ' + score + '% )';

            $(me).mouseover(function() {
                me.style["border-color"] = 'rgba(255, 156, 51, 1)';
                me.style["background"] = 'linear-gradient(to top,' + 'rgba(255, 156, 51, 0.7)' + score + '%, transparent ' + score + '% )';
                me.style["cursor"] = 'pointer';
            });

            $(me).mouseout(function() {
                me.style["border-color"] = color + '1)';
                me.style["background"] = 'linear-gradient(to top,' + color + '0.7)' + score + '%, transparent ' + score + '% )';
            });
        }
    }
}