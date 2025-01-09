from controller_agent import ControllerAgent

if __name__ == "__main__":
    # Configuration: Define the file path
    config = {
        'source_path': 'data/raw/SuperStoreUS-2015(Orders).csv',
    }

    # Initialize the controller agent with the configuration
    controller = ControllerAgent(config)

    # Execute the data analysis and generate plots
    controller.execute()
