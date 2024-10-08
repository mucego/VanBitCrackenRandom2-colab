import subprocess
import time
import os
import signal
import pickle
import random

Tips = 'bc1qus09g0n5jwg79gje76zxqmzt3gpw80dcqspsmm'


# Function to save the checkpoint
def save_checkpoint(start_keyspace, end_keyspace):
    checkpoint_data = {
        'start_keyspace': start_keyspace,
        'end_keyspace': end_keyspace
    }
    with open('checkpoint.pkl', 'wb') as f:
        pickle.dump(checkpoint_data, f)


# Function to load the checkpoint
def load_checkpoint():
    if os.path.exists('checkpoint.pkl'):
        with open('checkpoint.pkl', 'rb') as f:
            checkpoint_data = pickle.load(f)
        return checkpoint_data['start_keyspace'], checkpoint_data['end_keyspace']
    else:
        return '20000000000000000', '20010000000000000'


def delete_checkpoint():
    if os.path.exists('checkpoint.pkl'):
        os.remove('checkpoint.pkl')


def run_VBCrLinux(start_keyspace, end_keyspace):
    output_filename = f'{start_keyspace[:3]}.txt'  # Generate the output filename based on the start keyspace
    command = f'./VBCrLinux -t 0 -gpu -gpuId 0 -begr {start_keyspace} -endr {end_keyspace} -o {output_filename} -drk 1 -dis 1 -r 70000 -b 13zb1hQ13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'

    process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
    time.sleep(245)  # Wait for 245 seconds
    os.kill(process.pid, signal.CTRL_BREAK_EVENT)  # Send CTRL_BREAK_EVENT signal to terminate the process group
    process.wait()  # Wait for the process to exit


# Load the checkpoint if it exists, otherwise start from the beginning
start_keyspace, end_keyspace = load_checkpoint()

# Loop until explicitly interrupted
last_save_time = time.time()  # Track the last save time
save_interval = 60  # Save interval in seconds (1 minute)

while True:
    try:
        while int(end_keyspace, 16) <= int('4000fffffffffffff', 16):
            increment = ''.join(random.choices('0123456789abcdef', k=14))  # Generate a random 15-character hexadecimal value
            print("Random Increment:", increment)  # Display the randomly chosen increment
            start_keyspace = start_keyspace[:-len(increment)] + increment  # Append the increment to the right side of the start keyspace

            # Calculate the new end keyspace, making sure it does not exceed the maximum value
            new_end_keyspace = hex(int(start_keyspace, 16) + int(increment, 16) - 1)[2:]
            end_keyspace = min(new_end_keyspace, '4000fffffffffffff')  # Choose the smaller value between the new end keyspace and the maximum value

            run_VBCrLinux(start_keyspace, end_keyspace)
            start_keyspace = hex(int(end_keyspace, 16) + 1)[2:]

            # Save the checkpoint every minute
            current_time = time.time()
            elapsed_time = current_time - last_save_time
            if elapsed_time >= save_interval:
                save_checkpoint(start_keyspace, end_keyspace)
                last_save_time = current_time

            time.sleep(5)  # Wait for 5 seconds before restarting

        # Delete the checkpoint file when start keyspace begins with '4xxxxxxx'
        if start_keyspace.startswith('4'):
            delete_checkpoint()
            start_keyspace, end_keyspace = load_checkpoint()
        else:
            break

    except KeyboardInterrupt:
        save_checkpoint(start_keyspace, end_keyspace)  # Save the checkpoint if interrupted by KeyboardInterrupt
        break


# Delete the checkpoint file at the end of the keyspace
delete_checkpoint()
