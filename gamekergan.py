import arcade
import os
from pyglet.event import EVENT_HANDLE_STATE
from PIL import Image
import io
import time
import json

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"

TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 0.7
PLAYER_JUMP_SPEED = 20

LEFT_FACING = 0
RIGHT_FACING = 1

LEADERBOARD_FILE = "leaderboard.json"

def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=2)

class PlayerCharacter(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = 1
        self.jumping = False
        self.animation_time = 0
        self.animation_speed = 0.1

        # Загружаем текстуры для анимации ходьбы
        main_path = "pics/Char_walk_"
        self.walk_textures_right = []  # Для движения вправо
        self.walk_textures_left = []   # Для движения влево
        
        for i in range(6):
            # Загружаем оригинальную текстуру для движения вправо
            texture_right = arcade.load_texture(f"{main_path}{i}.png")
            self.walk_textures_right.append(texture_right)
            
            # Загружаем отраженную текстуру для движения влево
            img = Image.open(f"{main_path}{i}.png")
            img_flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
            temp_path = f"temp_flipped_{i}.png"
            img_flipped.save(temp_path)
            texture_left = arcade.load_texture(temp_path)
            self.walk_textures_left.append(texture_left)
            os.remove(temp_path)
            
        # Устанавливаем начальную текстуру
        self.texture = self.walk_textures_right[0]

    def update_animation(self, delta_time: float = 1 / 30):
        self.animation_time += delta_time

        if self.change_x < 0:
            self.character_face_direction = LEFT_FACING
            textures = self.walk_textures_left
        elif self.change_x > 0:
            self.character_face_direction = RIGHT_FACING
            textures = self.walk_textures_right
        else:
            textures = self.walk_textures_right if self.character_face_direction == RIGHT_FACING else self.walk_textures_left

        if self.change_x != 0:
            if self.animation_time >= self.animation_speed:
                self.cur_texture += 1
                if self.cur_texture >= len(textures):
                    self.cur_texture = 0
                self.texture = textures[self.cur_texture]
                self.animation_time = 0
        else:
            self.cur_texture = 0
            self.texture = textures[self.cur_texture]


class GameView(arcade.View):
    def __init__(self, nickname):
        super().__init__()
        self.nickname = nickname
        self.best_time = None
        self.start_time = None
        self.time_text = None
        self.score = 0
        self.level = 1
        self.player_texture = None
        self.player_sprite = None
        self.tile_map = None
        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.reset_score = True
        self.animation_time = 0
        self.frame = 0
        self.physics_engine = None
        self.background = None

        # Загружаем звуки
        self.collect_coin_sound = arcade.load_sound("pics/coin.mp3")
        self.jump_sound = arcade.load_sound("pics/jump.mp3")
        self.gameover_sound = arcade.load_sound("pics/game_over.mp3")

    def setup(self):
        # Загружаем фоновое изображение
        self.background = arcade.load_texture("pics/zadnik.png")

        layer_option = {
            "map1": {"use_spatial_hash": True},
            "back": {"use_spatial_hash": True},
            "Coins": {"use_spatial_hash": True},
            "DontTouch": {"use_spatial_hash": True}
        }
        print(f"pics/L{self.level}.json")
        self.tile_map = arcade.load_tilemap(f"pics/L{self.level}.json",
                                          scaling=TILE_SCALING,
                                          layer_options=layer_option
                                          )

        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.scene.add_sprite_list_after("Player", "back")
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        # Создаем физический движок
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene["map1"],
            gravity_constant=GRAVITY
        )

        # Настраиваем камеру
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        # Инициализируем счет
        self.score = 0
        self.start_time = time.time()
        self.time_text = arcade.Text(text=f"Время: 0.0 сек", x=0, y=0, font_size=40)

        # Устанавливаем цвет фона
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width)
        self.end_of_map *= self.tile_map.scaling
        print(self.end_of_map)

    def on_draw(self):
        self.clear()
        self.camera.use()

        arcade.draw_texture_rect(
            self.background,
            rect=arcade.LBWH(-3000, -3000, 6000, 6000)
        )

        self.scene.draw()

        self.gui_camera.use()
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.time_text.text = f"Время: {elapsed:.1f} сек"
        self.time_text.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.player_sprite.update_animation(delta_time)

        # Проверяем столкновения с монетами
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 75

        # Проверяем столкновения с опасными объектами
        if arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["DontTouch"]
        ):
            arcade.play_sound(self.gameover_sound)
            self.setup()

        # Проверяем условия победы
        if (self.player_sprite.center_x >= 2000 and 
            self.player_sprite.center_y >= 508 and 
            self.score >= 1125):
            elapsed = time.time() - self.start_time
            leaderboard = load_leaderboard()
            leaderboard.append({"nick": self.nickname, "time": elapsed})
            leaderboard = sorted(leaderboard, key=lambda x: x["time"])[:5]
            save_leaderboard(leaderboard)
            leaderboard_view = LeaderboardView(leaderboard, self.nickname, elapsed)
            leaderboard_view.window = self.window
            self.window.show_view(leaderboard_view)

        # Обновляем позицию камеры
        camera_x = self.player_sprite.center_x - WINDOW_WIDTH / 2 + WINDOW_WIDTH / 2
        camera_y = self.player_sprite.center_y - WINDOW_HEIGHT / 2 + WINDOW_HEIGHT / 2
        
        # Ограничиваем камеру границами карты (30x20 тайлов, каждый 144x144 пикселя)
        camera_x = max(0, min(camera_x, 2160))
        camera_y = max(0, min(camera_y, 1440))
        
        self.camera.position = (camera_x, camera_y)

    def on_key_press(self, key, modifiers):

        if key == arcade.key.ESCAPE:
            self.setup()

        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
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

class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture("pics/main2.png")
        self.nickname = ""
        self.input_active = True
        self.nick_text = arcade.Text("", self.window.width // 2, self.window.height // 2 - 130, arcade.color.WHITE, 64, anchor_x="center")

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.input_active = True
        self.nickname = ""
        self.nick_text.text = ""

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            rect=arcade.LBWH(0, 0, self.window.width, self.window.height)
        )
        self.nick_text.text = self.nickname
        self.nick_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER and self.nickname.strip():
            game_view = GameView(self.nickname.strip())
            game_view.window = self.window
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.BACKSPACE:
            self.nickname = self.nickname[:-1]

    def on_text(self, text):
        if self.input_active and len(self.nickname) < 16 and text.isprintable():
            self.nickname += text

class LeaderboardView(arcade.View):
    def __init__(self, leaderboard, current_nick, current_time):
        super().__init__()
        self.leaderboard = leaderboard
        self.current_nick = current_nick
        self.current_time = current_time
        self.background = arcade.load_texture("pics/table_of_records.png")

    def on_draw(self):
        self.clear()
        # Фон таблицы лидеров
        arcade.draw_texture_rect(
            self.background,
            rect=arcade.LBWH(0, 0, self.window.width, self.window.height)
        )

        # Таблица
        for i, entry in enumerate(self.leaderboard):
            color = arcade.color.WHITE
            if entry["nick"] == self.current_nick and abs(entry["time"] - self.current_time) < 0.01:
                color = arcade.color.LIGHT_GREEN
            arcade.draw_text(f"{i+1}. {entry['nick']} — {entry['time']:.2f} сек", self.window.width/2, self.window.height/2 + 80 - i*50, color, 36, anchor_x="center")
        arcade.draw_text("Нажмите ENTER для новой игры", self.window.width/2, self.window.height/2 - 200, arcade.color.GRAY, 24, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            start_view = StartView()
            start_view.window = self.window
            self.window.show_view(start_view)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    start_view = StartView()
    start_view.window = window
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()