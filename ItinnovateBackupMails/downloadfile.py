import mysql.connector
import json
import os


def download_file_from_database(file_id):
    try:
        # Load database and download configuration from config file
        with open("config.json") as config_file:
            config = json.load(config_file)

        # Connect to MySQL
        db_connection = mysql.connector.connect(**config["database"])
        cursor = db_connection.cursor()

        # Query the database to retrieve the file data
        query = "SELECT filename, data FROM attachments WHERE id = %s"
        cursor.execute(query, (file_id,))
        file_record = cursor.fetchone()

        if file_record:
            filename, file_data = file_record

            # Get download directory from config
            download_dir = config.get("download_directory", "")

            # Construct the output path
            output_path = os.path.join(download_dir, filename)

            # Write the file data to the specified output path
            with open(output_path, "wb") as file:
                file.write(file_data)

            print(f"File '{filename}' downloaded successfully to '{output_path}'.")
        else:
            print(f"File with ID {file_id} not found in the database.")

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL:", error)
    finally:
        # Close MySQL connections
        if 'db_connection' in locals():
            cursor.close()
            db_connection.close()


download_file_from_database(45)