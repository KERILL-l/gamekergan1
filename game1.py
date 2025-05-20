import arcade
from pyglet.event import EVENT_HANDLE_STATE

WINDOW_WIGHT = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE ="Platformer"

TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5

GRAVITY = 1
PLAYER_JUMP_SPEED = 20



class GameView(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIGHT, WINDOW_HEIGHT, WINDOW_TITLE)

        self.player_texture = None
        self.player_sprite = None
        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.score_text = None

        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def setup (self):

        self.scene = arcade.Scene()

        self.player_texture = arcade.load_texture(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png")

        self.player_sprite = arcade.Sprite(self.player_texture)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        self.scene.add_sprite_list( "Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Coins", use_spatial_hash=True)


        for x in range(0,1250,64):
            wall = arcade.Sprite (path_or_texture= ":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        coordinate_list = [[512, 96], [256,96], [768, 96]]

        for coordinate in coordinate_list:
            wall = arcade.Sprite (path_or_texture= ":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING)
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        for x in range (128, 1258, 256):
            coin = arcade.Sprite (path_or_texture=":resources:images/items/coinGold.png", scale=COIN_SCALING)
            coin.center_x = x
            coin.center_y = 96
            self.scene.add_sprite("Coins", coin)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls = self.scene["Walls"], gravity_constant=GRAVITY)

        self.camera = arcade.camera.Camera2D()

        self.gui_camera = arcade.camera.Camera2D()
        self.score = 0
        self.score_text = arcade.Text(text= f"Score: {self.score}", x = 0, y = 0)

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.scene.draw()

        self.gui_camera.use()
        self.score_text.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.camera.position = self.player_sprite.position

        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 75
            self.score_text.text = f"Score: {self.score}"


    def on_key_press(self, key, modifiers):

        if key == arcade.key.ESCAPE:
            self.setup()

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0


def main():
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
