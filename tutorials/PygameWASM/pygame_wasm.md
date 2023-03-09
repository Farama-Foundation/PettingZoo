# Tutorial
This tutorial provides a working example of using Pygame with WebAssembly to run and render a PettingZoo environment locally in the browser. 

The script displays a game of chess between two random agents, though it can be easily changed to any other PettingZoo environment, provided the dependencies are satisfied (see: [Modifying](#modifying-)). Features such as loading trained models or using interactive environments should be possible, but have not been tested.

## Pygame & WebAssembly (WASM)

[WebAssembly](https://webassembly.org/) (WASM) allows many languages to run locally in the browser with near-native performance. The python package [Pygbag](https://github.com/pygame-web/pygbag) allows us to run python scripts in the web using WebAssembly--including [Pygame](https://github.com/pygame/pygame), which is used for rendering PettingZoo environments. 

For more information and example scripts, see [pygame-web](https://github.com/pygame-web/pygame-web.github.io)

Packages may not all work natively using Pygbag, so any issues can be reported to [pkg-porting-wasm](https://github.com/pygame-web/pkg-porting-wasm)

Pygbag works via a virtual environment, and all dependencies must be downloaded locally as wheels and unzipped. `install.sh` script does this and moves the unzipped packages into `/modules` which needs to be added to the system path before importing. Pygbag only allows a single file `main.py` to be used, and requires a specific structure using `asyncio` (see [pygame-web](https://github.com/pygame-web/pygame-web.github.io))



## Usage:

1. (Optional) Create a virtual environment: `conda create -n pygame-wasm python=3.10`
2. (Optional) Activate the virtual environment: `conda activate pygame-wasm`
3. Install requirements: `pip install -r requirements.txt`
4. Run `bash install.sh` in order to download and unzip dependencies to be used in the WASM virtual machine.
5. Change directory to parent: `cd` .. 
6. Run pygbag on this directory: pygbag PygameWASM `
7. Open your browser and go to `http://localhost:8000/` (for debugging info: http://localhost:8000/#debug)

## Modifying:
Dependencies and versions can be changed in `install.sh`, which can be re-run (although it is safest to delete `/modules` and ensure there are not multiple versions of the same package)

## Debugging:

- Python 3.11 is recommended for WASM, but is currently not supported by PettingZoo, which may lead to errors. 

- Calling certain sub-modules (e.g., `package.submodule`) without explicitly importing them can also cause errors. For example, in `connect_four.py`, line 281 `        observation = np.array(pygame.surfarray.pixels3d(self.screen))` raises an error. 
  - This can be solved by explicitly importing the sub-module: add the line `import pygame.surfarray` to `main.py` (no need to modify the original file it was called in)