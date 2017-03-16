# P6: Data Visualization
Peter Eisenschmidt

## Summary

The visualization depicts the final standings of the first division of the German Bundesliga between 1996 and 2016.

## Design

### First Idea
The following [pdf](first_sketch.pdf) shows a first sketch of how I want to visualize the data. The idea is to display the data in a table where each row is for the standing and each column for each year.

The table contains the number of points for each standing/year. When selecting a standing (e.g. 1 for the champion or 16 to 18 for the relegated teams), a line chart should display the points for that standing for all years. The aim is to show if there are trends over the years, for example 
the number of points required to win the championship or avoid relegation to 2nd division.

Finally, when hovering the mouse over a data entry the name of the team should be displayed.

### First Version



## Feedback

### Feedback Number 1:

* What do you notice in the visualization?
	1.	I see the growing gap between the first ranked team to rest of the teams 
	2.	Intense competition amongst teams in the middle of the table 
* What questions do you have about the data?
	1.	Would be interested to actually know the team?
* What relationship do you notice?
	1. I do not see a relationship per se. It�s not clear whether I need to draw any relationship from this chart. One thing I notice however though trends in points of lower ranked teams and higher ranked teams are sort of inversely proportional but top ranked team and the bottom ranked teams are not really correlated.
* What do you think is the main takeaway from this visualization?
	1. It looks like Bundesliga is dominated by one team lately not having a clear contender against the top ranked team.
* Is there something you don�t understand in the graphic?
	1. Not really. I would just add it is slightly bothersome with flashing screen when highlighting different row. 

### Feedback Number 2:
* What do you notice in the visualization?
	1.	The deviation between the teams in the lower ranks is quite constant throughout the years. However, you can notice a growing gap between the first place and the remaining teams
* What questions do you have about the data?
	1.	None really, but it could be interesting to see the correlation to other data such as investments in players
* What relationship do you notice?
	1.  In some years you can notice that the points of the individual standings follow similar trends, as can be seen in 2002 or 2011
* What do you think is the main takeaway from this visualization?
	1. Maybe that the Bundesliga would be more interesting without Bayern Munich
* Is there something you don�t understand in the graphic?
	1. I think I understood everything

### Feedback Number 3:

1. What do you notice in the visualization? 
> The Bundesliga standings for the years 1996 till 2016.  The red curve illustrates for a particular point score the yearly distribution. 
2. What questions do you have about the data?
> Are the point scores similar for all the years, were the same grading principles applied? What influenced the increase in the top score for years 2013-2014?
3. What relationship do you notice?
> It comes to my notice that that point scores are similar for all the years lying within a certain band (horizontal curve)
4. What do you think is the main takeaway from this visualization?  
> I would assume we could take the average of point scores for a year which quite characterises the data for each point score.
5. Is there something you don�t understand in the graphic?
> It took sometime to realize what is shown in the table. For someone who doesn't follow soccer it is not really obvious what the numbers mean.
	
	
## Resources

The data is obtained from http://www.football-data.co.uk/ . It was processed using Python in order to get the final standings per year and to create the csv file used for the visualization.

The code for the table creation is inspired by this example:
http://bl.ocks.org/LeeMendelowitz/11383724


http://stackoverflow.com/questions/19757638/how-to-pivot-a-table-with-d3-js
http://stackoverflow.com/questions/14567809/how-to-add-an-image-to-an-svg-container-using-d3-js

http://bl.ocks.org/ilyabo/1373263

http://bl.ocks.org/d3noob/a22c42db65eb00d4e369