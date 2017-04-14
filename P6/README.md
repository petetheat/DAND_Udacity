# P6: Data Visualization
Peter Eisenschmidt

## Summary

The visualization depicts the final standings of the first division of the German Bundesliga between 1996 and 2016 for the Top 5 Teams. The goal is to show how a single team 
(Bayern Munich) has dominated the Bundesliga in the past 21 years.

## Design

### Data

The data is obtained from [www.football-data.co.uk](http://www.football-data.co.uk). I have chosen Bundesliga First Division data from 1996 till 2016, as the 
1995/96 season was the first season where the 3-points-for-a-win rule was adopted in Germany. Therefore, previous years wouldn't be comparable.

The data there contains the full results for each game. I used Python to calculate the points, total scored and conceded goals for each team and its 
corresponding standing for each year and wrote this to the file `bundesliga_stats.csv`. The file contains 378 observations (18 teams x 21 years) and looks as follows:

```
year,standing,teams,points,diff,goals,goals_conceded
1996,1,Dortmund,68,38.0,76.0,38.0
1996,2,Bayern Munich,62,20.0,66.0,46.0
1996,3,Schalke 04,56,9.0,45.0,36.0
1996,4,M'gladbach,53,1.0,52.0,51.0
......
2016,14,Darmstadt,38,-15.0,38.0,53.0
2016,15,Hoffenheim,37,-15.0,39.0,54.0
2016,16,Ein Frankfurt,36,-18.0,34.0,52.0
2016,17,Stuttgart,33,-25.0,50.0,75.0
2016,18,Hannover,25,-31.0,31.0,62.0
``` 

### First Idea

The following image shows a first sketch of how I wanted to visualize the data. 

![alt text][logo]

[logo]: first_sketch.png "First sketch"

The idea was to display the data in a table where each row is for the standing and each column for each year.

The table contains the number of points for each standing/year. When selecting a standing (e.g. 1 for the champion or 16 to 18 for the relegated teams), a 
line chart should display the points for that standing for all years. The aim is to show if there are trends over the years, for example the number of 
points required to win the championship or avoid relegation to 2nd division.

Finally, when hovering the mouse over a data entry the name of the team should be displayed.

I chose a table and a line chart for the following reasons: A table as it allows looking up the precise number of points for a given year and a line chart as it
allows determining trends in the data that are not directly visible in the table. I think as both chart types complement each other it is an efficient way to
convey the message that the Bundesliga is drifting apart. 

### First Version

When I first thought about how to visualize the data I imagined the table below the line chart. The line chart was supposed to display only the selected
standing. However, when I plotted the data in Python I saw that displaying all lines at the same time allowed seeing similar patters over the years, especially
in the lower point region. So I decided to plot all 18 lines at the same time and to allow the user to select a specific line by hovering the mouse over
the corresponding row in the table.

As displaying all lines at the same time required to increase the size if the SVG element, I also decided to invert the order of the table and the line chart: 
Instead of having the line chart on top of the table I placed it below.

For the first version I did not implement tooltips as they seemed rather complicated at first and I was not sure whether the team information was really
required to convey the message about how the Bundesliga is drifting apart.

Finally, I added the Bundesliga logo in the lower right bottom of the SVG element. The reason is that the logo is well known and seeing it might help people
understand quicker what is displayed in the visualization.

![alt text][logo2]

[logo2]: first_chart.png "First version"

The corresponding file is **`index_version1.html`**.

### Second Version

The feedback that I got (see next section) as all four people I asked for feedback noticed exactly what I wanted to convey with this visualization: The 
growing gap between a few top teams and the rest of the Bundesliga.

However, I noticed that it makes a huge difference if the person looking at the visualization is interested in soccer and follows the Bundesliga closely or if they
are not at all interested in it. The first group of people having a certain background knowledge understands immediately what the numbers in the table mean. 
The second group of people struggles at first as the table doesn't mean anything to them. This is why I added an explanatory sentence above the table.

I added the source of the data at the bottom. That was not based on any of the remarks I got but I think it is important to be transparent about where the 
data comes from.

Secondly, people remarked that when hovering over the table rows quickly the transition effect (I set the transition to 250 ms) caused a lot of rows to turn black.
Looking more closely into that I found out that this effect was even worse when using Internet Explorer 11 (I use Chrome and did all my checks there obviously without
checking the display on other browsers). As you don't know which browser your audience uses I decided to remove the transition effects completely. Comparing the
first and final version that even in Chrome it is more pleasing to the eye without the transition effects.

Thirdly, people said that it was good to highlight the line when hovering over a row but that it would be good to have the same effect vice versa, i.e. 
highlighting a row when hovering over a line. As all line are displayed at the same time you cannot see which position that line corresponds to. So, the 
visualization now allows interactivity in both directions.

I also aligned the circles of the line chart with the table columns, so that it makes it easier to find the year that you are looking at.

Lastly, as people told me that they would like to know which teams are behind the numbers (to see for example which team has actually dominated the Bundesliga
in recent years, as not everyone knows that) I added tooltips in both the table and the line chart that display the team name, the number of points, and
also the goal difference as often this is needed as tie breaker.  

This was something that I wanted to include from the beginning (see the first sketch) but at first it seemed too complicated in D3 so I left it out in the first
version. After the feedback however I decided to put it in the final version despite the headache it caused to implement it.

![alt text][logo3]

[logo3]: second_chart.png "Second version"

The corresponding file is **`index_version2.html`**.

### Third Version

After the first submission (see feedback below) I modified the visualization as follows: Firstly, I changed the header and the description to highlight that it
is actually only one team that really dominates the Bundesliga, namely Bayern Munich. This is emphasized by the introductory text that summarizes quickly Bayern's 
achievements over the past 21 years. 

Secondly, to show that I moved the line chart up again above the table. As Bayern has always been in the top ranked teams, the line chart only shows the Top 5 teams now.
In addition to that the team logos are displayed in order to allow the reader to see immediately Bayern's presence in the top ranks. 

The table at the bottom allows the reader to explore more details about other teams as well. 

![alt text][logo4]

[logo4]: third_chart.png "Third version"

The corresponding file is **`index_version3.html`**.

### Final Version

The feedback from the second review was that the visualization was potentially confusing (see details in the feedback section). I therefore changed the title of the line chart to **Top 5 Standings** instead of **Top 5 Teams**,
as this is what is actually displayed.

Also, as the message is how Bayern Munich dominates the Bundesliga, only Bayern's logo is now displayed at its corresponding standings. This allows seeing immediately where Bayern was placed in the past 21 years. To make sure that
everyone understand what this logo means, I have added it on top of the line chart big enough to see what it represents.

Lastly, as only the first 5 standings are displayed the corresponding rows of the table are highlighted in the same color as the lines.

![alt text][logo5]

[logo5]: final_chart.png "Final version"

The corresponding file is **`index.html`**.

## Feedback

I gathered feedback from 4 different people. Their background is different (2 engineers, 1 teacher, 1 photographer) and also their interest for soccer varies
from "I have no clue about soccer and I don't really care" to "I know the Bundesliga by heart".

### Feedback Number 1:

1. What do you notice in the visualization?
> I see the growing gap between the first ranked team to rest of the teams and intense competition amongst teams in the middle of the table 
2. What questions do you have about the data?
> Would be interested to actually know the team?
3. What relationship do you notice?
> I do not see a relationship per se. It’s not clear whether I need to draw any relationship from this chart. One thing I notice however though trends in points of lower ranked teams and higher ranked teams are sort of inversely proportional but top ranked team and the bottom ranked teams are not really correlated.
4. What do you think is the main takeaway from this visualization?
> It looks like Bundesliga is dominated by one team lately not having a clear contender against the top ranked team.
5. Is there something you don’t understand in the graphic?
> Not really. I would just add it is slightly bothersome with flashing screen when highlighting different row. 

### Feedback Number 2:
1. What do you notice in the visualization?
> The deviation between the teams in the lower ranks is quite constant throughout the years. However, you can notice a growing gap between the first place and the remaining teams
2. What questions do you have about the data?
> None really, but it could be interesting to see the correlation to other data such as investments in players
3. What relationship do you notice?
> In some years you can notice that the points of the individual standings follow similar trends, as can be seen in 2002 or 2011
4. What do you think is the main takeaway from this visualization?
> Maybe that the Bundesliga would be more interesting without Bayern Munich
5. Is there something you don’t understand in the graphic?
> I think I understood everything

### Feedback Number 3:

1. What do you notice in the visualization? 
> The Bundesliga standings for the years 1996 till 2016.  The red curve illustrates for a particular point score the yearly distribution. 
2. What questions do you have about the data?
> Are the point scores similar for all the years, were the same grading principles applied? What influenced the increase in the top score for years 2013-2014?
3. What relationship do you notice?
> It comes to my notice that that point scores are similar for all the years lying within a certain band (horizontal curve)
4. What do you think is the main takeaway from this visualization?  
> I would assume we could take the average of point scores for a year which quite characterises the data for each point score.
5. Is there something you don’t understand in the graphic?
> It took sometime to realize what is shown in the table. For someone who doesn't follow soccer it is not really obvious what the numbers mean.

### Feedback Number 4:

1. What do you notice in the visualization? 
>  It is pretty cool that you can highlight the lines by selecting a row
2. What questions do you have about the data?
> It would be good to know which teams are behind the values. For instance, I'd be interested to see how Werder Bremen performed throughout the years.
3. What relationship do you notice?
> The curves in the middle range are more homogeneous and closer together. The upper curves and also the lowest ranked curve shows bigger differences to the 
> other lines 
4. What do you think is the main takeaway from this visualization?  
> About 20 years ago, the points were more evenly distributed over the table. In the past few years, the top 50% of points seem to be taken by 4-5 teams only and the bottom 50% of points are taken by the remaining 13-14 teams.
5. Is there something you don’t understand in the graphic?
> At first I thought the points of the line chart were aligned with the table columns. I was confused not to find the right amount of points in the table. 
> Also at a first glance I didn't know what the numbers represented.

### Feedback First Submission:

The visualization looks awesome! But what is the message you want to convey? I couldn't quickly infer from looking at the visualization as a standalone project (without the readme.).

The goal in this project is that you find a story to tell first, and then use a visualization in the most effective way to tell it to the user. There may be a lot of interesting findings in the data presented, but it is not clear to the reader which one.

As general advices on improving communication:
* Use text along with the plots. Besides the introductory text, which is very good, use text to direct your reader towards the main message. Add anedoctes and interesting facts to make it even more appealing for the reader.
* Your title needs to reflect the explanatory aspect of the visualization, for example, "Bayern Munich and Dortmund dominate Bundesliga" (just an example, I noticed they won in the last years, I don't particularly favor any team). The current title "Bundesliga Standings between is 1996 and 2016" is 
suitable for an exploratory visualization. 

Considering the goal is to "to show the growing gap between a handful of top teams and the remaining teams and the domination of a few teams.", as described on the readme, more specific advices:
* The goal is to show dominance of top teams, but the team information is hiding in a tooltip, with no other visual encoding. The visual encoding hierarchy should follow the importance of each variable for the visualization message - since team is very important, it should be high up in the hierarchy. As a suggestion, if you want to show 2 or 3 teams dominated in the last year, add a small logo of the team above or below the dot in the first 3 lines. This way it will be easier to visualize if a particular team or groups teams have dominated the last years. This is just a suggestion, any other visual encoding will do fine as well.
* The visualization is too cluttered, it feels overplotted. Since you are aiming to show dominance in the top position, you can focus on the top standings. The lower part of the visualization, around the 11th standing to the bottom, doesn't add a lot to the message.

### Feedback Second Submission:

You've made some excellent design choices so far. I love the chart choices, the interactivity between the chart, the logo icons and all your clear, accessible labels. Fabulous.

However, I think currently your graphic is potentially very confusing. It took me about 10 minutes of looking at the chart, the README file and Googling football team logos to understand what is going on. 
Obviously I am not a football fan!

My conclusion is the main problem is a disconnect between the title - Top 5 Teams - and the line chart. From the title, I automatically assumed that each line was a team so I was trying to work out what the 
logos meant and whether some of them were in the wrong position. There are in fact logos for 12 teams (possibly more if I've missed one) on the line chart! I have now worked out that the lines 
represent the positions or standings!

Your main message is How Bayern Munich dominates the Bundesliga.... You need to make sure your charts tell this story loud and clear.

## Resources

The data is obtained from http://www.football-data.co.uk/ . It was processed using Python in order to get the final standings per year and to create the csv file used for the visualization.

I used the following websites as inspiration for the code:

http://bl.ocks.org/LeeMendelowitz/11383724

http://stackoverflow.com/questions/19757638/how-to-pivot-a-table-with-d3-js

http://stackoverflow.com/questions/14567809/how-to-add-an-image-to-an-svg-container-using-d3-js

http://bl.ocks.org/ilyabo/1373263

http://bl.ocks.org/d3noob/a22c42db65eb00d4e369

http://bl.ocks.org/WandaChen/045d423c0d092ed73568