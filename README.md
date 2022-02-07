# Demand Predictor QGIS Plugin

This is a QGIS plugin which uses Irish census data (but could be modified to include other sources) to predict demographic based demand. This can be used to predict demand for any number of different products/services as the distribution function can be easily changed to suit your needs.

<br>

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Getting Census Data](#getting-census-data)
- [How it Works](#how-it-works)

<br>

## Installation

To install this plugin simply download the code from this repository and place it in your python plugins folder. To download the code go to the homepage of this repository and click the green Code button in the top right. Then click Download ZIP.

![How to download code](/images/download-code.png)

<br>

To find the plugins folder you can open QGIS and at the top click Settings > User Profiles > Open Active Profile Folder.

![Find user folder](/images/user-folder.png)

<br>

Then once you have this folder open click into python > plugins and then paste the demand_predictor-master folder from inside the downloaded ZIP file. Finally, reload your QGIS and you should be able to see the plugin in the processing toolbox.

<br>

## Usage

Once the plugin is properly installed you should be able to see it in your processing toolbox. This should be available on the right side of your screen. It can also be accessed using Ctrl+Alt+t or by the Processing tab at the top of the screen.

![Processing toolbox](/images/processing-tools.png)

<br>

Once you have located the plugin double click on it or click the dropdown arrow. This should display the algorithms associated with the plugin of which there is just the one. Double click this and you should be greeted by the interface shown below.

![Plugin interface](/images/plugin-interface.png)

<br>

Below is a brief explanation of what each of the parameters means:

- **Input Layer**: this should be the file containing the Irish census data. Many different file formats should work but some common ones are .kml, .shp/.shx etc.
- **Male Distribution Function**: this is the function which governs how the male population scores are calculated. For more info chek out the How it Works section.
- **Female Distribution Function**: this is the function which governs how the female population scores are calculated. For more info check out the How it Works section.
- **Minimum Age**: below this age the algorithm will not add to the scores for any area.
- **Output Layer**: where you want the output to be stored. This can be left blank for a temporary layer and made permanent later.

<br>

## Getting Census Data

To get census data to use in this plug in visit [**this link**](https://census2016.geohive.ie/datasets/population-aged-0-19-by-sex-year-of-age-persons-aged-20-by-sex-and-age-group-small-areas-census-2016-theme-1-1-ireland-2016-cso-osi/explore?location=53.354325%2C-6.242087%2C12.67). While you can just hit download there it will download a data set for the entire island of Ireland which will take a long time to process. Luckily on this website you can also filter the data before you download it.

## How it Works
