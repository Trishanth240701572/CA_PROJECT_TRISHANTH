# Arith-Algos

Implementation of classic N-bit arithmetic algorithms in Python. Supports both unsigned and two's complement signed arithmetic with configurable bit widths.

## 🎯 Algorithms Implemented

1. **Addition & Subtraction**: Bitwise full-adder with carry/overflow detection
2. **Sequential Multiplication**: Basic shift-add algorithm  
3. **Booth's Multiplication (Radix-2)**: Efficient signed multiplication
4. **Bit/Naive Multiplication**: Partial products approach
5. **Bit-Pair Multiplication (Radix-4)**: Modified Booth examining 2 bits at a time
6. **Restoring Division**: Traditional algorithm with restoration step
7. **Non-Restoring Division**: More efficient without restoration

## 🔢 Number Systems

- **Unsigned**: Treats all bit patterns as positive integers (0 to 2^N-1)
- **Signed**: Uses two's complement representation (-2^(N-1) to 2^(N-1)-1)

### Two's Complement
Two's complement is the standard way to represent signed integers:
- Positive numbers: Same as unsigned (MSB = 0)
- Negative numbers: Flip all bits and add 1 (MSB = 1)
- Example (4-bit): 5 = 0101, -5 = 1011

## 🚀 Usage

### Basic Examples

```bash
cd python

# 8-bit unsigned addition
python arith_algorithms.py --width 8 --algo add 25 10

# 8-bit addition with carry
python arith_algorithms.py --width 8 --algo add 200 80

# 16-bit signed Booth's multiplication
python arith_algorithms.py --width 16 --signed --algo mul_booth -123 77

# 8-bit unsigned division
python arith_algorithms.py --width 8 --algo div_restoring 100 7
```

### Verification Mode

```bash
# Verify all algorithms with 400 random test cases (8-bit unsigned)
python arith_algorithms.py --width 8 --trials 400 verify

# Verify 16-bit signed arithmetic with 200 trials
python arith_algorithms.py --width 16 --signed --trials 200 verify

# Quick verification
python arith_algorithms.py --width 8 --trials 50 verify
```

### Command Format

```
python arith_algorithms.py [OPTIONS] --algo ALGORITHM [OPERANDS]
```

**Options:**
- `--width N` - Bit width (default: 8)
- `--signed` - Use signed (two's complement) arithmetic
- `--algo ALGORITHM` - Algorithm to run (required)
- `--trials N` - Number of trials for verify mode (default: 400)

**Algorithms:**
- `add` - Addition
- `sub` - Subtraction  
- `mul_seq` - Sequential multiplication
- `mul_booth` - Booth's multiplication (radix-2)
- `mul_bit` - Bit multiplication (naive)
- `mul_bitpair` - Modified Booth (radix-4)
- `div_restoring` - Restoring division
- `div_nonrestoring` - Non-restoring division
- `verify` - Test all algorithms with random data

## 📊 Sample Output

```bash
$ python arith_algorithms.py --width 8 --algo add 200 80
Result: 24
Flags: {'carry_out': 1}

$ python arith_algorithms.py --width 8 --algo mul_seq 15 12
Product: 180 (16-bit)

$ python arith_algorithms.py --width 8 --trials 100 verify
Verifying 100 trials for 8-bit unsigned arithmetic...
Verification: PASS
```

## ✅ Verification

The verification mode tests all 7 algorithms against Python's built-in arithmetic with random test cases:

- Uses fixed seed (42) for deterministic results
- Compares masked bit-width results to Python truth
- For division: verifies `a = q * b + r`
- Reports PASS/FAIL with detailed error messages

### Expected Results
```
Verifying 400 trials for 8-bit unsigned arithmetic...
Verification: PASS

Verifying 200 trials for 16-bit signed arithmetic...
Verification: PASS
```

## 🧪 Algorithm Notes

### Booth's Algorithm
Booth's algorithm handles signed multiplication efficiently by examining bit patterns to determine whether to add, subtract, or skip operations.

### Division Algorithms
- **Restoring**: Restores remainder after failed subtraction
- **Non-restoring**: Uses addition/subtraction based on remainder sign
- Both maintain: dividend = quotient × divisor + remainder

## 🔧 Development

### Project Structure
```
arith-algos/
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
├── python/
│   ├── arith_algorithms.py      # Complete implementation
│   └── requirements.txt         # Dependencies (empty - stdlib only)
└── .github/workflows/
    └── ci.yml                   # Continuous integration
```

### Running Tests Locally
```bash
# Quick verification
python arith_algorithms.py --width 8 --trials 100 verify
python arith_algorithms.py --width 16 --signed --trials 100 verify

# Test specific algorithms
python arith_algorithms.py --width 8 --algo add 25 10
python arith_algorithms.py --width 8 --algo div_restoring 100 7
```

## 🚢 Testing

Automated tests run on GitHub Actions with Python 3.10 & 3.12:
- 400 trials for 8-bit unsigned arithmetic  
- 200 trials for 16-bit signed arithmetic

## 📝 License

MIT License - feel free to use for educational purposes.

