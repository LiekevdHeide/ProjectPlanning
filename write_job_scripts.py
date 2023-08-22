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
!! early_cost!!
"""

JOBSCRIPT = """#!/bin/bash

#SBATCH --time=10:00:00
#SBATCH --mem=2G
#SBATCH --partition=regular
#SBATCH --output={slurm}
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=l.m.van.der.heide@rug.nl
#SBATCH --job-name={name}

module load Python/3.9.5-GCCcore-10.3.0
poetry run python {main} """

ARGUMENTS = ("--Deadline {deadline} "
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
             )


def experiment_one():
    # Check if python version ok (or if there is a newer one)
    mainLocation = "/home/p279495/ProjectPlanning/"
    location = mainLocation + "Experiments/"
    num_phases = 3
    work = 5
    prob_options = [[0, 1, 0], [0.1, 0.8, 0.1], [0.2, 0.6, 0.2]]
    epsilon = [0, 1, 2]
    pol_options = ["", "--threshold_pol_basic", "--threshold_pol_cost"]
    for L in range(0, 15, 14):
        for cost_overtime in range(2, 6, 3):
            for p in range(3):
                for alpha in range(1, 6, 4):
                    for pol in range(3):
                        var_epsilon = sum(
                            prob_options[p][i] * (epsilon[i] - 1) ** 2 for i in
                            range(len(epsilon)))
                        deadline = num_phases * work + L
                        deadline += alpha * var_epsilon

                        job_name = f"{L}_{cost_overtime}_{p}_{alpha}_{pol}"
                        print(job_name)
                        with open(
                                location + "scripts/job" + job_name + ".shw",
                                ) as script:
                            data = dict(
                                deadline=deadline,
                                L=L,
                                num_phases=3,
                                work=5,
                                shift_cost=1,
                                cost_overtime=cost_overtime,
                                freq=2,
                                cost_phase=15,
                                cost_early=-0.5,
                                policy_type=pol_options[pol],
                                name=job_name,
                                output=location + "Outputs2-11/" + job_name + "Out.txt",
                                slurm=location + "slurm/slurm-%j.out",
                                main=mainLocation + "main.py",
                            )

                            script.write(JOBSCRIPT.format(**data))
                            script.write(ARGUMENTS.format(**data))
                        with open(
                                location + "scripts/totalJobs.txt", "a") as allScripts:
                            allScripts.write("sbatch job" + job_name + ".sh \n")


if __name__ == "__main__":
    experiment_one()
