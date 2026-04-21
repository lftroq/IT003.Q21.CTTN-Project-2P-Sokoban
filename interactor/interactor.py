import subprocess
import os

mapSize = 16

def interact(filename, input: dict):
    """Execute a game interactor program with game state input.
    
    Runs an executable file with formatted game state information via stdin.
    The input dictionary is converted into a multi-line string format expected
    by the interactor program.
    
    Args:
        filename (str): Name of the executable file to run (relative to interactor folder).
        input (dict): Dictionary containing game state with keys:
            - 'size': Map size
            - 'cur': Current turn number
            - 'T': Total turns
            - 'maze': 2D list representing the game maze
            - 'playerHist': Player move history
            - 'oppHist': Opponent move history
            - 'playerDidMove': Whether player moved (per turn)
            - 'oppDidMove': Whether opponent moved (per turn)
            - 'playerScore': Player's current score
            - 'oppScore': Opponent's current score
    
    Returns:
        str: The stdout output from the executed program.
    """
    # prepare input
    inputLines = [f'{input["size"]} {input["cur"]} {input["T"]}']
    for i in range(mapSize):
        line = ""
        for j in range(mapSize): line += input["maze"][i][j]
        inputLines.append(line)
    
    for i in range(input["cur"] - 1):
        inputLines.append(f'{input["playerHist"][i]} {input["oppHist"][i]} {input["playerDidMove"][i]} {input["oppDidMove"][i]}')
    inputLines.append(f'{input["playerScore"]} {input["oppScore"]}')
    inputStr = '\n'.join(inputLines) + '\n'
    # print('=== INPUT ===')
    # print(inputStr)
    # print('=== END INPUT ===')

    # get output
    # stdout, stderr = 'R', None
    # return stdout
    exePath = os.path.abspath(os.path.join("interactor", filename))
    process = subprocess.Popen(
        [exePath],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        text = True,
        bufsize = 1
    )

    stdout, stderr = process.communicate(input = inputStr)


    # # print input
    # process.stdin.write(str(input["cur"]) + " " + str(input["T"]) + str(input["k"]) + "\n")
    # for i in range(mapSize):
    #     for j in range(mapSize):
    #         process.stdin.write(input["maze"][i][j] + "\n "[j + 1 < mapSize])
    # process.stdin.write(input["playerHist"] + "\n")
    # process.stdin.write(input["oppHist"] + "\n")
    # process.stdin.write(str(input["playerScore"]) + " " + str(input["oppScore"]) + "\n")
    # process.stdin.flush()
    # process.stdin.close()

    # # seek = process.stdout.readline().strip()
    # # while seek:
    # #     print(seek)
    # #     seek = process.stdout.readline().strip()

    # output = process.stdout.readline().strip()

    # print(stdout, stderr)
    process.wait()
    return stdout

def compile_cpp_files():
    """Compile all C++ files in the interactor directory.
    
    Searches the directory containing this script for all .cpp files and
    compiles each one using g++ to create corresponding executable files.
    Each compiled executable has the same name as the source file without
    the .cpp extension.
    
    Raises:
        subprocess.CalledProcessError: If compilation of any C++ file fails.
    """
    folder = os.path.dirname(os.path.abspath(__file__))
    cpp_files = [f for f in os.listdir(folder) if f.endswith('.cpp')]
    
    for cpp_file in cpp_files:
        cpp_path = os.path.join(folder, cpp_file)
        exe_name = os.path.splitext(cpp_file)[0]
        exe_path = os.path.join(folder, exe_name)
        
        compile_cmd = ['g++', cpp_path, '-o', exe_path]
        subprocess.run(compile_cmd, check=True)
        print(f"Compiled {cpp_file} to {exe_name}")

# compile_cpp_files()

# print('lol ', interact("demo", {
#     "cur": 3,
#     "T": 10,
#     "k": 1,
#     "maze": [['.', '.', '.', '.', '.', '.'],
#              ['.', '.', '.', '.', '.', '.'],
#              ['.', '.', '.', '.', '.', '.'],
#              ['.', '.', '.', '.', '.', '.'],
#              ['.', '.', '.', '.', '.', '.'],
#              ['.', '.', '.', '.', '.', '.']],
#     "playerHist": "LRUD",
#     "oppHist": "DURL",
#     "playerScore": 10,
#     "oppScore": 0
# }))