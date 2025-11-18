$(function(){
  function search() {
      var txt = $('input#search').val();
      if (txt) {
          var url = "https://www.ecosia.org/search?q=site:" + window.location.hostname + " " + encodeURIComponent(txt);
          window.open(url, '_blank');
      }
  }
  $('input#search').on('keydown', function(e) {
      if (e.which == 13) {
          e.preventDefault();
          search();
      }
  });
  $('input#submit-search').on('click', function(e) {
      e.preventDefault();
      search();
  });
});
