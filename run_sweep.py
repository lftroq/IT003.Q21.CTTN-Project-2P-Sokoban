"""
Sokoban Bot Parameter Sweep Script.

This script orchestrates a comprehensive parameter sweep across different
map sizes, generation modes, move limits, and bot difficulty matchups.
It leverages the headless simulator to run bulk matches and compiles
the results into a CSV report for further analysis.
"""
import csv
import sys
import os
import simulator
from core.config import BOT_MODELS

def main():
    """
    Execute the full parameter sweep and save results to a CSV file.

    The sweep iterates over predefined lists of map sizes, map generation modes,
    and move limits. For each combination, it tests three bot difficulty matchups
    (Easy vs Medium, Easy vs Hard, Medium vs Hard). The match outcomes are tallied
    and progressively appended to 'sweep_results.csv'.
    """
    sizes = [12, 16, 24]
    modes = ["SYM", "SEP", "NON"]
    limits = [50, 100, 150, 200]
    runs = 20
    
    pairs = [
        ("EASY", "MED"),
        ("EASY", "HARD"),
        ("MED", "HARD")
    ]
    
    csv_filename = "sweep_results.csv"
    
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["size", "mode", "limit", "runs", "P1 difficulty", "P2 difficulty", "P1 wins", "P2 wins", "Draw"])
        
        for size in sizes:
            for mode in modes:
                for limit in limits:
                    for p1_diff, p2_diff in pairs:
                        bot1 = BOT_MODELS[p1_diff]
                        bot2 = BOT_MODELS[p2_diff]
                        
                        print(f"Running size={size}, mode={mode}, limit={limit}, bots={bot1} vs {bot2}...", flush=True)
                        
                        results = {"P1 Wins!": 0, "P2 Wins!": 0, "Draw!": 0}
                        
                        for i in range(1, runs + 1):
                            result = simulator.run_match(bot1, bot2, limit, mode, size)
                            if result not in results:
                                results[result] = 0
                            results[result] += 1
                            print(f"Run #{i}: {result}", flush=True)
                        
                        writer.writerow([size, mode, limit, runs, p1_diff, p2_diff, results.get("P1 Wins!", 0), results.get("P2 Wins!", 0), results.get("Draw!", 0)])
                        file.flush()
                        
    print(f"Sweep complete! Results saved to {csv_filename}")

if __name__ == "__main__":
    main()
