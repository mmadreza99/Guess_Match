class ImageTile:
    """ Class that defines the memory tile standard for each tile in the memory game to be uncovered
    """
    def __init__(self, image, width, height):
        self._image = image
        self._width = width
        self._height = height
        self._tile_pos = []

    def __str__(self):
        return "Image name:" + self._image + "\nWidth:" + str(self._width) +"\nHeight:" + str(self._height) + "\n"

    def set_position(self, x_pos, y_pos):
        self._tile_pos .append((x_pos, y_pos))

    def get_position(self):
        assert self._tile_pos != []
        return self._tile_pos

    def display_img(self):
        pass