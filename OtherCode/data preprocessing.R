library(readr)
library(dplyr)
library(xts); library(lubridate); library(zoo)

#The viirs csv files can be downloaded at https://firms.modaps.eosdis.nasa.gov/country//
#Attribute fields can be founded at https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/v1-vnp14imgt#ed-viirs-375m-attributes
filenames = paste0("Archive Data/viirs-snpp_",seq(2012,2019),"_Australia.csv")

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
  select(-c(version, type, satellite, instrument,bright_ti4,bright_ti5))

#Write processed csv file
#write.csv(dat_victoria_wildfire,file = "wildfire data 2012-2019.csv")
