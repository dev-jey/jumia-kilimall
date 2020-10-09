$('#search-icon').click(() => {
  $('#search-icon').hide();
  $('#search-bar').show();
})

$('#arrow').click(() => {
  $('#search-bar').hide();
  $('#search-icon').show();
})

$('#search-bar').submit((e) => {
  e.preventDefault();
  var search = $('#search-text').val();
  window.location.replace(`/search?key=${search}`);
})