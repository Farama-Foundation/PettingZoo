{% assign url_arr = page.url | split: "/" %}
{% assign category_name = url_arr[1] | capitalize %}
{% assign img_link = "/assets/img/icons/" | append: category_name | append: "/" | append: page.title | replace: " ", "" | replace: ":", "" | append: ".png" %}
<img class="env-icon" src="{{ img_link }}">