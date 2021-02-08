library(dplyr)
library(xts); library(lubridate); library(zoo)
library(ggplot2);library(gganimate)
library(geosphere)
library(leaderCluster)
library(SpatialEpi)
library(tidyverse)  # data manipulation
library(cluster)    # clustering algorithms
library(factoextra) # clustering visualization
library(dendextend) # for comparing two dendrograms

#The viirs csv files can be downloaded at https://firms.modaps.eosdis.nasa.gov/country//

dat<- read_csv("wildfire data 2020-2021.csv")

dat <- dat %>% dplyr::select(c(latitude,longitude,acq_date))

str(dat)

#----------------------------------------------------------
#leaderCluster takes a matrix of coordinates and outputs cluster ids from running the leader algorithm.
#The coordinates can either be on points in the space R^n, or latitude/longitude pairs.
#A radius delta must be provided.

#Output: dataframe with latitude, longtitude, cluster, cluster-centroid latitude, longtitude
{
cluster = c()
cluster_centroids = matrix(nrow = 1, ncol = 2)
for(i in unique(dat$acq_date)){
  i = unique(dat$acq_date)[200]
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
cols = rainbow(length(unique(out)))[out]
plot(dat_small[,c(2,1)], pch=19, cex=0.7, col=cols)
points(dat_small[!duplicated(out),c(2,1),drop=FALSE], cex=2, col=unique(cols))
M = distm(dat_small[,c(2,1)])



library(ggpubr)
dat_small$cluster  = as.factor(out)
ggscatter(
  dat_small, x = "longitude", y = "latitude", 
  color = "cluster", palette = "npg", ellipse = TRUE, ellipse.type = "convex", size = 1.5,  legend = "right", ggtheme = theme_bw(),
  xlab = paste0("Longitude" ),
  ylab = paste0("Latitude" ),
  title = paste0("                          Fire Clusters on ",i)
)
max(M)/1000
which.max(M)
box()
#write.csv(dat,"wildfire data 2020-2021 + cluster.csv",row.names = FALSE)

