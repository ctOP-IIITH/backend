# oneM2M Wrapper ctOP Backend

This project is a backend for the oneM2M Wrapper ctOP, built with FastAPI.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.6+
- pip
- virtualenv

### Installation

1. Clone the repository
2. Navigate to the project directory
3. Create a virtual environment: `python3 -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install the dependencies: `pip install -r requirements.txt`
6. Run the server: `./run.sh`
7. Open the API documentation in your browser: http://localhost:8000/docs

## For Developers
Please use the following command to update requirements.txt after installing new packages:
```
pipreqs --force && echo "gunicorn==21.2.0" >> requirements.txt && echo "uvicorn==0.24.0.post1" >> requirements.txt && sort -o requirements.txt requirements.txt
```

### VS Code Settings

This repository includes a `.vscode` folder that contains settings to help ensure consistent behavior and standards across different development environments. These settings are defined in the `settings.json` file and include configurations for Python formatting and linting.

If you're using Visual Studio Code as your editor, these settings will be applied automatically when you open the workspace. If you're using a different editor, you may need to configure these settings manually.

Please note that these settings are recommendations and may be overridden based on personal preference or specific project requirements.

**Please have the following extensions installed:**
- Python
- Black
- Pylance
- Pylint

## Running the tests

**TODO**

## Deployment

**TODO**

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details
