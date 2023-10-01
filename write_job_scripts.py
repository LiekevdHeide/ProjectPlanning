"""
Make the setting files to run the experiment set on Peregrine.
Lead time       0, 2, 14
N               3
epsilon         [0, 1, 2]
p_e             [0, 1, 0], [0.1, 0.8, 0.1], [0.2, 0.6, 0.2]
W_n             10 (for all n)
c_t             1
c_t^2           2, 5
phase_c         [10, 10, 50]
overtime_f      2
T               [60, 70]
early_cost!!    -0.1
"""
import math

JOBSCRIPT = """#!/bin/bash

#SBATCH --time={time}
#SBATCH --mem={mem}G
#SBATCH --partition=regular
#SBATCH --chdir=../..
#SBATCH --output={slurm}
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=l.m.van.der.heide@rug.nl
#SBATCH --job-name={name}

module load Python/3.10.4-GCCcore-11.3.0
poetry run python {main} """

ARGUMENTS = (
    "--Deadline {deadline} "
    "--LeadTime {L} "
    "--NumPhases {num_phases} "
    "--work_per_phase {work} "
    "--shiftC {shift_cost} "
    "--shiftC_overtime {cost_overtime} "
    "--overtime_freq {freq} "
    "--phaseC {cost_phase} "
    "--earlyC {cost_early} "
    "{policy_type} "
    "--output_name {output_name} "
    "--epsilon_probs {epsilon_probs} "
)


def experiment_one():
    # Check if python version ok (or if there is a newer one)
    location = "./Experiments/"
    num_phases = 3
    work = 10
    mem = 1
    time = "0:20:00"
    prob_options = [[0, 1, 0], [0.1, 0.8, 0.1], [0.2, 0.6, 0.2]]
    lead_times = [0, 2, 14]
    pol_options = ["", "--threshold_pol_basic", "--threshold_pol_cost"]
    number_experiments = 0
    for L in range(len(lead_times)):
        for cost_overtime in range(2, 6, 3):
            for p in range(3):
                for deadline in range(60 + lead_times[L], 71 + lead_times[L], 10):
                    for pol in range(3):
                        number_experiments += 1
                        # deadline = num_phases * work
                        # deadline *= 2  # frequency
                        # deadline = lead_times[L] # alpha  + 
                        # deadline = math.ceil(deadline)
                        if lead_times[L] > 2 and pol == 0:
                            mem = 30
                            time = "5:00:00"

                        job_name = f"{lead_times[L]}_{cost_overtime}_{p}_{deadline}_{pol}"
                        print(job_name)
                        with open(
                            location + "scripts/job" + job_name + ".sh", "w"
                        ) as script:
                            data = dict(
                                deadline=deadline,
                                L=lead_times[L],
                                num_phases=num_phases,
                                work=work,
                                shift_cost=1,
                                cost_overtime=cost_overtime,
                                freq=2,
                                cost_phase= 10, # for phase 1, 2 (hardcoded *5 for phase 3)
                                cost_early=-0.1,
                                epsilon_probs=f"{prob_options[p][0]} "
                                              f"{prob_options[p][1]} "
                                              f"{prob_options[p][2]}",
                                policy_type=pol_options[pol],
                                name=job_name,
                                output_name=location
                                + "Output28-9/"
                                + job_name,
                                slurm=location + "slurm/slurm-%j.out",
                                main="main.py",
                                mem=mem,
                                time=time,
                            )

                            script.write(JOBSCRIPT.format(**data))
                            script.write(ARGUMENTS.format(**data))
                        with open(
                            location + "scripts/totalJobs.txt", "a"
                        ) as allScripts:
                            allScripts.write(
                                "sbatch job" + job_name + ".sh \n"
                            )
    print(f"Total number of experiments is {number_experiments}.")


if __name__ == "__main__":
    experiment_one()
