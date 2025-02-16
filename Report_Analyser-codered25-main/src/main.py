import json
import os
from controller_agent import ControllerAgent

if __name__ == "__main__":
    with open("src\\config.json") as f:
        config = json.load(f)

    os.makedirs(config["output_dir"], exist_ok=True)

    controller = ControllerAgent(config)
    controller.execute()
