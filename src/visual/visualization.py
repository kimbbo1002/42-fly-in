import arcade
from ..logic import Graph

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Fly-In"
PADDING = 100  # pixels of margin around the graph

node_colors = {
    "red": arcade.color.ALIZARIN_CRIMSON,
    "darkred": arcade.color.DARK_RED,
    "orange": arcade.color.SAE,
    "yellow": arcade.color.AMBER,
    "green": arcade.color.APPLE_GREEN,
    "darkgreen": arcade.color.DARK_GREEN,
    "blue": arcade.color.AZURE,
    "darkblue": arcade.color.DARK_BLUE,
    "purple": arcade.color.BRIGHT_LILAC,
    "violet": arcade.color.VIOLET,
    "pink": arcade.color.CARNATION_PINK,
    "crimson": arcade.color.CRIMSON,
    "white": arcade.color.FLORAL_WHITE,
    "black": arcade.color.ARSENIC,
    "grey": arcade.color.ASH_GREY,
    "brown": arcade.color.BROWN,
    "cyan": arcade.color.CYAN,
    "rainbow": arcade.color.ELECTRIC_INDIGO,  # no true rainbow; closest vivid fallback
}


class GameView(arcade.Window):
    def __init__(self, graph: Graph):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.graph = graph
        self.turn = 0
        self.max_turn = len(self.graph.drones[0].trace) - 1
        self.time_accum = 0.0
        self.turn_interval = 0.5  # seconds per turn during auto-play
        self.auto_play = True
        arcade.set_background_color(arcade.color.BLIZZARD_BLUE)

        # warn once at startup about unknown colors, not every frame
        for node in graph.nodes:
            if node.color not in node_colors:
                print(f"Warning: Cannot find color '{node.color}', setting to default 'white'")

        # compute scaling from actual node coordinate bounds
        xs = [n.x for n in graph.nodes]
        ys = [n.y for n in graph.nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max_x - min_x or 1
        span_y = max_y - min_y or 1
        usable_w = SCREEN_WIDTH - 2 * PADDING
        usable_h = SCREEN_HEIGHT - 2 * PADDING
        self.scale_x = usable_w / span_x
        self.scale_y = usable_h / span_y
        self.offset_x = PADDING - min_x * self.scale_x
        self.offset_y = PADDING - min_y * self.scale_y

        # node radius: large enough to be visible, small enough not to overlap
        n = len(graph.nodes)
        self.node_radius = max(18, min(usable_w / (n * 2.5), 40))

    def to_screen_coords(self, x: float, y: float):
        screen_x = self.offset_x + x * self.scale_x
        screen_y = self.offset_y + y * self.scale_y
        return screen_x, screen_y

    def on_update(self, delta_time: float) -> None:
        if self.auto_play:
            self.time_accum += delta_time
            if (
                self.time_accum >= self.turn_interval
                and self.turn < self.max_turn
            ):
                self.time_accum = 0.0
                self.turn += 1

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.RIGHT:
            self.auto_play = False
            if self.turn < self.max_turn:
                self.turn += 1
        elif key == arcade.key.LEFT:
            self.auto_play = False
            if self.turn > 0:
                self.turn -= 1
        elif key == arcade.key.SPACE:
            self.auto_play = not self.auto_play
            self.time_accum = 0.0

    def on_draw(self) -> None:
        self.clear()
        i = self.turn
        r = self.node_radius
        outline = max(1, r * 0.1)
        text_size = max(9, r * 0.45)

        # edges first so nodes render on top
        for edge in self.graph.edges:
            x1, y1 = self.to_screen_coords(edge.a.x, edge.a.y)
            x2, y2 = self.to_screen_coords(edge.b.x, edge.b.y)
            arcade.draw_line(x1, y1, x2, y2, arcade.color.BLACK,
                             max(2, r * 0.15))

        for node in self.graph.nodes:
            x, y = self.to_screen_coords(node.x, node.y)
            color = node_colors.get(node.color, arcade.color.FLORAL_WHITE)
            arcade.draw_circle_filled(x, y, r, color)
            arcade.draw_circle_outline(x, y, r, arcade.color.BLACK, outline)

            arcade.draw_text(
                f"{node.trace[i]}/{node.capacity}",
                x, y + r + 4,
                arcade.color.BLACK, max(8, text_size * 0.8),
                anchor_x='center', anchor_y='bottom'
            )

        for drone in self.graph.drones:
            x, y = self.to_screen_coords(drone.trace[i][0], drone.trace[i][1])
            half = r * 0.6
            arcade.draw_lrbt_rectangle_filled(
                x - half, x + half, y - half, y + half,
                arcade.color.BRIGHT_GREEN
            )
            arcade.draw_lrbt_rectangle_outline(
                x - half, x + half, y - half, y + half,
                arcade.color.BLACK, outline
            )
            arcade.draw_text(
                f"D{drone.id}",
                x, y,
                arcade.color.BLACK, max(8, text_size * 0.8),
                anchor_x='center', anchor_y='center'
            )

        # HUD
        status = "▶ Auto" if self.auto_play else "⏸ Manual"
        arcade.draw_text(
            f"Turn: {self.turn}/{self.max_turn}  |  {status}  " +
            "|  ← → navigate  |  SPACE toggle auto",
            10, 10, arcade.color.BLACK, 12
        )


def sim_visual(graph: Graph):
    view = GameView(graph)
    view.run()
