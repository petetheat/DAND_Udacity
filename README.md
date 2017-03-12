# P6: Data Visualization
Peter Eisenschmidt

## Summary

The visualization depicts the final standings of the first division of the German Bundesliga between 1996 and 2016.

## Design

The following [pdf](first_sketch.pdf) shows a first sketch of how I want to visualize the data. The idea is to display the data in a table where each row is for the standing and each column for each year.

The table contains the number of points for each standing/year. When selecting a standing (e.g. 1 for the champion or 16 to 18 for the relegated teams), a line chart should display the points for that standing for all years. The aim is to show if there are trends over the years, for example 
the number of points required to win the championship or avoid relegation to 2nd division.

Finally, when hovering the mouse over a data entry the name of the team should be displayed.

## Feedback

## Resources

The data is obtained from http://www.football-data.co.uk/ . It was processed using Python in order to get the final standings per year and to create the csv file used for the visualization.

The code for the table creation is inspired by this example:
http://bl.ocks.org/LeeMendelowitz/11383724


http://stackoverflow.com/questions/19757638/how-to-pivot-a-table-with-d3-js
http://stackoverflow.com/questions/14567809/how-to-add-an-image-to-an-svg-container-using-d3-js

http://bl.ocks.org/ilyabo/1373263