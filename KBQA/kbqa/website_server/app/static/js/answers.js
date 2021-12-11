function load_answer_area(data) {
  var question = data["question"];
  var answers = data["answers"];
  var query = data["query"];
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
  var code = document.createElement("code");
  code.innerHTML = query;

  pre.appendChild(code);
  query_content.appendChild(pre);
  query_div.appendChild(query_btn);
  query_div.appendChild(query_content);
  answer_area.appendChild(query_div);

  answer_area.style.display = "block";
}
