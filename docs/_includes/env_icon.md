{% assign url_arr = page.url | split: "/" %}
{%- if url_arr[1] == "magent" -%}
    {% assign category_name = "MAgent" %}
{%- elsif url_arr[1].size < 5 -%}
    {% assign category_name = url_arr[1] | upcase %}
{%- else -%}
    {% assign category_name = url_arr[1] | capitalize %}
{%- endif -%}
{%- if page.alt_title -%}
    {% assign img_link = "/assets/img/icons/" | append: category_name | append: "/" | append: page.alt_title | replace: " ", "" | replace: ":", "" | append: ".png" %}
{%- else -%}
    {% assign img_link = "/assets/img/icons/" | append: category_name | append: "/" | append: page.title | replace: " ", "" | replace: ":", "" | append: ".png" %}
{%- endif -%}
<img class="env-icon" src="{{ img_link }}">