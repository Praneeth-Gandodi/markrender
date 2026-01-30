"""
Streaming demo for MarkRender
Simulates LLM streaming response
"""

import time
from markrender import MarkdownRenderer


def simulate_streaming():
    """Simulate streaming LLM response"""
    
    # Simulated markdown response chunks
    response = """
# Quantum Computing Explained

Quantum computing is a revolutionary technology that leverages the principles of **quantum mechanics** to process information.

## Key Concepts

### 1. Qubits

Unlike classical bits that can only be 0 or 1, **qubits** can exist in a *superposition* of both states simultaneously.

```python
# Classical bit
bit = 0  # or 1

# Qubit (conceptual)
qubit = alpha|0⟩ + beta|1⟩
```

### 2. Superposition

Superposition allows quantum computers to:
- Process multiple possibilities at once
- Explore solution spaces exponentially faster
- Solve certain problems classical computers cannot

### 3. Entanglement

When qubits become entangled:
- [x] Their states become correlated
- [x] Measuring one affects the other
- [x] Distance doesn't matter

## Comparison Table

| Aspect | Classical | Quantum |
|--------|-----------|---------|
| Basic unit | Bit (0 or 1) | Qubit (superposition) |
| Gates | AND, OR, NOT | Hadamard, CNOT, etc. |
| Speed | Linear | Exponential (for some problems) |

## Applications

> Quantum computing promises to revolutionize fields like cryptography, drug discovery, and optimization problems.

Some exciting applications include:

1. **Cryptography** - Breaking current encryption :lock:
2. **Drug Discovery** - Simulating molecular interactions :pill:
3. **Optimization** - Solving complex logistics problems :package:
4. **AI/ML** - Accelerating machine learning :robot:

## Example Algorithm

```python
from qiskit import QuantumCircuit

# Create a quantum circuit
qc = QuantumCircuit(2, 2)

# Apply Hadamard gate
qc.h(0)

# Apply CNOT gate
qc.cx(0, 1)

# Measure
qc.measure([0, 1], [0, 1])
```

### Challenges

Current quantum computers face several challenges:

- **Decoherence** - Qubits lose their quantum state quickly
- **Error rates** - High error rates require error correction
- **Scalability** - Building large-scale quantum computers is difficult

---

*For more information, visit [IBM Quantum](https://www.ibm.com/quantum)*

Hope this helps! :wave:
"""
    
    # Split into chunks (simulating streaming)
    chunk_size = 10  # characters per chunk
    for i in range(0, len(response), chunk_size):
        chunk = response[i:i + chunk_size]
        yield chunk
        time.sleep(0.01)  # Simulate network delay


def main():
    """Streaming markdown rendering demo"""
    
    print("Simulating streaming LLM response...\n")
    print("=" * 80)
    print()
    
    # Create renderer
    renderer = MarkdownRenderer(
        theme='github-dark',
        code_background=False,
        line_numbers=True
    )
    
    # Render streaming chunks
    for chunk in simulate_streaming():
        renderer.render(chunk)
    
    # Finalize rendering
    renderer.finalize()
    
    print()
    print("=" * 80)
    print("\n\nStreaming complete! ✓")


if __name__ == '__main__':
    main()
