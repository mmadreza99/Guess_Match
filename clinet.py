import socket
import pygame
import sys

host = "127.0.0.1"
port = 5012
screen = pygame.display.set_mode((320, 240), 0)
while True:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    received = []
    # loop recv, it returns empty string when done, then transmitted data is completely received
    while True:
        recvd_data = client_socket.recv(230400)
        if not recvd_data:
            break
        else:
            received.append(recvd_data)

    dataset = ''.join(received)
    image = pygame.image.fromstring(dataset, (320, 240), "RGB")  # convert received image from string
    screen.blit(image, (0, 0))  # "show image" on the screen
    pygame.display.update()

    # check for quit events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
