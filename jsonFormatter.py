import os

# This python app simply formats the json of the afghan data as it yields an error when
# attempting to parse it in python.

def main():
    cwd = os.getcwd()
    path = f"{cwd}/tester"
    os.chdir(path)

    for file in os.listdir():
        f_path = f"{path}/{file}" if file.endswith('.json') else None

        if f_path is not None:
            # Prepend json data with 'data' key value
            with open(f_path, 'r+') as f:
                line = '{"data":['
                content = f.read()
                f.seek(0, 0)
                f.write(line.rstrip('\r\n') + '\n' + content + ']}')

            # Add ',' at end of every tweet object (creating list)
            with open(f_path) as f:
                lines = f.read().splitlines()
            with open(f_path, "w") as f:
                length = len(lines)
                for index, line in enumerate(lines):
                    if index == 0 or index == length-1:
                        print(line, file=f)
                    else:
                        print(line + ',', file=f)

    print('All files formatted.')

if __name__ == "__main__":
    main()