$('.ttbutton').tooltip({container: 'body'});
(function($) {
    var cover = $('.cover');
    cover.css({'background-image': "url('" + cover.data('bg') + "')"});
})(jQuery);
