# Example: same question, two users (secure mode)

Generated with `python -m securerag compare --left maya --right jonathan` on the sample Lakeside Auto Group corpus. Fictional figures.

Same question, two users. Mode: secure.
========================================================================
LEFT
User: Maya Chen · Service Advisor · Lakeside Honda
Role / store / clearance: Service Advisor · Lakeside Honda · internal
Mode: secure
Question: What is the general manager pay plan at Lakeside Honda?

Answer:
I don't have any documents you are allowed to see that answer this question.

Retrieved 0 chunk(s) from 18 candidates after the filter.
Filtered out before ranking: 43 chunk(s) (24 confidential, 5 internal, 14 restricted). Their content is not shown.

========================================================================
RIGHT
User: Jonathan Hale · CFO · Group / all stores
Role / store / clearance: CFO · Group / all stores · restricted
Mode: secure
Question: What is the general manager pay plan at Lakeside Honda?

Answer:
Lakeside Honda General Manager pay plan for calendar year 2026 (sample — fictional figures). [1] Base salary is $185,000, paid biweekly. [1] This plan applies to Patricia Walsh, General Manager of Lakeside Honda. [1]

Citations:
  [1] General Manager pay plan — Lakeside Honda — 2026 (restricted, hr-pay-plan-gm-honda)

Retrieved 3 chunk(s) from 60 candidates after the filter.
Filtered out before ranking: 1 chunk(s) (1 restricted). Their content is not shown.

Retrieved chunks (with ACL tags):
  - General Manager pay plan — Lakeside Honda — 2026  score=0.234  sensitivity=restricted  roles=hr_director,cfo  stores=honda
    Lakeside Honda General Manager pay plan for calendar year 2026 (sample — fictional figures). This plan applies to Patricia Walsh, General Manager of Lakeside Honda. Distribution is limited to the CFO and the HR Director.  Base salary is $185,000, paid biweekly. The variable plan 
  - Honda store headcount extract — October 2026  score=0.119  sensitivity=confidential  roles=gm,hr_director,cfo  stores=honda
    Lakeside Honda headcount extract as of October 31, 2026 (sample). This extract is for the Honda GM, the HR Director, and the CFO. It does not include pay rates.  Honda headcount is 78: sales 22, F&I 4, service 28, parts 8, office and porters 16. Open requisitions at this store: t
  - Store P&L — Lakeside Honda — October 2026  score=0.113  sensitivity=confidential  roles=gm,cfo,controller  stores=honda
    Lakeside Honda monthly P&L for October 2026 (sample — fictional figures). Distribution is the Honda General Manager, the CFO, and the Controller. Other store GMs and department employees do not receive this file.  October revenue is $4,820,000. Departmental gross: new $410,000, u
