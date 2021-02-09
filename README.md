# Data-Driven Drone Deployment Models for WildfireManagement
MCM Spring 2021 Repo
Bohan Wu, Kevin Zheng, Shaan Nagy
<a href="/blob/main/paper.pdf" >The paper can be found here.</a>
![alt text](https://bloximages.newyork1.vip.townnews.com/ifiberone.com/content/tncms/assets/v3/editorial/8/82/88246d38-9f5b-11e8-a835-cb2c775cdd7b/5b72269f088c8.image.png?resize=400%2C247)

The use of drone technology in wildfire management is a popular topic in the emergency response community. In particular, the use of drones for communications and situational surveillance has received much attention. In this paper we develop two drone deployment models:

• First, we develop a genetic algorithm to position communications drones in a given fire event.

• Second, we engineer a geographic and topologically inspired approach for surveillance drone
deployment along the perimeter of the fire.

In addition to the drone deployment models, we implement a clustering method based on Hartigan’s Leader Algorithm to aggregate the satellite fire points into distinct ”fire events”, each of which can be managed by a single EOC and its drone deployment system. These ”fire events” define the local environments in which the two drone models execute.
To project future wildfire trends, we implemented an multivariate ARIMA model with exogenous climate predictors to predict the change in monthly average area burned by wildfire(in km2) during 2020-2030 based on historical data from 2012-2021. In particular, we look at the year 2025 and illustrate how our model will adapt to the increasing fire size and prolonging fire season in the upcoming decade.

We then integrate these drone models into a global drone deployment strategy which is capable of assigning drones to fire events. The optimal deployment strategy may then be discovered by solving a nuanced optimization optimization problem.
