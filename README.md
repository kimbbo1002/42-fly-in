_This project has been created as part of the 42 curriculum by \<bokim\>_

# Fly-In

## Description
This project implements an efficient drone routing system that navigates multiple drones across connected zones, minimizing simulation turns while respecting movement constraints and capacity bottlenecks.

---

## Instructions

### Makefile Rules
* `make`: Installs project dependencies using `uv` and sets up the virtual environment.
* `make run`: Runs the main program loop (automatically boots the map selection interface).
* `make debug`: Runs the built-in Python debugger (`pdb`) for stepping through route evaluations.
* `make lint` / `make lint-strict`: Performs static syntax checking and type analysis using `flake8` and `mypy`.
* `make fclean`: Wipes the local virtual environment and removes lock files (`uv.lock`, `.venv/`).

### How to Launch the Program
1. Run `make` to initialize the project workspace.
2. Run `make run` to launch the application.
3. Select a network configuration map from the file dialog window that appears.

### How to Add a Map
* Pre-configured maps are stored in the `maps/` directory at the project root.
* To add a custom configuration, place your formatted `.txt` map file inside the `maps/` folder.
* Launch the simulation via `make run` and pick your file from the interface.

### UI Controls During Visualization
* `SPACE`: Toggle between automatic playback mode and manual frame stepping.
* `RIGHT ARROW (→)`: Move forward exactly one turn in the routing timeline.
* `LEFT ARROW (←)`: Rewind back exactly one turn to audit past positions and capacity stresses.

---

## Technical Explanation

### Pathfinding & Network Flow (Dijkstra's Algorithm)

#### Overview of Dijkstra's Algorithm
Dijkstra's Algorithm is a graph search algorithm that solves the single-source shortest path problem for a graph with non-negative edge path costs, producing a shortest-path tree. 

In this simulation framework, the algorithm is inverted structurally: it executes globally from the target destination (`end_hub`) backward across directed edges. This generates a static distance vector field across all network hubs, ensuring every node knows its exact minimum distance parameters to the goal before any movement loop begins.

#### Project Implementation Mechanics

* **Pre-Computation Phase (`min_distance`)**: 
  Before any drones are dispatched from the staging area, a topological sweep calculates the exact edge-weight distance mapping from the `end_hub` back to all reachable nodes. This computed integer score is permanently cached inside each node's `distance` attribute. Any node with a value of `-1` represents an unresolvable path or structural dead end.

* **Congestion-Aware Reverse Dispatch**:
  To mitigate gridlock within high-density bottlenecks, drone updates are processed sequentially each turn, sorted by proximity to the goal:
  
  $$\text{Sort Order} = \arg\min_{\text{distance}}(\text{Drone.node})$$

  By prioritizing the clearance of drones closest to the destination first, the pipeline naturally pulls traffic forward, vacating capacity slots in front of trailing drones.

* **Dynamic Local Traversal**:
  During a turn execution cycle, each drone independently evaluates adjacent downstream nodes. It selects the candidate node that simultaneously satisfies network capacity thresholds (both node occupant limits and link limits) while maximizing progress toward the goal:

  $$\text{Target Node} = \arg\min_{n \in \text{Neighbors}} (\text{Distance}_n)$$

---

### Visualization Layer (Arcade Framework)

The project includes an interactive, frame-by-frame graphics rendering engine built on top of the Python `arcade` library. It translates abstract topological network states into visual metrics, allowing developers to monitor edge congestion, node overflows, and pathing anomalies in real time.

#### Multi-Coordinate Space Projection (Mapping Math)
The simulation logic tracks hubs using abstract grid dimensions (e.g., $x \in [0, 23]$, $y \in [-2, 2]$). Monitors, however, render objects using a localized absolute pixel coordinate grid where the origin $(0,0)$ sits at the bottom-left window edge. 

To bridge this gap without distorting or clipping data shapes, the visualizer applies a two-dimensional linear transform mapping via scale scaling and dynamic center-biasing:

$$X_{\text{screen}} = X_{\text{offset}} + (X_{\text{grid}} \cdot S_x)$$

$$Y_{\text{screen}} = Y_{\text{offset}} + (Y_{\text{grid}} \cdot S_y)$$

Where:
* $S_x, S_y$ represent directional scaling multipliers that stretch microscopic unit intervals into visible screen gaps.
* $X_{\text{offset}}$ shifts the graph layout horizontally to reserve left margins.
* $Y_{\text{offset}}$ maps the central node row ($y=0$) onto the screen's literal vertical midpoint ($\text{Height} / 2$), ensuring negative coordinates do not render below the viewable threshold.

#### Dynamic Node Resizing Engine
When reading maps with massive topological structures, rendering nodes at a fixed size leads to severe screen crowding and overlapping boundaries. To fix this, the engine dynamically recalculates object radii based on the absolute complexity of the loaded dataset.

The system scales node elements down using an inverse-square relationship relative to total graph volume ($N_{\text{nodes}}$), clamped safely within maximum bounds for clarity and minimum bounds to prevent geometric disappearance:

$$R_{\text{node}} = \max\left(R_{\text{min}}, \min\left(\frac{C}{\sqrt{N_{\text{nodes}}}}, R_{\text{max}}\right)\right)$$

Where:
* $C$ is a baseline scaling factor (e.g., $120$) that sets structural proportions.
* $R_{\text{max}}$ prevents low-volume nodes from appearing bloated ($20\text{px}$).
* $R_{\text{min}}$ guarantees a readable surface area even in dense network layouts ($5\text{px}$).

To maintain strict visual layout proportions across varying layout shapes, typography assets are linked directly to this calculated variable:

$$\text{Font Size} = \max\left(6, \min(R_{\text{node}} - 2, 11)\right)$$

This layout adjustment forces labels to shrink symmetrically alongside their respective parent nodes, protecting display readability across large, complex graph layouts.

#### Arcade Lifecycle Integration & Event Loop
The Arcade framework shifts the project from a standard imperative execution model (e.g., a structural sequential `while` loop) into an asynchronous, event-driven graphics pipeline. Once `arcade.run()` is invoked, control is handed over to Arcade's master window thread loop, which coordinates rendering and updates continuously.

```text
       [ Start Arcade Application ]
                     │
                     ▼
             ┌───────────────┐
             │ arcade.run()  │◄────────────────────────┐
             └───────┬───────┘                         │
                     │                                 │
     ┌───────────────┴───────────────┐                 │
     ▼                               ▼                 │
┌──────────────────┐       ┌──────────────────┐        │ Continuous Loop
│   on_update()    │       │    on_draw()     │        │ (60 FPS Window)
│                  │       │                  │        │
│ Updates clock &  │       │ Reads snapshot at│        │
│ ticks sim forward│       │ self.history[idx]│        │
│ live every turn  │       │ & paints pixels  │        │
└────────┬─────────┘       └────────┬─────────┘        │
         │                          │                  │
         └──────────────────────────┴──────────────────┘
                         ▲
                         │ Intercepts keystrokes
               ┌─────────┴─────────┐
               │   on_key_press()  │ ───► Updates frame index counter (idx)
               └───────────────────┘
