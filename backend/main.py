from fastapi import FastAPI
from pydantic import BaseModel
import pennylane as qml
from pennylane import qchem
from dotenv import load_dotenv
import numpy as np
from google import genai
import re
import json
import os

app = FastAPI()
load_dotenv()
client = genai.Client(api_key=os.environ.get("GENAI_API_KEY"))

atomic_numbers = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
    "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19,
    "Ca": 20, "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28,
    "Cu": 29, "Zn": 30, "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36, "Rb": 37,
    "Sr": 38, "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42, "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46,
    "Ag": 47, "Cd": 48, "In": 49, "Sn": 50, "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55,
    "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60, "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64,
    "Tb": 65, "Dy": 66, "Ho": 67, "Er": 68, "Tm": 69, "Yb": 70, "Lu": 71, "Hf": 72, "Ta": 73,
    "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79, "Hg": 80, "Tl": 81, "Pb": 82,
    "Bi": 83, "Po": 84, "At": 85, "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90, "Pa": 91,
    "U": 92
}

class MoleculeRequest(BaseModel):
    symbols: list[str]
    coordinates: list[float]
    charge: int = 0
    multiplicity: int = 1

class MoleculeNameRequest(BaseModel):
    formula: str
    charge: int = 0
    multiplicity: int = 1

def parse_formula(formula: str) -> list[str]:
    pattern = r"([A-Z][a-z]?)(\d*)"
    symbols = []
    for elem, count in re.findall(pattern, formula):
        count = int(count) if count else 1
        symbols.extend([elem] * count)
    return symbols

def generate_coordinates(formula, num_cases=5):
    prompt = (
        f"Generate {num_cases} realistic 3D geometries (in Angstroms) for molecule {formula}. "
        "Return ONLY valid JSON: list of lists of coordinates [[x1,y1,z1],[x2,y2,z2],...]."
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{"text": prompt}]
    )
    text = response.text.strip()
    text = re.sub(r"^```json|```$", "", text, flags=re.IGNORECASE).strip()
    return json.loads(text)

# Playground route

@app.post("/playground")
def compute_ground_state(mol: MoleculeRequest):
    try:
        symbols = mol.symbols
        coords = np.array(mol.coordinates).reshape(len(symbols), 3)
        charge = mol.charge
        mult = mol.multiplicity

        # Hamiltonian
        H, n_qubits = qchem.molecular_hamiltonian(symbols, coords, charge=charge, mult=mult)
        n_electrons = sum(atomic_numbers[s] for s in symbols) - charge

        # Device
        dev = qml.device("default.qubit", wires=n_qubits)

        # VQE circuit
        @qml.qnode(dev)
        def circuit(params):
            hf = qchem.hf_state(n_electrons, n_qubits)
            qml.BasisState(hf, wires=range(n_qubits))
            depth = params.shape[0]
            for d in range(depth):
                for w in range(n_qubits):
                    qml.RY(params[d, w], wires=w)
            return qml.expval(H)

        depth = 2
        params = np.zeros((depth, n_qubits))
        opt = qml.GradientDescentOptimizer(stepsize=0.4)

        energy = None
        for _ in range(20):
            params, energy = opt.step_and_cost(circuit, params)

        return {
            "symbols": symbols,
            "coordinates": coords.tolist(),
            "ground_state_energy": float(energy),
            "qubits_used": n_qubits
        }

    except Exception as e:
        return {"error": str(e)}


# GroundState Route

@app.post("/ground-state")
def molecule_ground_states(req: MoleculeNameRequest):
    try:
        symbols = parse_formula(req.formula)
        charge = req.charge
        mult = req.multiplicity

        coords_sets = generate_coordinates(req.formula, num_cases=5)
        results = []
        most_stable = None
        lowest_energy = None

        for coords in coords_sets:
            coords = np.array(coords)
            n_electrons = sum(atomic_numbers[s] for s in symbols) - charge

            # Build Hamiltonian
            try:
                H, n_qubits = qchem.molecular_hamiltonian(symbols, coords, charge=charge, mult=mult)
            except Exception:
                continue

            # Small molecules: VQE
            if n_qubits <= 6:
                dev = qml.device("default.qubit", wires=n_qubits)
                @qml.qnode(dev)
                def circuit(params):
                    hf = qchem.hf_state(n_electrons, n_qubits)
                    qml.BasisState(hf, wires=range(n_qubits))
                    depth = params.shape[0]
                    for d in range(depth):
                        for w in range(n_qubits):
                            qml.RY(params[d, w], wires=w)
                    return qml.expval(H)
                depth = 2
                params = np.zeros((depth, n_qubits))
                opt = qml.GradientDescentOptimizer(stepsize=0.4)
                energy = None
                for _ in range(20):
                    params, energy = opt.step_and_cost(circuit, params)

            # Medium molecules: HF expectation
            elif n_qubits <= 20:
                dev = qml.device("default.qubit", wires=n_qubits)
                hf_state = qchem.hf_state(n_electrons, n_qubits)
                @qml.qnode(dev)
                def hf_circuit():
                    qml.BasisState(hf_state, wires=range(n_qubits))
                    return qml.expval(H)
                energy = hf_circuit()

            else:
                results.append({
                    "coordinates": coords.tolist(),
                    "ground_state_energy": None,
                    "note": "Too many qubits"
                })
                continue

            results.append({
                "coordinates": coords.tolist(),
                "ground_state_energy": float(energy)
            })

            if lowest_energy is None or (energy is not None and energy < lowest_energy):
                lowest_energy = energy
                most_stable = {"coordinates": coords.tolist(), "ground_state_energy": float(energy)}

        return {
            "formula": req.formula,
            "results": results,
            "most_stable": most_stable
        }

    except Exception as e:
        return {"error": str(e)}
