"""Prototype + verification of numpy's SeedSequence -> PCG64 seeding, to be ported to C++.

Ground truth: np.random.default_rng(seed).bit_generator.state for seeds 0,1,3,5,7,42,12345.
This script re-derives that state from scratch and must match exactly before anything gets
ported into soc_core.cpp.
"""
import numpy as np

MASK32 = 0xFFFFFFFF
XSHIFT = 16
INIT_A = 0x43b0d7e5
MULT_A = 0x931e8875
INIT_B = 0x8b51f9dd
MULT_B = 0x58f38ded
MIX_MULT_L = 0xca01f9dd
MIX_MULT_R = 0x4973f715


def hashmix(value, hash_const):
    value ^= hash_const[0]
    hash_const[0] = (hash_const[0] * MULT_A) & MASK32
    value = (value * hash_const[0]) & MASK32
    value ^= value >> XSHIFT
    return value & MASK32


def mix(x, y):
    result = ((MIX_MULT_L * x) - (MIX_MULT_R * y)) & MASK32
    result ^= result >> XSHIFT
    return result & MASK32


def mix_entropy(pool_size, entropy):
    mixer = [0] * pool_size
    hash_const = [INIT_A]
    for i in range(pool_size):
        if i < len(entropy):
            mixer[i] = hashmix(entropy[i], hash_const)
        else:
            mixer[i] = hashmix(0, hash_const)
    for i_src in range(pool_size):
        for i_dst in range(pool_size):
            if i_src != i_dst:
                mixer[i_dst] = mix(mixer[i_dst], hashmix(mixer[i_src], hash_const))
    for i_src in range(pool_size, len(entropy)):
        for i_dst in range(pool_size):
            mixer[i_dst] = mix(mixer[i_dst], hashmix(entropy[i_src], hash_const))
    return mixer


def generate_state_u32(pool, n_words):
    hash_const = INIT_B
    out = [0] * n_words
    for i_dst in range(n_words):
        data_val = pool[i_dst % len(pool)]
        data_val ^= hash_const
        hash_const = (hash_const * MULT_B) & MASK32
        data_val = (data_val * hash_const) & MASK32
        data_val ^= data_val >> XSHIFT
        out[i_dst] = data_val & MASK32
    return out


def seed_to_state_inc(seed, pool_size=4):
    entropy = [seed & MASK32]  # seed < 2**32 for our range (0..9999); single word suffices
    pool = mix_entropy(pool_size, entropy)
    words32 = generate_state_u32(pool, 8)  # need 4 uint64 = 8 uint32
    u64 = [(words32[2 * i] | (words32[2 * i + 1] << 32)) for i in range(4)]
    initstate = (u64[0] << 64) | u64[1]
    initseq = (u64[2] << 64) | u64[3]

    MASK128 = (1 << 128) - 1
    inc = ((initseq << 1) | 1) & MASK128
    mult = 0x2360ED051FC65DA44385DF649FCCF645
    state = 0
    state = (state * mult + inc) & MASK128
    state = (state + initstate) & MASK128
    state = (state * mult + inc) & MASK128
    return state, inc


if __name__ == "__main__":
    seeds = [0, 1, 3, 5, 7, 42, 12345]
    ok = True
    for s in seeds:
        rng = np.random.default_rng(s)
        st = rng.bit_generator.state["state"]
        want_state, want_inc = st["state"], st["inc"]
        got_state, got_inc = seed_to_state_inc(s)
        match = (got_state == want_state) and (got_inc == want_inc)
        ok &= match
        print(f"seed={s:6d}  state {'OK' if got_state==want_state else 'MISMATCH'}  "
              f"inc {'OK' if got_inc==want_inc else 'MISMATCH'}")
        if not match:
            print(f"   want_state={want_state:#034x} got_state={got_state:#034x}")
            print(f"   want_inc  ={want_inc:#034x} got_inc  ={got_inc:#034x}")
    print("ALL MATCH" if ok else "MISMATCHES FOUND")
