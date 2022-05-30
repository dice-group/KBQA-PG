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

    clear_error_loading_area();
    show_loading_area();

    var form = $(this);
    var url = form.attr("action");

    $.ajax({
      type: "POST",
      url: url,
      data: form.serialize(),
      success: function (data) {
        clear_error_loading_area();
        load_answer_area(data);
        show_hide_query();
        scroll_to_answer_area();
      },
      error: function (request, status, error) {
        clear_error_loading_area();
        handle_errors(request.status);
      },
    });
  });
}

function handle_errors(error_code) {
  var error_msg = "";

  if (error_code == 400) {
    error_msg == "The request was not in a correct format (400: Bad request)";
  } else if (error_code == 500) {
    error_msg =
      "There seems to be a problem in the endpoint. Please try again later (500: Internal Server Error)";
  } else if (error_code == 502) {
    error_msg =
      "The server is not able to process your request. Please try again later (502: Bad Gateway)";
  } else if (error_code == 504) {
    error_msg =
      "The endpoint is taking too long to find an answer. Please try another question (504: Gateway Timeout)";
  } else {
    error_msg = "An unknown error occured";
  }

  show_error_msg(error_msg);
  console.log(error_msg);
}
