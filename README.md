# Backend

## Run the project

```
POSTGRESQL_DATABASE_MASTER_URL=postgresql+asyncpg://root:dotmail123@postgres/succeedex POSTGRESQL_DATABASE_SLAVE_URL=postgresql+asyncpg://root:dotmail123@postgres/succeedex SECRET_KEY=2ae7ea295c404bacbca5f608b621f8dd fastapi dev main.py
```

## Features

- User authentication and authorization
- CRUD operations for user management
- Integration with PostgreSQL for data storage
- Asynchronous processing with FastAPI
- Secure handling of sensitive information with environment variables

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/backend-crm.git
    cd backend-crm
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up the environment variables:
    ```sh
    cp .env.example .env
    # Edit the .env file with your configuration
    ```

## Usage

To run the project, use the following command:
```sh
POSTGRESQL_DATABASE_MASTER_URL=postgresql+asyncpg://root:dotmail123@postgres/succeedex POSTGRESQL_DATABASE_SLAVE_URL=postgresql+asyncpg://root:dotmail123@postgres/succeedex SECRET_KEY=2ae7ea295c404bacbca5f608b621f8dd fastapi dev main.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.