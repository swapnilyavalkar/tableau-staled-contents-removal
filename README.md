---

# 🧹 Tableau Server Staled Dashboard Cleanup Script

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-1.3%2B-green.svg)
![Tableau Server Client](https://img.shields.io/badge/Tableau%20Server%20Client-0.15%2B-orange.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

## 🛠️ Overview

This Python script automates the process of cleaning up unused\staled Tableau dashboards that haven’t been accessed in the last 180 days. The script connects to Tableau Server, identifies and downloads these dashboards, and then removes them from the server. It also sends email notifications about the operation's success or failure.

## 🚀 Features

- **Automated Cleanup**: Removes dashboards not accessed in the last 180 days.
- **Backup**: Downloads dashboards to a local directory before deletion.
- **Email Notifications**: Sends detailed email reports on success, failure, or non-required operations.
- **Logging**: Provides comprehensive logging for all operations, including error tracking.
- **Data Management**: Exports data of cleaned-up dashboards to Excel files for audit purposes.

## 📦 Prerequisites

- **Python 3.8+**
- **Pandas** (`pip install pandas`)
- **Tableau Server Client** (`pip install tableauserverclient`)
- **PostgreSQL Client** (`pip install psycopg2`)
- Basic knowledge of Tableau Server and PostgreSQL.

## 📝 Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/swapnilyavalkar/Tableau-Staled-Contents-Removal.git
   cd Tableau-Staled-Contents-Removal
   ```

2. **Configure the Script**:
   - Update the `pgdatabase.ini`, `LocalOperations.py` and `Variables.py` files with your environment-specific settings like Tableau Server credentials, PostgreSQL connection parameters, and email server details.
   - Adjust the `workbook_age_threshold` and directory paths as needed.
   - `TriggerAlerts.py` can be used send alert emails to users before actually deleting the workbooks.

## 🖥️ Usage

To run the script and perform the cleanup:

```bash
python ExecuteRemoval.py
```

### Example Output

- Logs are generated in the `logs/` directory.
- Cleaned-up dashboards are saved in `data_files/`.
- Email notifications are sent to the specified recipients.

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributions

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/swapnilyavalkar/Tableau-Staled-Contents-Removal/issues) or open a pull request.

---