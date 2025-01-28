# CRUD Python MySQL

A simple and flexible CRUD (Create, Read, Update, Delete) application built with Python and MySQL. This project allows you to manage data with basic operations connected to a MySQL database using Python.

## Features

- **Create**: Insert new records into the MySQL database.
- **Read**: Retrieve data from the MySQL database.
- **Update**: Modify existing records in the database.
- **Delete**: Remove records from the database.

## Technologies Used

- Python
- MySQL
- Python's `mysql-connector` library
- Command Line Interface (CLI)

## Setup

### Prerequisites

- **Python 3.x** installed.
- **MySQL** server running and accessible.
- A MySQL database created for this project.

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/adenpribadi/crud-python-mysql.git
   cd crud-python-mysql
   ``` 
2. Create a virtual environment (optional but recommended):
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
  ```

3. Install the required dependencies:
  ```bash
  pip install -r requirements.txt
  ```

4. Configure MySQL:
  Ensure MySQL is running.
  Create a new database (if not already done):
  ```sql
  CREATE DATABASE crud_db;
  ```

5. Update database credentials in the config.py file to match your MySQL configuration (e.g., username, password, database name).
  
6. Run the application:
  ```bash
  python app.py
  ```

File Structure
```graphql
  crud-python-mysql/
  │
  ├── app.py              # Main Python script to run the CRUD operations.
  ├── config.py           # Configuration file for MySQL database connection.
  ├── requirements.txt    # List of Python dependencies.
  └── README.md           # This file.
```

Usage
Once the application is running, you can perform CRUD operations directly through the CLI:

Create: Add a new record.
Read: View all records in the database.
Update: Modify an existing record.
Delete: Remove a record from the database.
Example commands:
```bash
python app.py create
python app.py read
python app.py update
python app.py delete
```

License
This project is open-source and available under the MIT License.

Contributing
Feel free to fork this repository, make changes, and submit pull requests for enhancements or bug fixes.

Contact
For more information or support, please contact the repository owner or open an issue in this GitHub project.
```markdown
### Penjelasan:
- **`Features`** menjelaskan fitur-fitur utama aplikasi.
- **`Technologies Used`** menyebutkan teknologi yang digunakan di project ini.
- **`Setup`** menjelaskan langkah-langkah untuk mengatur dan menjalankan project di komputer lokal.
- **`File Structure`** memberikan gambaran umum struktur file dalam project.
- **`Usage`** memberikan contoh penggunaan aplikasi.
- **`License`** dan **`Contributing`** memberikan informasi tentang lisensi dan kontribusi terhadap project.
- **`Contact`** untuk memberikan cara menghubungi atau memberikan dukungan lebih lanjut.
```

Cukup sesuaikan file ini dengan kebutuhan proyek Anda. Semoga membantu! 😊
