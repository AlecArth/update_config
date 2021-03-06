import os
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
import time
import subprocess
import time
import argparse

def updateSeedNum(file_path, seed_file_path, newSeed=-1):
    print("updateSeedNum")
    seedNum = 0
    if newSeed == -1:
        seedNum = int(getCurrentSeed(seed_file_path))
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                if line[:5] == "seed:":
                    if newSeed != -1:
                        seedNum = newSeed
                        updatedSeed = "seed: "+str(newSeed)+"\n"
                    else:
                        seedNum += 1
                        updatedSeed = "seed: "+str(seedNum)+"\n"
                    new_file.write(line.replace(line, updatedSeed))
                else:
                    new_file.write(line)
    #Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
    # Update seed save file.
    saveCurrentSeed(seed_file_path, seedNum)

def getCurrentSeed(seed_file_path):
    print("getCurrentSeed")
    if os.path.exists(seed_file_path):
        with open(seed_file_path) as file:
            first_line = file.readline()
        return first_line
    else:
        return 1000

def saveCurrentSeed(seed_file_path, seedNum):
    print("saveCurrentSeed")
    if os.path.exists(seed_file_path):

        file = open(seed_file_path, 'w')
        file.write(str(seedNum))
        file.close()
    else:
        file = open(seed_file_path, 'x')
        file.write("1000")
        file.close()

def threeRovers(file_path):
    updateRoverNumber(file_path, "  scouts: 2", "  scouts: 1")
    updateRoverNumber(file_path, "  excavators: 2", "  excavators: 1")
    updateRoverNumber(file_path, "  haulers: 2", "  haulers: 1")

def sixRovers(file_path):
    updateRoverNumber(file_path, "  scouts: 1", "  scouts: 2")
    updateRoverNumber(file_path, "  excavators: 1", "  excavators: 2")
    updateRoverNumber(file_path, "  haulers: 1", "  haulers: 2")

def updateRoverNumber(file_path, pattern, subst):
    print("updateRoverNumber")
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    copymode(file_path, abs_path)
    remove(file_path)
    move(abs_path, file_path)

def runGitCommands(cwd, branch, pull):
    print("runGitCommands")
    subprocess.run(["clear"], cwd=cwd)
    time.sleep(1)
    os.system("cd "+cwd+" && make stop-all-containers")
    time.sleep(1)
    os.system("git -C "+cwd+" stash")
    time.sleep(1)
    if branch != "master":
        print(branch)
        command = "git -C "+cwd+" checkout master"
        os.system(command)
        time.sleep(1)
        os.system("git -C "+cwd+" pull")
        time.sleep(1)
        command = "git -C "+cwd+" checkout "+branch
        os.system(command)
    time.sleep(1)
    if pull:
        print("pull happened")
        os.system("git -C "+cwd+" pull")
        time.sleep(1)

def runCommands(cwd, clear_docker_cache, init):
    print("runCommands")
    if clear_docker_cache:
        os.system("docker images -a -q | xargs docker rmi -f")
        time.sleep(1)
        subprocess.Popen(["make", "run-sim"], cwd=cwd)
        time.sleep(60)
        os.system("cd "+cwd+" && make kill-all-containers")
        time.sleep(1)
        init = True
    if init:
        print("init ran")
        subprocess.run(["make", "init"], cwd=cwd)
        time.sleep(1)
    subprocess.run(["make", "build-solution"], cwd=cwd)
    time.sleep(1)
    if not clear_docker_cache:
        subprocess.run(["make", "run-sim"], cwd=cwd)

def main():
    parser = argparse.ArgumentParser(description='Process arguments.')
    parser.add_argument('--cwd', type=str, default="../competition-round/")
    parser.add_argument('--configfilepath', type=str, default="../competition-round/config.yml")
    parser.add_argument('--seedfilepath', type=str, default="seedNumber.txt")
    parser.add_argument('--branch', type=str, default="master")
    parser.add_argument('--pull', action="store_true")
    parser.add_argument('--numofrovers', type=int, default=6)
    parser.add_argument('--seed', type=int, default=-1)
    parser.add_argument('--cleardockercache', action="store_true")
    parser.add_argument('--init', action="store_true")
    args = parser.parse_args()
    print(args)

    cwd = args.cwd
    config_file_path = args.configfilepath
    seed_file_path = args.seedfilepath
    branch=args.branch
    pull = args.pull
    num_of_rovers = args.numofrovers
    new_seed=args.seed
    clear_docker_cache = args.cleardockercache
    init = args.init

    runGitCommands(cwd, branch, pull)
    updateSeedNum(config_file_path, seed_file_path, new_seed)
    if num_of_rovers == 3:
        threeRovers(config_file_path)
    else:
        sixRovers(config_file_path)
    runCommands(cwd, clear_docker_cache, init)


if __name__ == "__main__":
    main()
