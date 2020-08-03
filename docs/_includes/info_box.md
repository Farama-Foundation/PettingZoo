{% assign url_arr = page.url | split: "/" %}
{% assign underscore_name_list = url_arr[2] | split: "." %}
{% assign underscore_name = underscore_name_list[0] %}
{% assign category_name = url_arr[1] %}

<div class="floatright" markdown="1">

<a href="{{category_name}}_{{underscore_name}}.gif">
<img src="{{category_name}}_{{underscore_name}}.gif" alt="environment gif" />
</a>

This environment is part of the [{{category_name}} environments](../{{category_name}}). Please read that page first for general information.

Name | Value
--- | ---
Actions | {{ page.actions }}
Agents | {{ page.agents }}
Manual Control | {{ page.manual-control }}
Action Shape | {{ page.action-shape }}
Action Values | {{ page.action-values }}
Observation Shape | {{ page.observation-shape }}
Observation Values | {{ page.observation-values }}
Import | `{{ page.import }}`
Agents | `{{ page.agent-labels }}`
{% if page.average-total-reward %}Average Total Reward | {{ page.average-total-reward }}{% endif %}

{% if page.aec-diagram %}
![AEC diagram]({{page.aec-diagram}})
{% endif %}

</div>

## {{page.title}}
