function initialize() {
  //scroll_to_answer_area();
  submit_question();
}

function scroll_to_answer_area() {
  var answer_area = document.getElementById("answer_area");
  answer_area.style.display = "block";
  answer_area.scrollIntoView({ behavior: "smooth" });
}

function show_hide_query() {
  $(document).ready(function () {
    $("#query_btn").click(function () {
      $(".query").slideToggle("fast", function () {
        if ($(this).is(":visible")) {
          $("#query_btn").prop("value", "Hide SPARQL-Query");
        } else {
          $("#query_btn").prop("value", "Show SPARQL-Query");
        }
      });
    });
  });
}

function submit_question() {
  $(".form_input").submit(function (event) {
    event.preventDefault();

    var form = $(this);
    var url = form.attr("action");

    $.ajax({
      type: "POST",
      url: url,
      data: form.serialize(),
      success: function (data) {
        load_answer_area(data);
        show_hide_query();
        scroll_to_answer_area();
      },
    });
  });
}
