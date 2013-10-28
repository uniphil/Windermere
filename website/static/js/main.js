$('.ttbutton').tooltip({container: 'body'});
$('.ttbuttonbot').tooltip({container: 'body', placement: 'left'});
(function($) {
    var cover = $('.cover');
    cover.css({'background-image': "url('" + cover.data('bg') + "')"});
})(jQuery);
