import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

BOHAN_CSV_FILENAME = '../Data/fire_data_for_drones.csv'
df = pd.read_csv(BOHAN_CSV_FILENAME,  converters={'fires_cart': eval})

# eoc = [(-21.99669561737069, 32.44489189482008)]
# drones = [(-19.52868792817113, 34.2705572209461), (-7.190760785669463, 23.688831186397806), (0.34876965180274944, 31.783410608267477), (-7.748748367371373, 6.717920404532752)]

# eoc = [(12.921067606696072, -6.756874618431407)]
# drones = [(1.9608339629295113, 35.80634897876161), (-4.794528253072393, -0.2552633407565299), (-6.630470475785648, 7.616618011400275), (-8.524549332267, 20.77731185488296)]

eoc = [(11.833271398507511, 3.216696242220717)]
drones = [(1.190637223650163, 32.08096760760307), (-6.511574545731568, 7.12558041915155), (-11.813109488836092, 20.510340208506793), (23.523091228361576, 31.753058672675742)]
fires = [(-10,5), (-8,6), (6,32), (0, 36), (-9,5.5)]

fig=plt.figure()
ax=fig.add_axes([0,0,1,1])

ax.scatter([item[0] for item in eoc], [item[1] for item in eoc], color='g')
eocCirc = plt.Circle(eoc[0], 20, color = 'g', alpha = 0.1)
plt.gca().add_artist(eocCirc)

ax.scatter([item[0] for item in drones], [item[1] for item in drones], color='b')
droneSmallCircs = [plt.Circle(drone, 5, color = 'b', alpha = 0.25) for drone in drones]
droneBigCircs = [plt.Circle(drone, 20, color = 'b', alpha = 0.1) for drone in drones]
[plt.gca().add_artist(droneCirc) for droneCirc in droneSmallCircs + droneBigCircs]

ax.scatter([item[0] for item in fires], [item[1] for item in fires], color='r')
plt.xlabel('X (km)')
plt.ylabel('Y (km)')
ax.set_title('Example Drone Network')
# plt.show()


def diameter(clusterPoints):
    md = 0
    for i in range(len(clusterPoints)):
        for j in range(i,len(clusterPoints)):
            if (clusterPoints[i][0] - clusterPoints[j][0])**2 + (clusterPoints[i][1] - clusterPoints[j][1])**2 > md:
                md = (clusterPoints[i][0] - clusterPoints[j][0])**2 + (clusterPoints[i][1] - clusterPoints[j][1])**2
    print(np.sqrt(md)) 


'''
Reads a cluster off the csv and returns (cluster row number, fireCoords, date)
'''
def read_cluster(row):
    return (row, df.at[row,'fires_cart'], df.at[row, 'acq_date'])


def read_distributions(string_dist):
    a = [eval(i) for i in string_dist]
    return max(a[-1].keys())

def read_distribution_files(cluster_num):
    folderName = './1st_attempt_drone_position_GA_cluster_' + str(cluster_num) + '/'
    bestList = []
    i = 2
    while True:
        try:
            dist = folderName + str(i) + '_drones_drone_distribution.txt'
            dist = open(dist, "r")
            bestList.append(read_distributions(dist.readlines()))
        except:
            break
        i += 2
    return bestList

# print(read_distribution_files(9))
# print(len(read_distribution_files(9)) * 2)
# b = [(-3.2128728141608454, -33.85583319503172), (24.828049235098185, -28.339002501401403), (-21.27866590286173, -35.333370050442156), (-21.765347702085318, -35.02086141264846), (5.710052432304686, -29.21895158062232), (-22.144231266469543, -32.71949857171202), (-23.056323262235207, -32.477242991170066), (-22.207193352641866, -32.33564362061941), (-30.47919979083637, -31.745710902581337), (-22.461453549999927, -28.435616160599203), (-22.250795551892455, -28.65225603926614), (29.277105276004505, -16.77767882340893), (28.872300446378297, -16.84607936866249), (28.80749365071501, -16.46816370758929), (29.61856148365227, -16.33093711207821), (29.213732183222735, -16.399321054034232), (29.085547370015515, -15.644378293556926), (-74.17356797516267, -25.475812863775932), (-25.889700444334125, -17.043726031217844), (-74.41060700165455, -25.63831042101109), (-74.48147940820962, -25.248582651706013), (-21.660610207482822, -15.843218652746367), (-22.070518634898065, -15.912883164942757), (47.06769042405604, -3.775589081105999), (-21.716951716826532, -15.459348607494343), (-28.545442738693065, -13.070043906520278), (-27.76051916709216, -12.543314207976431), (-28.183976592669833, -12.614544352196804), (-28.2406421988111, -12.2298320608421), (-25.52243565649982, -10.589014067398342), (-25.937877953410286, -10.658884364250685), (56.86474598238838, 3.6717662175163133), (-25.58429589434192, -10.2051888423993), (30.603974841946357, 0.8031809227560038), (30.547249349870718, 1.1814043179574378), (5.0160926046189465, -3.1034709003907968), (5.685680579109852, -1.821466012518197), (45.168482615297314, 8.271539859099285), (45.10835665905932, 8.64743675181451), (44.71017479258945, 8.580097343050383), (-32.46521945262025, -3.7336146564014845), (-33.30347151626567, -3.876201484119903), (-33.72873501812141, -3.948605631800074), (-40.45705278984945, -5.0915624185247665), (-32.95274317110575, -3.4222091817044307), (-40.52512542699569, -4.70787793929285), (24.02224676305549, 6.626067803933322), (-41.01422993420085, -4.394840291408954), (-41.43259305247275, -4.465494413571612), (-39.868137620541006, -3.4091696933258056), (-40.29734859728111, -3.4823710440415514), (24.786758238970382, 9.472346857106022), (24.38737139533239, 9.40493246239706), (24.722874777394562, 9.849324634704795), (25.055753102633176, 10.293710969564422), (-81.23278250584956, -7.206147500543131), (-83.12395808929232, -6.7209674317478605), (51.17506440971889, 20.058761644502027), (50.77637717563213, 19.99049111586595), (-11.201672732078288, 10.618379086101305), (-11.622367347027867, 10.546221514918297), (33.75083367108075, 19.034470204580014), (-10.470738927656553, 11.526609617616202), (-10.103128330641372, 11.980869376789167), (-10.538798548253071, 11.906306836911996), (-10.611031985017709, 12.285110098374851), (-10.176673231012431, 12.359674728594943), (-11.877530963390084, 12.069989485584184), (36.77805255916816, 23.027942616086715), (-12.272594577314493, 14.745092762249257), (-12.659694563514908, 14.680590821073976), (37.495879163955365, 23.535830410953167), (37.04729131159774, 23.84635218967076), (36.657967706687074, 23.78080925525364), (66.0454084603763, 33.35289461948047), (41.395981575139444, 30.378402706079083), (45.464206506358444, 32.999877115672035), (46.14340423009557, 33.88688886094231), (45.73734199453529, 33.81753007432348), (44.167376864029315, 33.552042841633074), (46.084357909360406, 34.26232232320984), (45.676946653453676, 34.19341190504699), (46.369790009281076, 35.08243778091278), (46.30673708431362, 35.457006045957684), (-46.988514738920955, 35.532012267114844)]
# md = 0
# for point in b:
#     for pt in b:
#         if np.sqrt((point[0] - pt[0])**2 - (point[1] - pt[1])**2) > md:
#             md = np.sqrt((point[0] - pt[0])**2 - (point[1] - pt[1])**2)
# print(md)


# print(read_distribution_files(4))
# print(len(read_distribution_files(4)) * 2)
# b = [(-0.019214475215788836, -0.3484646939584718), (-0.6894814710040634, -0.09144552728409124), (-0.5154460828646842, -0.36745957431491943), (-0.025933248002021656, 0.3488714004524411), (0.45823366256758913, 0.36794869349963355), (-0.18916844427235668, -0.0676676957380354), (0.2936482375292873, -0.04569515166335227), (0.05228033868576432, -0.6016281062165669), (-0.14869103046108934, -0.05157364591163802), (0.5660491552372785, 0.17915194425139253), (0.20871828545369334, 0.06351937228188276), (0.009066983181164688, 0.6143539680596732)]
# md = 0
# for point in b:
#     for pt in b:
#         if np.sqrt((point[0] - pt[0])**2 - (point[1] - pt[1])**2) > md:
#             md = np.sqrt((point[0] - pt[0])**2 - (point[1] - pt[1])**2)
# print(md)


# clusts = list(filter(lambda item: item[2] == '1/1/2020',[read_cluster(row) for row in range(df.shape[0])]))
# print([diameter(c[1]) for c in clusts])



print(32 * sum([(a/144)**2 for a in [105.06890965958614, 6.83709826047657, 157.57459948855362, 84.88374177233833, 1.554413406252092, 0.8178508325190689, 2.4892576546151086]]))
print(144**2)