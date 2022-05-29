function load_answer_area(data) {
  var question = data["question"];
  var answers = data["answers"];
  var query = data["query"];

  query = format_sparql_query(query);
  query = query.replace(/</g, "&lt;");
  query = query.replace(/>/g, "&gt;");

  var answer_area = document.getElementById("answer_area");
  answer_area.innerHTML = "";

  var line1 = document.createElement("hr");
  line1.className = "hline";

  var line2 = document.createElement("hr");
  line2.className = "hline";

  // ------- question -------

  var question_div = document.createElement("div");
  var question_field = document.createElement("h2");
  question_field.className = "titles question";
  question_field.innerHTML = '"' + question + '"';

  question_div.appendChild(question_field);
  answer_area.appendChild(question_div);

  answer_area.appendChild(line1);

  // ------- answer -------

  var answer_div = document.createElement("div");

  var answer_list = document.createElement("ul");
  answer_list.className = "answer_list";

  for (const answer of answers) {
    var answer_element = document.createElement("li");
    answer_element.className = "answer_element";
    answer_element.innerHTML = answer;
    answer_list.appendChild(answer_element);
  }

  answer_div.appendChild(answer_list);
  answer_area.appendChild(answer_div);

  answer_area.appendChild(line2);

  // query
  var query_div = document.createElement("div");
  query_div.id = "query_field";

  var query_btn = document.createElement("input");
  query_btn.type = "button";
  query_btn.id = "query_btn";
  query_btn.className = "query_btn";
  query_btn.value = "Show SPARQL-Query";

  var query_content = document.createElement("div");
  query_content.className = "query";

  var pre = document.createElement("pre");
  pre.className = "query_display";
  pre.innerHTML = query;

  query_content.appendChild(pre);
  query_div.appendChild(query_btn);
  query_div.appendChild(query_content);
  answer_area.appendChild(query_div);

  answer_area.style.display = "block";
}

function show_error_msg(error_msg) {
  var error_area = document.getElementById("error_area");
  error_area.innerHTML = error_msg;
}

function show_loading_area() {
  var loading_area = document.getElementById("loading_area");
  loading_area.innerHTML = "";

  // Most parts are copied from https://www.w3schools.com/howto/howto_css_loader.asp
  var loader = document.createElement("div");
  loader.className = "loader";

  loading_area.appendChild(loader);
}

function clear_error_loading_area() {
  var error_area = document.getElementById("error_area");
  error_area.innerHTML = "";

  var loading_area = document.getElementById("loading_area");
  loading_area.innerHTML = "";
}

function format_sparql_query(query) {
  keywords = [
    "SELECT",
    "DISTINCT",
    "WHERE",
    "ASK",
    "UNION",
    "FILTER",
    "CONSTRUCT",
    "LIMIT",
    "OFFSET",
    "COUNT",
    "GROUP",
    "BY",
    "OFFSET",
  ];

  // replace keywords with upper case keywords
  for (const keyword of keywords) {
    query = query.replace(keyword.toLowerCase(), keyword);
  }

  var open_pattern = /( )*\{( )*/g;
  query = query.replace(open_pattern, "{\n");

  var close_pattern = /( )*\}( )*/g;
  query = query.replace(close_pattern, "\n} ");

  var point_pattern = /( )+\.|\.( )+/g;
  query = query.replace(point_pattern, " .\n");

  var semicolon_pattern = /( )+\;|\;( )+/g;
  query = query.replace(semicolon_pattern, " ;\n     ");

  // format keywords
  var where_pattern = /( )*WHERE( )*/g;
  query = query.replace(where_pattern, "\nWHERE ");

  var union_pattern = /( )*UNION( )*/g;
  query = query.replace(union_pattern, " UNION ");

  var limit_pattern = /( )*LIMIT( )*/g;
  query = query.replace(limit_pattern, "\nLIMIT ");

  var order_pattern = /( )*ORDER BY( )*/g;
  query = query.replace(order_pattern, "\nORDER BY ");

  var group_pattern = /( )*GROUP BY( )*/g;
  query = query.replace(group_pattern, "\nGROUP BY ");

  var having_pattern = /( )*HAVING( )*/g;
  query = query.replace(having_pattern, "\nHAVING ");

  var offset_pattern = /( )*OFFSET( )*/g;
  query = query.replace(offset_pattern, "\nOFFSET ");

  // add indents
  var indents = 0;
  var formated_query = "";

  for (var i = 0; i < query.length; i++) {
    if (query.charAt(i) == "\n") {
      if (query.charAt(i - 1) == "{") {
        indents++;

        formated_query += "\n" + "    ".repeat(indents);
      } else if (query.charAt(i + 1) == "}") {
        indents--;

        if (indents >= 0) {
          formated_query += "\n" + "    ".repeat(indents);
        }
      } else {
        formated_query += "\n" + "    ".repeat(indents);
      }
    } else {
      formated_query += query.charAt(i);
    }
  }

  // remove empty lines
  var empty_line_pattern = /^\s*[\r\n]/gm;
  formated_query = formated_query.replace(empty_line_pattern, "");

  return formated_query;
}
