$('.ttbutton').tooltip({container: 'body'});
$('.ttbuttonbot').tooltip({container: 'body', placement: 'left'});

var cover = $('.page-header.cover'),
    mask = $('.page-header .mask');
(function rotate_cover() {
  if (cover.length < 1) return;

  $.getJSON('/random-feature-photo', function(data) {
    var photo_url = 'url(\'' + data.photo + '?size=1140\')';
    mask.addClass('fade-in')
        .css('background-image', photo_url);
    $('.photo-showoff .title').text(data.title);
    setTimeout(function() {
      cover.css('background-image', photo_url);
      mask.removeClass('fade-in');
    }, 1500);
  });
  t = setTimeout(rotate_cover, 6000);
})();

var keep_reading_link = $('[href="#keep-reading-studying-here"]'),
    keep_reading_content = $('#keep-reading-studying-here');
(function keep_reading() {
  if (keep_reading_link.length < 1) return;
  keep_reading_content.hide();
  keep_reading_link.on('click', function readMore(e) {
    e.preventDefault();
    keep_reading_link.remove();
    keep_reading_content.slideDown();
  });
})();
