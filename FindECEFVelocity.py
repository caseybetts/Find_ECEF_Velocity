#Casey Betts 2022
#This program takes the data from a .csv file and outputs a speed and a velocity vector for some given times
#The .csv file must be fomated as: Time since the Unix epoch [seconds], WGS84 latitude [degrees], WGS84 longitude [degrees], WGS84 altitude [kilometers]
#The .csv file must be named: Data.csv
#
#importing needed libraries
import math
from pandas import Series,DataFrame
import pandas as pd

#constant WGS84 Parameters to be used in conversion function
a = 6378137.0 #semi-major axis (m)
b = 6356752.31424518 #semi-minor axis (m)
e = (((a**2)-(b**2))/(b**2))**.5 #unitless

#reading in the dataframe
dframe = pd.read_csv('Data.csv', header=None, names=('time', 'lat', 'lon', 'alt'))

#function to convert lla coordinates to ecef coordinates
#returns a 3-element list [X,Y,Z] in ecef
def llaToecef(phi, lamb, h):
    #convert angles from radians to degrees
    phi = float(phi)*math.pi/180
    lamb = float(lamb)*math.pi/180
    h = float(h)
    #distance from earth mass center to ellipse surface
    N = a / (1-(e**2)*(math.sin(phi)**2))**.5 #distance from earth center to curvature (meters)
    #cartessian coordinates
    X = (N + h)*math.cos(phi)*math.cos(lamb)
    Y = (N + h)*math.cos(phi)*math.sin(lamb)
    Z = (((b**2)/(a**2)) * N + h) * math.sin(phi)
    return [X,Y,Z] #meters

#function to find indexes of 2 earlier enteries and 2 later enteries
#input any time between 1532332859.04 and 1532335359.04
def times(time):
    #finding the index of the largest time smaller than the input time
    j = len(dframe.index)-1
    while dframe.loc[j,'time'] > time:
        j -=1
    #finding the index of the smallest time larger than the input time
    k = 1
    while dframe.loc[k,'time'] < time:
        k += 1
    #retuning a list of two indexes below and two indexes above the input time
    return [j-1, j, k, k+1]

#function to take two points in ecef coordinates (meters) and return the distance between them
def distance(p1,p2):
    return (((p2[0]-p1[0])**2)+((p2[1]-p1[1])**2)+((p2[2]-p1[2])**2))**.5 #meters

#recieves a distance and two times and returns speed
def speed(dist,t1,t2):
    return dist/(t2-t1) #meters/sec

#receives two velocities and their associated times and the time at which the velocity is desired
#returns the velocity at the requested time
def interpolate(v1, v2, t1, t2, t_in):
    a = (v2 - v1)/(t2 - t1)
    return a*(t_in - t1) + v1 #meters/sec

#function to prompt user for a time and checks that input time is within bounds, otherwise will print statement and end running script
def user_time():
    time = float(input("Please enter requested time in seconds: "))
    if time > 1532335354.04:
        print("Time must be between 1532332864.04s and 1532335354.04s")
    elif time == 1532332859.04:
        print("Velocity at 1532332859.04s: 0 m/s")
    elif time < 1532332864.04:
        print("Time must be between 1532332864.04s and 1532335354.04s")
    else:
        display(time)

#primary function to accept an input time and desired output type, velocity vector or speed, then finds data from dataframe to calculate each
def __main__(input_time, type):
    tlist = times(input_time)
    #pulling values from the data file into 3-element lists for each time
    point1 = llaToecef(dframe.loc[tlist[0],'lat'], dframe.loc[tlist[0],'lon'], dframe.loc[tlist[0],'alt']) #meters
    point2 = llaToecef(dframe.loc[tlist[1],'lat'], dframe.loc[tlist[1],'lon'], dframe.loc[tlist[1],'alt']) #meters
    point3 = llaToecef(dframe.loc[tlist[2],'lat'], dframe.loc[tlist[2],'lon'], dframe.loc[tlist[2],'alt']) #meters
    point4 = llaToecef(dframe.loc[tlist[3],'lat'], dframe.loc[tlist[3],'lon'], dframe.loc[tlist[3],'alt']) #meters
    #finding the speed on each given axis between time 1 and time 2
    s_x_1 = speed(point2[0]-point1[0],dframe.loc[tlist[0],'time'], dframe.loc[tlist[1],'time']) #meters/sec
    s_y_1 = speed(point2[1]-point1[1],dframe.loc[tlist[0],'time'], dframe.loc[tlist[1],'time']) #meters/sec
    s_z_1 = speed(point2[2]-point1[2],dframe.loc[tlist[0],'time'], dframe.loc[tlist[1],'time']) #meters/sec
    #finding the speed on each given axis between time 3 and time 4
    s_x_2 = speed(point4[0]-point3[0],dframe.loc[tlist[2],'time'], dframe.loc[tlist[3],'time']) #meters/sec
    s_y_2 = speed(point4[1]-point3[1],dframe.loc[tlist[2],'time'], dframe.loc[tlist[3],'time']) #meters/sec
    s_z_2 = speed(point4[2]-point3[2],dframe.loc[tlist[2],'time'], dframe.loc[tlist[3],'time']) #meters/sec
    #finding speed based on each point
    total_speed1 = speed(distance(point1,point2),dframe.loc[tlist[0],'time'], dframe.loc[tlist[1],'time']) #meters/sec
    total_speed2 = speed(distance(point3,point4),dframe.loc[tlist[2],'time'], dframe.loc[tlist[3],'time']) #meters/sec
    #calculating the time halfway between the points given in the input file. These will coincide with the calculated speeds
    time1 = (dframe.loc[tlist[1],'time']+dframe.loc[tlist[0],'time'])/2 #sec
    time2 = (dframe.loc[tlist[3],'time']+dframe.loc[tlist[2],'time'])/2 #sec
    #calculating the velocity vector and the total speed of the object at the input time
    velocity_vector = [interpolate(s_x_1,s_x_2,time1,time2,input_time),interpolate(s_y_1,s_y_2,time1,time2,input_time),interpolate(s_z_1,s_z_2,time1,time2,input_time)] #meters/sec
    total_int_speed = interpolate(total_speed1,total_speed2,time1,time2,input_time) #meters/sec
    #returning values based on desired type
    if type == 'vector':
        return velocity_vector
    elif type == 'speed':
        return total_int_speed

#receives a time and displays the resulting velocity vector and speed
def display(sec):
    print(f"\tECEF velocity vector at {sec}s: ", __main__(sec, 'vector'),"m/s")
    print(f"\tECEF speed at {sec}s: ", __main__(sec, 'speed'),"m/s")

#Running this script will automatically display results for times 1532334000 and 1532335268 and then ask the user to input a time
display(1532334000)
display(1532335268)
user_time()
