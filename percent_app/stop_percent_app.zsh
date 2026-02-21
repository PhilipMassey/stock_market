#!/bin/zsh

# Script to stop the percent_app started by run_percent_app.zsh

# Port used by the app (matches app.py)
PORT=8561

# Find the PID of the python process running on the port
PIDS=$(lsof -ti :$PORT)

if [ -z "$PIDS" ]; then
    echo "No running percent_app process found on port $PORT."
    exit 0
fi

echo "Found active process(es) on port $PORT with PID(s): $PIDS"

# Initialize list of PIDs to kill (including parents)
ALL_PIDS=()

# Convert newline-separated string to array
for PID in ${(f)PIDS}; do
    ALL_PIDS+=($PID)
    # Check for parent process (handles Flask/Dash reloader)
    # Get Parent PID (PARENT_ID)
    PARENT_ID=$(ps -o ppid= -p $PID 2>/dev/null | tr -d ' ')
    
    if [[ -n "$PARENT_ID" && "$PARENT_ID" -ne 1 ]]; then
        # Check if parent command contains 'python'
        # On macOS, ps -o comm= often returns the executable name like 'Python'
        PARENT_CMD=$(ps -p $PARENT_ID -o comm= 2>/dev/null)
        if echo "$PARENT_CMD" | grep -qi "python"; then
            echo "Identified parent process $PARENT_ID (likely reloader) for worker $PID"
            ALL_PIDS+=($PARENT_ID)
        fi
    fi
done

# Remove duplicates
UNIQUE_PIDS=(${(u)ALL_PIDS})

echo "Stopping process(es): ${UNIQUE_PIDS[@]}"

# Try graceful shutdown first (SIGTERM) on ALL processes at once
# This minimizes the chance of a reloader restarting a worker
kill "${UNIQUE_PIDS[@]}" 2>/dev/null
sleep 2

# Check if processes are still running and force kill if needed
for PID in "${UNIQUE_PIDS[@]}"; do
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Process $PID still running, forcing shutdown..."
        kill -9 "$PID" 2>/dev/null
    else
        echo "Process $PID stopped."
    fi
done

# Final Verification
STILL_RUNNING=0
for PID in "${UNIQUE_PIDS[@]}"; do
     if ps -p "$PID" > /dev/null 2>&1; then
        echo "WARNING: Failed to force stop process $PID"
        STILL_RUNNING=1
     fi
done

if [ $STILL_RUNNING -eq 0 ]; then
    echo "All percent_app processes stopped successfully."
fi
