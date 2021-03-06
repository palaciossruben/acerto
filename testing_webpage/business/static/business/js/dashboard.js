var LAST_SHOWING_ROWS = {"recommended": 0,
                         "relevant": 0,
                         "applicants": 0};

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
        }
    }
}

function set_background(image_name, id_string){

    image_name = image_name.replace("&#39;","");
    if (image_name == 'default' || image_name == 'None'){
        image_name = "Start_BG-07.jpg)";
    }

    var me = document.getElementById(id_string);
    if(me == null){
    }else{
        if ($(window).width() < 768) {
        image_name = 'cel-' + image_name;
        var url = 'url(../../../../../static/business/img/' + image_name;
        me.style["background-image"] = url;
    }else{
        var url = 'url(../../../../../static/business/img/min-' + image_name;
        me.style["background-image"] = url;
    }}
}

/*!
 * jQuery sticky sidebar scroll plugin
 * For complete usage instructions, see
 * http://www.skipser.com/p/2/p/sticky-sidebar-div-jquery-plugin.html
 * Date: Sun Feb 10 2013 12:00:00 GMT
 */

(function($, undefined){
	$.extend({

		/**

		 * StickySidebarScroll initiated

		 * @param {Object} el - a jquery element, DOM node or selector string

		 * @param {Object} config - offset - forcemargin

		 */

		"stickysidebarscroll": function(el, config){

			if (config && config.offset) {

				config.offset.bottom = parseInt(config.offset.bottom,10);

				config.offset.top = parseInt(config.offset.top,10);

			}else{

				config.offset = {bottom: 100, top: 0};

			}

			var el =$(el);

			if(el && el.offset()){

				var el_top = el.offset().top,

				el_left = el.offset().left,

				el_height = el.outerHeight(true),

				el_width = el.outerWidth(),

				el_position = el.css("position"),

				el_position_top = el.css("top"),

				el_margin_top = parseInt(el.css("marginTop"),10),

				doc_height=$(document).height(),

				max_height = $(document).height() - config.offset.bottom,

				top = 0,

				swtch = false,

				locked=false,

				pos_not_fixed = false;

				/* we prefer feature testing, too much hassle for the upside */

				/* while prettier to use position: fixed (less jitter when scrolling) */

				/* iOS 5+ + Andriud has fixed support, but issue with toggeling between fixed and not and zoomed view, is iOs only calls after scroll is done, so we ignore iOS 5 for now */

				if (config.forcemargin === true || navigator.userAgent.match(/\bMSIE (4|5|6)\./) || navigator.userAgent.match(/\bOS (3|4|5|6)_/) || navigator.userAgent.match(/\bAndroid (1|2|3|4)\./i)){

					pos_not_fixed = true;

				}

				$(window).bind('scroll resize orientationchange load',el,function(e){

					if(doc_height !== $(document).height()) {

						max_height = $(document).height() - config.offset.bottom;

						doc_height=$(document).height();

					}

					//Offset can change due to dynamic elements at the top. So measure it everytime.
					if(locked == false) {

						el_top = el.offset().top;

					}
					var el_height = el.outerHeight(),

						scroll_top = $(window).scrollTop();

					//if we have a input focus don't change this (for ios zoom and stuff)
					if(pos_not_fixed && document.activeElement && document.activeElement.nodeName === "INPUT"){

						return;
					}

					locked=true;

					if (scroll_top >= (el_top-(el_margin_top ? el_margin_top : 0)-config.offset.top)){

						if(max_height < (scroll_top + el_height + el_margin_top + config.offset.top)){

							top = (scroll_top + el_height + el_margin_top + config.offset.top) - max_height;

						}else{
							top = 0;
						}

						if (pos_not_fixed){

							//if we have another element above with a new margin, we have a problem (double push down)

							//recode to position: absolute, with a relative parent

							el.css({'marginTop': parseInt(((el_margin_top ? el_margin_top : 0) + (scroll_top - el_top - top) + 2 * config.offset.top),10)+'px'});

						}else{
							el.css({'position': 'fixed','top':(config.offset.top-top)+'px', 'width':el_width +"px"});
						}
					}else{
						locked=false;
						el_left = el.offset().left;
						el.css({'position': el_position,'top': el_position_top, 'left': el_left, 'width':el_width +"px", 'marginTop': (el_margin_top ? el_margin_top : 0)+"px"});
					}
				});
			}
		}
	});
})(jQuery);

/*
function not_blocked(business_state, free_trial, campaign_state){

    var limit = 0;

    if (free_trial == 'False'){
        limit = 0;
    }
    else if(free_trial == 'True' && campaign_state != "Inactive" ){
        if (business_state == 'aplicantes'){
            limit = 10;
        }else{
            limit = 1;
        }
    }else{
        limit = 0;
    }

    var candidate_divs= $('.candidate-div a');
    for (var i = 0; i < limit; i++) {
        $(candidate_divs[i]).attr('href', $(candidate_divs[i]).attr('href').replace('/remove',''));
        $(candidate_divs[i]).attr('onclick', "");

    }
    var candidate_divs= $('.candidate-div span');
    for (var i = 0; i < limit; i++) {
        $(candidate_divs[i]).hide();
    }
}*/


function request_candidates(state, campaign_id){

    let base_url = 'https://peaku.co' //'http://127.0.0.1:8000'
    let current_num = $('#' + state + ' > div').length; // count direct descendants tags div...

    if (LAST_SHOWING_ROWS[state] < current_num){
        LAST_SHOWING_ROWS[state] = current_num

        let url = `${base_url}/seleccion-de-personal/tablero-de-control/${campaign_id}/request-candidates?current_num=${current_num}&state=${state}`;
        console.log(url)

        $.ajax({
            type: 'GET',
            url: url,
            processData: false,
            contentType: false
        }).done(function(data) {
            $('#' + state).append(data);
        });
    }
}
