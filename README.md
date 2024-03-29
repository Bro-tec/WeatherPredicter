# WeatherPredicter
A way to predict weather data

<br>

This Code focused to predict data based on weather-data in germany using DWD data.
The data gets retrieverd using Brightsky Api.

<br>

### Following libraries are needed:
- datetime
- asyncio
- pandas
- numpy
- math
- random
- warnings
- matplotlib
- os
- json
- tqdm
- sklearn
- torch
- torchmetrics
- requests
- aiohttp

<br>

## First u need to get the get stations.csv
Run the file get_DWD_data.py in the folder CollectData 
#### or 
load the stations.csv from **[Google Drive](https://drive.google.com/drive/folders/1a8JoFlJ9xNWByvjP25ytz66WRIDUyy0E?usp=sharing)** and save it into the Weatherpredicter folder.

<br>

## The next step is to train the models.
Run the files trainDailyModels.py and trainHourlyModes.py in the folder WeatherPredicter. <br>
You can run the Normal mode but its recomendet to use the Timestamp mode, if the device has enough memory. <br> 
your models and the model histories will be saved into Models and you can see the confusion matrix for the labels, the loss and the accuracy curve in Plots
#### or 
load all models and history data from **[Google Drive](https://drive.google.com/drive/folders/1a8JoFlJ9xNWByvjP25ytz66WRIDUyy0E?usp=sharing)** and save it into the Models folder.

<br>

## Now You are ready
Run the file predictModels,py in the folder WeatherPredicter and chose the preferences of your Model. <br>
If you saved the Model from the google drive, then you should run the code on normal mode. <br>
The plots will be saved in the Plots folder.

<br>

## Documentation

**[German Documentation](https://drive.google.com/file/d/17Y7CCb8q_BkaXafY_krfXaMJ5eqAW4U2/view?usp=sharing)**


**[English Documentation](https://drive.google.com/file/d/19pABBdGhXleA2T1tDr-GP1gwyDyeFwrg/view?usp=sharing)**

<br>

## Presentation

**[German Presentation](https://docs.google.com/presentation/d/1Tj1JBiOdr7fzXeiFHC5kwvETWVYObkYu/edit#slide=id.p1)**


**[German Presentation (PDF)](https://drive.google.com/drive/folders/1a8JoFlJ9xNWByvjP25ytz66WRIDUyy0E)** 

