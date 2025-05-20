import arcade
from pyglet.event import EVENT_HANDLE_STATE

WINDOW_WIGHT = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE ="Platformer"

TILE_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5

class GameView(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIGHT, WINDOW_HEIGHT, WINDOW_TITLE)

        self.player_texture = arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png")
        self.player_sprite = arcade.Sprite(self.player_texture)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        for x in range(0,1250,64):
            wall = arcade.Sprite (path_or_texture= ":resources:images/tiles/grassMid.png", scale=0.5)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        coordinate_list = [[512, 96], [256,96], [768, 96]]

        for coordinate in coordinate_list:
            wall = arcade.Sprite (path_or_texture= ":resources:images/tiles/boxCrate_double.png", scale=0.5)
            wall.position = coordinate
            self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEngineSimple( self.player_sprite, self.wall_list)

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

    def setup(self):
        pass

    def on_draw(self):
        self.clear()
        self.player_list.draw()
        self.wall_list.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()

    def on_key_press(self, key, modifiers):

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0


def main():
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
