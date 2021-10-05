{% assign url_arr = page.url | split: "/" %}
{% assign underscore_name_list = url_arr[2] | split: "." %}
{% assign underscore_name = underscore_name_list[0] %}
{% assign category_name = url_arr[1] %}

<div class="floatright" markdown="1">

<a href="{{category_name}}_{{underscore_name}}.gif">
<img src="{{category_name}}_{{underscore_name}}.gif" alt="environment gif" />
</a>

This environment is part of the [{{category_name}} environments](../{{category_name}}). Please read that page first for general information.


{% if page.state-shape and page.average-total-reward %}
Name | Value
--- | ---
Actions | {{ page.actions }}
Agents | {{ page.agents }}
Parallel API | {% if page.is_parallel %} Yes {% else %} No {% endif %}
Manual Control | {{ page.manual-control }}
Action Shape | {{ page.action-shape }}
Action Values | {{ page.action-values }}
Observation Shape | {{ page.observation-shape }}
Observation Values | {{ page.observation-values }}
Import | `{{ page.import }}`
Agents | `{{ page.agent-labels }}`
State Shape | {{ page.state-shape }}
State Values | {{ page.state-values }}
Average Total Reward | {{ page.average-total-reward }}
{% elsif page.state-shape %}
Name | Value
--- | ---
Actions | {{ page.actions }}
Agents | {{ page.agents }}
Parallel API | {% if page.is_parallel %} Yes {% else %} No {% endif %}
Manual Control | {{ page.manual-control }}
Action Shape | {{ page.action-shape }}
Action Values | {{ page.action-values }}
Observation Shape | {{ page.observation-shape }}
Observation Values | {{ page.observation-values }}
Import | `{{ page.import }}`
Agents | `{{ page.agent-labels }}`
State Shape | {{ page.state-shape }}
State Values | {{ page.state-values }}
{% elsif page.average-total-reward %}
Name | Value
--- | ---
Actions | {{ page.actions }}
Agents | {{ page.agents }}
Parallel API | {% if page.is_parallel %} Yes {% else %} No {% endif %}
Manual Control | {{ page.manual-control }}
Action Shape | {{ page.action-shape }}
Action Values | {{ page.action-values }}
Observation Shape | {{ page.observation-shape }}
Observation Values | {{ page.observation-values }}
Import | `{{ page.import }}`
Agents | `{{ page.agent-labels }}`
Average Total Reward | {{ page.average-total-reward }}
{% else %}
Name | Value
--- | ---
Actions | {{ page.actions }}
Agents | {{ page.agents }}
Parallel API | {% if page.is_parallel %} Yes {% else %} No {% endif %}
Manual Control | {{ page.manual-control }}
Action Shape | {{ page.action-shape }}
Action Values | {{ page.action-values }}
Observation Shape | {{ page.observation-shape }}
Observation Values | {{ page.observation-values }}
Import | `{{ page.import }}`
Agents | `{{ page.agent-labels }}`
{% endif %}


#### Agent Environment Cycle

<a href="/assets/img/aec/{{category_name}}_{{underscore_name}}_aec.svg">
<img src="/assets/img/aec/{{category_name}}_{{underscore_name}}_aec.svg" alt="environment aec diagram" />
</a>

</div>
