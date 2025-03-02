from sqlalchemy import text

def file_exec(file_path, conn):
    with open(file_path, "r") as file:
        sql_command = ''
        for line in file:
            # Ignore commented lines
            if not line.startswith('--') and line.strip('\n'):
                # Append line to the command string
                sql_command += line.strip('\n')
                # If the command string ends with ';', it is a full statement
                if sql_command.endswith(';'):
                    # Try to execute statement and commit it
                    try:
                        conn.execute(text(sql_command))
                        conn.commit()
                    # Assert in case of error
                    except Exception as e:
                        print(e)
                    # Finally, clear command string
                    finally:
                        sql_command = ''