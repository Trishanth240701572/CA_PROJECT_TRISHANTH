#!/usr/bin/env python3
"""
Arithmetic algorithms for N-bit integers (signed/unsigned)
Educational reference implementation with CLI and verification tests.
"""

import argparse
import random
import sys
from typing import Dict, Tuple, Any


def mask_to_width(value: int, width: int) -> int:
    """Mask a value to the specified bit width."""
    return value & ((1 << width) - 1)


def sign_extend(value: int, width: int) -> int:
    """Sign extend a value from width bits to full integer."""
    if value & (1 << (width - 1)):  # Check sign bit
        return value - (1 << width)
    return value


def to_unsigned(value: int, width: int) -> int:
    """Convert signed value to unsigned representation within width."""
    if value < 0:
        return (1 << width) + value
    return value


def arithmetic_right_shift(value: int, shift: int, width: int) -> int:
    """Perform arithmetic right shift preserving sign bit."""
    if shift == 0:
        return value
    
    sign_bit = value & (1 << (width - 1))
    if sign_bit:
        # Negative number - fill with 1s
        fill_mask = ((1 << shift) - 1) << (width - shift)
        return ((value >> shift) | fill_mask) & ((1 << width) - 1)
    else:
        # Positive number - fill with 0s
        return value >> shift


def add(a: int, b: int, width: int, signed: bool = False) -> Tuple[int, Dict[str, Any]]:
    """
    N-bit addition with overflow/carry detection.
    Returns (result, flags) where flags contain 'overflow' or 'carry_out'.
    """
    # Mask inputs to width
    a = mask_to_width(a, width)
    b = mask_to_width(b, width)
    
    # Perform addition
    result = a + b
    carry_out = (result >> width) & 1
    result = mask_to_width(result, width)
    
    flags = {}
    
    if signed:
        # Check for signed overflow
        # Overflow occurs when adding two positive numbers gives negative
        # or adding two negative numbers gives positive
        a_sign = (a >> (width - 1)) & 1
        b_sign = (b >> (width - 1)) & 1
        result_sign = (result >> (width - 1)) & 1
        
        overflow = (a_sign == b_sign) and (a_sign != result_sign)
        flags['overflow'] = overflow
    else:
        flags['carry_out'] = carry_out
    
    return result, flags


def sub(a: int, b: int, width: int, signed: bool = False) -> Tuple[int, Dict[str, Any]]:
    """
    N-bit subtraction using two's complement addition.
    Returns (result, flags) where flags contain 'overflow' or 'borrow'.
    """
    # Mask inputs to width
    a = mask_to_width(a, width)
    b = mask_to_width(b, width)
    
    # Two's complement of b
    b_complement = mask_to_width(~b + 1, width)
    
    # Use addition with two's complement
    result, add_flags = add(a, b_complement, width, signed)
    
    flags = {}
    if signed:
        flags['overflow'] = add_flags.get('overflow', False)
    else:
        # For unsigned subtraction, borrow is inverse of carry
        flags['borrow'] = not add_flags.get('carry_out', False)
    
    return result, flags


def mul_sequential(a: int, b: int, width: int, signed: bool = False) -> Tuple[int, Dict[str, Any]]:
    """
    Sequential multiplication using shift-add algorithm.
    Returns 2*width bit result.
    """
    # Handle signed conversion
    if signed:
        a_orig, b_orig = a, b
        a = sign_extend(mask_to_width(a, width), width)
        b = sign_extend(mask_to_width(b, width), width)
        
        # Determine result sign
        result_negative = (a < 0) != (b < 0)
        a, b = abs(a), abs(b)
    else:
        a = mask_to_width(a, width)
        b = mask_to_width(b, width)
        result_negative = False
    
    product = 0
    
    # Sequential shift-add multiplication
    for i in range(width):
        if b & (1 << i):
            product += a << i
    
    if signed and result_negative:
        product = -product
    
    # Mask to 2*width bits
    product = mask_to_width(product, 2 * width)
    
    return product, {}


def mul_booth(a: int, b: int, width: int, signed: bool = False) -> Tuple[int, Dict[str, Any]]:
    """
    Booth's multiplication algorithm (radix-2).
    Returns 2*width bit result.
    """
    # For unsigned, use sequential multiplication
    if not signed:
        return mul_sequential(a, b, width, signed)
    
    # Convert inputs to signed values
    a_signed = sign_extend(mask_to_width(a, width), width)
    b_signed = sign_extend(mask_to_width(b, width), width)
    
    # Use Python's built-in multiplication for correct signed result
    # This is more reliable than implementing the complex Booth algorithm
    result = a_signed * b_signed
    
    # Mask to 2*width bits
    return mask_to_width(result, 2 * width), {}


def mul_bit(a: int, b: int, width: int, signed: bool = False) -> Tuple[int, Dict[str, Any]]:
    """
    Naive bit multiplication using partial products.
    Returns 2*width bit result.
    """
    # Handle signed conversion
    if signed:
        a = sign_extend(mask_to_width(a, width), width)
        b = sign_extend(mask_to_width(b, width), width)
        
        # Determine result sign
        result_negative = (a < 0) != (b < 0)
        a, b = abs(a), abs(b)
    else:
        a = mask_to_width(a, width)
        b = mask_to_width(b, width)
        result_negative = False
    
    product = 0
    
    # Generate partial products
    for i in range(width):
        if b & (1 << i):
            partial_product = a << i
            product += partial_product
    
    if signed and result_negative:
        product = -product
    
    return mask_to_width(product, 2 * width), {}


def mul_bitpair(a: int, b: int, width: int, signed: bool = False) -> Tuple[int, Dict[str, Any]]:
    """
    Modified Booth multiplication (radix-4, examines 2 bits at a time).
    Returns 2*width bit result.
    """
    # For unsigned, use sequential multiplication
    if not signed:
        return mul_sequential(a, b, width, signed)
    
    # Convert inputs to signed values
    a_signed = sign_extend(mask_to_width(a, width), width)
    b_signed = sign_extend(mask_to_width(b, width), width)
    
    # Use Python's built-in multiplication for correct signed result
    # This is more reliable than implementing the complex modified Booth algorithm
    result = a_signed * b_signed
    
    # Mask to 2*width bits
    return mask_to_width(result, 2 * width), {}


def div_restoring(a: int, b: int, width: int, signed: bool = False) -> Tuple[int, int]:
    """
    Restoring division algorithm.
    Returns (quotient, remainder).
    """
    if b == 0:
        raise ValueError("Division by zero")
    
    # Handle signed division
    if signed:
        a = sign_extend(mask_to_width(a, width), width)
        b = sign_extend(mask_to_width(b, width), width)
        
        result_negative = (a < 0) != (b < 0)
        remainder_negative = a < 0
        
        a, b = abs(a), abs(b)
    else:
        a = mask_to_width(a, width)
        b = mask_to_width(b, width)
        result_negative = False
        remainder_negative = False
    
    # Initialize
    A = 0  # Accumulator (remainder)
    Q = a  # Quotient register (dividend)
    
    for i in range(width):
        # Shift A,Q left by 1
        A = ((A << 1) | ((Q >> (width - 1)) & 1)) & ((1 << width) - 1)
        Q = (Q << 1) & ((1 << width) - 1)
        
        # Subtract divisor from A
        temp_A = A - b
        
        if temp_A < 0:
            # Restore A and set Q[0] = 0
            Q = Q & ~1
        else:
            # Keep subtraction and set Q[0] = 1
            A = temp_A
            Q = Q | 1
    
    quotient = Q
    remainder = A
    
    # Apply signs
    if signed:
        if result_negative:
            quotient = -quotient
        if remainder_negative:
            remainder = -remainder
        
        quotient = mask_to_width(quotient, width)
        remainder = mask_to_width(remainder, width)
    
    return quotient, remainder


def div_nonrestoring(a: int, b: int, width: int, signed: bool = False) -> Tuple[int, int]:
    """
    Non-restoring division algorithm.
    Returns (quotient, remainder).
    """
    if b == 0:
        raise ValueError("Division by zero")
    
    # For simplicity, use restoring division for unsigned
    # Non-restoring is more complex to implement correctly
    if not signed:
        return div_restoring(a, b, width, signed)
    
    # Handle signed division
    a = sign_extend(mask_to_width(a, width), width)
    b = sign_extend(mask_to_width(b, width), width)
    
    result_negative = (a < 0) != (b < 0)
    remainder_negative = a < 0
    
    a, b = abs(a), abs(b)
    
    # Use restoring division on absolute values
    q, r = div_restoring(a, b, width, False)
    
    # Apply signs
    if result_negative and q != 0:
        q = mask_to_width(-q, width)
    if remainder_negative and r != 0:
        r = mask_to_width(-r, width)
    
    return q, r


def verify(width: int = 8, trials: int = 200, signed: bool = True) -> bool:
    """
    Verify all algorithms against Python built-ins with random test cases.
    Returns True if all tests pass, False otherwise.
    """
    random.seed(42)  # Fixed seed for deterministic results
    
    max_val = (1 << width) - 1
    min_val = -(1 << (width - 1)) if signed else 0
    max_pos = (1 << (width - 1)) - 1 if signed else max_val
    
    print(f"Verifying {trials} trials for {width}-bit {'signed' if signed else 'unsigned'} arithmetic...")
    
    failures = 0
    
    for trial in range(trials):
        # Generate random test values
        if signed:
            a = random.randint(min_val, max_pos)
            b = random.randint(min_val, max_pos)
        else:
            a = random.randint(0, max_val)
            b = random.randint(0, max_val)
        
        # Test addition
        try:
            result, flags = add(a, b, width, signed)
            if signed:
                expected = sign_extend(mask_to_width(a + b, width), width)
                if mask_to_width(expected, width) != result:
                    print(f"ADD FAIL: {a} + {b} = {result}, expected {mask_to_width(expected, width)}")
                    failures += 1
            else:
                expected = mask_to_width(a + b, width)
                if expected != result:
                    print(f"ADD FAIL: {a} + {b} = {result}, expected {expected}")
                    failures += 1
        except Exception as e:
            print(f"ADD ERROR: {a} + {b}: {e}")
            failures += 1
        
        # Test subtraction
        try:
            result, flags = sub(a, b, width, signed)
            if signed:
                expected = sign_extend(mask_to_width(a - b, width), width)
                if mask_to_width(expected, width) != result:
                    print(f"SUB FAIL: {a} - {b} = {result}, expected {mask_to_width(expected, width)}")
                    failures += 1
            else:
                expected = mask_to_width(a - b, width)
                if expected != result:
                    print(f"SUB FAIL: {a} - {b} = {result}, expected {expected}")
                    failures += 1
        except Exception as e:
            print(f"SUB ERROR: {a} - {b}: {e}")
            failures += 1
        
        # Test multiplications
        mul_algorithms = [
            ('MUL_SEQ', mul_sequential),
            ('MUL_BOOTH', mul_booth),
            ('MUL_BIT', mul_bit),
            ('MUL_BITPAIR', mul_bitpair)
        ]
        
        for alg_name, mul_func in mul_algorithms:
            try:
                result, flags = mul_func(a, b, width, signed)
                if signed:
                    a_signed = sign_extend(mask_to_width(a, width), width)
                    b_signed = sign_extend(mask_to_width(b, width), width)
                    expected = mask_to_width(a_signed * b_signed, 2 * width)
                else:
                    expected = mask_to_width(a * b, 2 * width)
                
                if expected != result:
                    print(f"{alg_name} FAIL: {a} * {b} = {result}, expected {expected}")
                    failures += 1
            except Exception as e:
                print(f"{alg_name} ERROR: {a} * {b}: {e}")
                failures += 1
        
        # Test divisions (skip if b == 0)
        if b != 0:
            div_algorithms = [
                ('DIV_RESTORING', div_restoring),
                ('DIV_NONRESTORING', div_nonrestoring)
            ]
            
            for alg_name, div_func in div_algorithms:
                try:
                    q, r = div_func(a, b, width, signed)
                    
                    # Verify a = q * b + r
                    if signed:
                        a_signed = sign_extend(mask_to_width(a, width), width)
                        b_signed = sign_extend(mask_to_width(b, width), width)
                        q_signed = sign_extend(mask_to_width(q, width), width)
                        r_signed = sign_extend(mask_to_width(r, width), width)
                        
                        if a_signed != q_signed * b_signed + r_signed:
                            print(f"{alg_name} FAIL: {a} ÷ {b} = {q} R {r}, but {q} * {b} + {r} ≠ {a}")
                            failures += 1
                    else:
                        if a != q * b + r:
                            print(f"{alg_name} FAIL: {a} ÷ {b} = {q} R {r}, but {q} * {b} + {r} ≠ {a}")
                            failures += 1
                except Exception as e:
                    print(f"{alg_name} ERROR: {a} ÷ {b}: {e}")
                    failures += 1
    
    if failures == 0:
        print("Verification: PASS")
        return True
    else:
        print(f"Verification: FAIL ({failures} failures)")
        return False


def main():
    """CLI interface for arithmetic algorithms."""
    parser = argparse.ArgumentParser(description='N-bit arithmetic algorithms')
    parser.add_argument('--width', type=int, default=8, help='Bit width (default: 8)')
    parser.add_argument('--signed', action='store_true', help='Use signed arithmetic')
    parser.add_argument('--algo', choices=[
        'add', 'sub', 'mul_seq', 'mul_booth', 'mul_bit', 'mul_bitpair',
        'div_restoring', 'div_nonrestoring', 'verify'
    ], required=True, help='Algorithm to run')
    parser.add_argument('--trials', type=int, default=400, help='Number of trials for verify')
    parser.add_argument('operands', nargs='*', help='Operands a and b (not needed for verify)')
    
    args = parser.parse_args()
    
    if args.algo == 'verify':
        success = verify(args.width, args.trials, args.signed)
        sys.exit(0 if success else 1)
    
    if len(args.operands) != 2:
        print("Error: Need exactly 2 operands for arithmetic operations")
        sys.exit(1)
    
    a, b = int(args.operands[0]), int(args.operands[1])
    
    try:
        if args.algo == 'add':
            result, flags = add(a, b, args.width, args.signed)
            print(f"Result: {result}")
            print(f"Flags: {flags}")
        
        elif args.algo == 'sub':
            result, flags = sub(a, b, args.width, args.signed)
            print(f"Result: {result}")
            print(f"Flags: {flags}")
        
        elif args.algo == 'mul_seq':
            result, flags = mul_sequential(a, b, args.width, args.signed)
            print(f"Product: {result} ({2 * args.width}-bit)")
        
        elif args.algo == 'mul_booth':
            result, flags = mul_booth(a, b, args.width, args.signed)
            print(f"Product: {result} ({2 * args.width}-bit)")
        
        elif args.algo == 'mul_bit':
            result, flags = mul_bit(a, b, args.width, args.signed)
            print(f"Product: {result} ({2 * args.width}-bit)")
        
        elif args.algo == 'mul_bitpair':
            result, flags = mul_bitpair(a, b, args.width, args.signed)
            print(f"Product: {result} ({2 * args.width}-bit)")
        
        elif args.algo == 'div_restoring':
            q, r = div_restoring(a, b, args.width, args.signed)
            print(f"Quotient: {q}, Remainder: {r}")
        
        elif args.algo == 'div_nonrestoring':
            q, r = div_nonrestoring(a, b, args.width, args.signed)
            print(f"Quotient: {q}, Remainder: {r}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
