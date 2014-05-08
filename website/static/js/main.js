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
