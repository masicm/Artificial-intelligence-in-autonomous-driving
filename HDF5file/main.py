
import argparse
import os
import sys
from master_world import CarlaWorld
from shranjevanje import HDF5Saver
import h5py
import cv2
import numpy as np
from matplotlib import pyplot as plt
import math

def image(rgb_data,  depth_data, save_to_many_single_files=False):
    if save_to_many_single_files:
        cv2.imwrite('raw_img.jpeg', rgb_data)
    if save_to_many_single_files:
        cv2.imwrite('filtered_boxed_img.png', rgb_data)
    depth_data[depth_data==1000] = 0.0
    normalized_depth = cv2.normalize(depth_data, depth_data, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    normalized_depth = np.stack((normalized_depth,)*3, axis=-1)  
    if save_to_many_single_files:
        cv2.imwrite('depth_minmaxnorm.png', normalized_depth)
    return rgb_data, normalized_depth


def video(hdf5_file):
    with h5py.File(hdf5_file, 'r') as file:
        frame_width = file.attrs['sensor_width']
        frame_height = file.attrs['sensor_height']
        out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 20, (frame_width*2, frame_height))
        speed_np = np.array([])
        for time_idx, time in enumerate(file['timestamps']['timestamps']):
            rgb_data = np.array(file['rgb'][str(time)])
            depth_data = np.array(file['depth'][str(time)])
            e = np.array(file['ego_speed'][str(time)])
            speed = math.sqrt(e[0]*e[0] + e[1]*e[1] + e[2]*e[2])
            speed = speed * 3.6
            speed_np = np.append(speed_np,round(speed,2))
            
            #proj_info = dict(f['geographic']['map_projection'].attrs.items())
            #print(proj_info)
            #e = dict(file['ego_speed'])
            #ego_speed = e.get('ego_speed.attrs')
            #ego_speed = np.array(ego_speed)
            #sys.stdout.write(str(speed))
            #ego_speed = np.array(file['egospeed'][str(ego_speed)])

            #plt.plot(data['velocity'])
            #plt.xticks(range(len(data['time'])), data['time'])

            steer = np.array(file['steer'][str(time)])
            #sys.stdout.write(str(steer))

            throttle = np.array(file['throttle'][str(time)])

            brake = np.array(file['brake'][str(time)])


            sys.stdout.flush()
            rgb_frame, depth_frame = image(rgb_data, depth_data)
            composed_frame = np.hstack((rgb_frame, depth_frame))
            #composed_frame = depth_frame        
            cv2.putText(composed_frame, 'valocity', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            #cv2.putText(composed_frame, 'ego_speed', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            #cv2.putText(composed_frame, ego_speed, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            #cv2.putText(composed_frame, str(time), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(composed_frame, str(round(speed,2)), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(composed_frame, ' km/h', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(composed_frame, 'throttle', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(composed_frame, str(throttle), (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(composed_frame, 'brake', (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(composed_frame, str(brake), (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(composed_frame, 'steer', (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(composed_frame, str(steer), (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            out.write(composed_frame)
        #print(speed_np)
        #time = np.linspace(0,100,100)
        #plt.plot(time,speed_np)
        #   plt.show()

def plot(hdf5_file):
    with h5py.File(hdf5_file, 'r') as file:
        speed_np = np.array([])
        steer_np = np.array([])
        throttle_np = np.array([])
        brake_np = np.array([])
        for time_idx, time in enumerate(file['timestamps']['timestamps']):
            e = np.array(file['ego_speed'][str(time)])
            speed = math.sqrt(e[0]*e[0] + e[1]*e[1] + e[2]*e[2])
            speed = speed * 3.6
            speed_np = np.append(speed_np,round(speed,2))
            

            steer = np.array(file['steer'][str(time)])
            steer_np = np.append(steer_np,steer)
            throttle = np.array(file['throttle'][str(time)])
            throttle_np  = np.append(throttle_np,throttle)
            brake = np.array(file['brake'][str(time)])
            brake_np = np.append(brake_np,brake)
    time = np.linspace(0,100,100)
    fig = plt.figure()
    g1 = plt.subplot(4,1,1)
    plt.title('Velocity')
    plt.plot(time,speed_np)
    plt.xlabel('time '); plt.ylabel('velocity')
    #plt.xlabel("time")
    #plt.ylabel("velocity")
    g2 = plt.subplot(4,1,2)
    plt.title('Steer')
    plt.plot(time,steer_np)
    plt.xlabel('time '); plt.ylabel('steer')
    #plt.xlabel("time")
    #plt.ylabel("steer")
    g3 = plt.subplot(4,1,3)
    plt.title('Throttle')
    plt.plot(time,throttle_np)
    plt.xlabel('time '); plt.ylabel('throttle')
    #plt.xlabel("time")
    #plt.ylabel("throttle")
    
    g4 = plt.subplot(4,1,4)
    plt.title('Brake')
    plt.plot(time,brake_np)
    plt.xlabel('time '); plt.ylabel('brake')
    #plt.xlabel("time")
    #plt.ylabel("brake")
    plt.subplots_adjust(hspace=1.4)
    plt.subplots_adjust(wspace=1.4)
    plt.figure(fig)
    g1.relim()
    g1.autoscale_view()
    g2.relim()
    g2.autoscale_view()
    g3.relim()
    g3.autoscale_view()
    g4.relim()
    g4.autoscale_view()
    plt.draw()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Settings for the data capture", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('hdf5_file', default=None, type=str, help='name of hdf5 file to save the data')

    args = parser.parse_args()
    assert(args.hdf5_file is not None)
   
    sensor_width = 1024
    sensor_height = 768
    fov = 90
    
    HDF5_file = HDF5Saver(sensor_width, sensor_height, os.path.join("data", args.hdf5_file + ".hdf5"))
    CarlaWorld = CarlaWorld(HDF5_file=HDF5_file)

    timestamps = []
    to_run = 1
    print('Recording stared...')
    CarlaWorld.spawn_npcs(number_of_vehicles=1)
    ego_vehicle_iteration = 0
    while ego_vehicle_iteration < to_run:
        CarlaWorld.data_n(sensor_width, sensor_height, fov,
                        frames_to_record_one_ego=100, timestamps=timestamps)
        ego_vehicle_iteration += 1

    #CarlaWorld.remove_npcs()
   
    CarlaWorld.HDF5_file.record_all_timestamps(timestamps)
    HDF5_file.close_HDF5()
    CarlaWorld.remove_sensors()

    video(os.path.join('data', args.hdf5_file + ".hdf5"))
    plot(os.path.join('data', args.hdf5_file + ".hdf5"))