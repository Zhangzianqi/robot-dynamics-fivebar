"""Independent Cartesian Christoffel / potential-gradient dynamics check.

Run from any working directory::

    python code/validate_parallel_christoffel.py

The compared force in robot_model.parallel_inverse is assembled by mapping the
two branches' inverse-dynamics torques.  This check independently reconstructs
the Cartesian velocity-quadratic term from spatial derivatives of M_x and the
gravity force from the gradient of the whole robot's potential energy.  Both
methods intentionally share the same rigid-body geometry and mass parameters.
No result is an experimental measurement.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import robot_model as model


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "outputs" / "validation" / "parallel_independent_checks.json"


def cartesian_mass(point: np.ndarray) -> np.ndarray:
    """Read the energy-derived Cartesian mass, without branch force terms."""
    zero = np.zeros(2)
    return model.parallel_inverse(point, zero, zero)[2]


def cartesian_potential(point: np.ndarray) -> float:
    """At zero Cartesian speed the total mechanical energy is potential."""
    return float(model.parallel_energy(point, np.zeros(2)))


def reconstruct_force(
    point: np.ndarray,
    velocity: np.ndarray,
    acceleration: np.ndarray,
    step: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return force, velocity-quadratic term and potential gradient.

    dM[i,j,k] = partial M[i,j] / partial x[k].  The Christoffel contraction is
    c = Mdot @ velocity - 0.5 * [velocity.T @ dM[:,:,i] @ velocity]_i.
    This formula avoids using either branch's C or inverse-dynamics torque.
    """
    mass = cartesian_mass(point)
    dmass = np.empty((2, 2, 2))
    gravity = np.empty(2)
    for coordinate in range(2):
        shift = np.eye(2)[coordinate] * step
        dmass[:, :, coordinate] = (
            cartesian_mass(point + shift) - cartesian_mass(point - shift)
        ) / (2 * step)
        gravity[coordinate] = (
            cartesian_potential(point + shift)
            - cartesian_potential(point - shift)
        ) / (2 * step)

    mdot = np.einsum("ijk,k->ij", dmass, velocity)
    kinetic_gradient = np.array(
        [velocity @ dmass[:, :, coordinate] @ velocity for coordinate in range(2)]
    )
    velocity_force = mdot @ velocity - 0.5 * kinetic_gradient
    force = mass @ acceleration + velocity_force + gravity
    return force, velocity_force, gravity


def validate(samples: int = 50, seed: int = 20261027, step: float = 1e-6) -> dict:
    if samples < 1:
        raise ValueError("samples must be positive")
    if not step > 0:
        raise ValueError("step must be positive")

    rng = np.random.default_rng(seed)
    records = []
    for index in range(samples):
        # Keep draw order and ranges identical to the independent review.
        point = np.array([rng.uniform(-0.04, 0.04), rng.uniform(0.355, 0.405)])
        velocity = rng.uniform(-0.15, 0.15, 2)
        acceleration = rng.uniform(-0.4, 0.4, 2)

        torque_branch, force_branch, _, gravity_branch, _ = model.parallel_inverse(
            point, velocity, acceleration
        )
        force_christoffel, velocity_force, gravity_gradient = reconstruct_force(
            point, velocity, acceleration, step
        )
        jacobian = model.parallel_kinematics(point)[4]
        torque_christoffel = jacobian.T @ force_christoffel
        records.append(
            {
                "sample_index": index,
                "position_m": point.tolist(),
                "velocity_m_s": velocity.tolist(),
                "acceleration_m_s2": acceleration.tolist(),
                "branch_mapped_force_N": force_branch.tolist(),
                "christoffel_force_N": force_christoffel.tolist(),
                "christoffel_velocity_force_N": velocity_force.tolist(),
                "branch_mapped_torque_Nm": torque_branch.tolist(),
                "christoffel_torque_Nm": torque_christoffel.tolist(),
                "force_max_abs_error_N": float(
                    np.max(np.abs(force_branch - force_christoffel))
                ),
                "torque_max_abs_error_Nm": float(
                    np.max(np.abs(torque_branch - torque_christoffel))
                ),
                "gravity_max_abs_error_N": float(
                    np.max(np.abs(gravity_branch - gravity_gradient))
                ),
            }
        )

    maxima = {
        "Cartesian_dynamics_max_force_error_N": max(
            record["force_max_abs_error_N"] for record in records
        ),
        "active_torque_max_error_Nm": max(
            record["torque_max_abs_error_Nm"] for record in records
        ),
        "potential_gradient_max_error_N": max(
            record["gravity_max_abs_error_N"] for record in records
        ),
    }
    tolerance = 1e-6
    passed = all(value < tolerance for value in maxima.values())
    q = np.deg2rad([45.0, -60.0])
    dq = np.array([0.4, -0.3])
    ddq = np.array([0.6, 0.2])
    return {
        "method": "Cartesian Christoffel contraction and total potential gradient",
        "comparison": "Branch inverse dynamics mapped by virtual work",
        "shared_inputs": "Rigid-body geometry, masses and Cartesian kinetic energy",
        "samples": samples,
        "random_seed": seed,
        "numpy_version": np.__version__,
        "finite_difference_step_m": step,
        "sampling_ranges": {
            "px_m": [-0.04, 0.04],
            "py_m": [0.355, 0.405],
            "each_cartesian_velocity_m_s": [-0.15, 0.15],
            "each_cartesian_acceleration_m_s2": [-0.4, 0.4],
        },
        "maximum_absolute_errors": maxima,
        "absolute_acceptance_tolerance": {
            "force_N": tolerance,
            "torque_Nm": tolerance,
            "gravity_N": tolerance,
        },
        "passed": passed,
        "serial_numeric_example": {
            "q_deg": [45.0, -60.0],
            "dq_rad_s": dq.tolist(),
            "ddq_rad_s2": ddq.tolist(),
            "point_world_m": model.fk(q).tolist(),
            "jacobian_m_per_rad": model.jac(q).tolist(),
            "mass_kg_m2": model.mass(q).tolist(),
            "coriolis_matrix_kg_m2_s": model.coriolis(q, dq).tolist(),
            "gravity_Nm": model.grav(q).tolist(),
            "tau_lagrange_Nm": model.inverse_lagrange(q, dq, ddq).tolist(),
            "tau_newton_euler_Nm": model.inverse_newton_euler(q, dq, ddq).tolist(),
        },
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20261027)
    parser.add_argument("--step", type=float, default=1e-6)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = validate(args.samples, args.seed, args.step)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["maximum_absolute_errors"], indent=2))
    print(f"Passed: {result['passed']}; output: {args.output.resolve()}")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
