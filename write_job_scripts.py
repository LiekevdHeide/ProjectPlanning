"""
Make the setting files to run the experiment set on Peregrine.
Lead time       0, 14
N               3
epsilon         [0, 1, 2]
p_e             [0, 1, 0], [0.1, 0.8, 0.1], [0.2, 0.6, 0.2]
W_n             5 (for all n)
c_t             1
c_t^2           2, 5
phase_c         [15, 15, 30]
overtime_f      2
T               15 + L + alpha * Var(epsilon)
alpha           1, 5
early_cost!!    -0.5
"""
import math

JOBSCRIPT = """#!/bin/bash

#SBATCH --time=1:00:00
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
    work = 5
    prob_options = [[0, 1, 0], [0.1, 0.8, 0.1], [0.2, 0.6, 0.2]]
    lead_times = [0, 2, 14]
    pol_options = ["", "--threshold_pol_basic", "--threshold_pol_cost"]
    for L in range(len(lead_times)):
        for cost_overtime in range(2, 6, 3):
            for p in range(3):
                for alpha in range(2):
                    for pol in range(3):
                        deadline = num_phases * work
                        deadline *= 2  # frequency
                        deadline += alpha * work  + lead_times[L]
                        deadline = math.ceil(deadline)
                        mem = 10
                        if lead_times[L] == 0 and pol == 0:
                            mem = 10
                        if lead_times[L] == 2 and pol == 0:
                            mem = 20
                        if lead_times[L] == 14 and pol == 0:
                            mem = 40
                        if lead_times[L] == 28 and pol == 0:
                            mem = 200

                        job_name = f"{lead_times[L]}_{cost_overtime}_{p}_{alpha}_{pol}"
                        print(job_name)
                        with open(
                            location + "scripts/job" + job_name + ".sh", "w"
                        ) as script:
                            data = dict(
                                deadline=deadline,
                                L=lead_times[L],
                                num_phases=3,
                                work=5,
                                shift_cost=1,
                                cost_overtime=cost_overtime,
                                freq=2,
                                cost_phase=15,
                                cost_early=0,
                                epsilon_probs=f"{prob_options[p][0]} "
                                              f"{prob_options[p][1]} "
                                              f"{prob_options[p][2]}",
                                policy_type=pol_options[pol],
                                name=job_name,
                                output_name=location
                                + "Output26-8betterT/"
                                + job_name,
                                slurm=location + "slurm/slurm-%j.out",
                                main="main.py",
                                mem=mem,
                            )

                            script.write(JOBSCRIPT.format(**data))
                            script.write(ARGUMENTS.format(**data))
                        with open(
                            location + "scripts/totalJobs.txt", "a"
                        ) as allScripts:
                            allScripts.write(
                                "sbatch job" + job_name + ".sh \n"
                            )


if __name__ == "__main__":
    experiment_one()
