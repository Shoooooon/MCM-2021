library(dplyr)
library(xts); library(lubridate); library(zoo)
library(ggplot2);library(gganimate)
library(geosphere)
library(leaderCluster)
library(ggplot2)
library(raster)
library(pathmapping)


#The viirs csv files can be downloaded at https://firms.modaps.eosdis.nasa.gov/country//

dat<- read_csv("wildfire data 2012-2021.csv")

dat <- dat %>% dplyr::select(c(latitude,longitude,acq_date))

str(dat)

#----------------------------------------------------------
#leaderCluster takes a matrix of coordinates and outputs cluster ids from running the leader algorithm.
#The coordinates can either be on points in the space R^n, or latitude/longitude pairs.
#A radius delta must be provided.
#The radius is chosen to be 90km to account for EOC distribution. 
#Output: dataframe with latitude, longtitude, cluster, cluster-centroid latitude, longtitude
{
  cluster = c()
  cluster_centroids = matrix(nrow = 1, ncol = 2)
  for(i in unique(dat$acq_date)){
    dat_small = dat%>% filter(acq_date == i) %>% dplyr::select(latitude,longitude)
    res  = leaderCluster(dat_small,radius = 90, distance= "haversine",max_iter = 1000)
    out = res$cluster_id
    cluster_centroids = rbind(cluster_centroids, sapply(out,function(x) res$cluster_centroids[x,]) %>%t())
    cluster = append(cluster,out)
  }
  cluster_centroids = na.exclude(cluster_centroids)
  dat$cluster = cluster
  dat$cluster_centroid_lat = cluster_centroids[,1];dat$cluster_centroid_long = cluster_centroids[,2]
}
write_csv(dat,"wildfire data 2012-2021 + cluster.csv")

                                                        
#----------------------------------------------------------

#Then we get spatial coordiantes with python; run file under "data transformation"
dat<- read_csv("wildfire data 2012-2021 + cluster.csv")

dat$acq_date = as.Date(dat$acq_date,format = "%m/%d/%Y")
#For each day i,cluster j, calculate fire size s_{i,j}
fire_sizes = dat %>% group_by(acq_date,cluster) %>%
  group_map(~nrow(as.matrix(.x$fire_cart_x,.x$fire_cart_y)))%>%
  unlist()


dat %>% group_by(acq_date,cluster) %>%head()

df1 = dat %>%   distinct(acq_date,cluster);df1$size = fire_sizes

#Define large fire as day with total area burned> 410.2

burned = df1 %>% group_by(acq_date) %>% summarize(area_burned = sum(size))%>%
  mutate(num_large_fire = (area_burned > 410.2))

ggplot(df2, aes(x = acq_date, y = log(area_burned)))+ 
  geom_line(aes(color = "red"))+
  geom_line()
  labs(x = "date", y = "log(area burned)")+
    ggtitle("Total area ")
#----------------------------------------------------------
library(xts)
require(forecast)
require(tsbox)
require(astsa)
library(zoo)
library(seasonal)

burned.xts = xts(sqrt(burned$area_burned), order.by=burned$acq_date) 
plot(burned.xts,main = "sqrt(Area burned), km^2", col="red",lwd = 0.2)
ggAcf(burned.xts)
pacf(burned.xts)
#Slight seasonal pattern, When data are seasonal, the autocorrelations will be larger for the seasonal lags (at multiples of the seasonal frequency) than for other lags.

burned$month <- factor(format(burned$acq_date, "%b"), levels = month.abb)
burned$month_num <- as.numeric(format(burned$acq_date, "%m"))
burned$year <- format(burned$acq_date, "%Y")
burned$date <- format(burned$acq_date, "%d")
burned$yearmonth <- as.yearmon(format(burned$acq_date, "%Y/%m"),format = "%Y/%m")

autoplot(burned.xts) + xlab("Year") + ylab("Area burned (in km^2)")



#Average Monthly Fire Size Time Series
avg_size_fire = burned %>%
  group_by(yearmonth)%>%
  mutate(fire_num = sum(num_large_fire),prob_fire = mean(num_large_fire),avg_size = mean(area_burned))%>%
  dplyr::select(fire_num,prob_fire,avg_size,year,month) %>% distinct()

ggplot(avg_size_fire)+
  geom_line(aes(yearmonth,avg_size))+xlab("Time")+
  ylab("Average Fire Size (km^2)")+ggtitle("Average Fire Size 2012-2020 From November to May")

#--------------------------------------------------
#Fit ARIMA
climate <- read_csv("climate data/max temp+rainfall+solar.csv", col_types = cols(Date = col_date(format = "%Y-%m-%d")))
climate$month <- as.numeric(format(climate$Date, "%m"))
climate$year <- format(climate$Date, "%Y")
climate$date <- format(climate$Date, "%d")
climate$yearmonth <- as.yearmon(format(climate$Date, "%Y/%m"),format = "%Y/%m")

df_climate = climate%>%filter(month< 6|month>10) %>% 
  group_by(yearmonth)%>%
  summarize(avg_solar = mean(solar,na.rm = TRUE),
            avg_rainfall= mean(rainfall,na.rm = TRUE),
            avg_max_temp = mean(max_temp,na.rm = TRUE),month = month)%>%distinct()

df_climate$avg_max_temp = df_climate$avg_max_temp %>%scale()
df_climate$avg_solar = df_climate$avg_solar%>%scale()
df_climate$avg_rainfall = df_climate$avg_rainfall%>%scale()


Xreg = as.matrix(df_climate[,2:4])
Xreg[,3] = na.fill(Xreg[,3],0) #fill in missing (normalized) temperature with 0

firesize.xts = xts(avg_size_fire$avg_size %>% log(), order.by=avg_size_fire$yearmonth) 
size_fit = auto.arima(firesize.xts,xreg = Xreg)

#checkresiduals(size_fit)

#--------------------------------------------------
#Prediction With ARIMA
solar_2025 <- read_csv("climate data/solar 2025.csv",col_types = cols_only(rsds_djf = col_double()))

max_temp_2025 <- read_csv("climate data/max temp 2025.csv",  col_types = cols_only(tasmax_djf = col_guess()))
rainfall_2025 <- read_csv("climate data/rainfall 2025.csv",col_types = cols_only(pr_djf = col_guess()))

df_climate2 = climate%>%group_by(month)%>%summarize(avg_solar = mean(solar,na.rm= TRUE),
                                                    avg_rainfall = mean(rainfall,na.rm = TRUE),
                                                    avg_temp = mean(max_temp,na.rm= TRUE))

delta = c(mean(max_temp_2025$tasmax_djf),mean(rainfall_2025$pr_djf),mean(solar_2025$rsds_djf,na.rm = TRUE))


newX = as.matrix(df_climate2[,2:4])
newX_mat = apply(newX,1,function(x) return (x-delta)) %>%t()

newX = apply(newX_mat[,],2,scale)
colnames(newX) = colnames(Xreg)

autoplot(forecast(size_fit,xreg = newX))+
  geom_vline(xintercept = 6.4, linetype="dotted", color = "red", size=1.5)+
  annotate("text", 6.5, 7, vjust = -1, label = "2025", color = "red")+
  labs(y = "log(fire size)")+
  scale_x_discrete(labels= avg_size_fire$yearmonth)
