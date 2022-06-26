import glob
import os
import sys
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla
import random
import time
import numpy as np
import math
from spawn_npc import NPCClass
from set_synchronous_mode import CarlaSyncMode



class CarlaWorld:
    def __init__(self, HDF5_file):
        self.HDF5_file = HDF5_file
        client = carla.Client('localhost', 2000)
        client.set_timeout(20.0)
        self.world = client.get_world()
     
        self.blueprint_library = self.world.get_blueprint_library()
        # Sensors stuff
        self.camera_x_location = 1.0
        self.camera_y_location = 0.0
        self.camera_z_location = 2.0
        self.sensors_list = []
    
        self.total_recorded_frames = 0
        self.first_time_simulating = True
        

    def remove_npcs(self):
        print('Destroying actors...')
        self.NPC.remove_npcs()
        print('Done destroying actors.')

    def spawn_npcs(self, number_of_vehicles):
        self.NPC = NPCClass()
        self.vehicles_list= self.NPC.create_npcs(number_of_vehicles)


    def put_rgb_sensor(self, vehicle, sensor_width=640, sensor_height=480, fov=110):
        bp = self.blueprint_library.find('sensor.camera.rgb')
        bp.set_attribute('image_size_x', f'{sensor_width}')
        bp.set_attribute('image_size_y', f'{sensor_height}')
        bp.set_attribute('fov', f'{fov}')

    
        spawn_point = carla.Transform(carla.Location(x=self.camera_x_location, z=self.camera_z_location))
        self.rgb_camera = self.world.spawn_actor(bp, spawn_point, attach_to=vehicle)
        self.rgb_camera.blur_amount = 0.0
        self.rgb_camera.motion_blur_intensity = 0
        self.rgb_camera.motion_max_distortion = 0

        calibration = np.identity(3)
        calibration[0, 2] = sensor_width / 2.0
        calibration[1, 2] = sensor_height / 2.0
        calibration[0, 0] = calibration[1, 1] = sensor_width / (2.0 * np.tan(fov * np.pi / 360.0))
        self.rgb_camera.calibration = calibration  
        self.sensors_list.append(self.rgb_camera)
        return self.rgb_camera

    def put_depth_sensor(self, vehicle, sensor_width=640, sensor_height=480, fov=110):
        bp = self.blueprint_library.find('sensor.camera.depth')
        bp.set_attribute('image_size_x', f'{sensor_width}')
        bp.set_attribute('image_size_y', f'{sensor_height}')
        bp.set_attribute('fov', f'{fov}')

        # Adjust sensor relative position to the vehicle
        spawn_point = carla.Transform(carla.Location(x=self.camera_x_location, z=self.camera_z_location))
        self.depth_camera = self.world.spawn_actor(bp, spawn_point, attach_to=vehicle)
        self.sensors_list.append(self.depth_camera)
        return self.depth_camera

   
    
    def process_depth_data(self, data, sensor_width, sensor_height):
     
        data = np.array(data.raw_data)
        data = data.reshape((sensor_height, sensor_width, 4))
        data = data.astype(np.float32)
        normalized_depth = np.dot(data[:, :, :3], [65536.0, 256.0, 1.0])
        normalized_depth /= 16777215.0  
        depth_meters = normalized_depth * 1000
        return depth_meters
    
    def process_rgb_img(self, img, sensor_width, sensor_height):
        img = np.array(img.raw_data)
        img = img.reshape((sensor_height, sensor_width, 4))
        img = img[:, :, :3]  
        s = img.mean()
        return img,s

    def remove_sensors(self):
        for sensor in self.sensors_list:
            sensor.destroy()
        self.sensors_list = []

    def data_n(self, sensor_width, sensor_height, fov, frames_to_record_one_ego=1, timestamps=[]):
        current_ego_recorded_frames = 0

        ego_vehicle = random.choice([x for x in self.world.get_actors().filter("vehicle.*") ])
        self.put_rgb_sensor(ego_vehicle, sensor_width, sensor_height, fov)
        self.put_depth_sensor(ego_vehicle, sensor_width, sensor_height, fov)
       

        with CarlaSyncMode(self.world, self.rgb_camera, self.depth_camera, fps=30) as sync_mode:
            if self.first_time_simulating:
                for _ in range(30):
                    sync_mode.tick_no_data()

            while current_ego_recorded_frames <= frames_to_record_one_ego:
                if current_ego_recorded_frames == frames_to_record_one_ego:
                    return timestamps
                wait_frame_ticks = 0
                while wait_frame_ticks < 5:
                    sync_mode.tick_no_data()
                    wait_frame_ticks += 1
             
                _,rgb_data, depth_data = sync_mode.tick(timeout=2.0)  
               
                rgb_array,rgb_s = self.process_rgb_img(rgb_data, sensor_width, sensor_height)
                depth_array = self.process_depth_data(depth_data, sensor_width, sensor_height)

                
                

                ego_speed = ego_vehicle.get_velocity()
                ego_speed = np.array([ego_speed.x, ego_speed.y, ego_speed.z])

                steer = ego_vehicle.get_control().steer

                throttle = ego_vehicle.get_control().throttle
                brake = ego_vehicle.get_control().brake



                timestamp = round(time.time() * 1000.0)

                self.HDF5_file.recording(rgb_array, depth_array, rgb_s, ego_speed, steer ,throttle, brake,timestamp)
                current_ego_recorded_frames += 1
                self.total_recorded_frames += 1
                timestamps.append(timestamp)

                sys.stdout.write("\r")
               
                sys.stdout.write('Frame {0}/{1}'.format(
                    self.total_recorded_frames, 100))
                #sys.stdout.write(str(ego_vehicle.get_velocity()))
                sys.stdout.flush()