// This is what changes body from hidden
(function($) {
	//if ($(window).width() >= 1024) {
	//	$('html, body').animate({scrollTop:20}, 300);
	//}
})(jQuery);

$(document).ready(function() {

	$('#my_popup').popup({
		type: 'overlay',
		transition: 'all 0.3s',
	});

    $('a[href=#top]').click(function(){
		if ($(window).width() >= 800) {
			$('html, body').animate({scrollTop:0}, 300);
			$('html, body').animate({scrollTop:20}, 300);
		}
		else {
			$('html, body').animate({scrollTop:0}, 300);
		}
        return false;
    });
    $('a[href=#contacts]').click(function(){
		jump('#contacts');
        return false;
    });
    $('a[href=#overview]').click(function(){
		jump('#overview');
        return false;
    });
    $('a[href=#news]').click(function(){
		jump('#news');
        return false;
    });
    $('a[href=#schedule]').click(function(){
		jump('#schedule');
        return false;
    });
    $('a[href=#tutorial]').click(function(){
		jump('#tutorial');
        return false;
    });
    $('a[href=#homework]').click(function(){
		jump('#homework');
        return false;
    });
    $('a[href=#exams]').click(function(){
		jump('#exams');
        return false;
    });
    $('a[href=#policies]').click(function(){
		jump('#policies');
        return false;
    });
    $('a[href=#links]').click(function(){
		jump('#links');
        return false;
    });

});

function jump(id) {
	var position = $(id).position();
	var curr_pos = $(document).scrollTop();

	var page_height = $(document).height();
	var window_height = $(window).height();

	var bottom = page_height - window_height - 50;
	var bottom_bounce = page_height - window_height - 10;

	if (position.top > bottom) {
		$('html, body').animate({scrollTop:bottom_bounce}, 300);
		$('html, body').animate({scrollTop:bottom}, 300);
	}
	else {
		if (curr_pos + 48 >= position.top) {
			$('html, body').animate({scrollTop:position.top - 78}, 300);
			$('html, body').animate({scrollTop:position.top - 48}, 300);
		}
		else {
			$('html, body').animate({scrollTop:position.top - 18}, 300);
			$('html, body').animate({scrollTop:position.top - 48}, 300);
		}
	}
}

