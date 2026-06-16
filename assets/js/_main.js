/* ==========================================================================
   jQuery plugin settings and other scripts
   ========================================================================== */

$(document).ready(function () {
  function bumpFooter() {
    $("body").css("margin-bottom", $(".page__footer").outerHeight(true));
  }

  bumpFooter();
  $(window).on("resize", bumpFooter);

  function stickySideBar() {
    var show = $(".author__urls-wrapper button").length === 0
      ? $(window).width() > 925
      : !$(".author__urls-wrapper button").is(":visible");

    if (show) {
      $(".author__urls").show();
    } else {
      $(".author__urls").hide();
    }
  }

  stickySideBar();
  $(window).on("resize", stickySideBar);

  $(".author__urls-wrapper button").on("click", function () {
    $(".author__urls").fadeToggle("fast");
    $(".author__urls-wrapper button").toggleClass("open");
  });

  $("a").smoothScroll({ offset: -72 });
});
