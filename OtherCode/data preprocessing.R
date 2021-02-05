library(readr)
library(dplyr)
library(xts); library(lubridate); library(zoo)
library(plotly)
library(ggplot2)
library(ggmap)
library(leaflet)
library(gganimate)
library(av)

#The viirs csv files can be downloaded at https://firms.modaps.eosdis.nasa.gov/country//
#Attribute fields can be founded at https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/v1-vnp14imgt#ed-viirs-375m-attributes
#The data includes record from 01/01/2012 to 02/04/2021
filenames = paste0("Archive Data/viirs-snpp_",seq(2012,2020),"_Australia.csv")


dat_all<- read_csv(filenames[1])
for(name in filenames[2:length(filenames)]){
  dat_all = rbind(dat_all,read_csv(name) )
}

#-----------------------------------------------------------------
#Make csv file: 
#1) Select Victoria
dat_victoria = dat_all %>% filter((latitude < -36&latitude >= -39& longitude <142& longitude >= 141)|
                                    (latitude < -35&latitude >= -39& longitude <144& longitude >= 142)|
                                    (latitude < -36 &latitude >= -39& longitude <148& longitude >= 144)|
                                    (latitude < -37 &latitude >= -39& longitude <150& longitude >= 148))

#2)
#-Select only wildfire: type = 0
#Remove unnecessary attributes: version, type, satellite, instrument,bright_ti4,bright_ti5
dat_victoria_wildfire = dat_victoria%>% filter(type == 0)%>%
  dplyr::select(-c(version, type, satellite, instrument,bright_ti5))

#Write processed csv file
#write.csv(dat_victoria_wildfire,file = "wildfire data 2012-2021.csv")
dat_victoria_wildfire2019 = dat_victoria_wildfire %>% select(latitude,longitude ,bright_ti4,acq_date) %>%
  filter(year(acq_date) == 2019)


leaflet(data = dat_victoria_wildfire2019) %>%
  addTiles() %>%
  addCircleMarkers(lat = ~latitude, lng = ~longitude, stroke = FALSE, fillOpacity = 0.6) #%>%
  #addLegend(position = "bottomleft", pal = pal, values = ~pop)

str(dat_victoria_wildfire2019)

ggplot(dat_victoria_wildfire2019, aes(longitude, latitude, color = bright_ti4)) +
  geom_point(alpha = 0.7, show.legend = FALSE) +
  scale_size(range = c(2, 12)) +
  # Here comes the gganimate specific bits
  labs(title = 'Year: {frame_time}', x = 'GDP per capita', y = 'life expectancy') +
  transition_time(acq_date) +
  ease_aes('linear')

world <- map_data("world")
Australia <- world %>% filter(region == "Australia")
summary(australia$subregion %>% as.factor())

p = ggplot(dat_victoria_wildfire2019,
       aes(x = longitude, y = latitude,color = bright_ti4))+
  geom_map(data = Australia,
           map = Australia,
           aes(long,lat,map_id = region),
           color = '#333300', fill = '#663300',
           # lighter background for better visibility
           alpha = 0.5) +
  geom_point(size = 2.5) +
  geom_point(size = bright_ti4)+
  # limit coordinates to relevant range
  coord_quickmap(x = c(140, 155), y = c(-30, -45)) +
  transition_states(states = acq_date)

gganimate::animate(
  p + enter_fade() + exit_fly(y_loc = 1),
  renderer = av_renderer()
)
