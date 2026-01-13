# CMPE300 Project 2: Parallel Grid-Based Battle Simulation

A distributed parallel computing simulation of a grid-based battle system using MPI (Message Passing Interface). Units from four different factions (Earth, Fire, Water, Air) engage in strategic combat across a partitioned grid, with each grid section managed by separate parallel processes.

## 📋 Overview

This project implements a sophisticated parallel simulation where:
- **Master Process** coordinates the simulation and manages input/output
- **Worker Processes** handle grid partitions in parallel, managing unit combat, movement, and interactions
- **Four Unit Factions** with unique abilities, attack patterns, and characteristics
- **Wave-based Gameplay** where multiple waves of units enter the battlefield
- **Inter-process Communication** for handling units that interact across partition boundaries

## 🎮 Unit Types & Characteristics

| Unit | HP | Attack | Heal | Threshold | Special Ability |
|------|----|----|------|-----------|-----------------|
| 🌍 **Earth** | 18 | 2 | 3 | 9 | **Fortification**: Takes 50% reduced damage |
| 🔥 **Fire** | 12 | 4 | 1 | 6 | **Rage**: Attack increases with consecutive attacks (max +2) |
| 💧 **Water** | 14 | 3 | 2 | 7 | **Diagonal Attacks**: Attacks diagonally adjacent cells |
| 🛩️ **Air** | 10 | 2 | 2 | 5 | **Mobility**: Can move to empty cells; attacks in extended range |

### Attack Patterns
- **Earth**: Cardinal directions (↑ ↓ ← →)
- **Fire**: All 8 adjacent cells
- **Water**: Diagonals (↖ ↗ ↙ ↘)
- **Air**: Extended range (up to 2 cells in all 8 directions)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Master Process (Rank 0)            │
│  • Parse input                               │
│  • Coordinate waves                          │
│  • Aggregate results                         │
│  • Generate output                           │
└─────────────────────────────────────────────┘
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Worker 1 │  │ Worker 2 │  │ Worker N │
│ (Rank 1) │  │ (Rank 2) │  │ (Rank N) │
├──────────┤  ├──────────┤  ├──────────┤
│ Subgrid  │  │ Subgrid  │  │ Subgrid  │
│ Section  │  │ Section  │  │ Section  │
└──────────┘  └──────────┘  └──────────┘
```

### File Structure

```
.
├── main.py              # Entry point, orchestrates simulation
├── simulation.py        # Grid and Unit classes
├── communication.py     # MPI communication logic
├── parser.py           # Input file parser
├── utils.py            # Helper functions
├── exec.sh             # Example execution script
├── inputs/             # Sample input files
└── outputs/            # Generated output files
```

## 🚀 Getting Started

### Prerequisites
- **Python 3.x**
- **mpi4py** library
- **NumPy** library
- **MPI Implementation** (OpenMPI, MPICH, or MS-MPI)

### Installation

1. **Install Python dependencies:**
```bash
pip install mpi4py numpy
```

2. **Install MPI implementation:**

**macOS:**
```bash
brew install open-mpi
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install openmpi-bin openmpi-common libopenmpi-dev
```

**Windows:**
- Download and install [MS-MPI](https://docs.microsoft.com/en-us/message-passing-interface/microsoft-mpi)

## 🎯 Usage

### Basic Execution

```bash
mpiexec -n <number_of_processes> python main.py <input_file> <output_file>
```

**Example:**
```bash
mpiexec -n 10 python main.py input1.txt output1.txt
```

### Process Count Requirements

⚠️ **Important**: The number of processes must be **a perfect square plus 1**

- Total processes = `sqrt_p × sqrt_p + 1`
- Examples: 5 (2×2+1), 10 (3×3+1), 17 (4×4+1), 26 (5×5+1), etc.

| Total Processes | Worker Processes | Grid Partition |
|----------------|------------------|----------------|
| 5 | 4 | 2×2 |
| 10 | 9 | 3×3 |
| 17 | 16 | 4×4 |
| 26 | 25 | 5×5 |

### Oversubscribing (More processes than CPU cores)

```bash
mpiexec --oversubscribe -n 10 python main.py input1.txt output1.txt
```

## 📝 Input Format

```
<grid_size> <wave_count> <units_per_faction> <rounds>
Wave 1:
E: <x1> <y1>, <x2> <y2>
F: <x1> <y1>, <x2> <y2>
W: <x1> <y1>, <x2> <y2>
A: <x1> <y1>, <x2> <y2>
Wave 2:
...
```

**Example:**
```
8 2 2 4
Wave 1:
E: 0 0, 1 1
F: 2 2, 3 3
W: 4 4, 4 5
A: 6 6, 7 7
Wave 2:
E: 1 0, 2 1
F: 3 2, 4 3
W: 5 4, 6 5
A: 7 6, 0 7
```

## 📊 Output

### Standard Output
- Final grid state saved to specified output file
- Shows faction of units at each grid position (E/F/W/A or . for empty)

### Detailed Output
Controlled by `DEBUG` variable in `main.py`:

**Debug Mode ON** (`DEBUG = True`):
- Detailed logs printed to terminal
- Shows unit initialization, attacks, damage, healing, deaths

**Debug Mode OFF** (`DEBUG = False`):
- Detailed logs saved to `<output_file>_detailed.txt`
- Clean execution without terminal spam

## 🔧 Configuration

Edit `main.py` to change debug mode:
```python
DEBUG = False  # Set to True for terminal output
```

## 🧪 Testing

**Note**: Input and output `.txt` files are not included in the repository. Generate your own test cases using the provided script.

### Generating Test Inputs

Use the random input generator:
```bash
python inputs/generateRandomInput.py
```

This will create random test cases in the `inputs/` directory.

### Running Tests

**Quick Test:**
```bash
mpiexec -n 10 python main.py inputs/randomInput0.txt output_test.txt
```

## 🛠️ Implementation Details

### Communication Strategy
- **2D Grid Communication**: Uses 8-directional message passing
- **Tag System**: Dedicated tags for each direction (11-18)
- **Odd-Even Protocol**: Alternating send/receive to prevent deadlocks
- **Boundary Handling**: Special cases for edge and corner processors

### Simulation Flow
1. **Initialization**: Master parses input and distributes subgrids
2. **Decision Phase**: Each unit decides to attack or heal
3. **Attack Phase**: Units attack according to their patterns
4. **Communication**: Cross-boundary attacks sent via MPI messages
5. **Resolution**: Damage, movement, and healing resolved
6. **Collection**: Master aggregates results from workers
7. **Repeat**: Process continues for all rounds and waves

### Parallel Optimization
- Grid partitioning minimizes inter-process communication
- Asynchronous message passing for boundary interactions
- Local computation maximized within each partition

## 📚 Project Structure

- **`main.py`**: Orchestrates simulation, handles master process logic
- **`simulation.py`**: Defines Grid and Unit classes with game mechanics
- **`communication.py`**: Implements MPI message passing protocols
- **`parser.py`**: Parses input files into simulation data structures
- **`utils.py`**: Helper functions for coordinate mapping and message handling

## 🤝 Contributing

This is an academic project for CMPE300 - Analysis of Algorithms course. 

## 📄 License

This project is part of coursework for Boğaziçi University CMPE300.

## 🎓 Course Information

**Course**: CMPE300 - Analysis of Algorithms  
**Project**: Parallel Grid Simulation

---

**Note**: Grid size must be divisible by `sqrt(number_of_worker_processes)` for proper partitioning.
