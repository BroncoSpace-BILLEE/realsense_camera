import socket
import numpy as np
import pyrealsense2 as rs
from cv_bridge import CvBridge

def initialize_camera():
	# Initializes the camera for all the frames being analyzed
	imu_pipeline = rs.pipeline()
	imu_config = rs.config()
	imu_config.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 200)
	imu_config.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 200)
	imu_pipeline.start(imu_config)

	camera_pipeline = rs.pipeline()
	camera_config = rs.config()

	camera_config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
	camera_config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)

	camera_pipeline.start(camera_config)

	return imu_pipeline, camera_pipeline

def main():

	_, camera_pipeline = initialize_camera()

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	server_address = ('localhost', 12345)

	print("Starting UDP Server")

	server_socket.bind(server_address)

	bridge = CvBridge()

	while True:

		frames = camera_pipeline.wait_for_frames()

		color_frame = frames.get_color_frame()

		image_data = np.asarray(color_frame.get_data(), dtype=np.uint8)

		compressed_data = bridge.cv2_to_compressed_imgmsg(image_data, 'jpg').data

		image_data = np.asarray(compressed_data, dtype=np.uint8)

		split_data = np.array_split(image_data, 3)

		print("waiting to recieve message")

		data, address = server_socket.recvfrom(4096)

		print(f'Recieved {np.frombuffer(data, dtype=np.int32)}')

		server_socket.sendto(split_data[0].tobytes(), address)
		server_socket.sendto(split_data[1].tobytes(), address)
		server_socket.sendto(split_data[2].tobytes(), address)
		

main()