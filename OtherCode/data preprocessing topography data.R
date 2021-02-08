# load packages
library(rgbif) # Interface to the Global 'Biodiversity' Information Facility API
library(dplyr) # A Grammar of Data Manipulation

dat<- read_csv("wildfire data 2020-2021.csv")

# fetch elevations 
# use your GeoNames username after enabling webservices for it
n = nrow(dat)

#missingElevations = c()
for(i in seq(65075,n)){
  ele_i = elevation(latitude = dat$latitude[i],longitude = dat$longitude[i],username = "bohanwu2021")
  missingElevations = append(missingElevations, ele_i)
}

length(missingElevations)
#8485
#20505
#29091
#44242
#61033
#65074
253746/3

missing_elev1 = missingElevations[seq(3,25455,by = 3)]%>% as.numeric()
missing_elev2 = missingElevations[seq(25458,61515,by = 3)]%>% as.numeric()
missing_elev3 = missingElevations[seq(61518,87273,by = 3)]%>% as.numeric()
missing_elev4 = missingElevations[seq(87276,132726,by = 3)]%>% as.numeric()
missing_elev5 = missingElevations[seq(132729,183099,by = 3)]%>% as.numeric()
missing_elev6 = missingElevations[seq(183099+3,195222,by = 3)]%>% as.numeric()
missing_elev7 = missingElevations[seq(195222+3,253746,by = 3)]%>% as.numeric()
missing_elev = c(missing_elev1,missing_elev2,missing_elev3,missing_elev4,missing_elev5,
                 missing_elev6,missing_elev7)
dat$elev = missing_elev

hist(dat$elev)
#lowest point in Victoria is -52m,if a data point 
dat$elev[dat$elev<(-52)] = 0

write.csv(dat,file = "wildfire data 2020-2021 w Elevation.csv",row.names = FALSE)

