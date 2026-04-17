import sys
import os
import random

MOD = 10**9 + 7

def solve_for_N(N):
    """Return answer for given N using DP on bits."""
    # dp[carry] = number of ways for processed bits
    dp = [0, 0]
    dp[0] = 1  # initially no carry
    
    # Process bits from LSB to MSB
    for i in range(0, 61):  # 10^18 < 2^60
        bit = (N >> i) & 1
        new_dp = [0, 0]
        
        # a_i, b_i in {0,1}
        # (a_i xor b_i) = u_i, (a_i + b_i + carry_in) = v_i + 2*carry_out
        # We need u_i <= bit_N and v_i <= bit_N for this position?
        # Actually constraint is u <= N and v <= N overall, not per bit.
        # Standard approach: count pairs (u,v) with u <= N, v <= N
        # and there exist a,b >=0 with a xor b = u, a + b = v.
        # Condition: u <= v and (v - u) is even and non-negative.
        # But we need to count via bit DP.
        
        # Alternative known combinatorial fact:
        # For fixed N, answer = sum_{k=0..N} f(k) where f(k)=#{(a,b): a xor b = k, a+b = k+2t}
        # Actually known solution: answer = number of pairs (u,v) with u|v = u+v? Not exactly.
        
        # Let's implement the standard bit DP from editorial of typical problem:
        # Count pairs (a,b) with a xor b <= N and a+b <= N.
        # But we need pairs (u,v) with u<=N, v<=N and existence of a,b.
        # Condition: u <= v and (v-u) even.
        # Also (u & (v-u)//2) == 0.
        # Because if a xor b = u, a+b = v, then let x = (v-u)//2 = a & b, y = u = a xor b.
        # Then a = x + (y if no carry?) Actually a = x + (y if ...). Known: a = (v+u)/2, b=(v-u)/2.
        # Wait: v = a+b, u = a xor b => v-u = 2*(a & b) >=0 and even.
        # So given u,v, we can recover a = (v+u)/2, b=(v-u)/2 must be integers >=0.
        # So condition: v >= u, (v-u) even, and (v+u)/2, (v-u)/2 are nonnegative integers (automatically if v>=u).
        # Also (v-u)/2 & u == 0 because (a & b) & (a xor b) = 0.
        # So count pairs (u,v): 0<=u<=v<=N, v-u even, ((v-u)//2 & u) == 0.
        
        # Now we can DP over bits of u and v with N constraint.
        # dp[pos][carry_u][carry_v] but that's large.
        # Actually we can DP on bits of N, processing u,v bits simultaneously with constraint <= N.
        # Let's define dp[eq_u][eq_v] = count where eq_u means prefix of u equals prefix of N so far,
        # similarly eq_v for v.
        # But v >= u constraint: we need to ensure that.
        # We can incorporate v >= u by another state cmp: 0 = u==v so far, 1 = u<v already.
        
        # This is getting complex. Let's implement known solution from AtCoder problem "Xor Sum 2"?
        # Actually this is exactly AtCoder ABC 098 D? No.
        
        # Let's search memory: This is AtCoder ABC 197 F? No.
        # I recall a problem: count pairs (u,v) with u<=N, v<=N and (u & (v-u)) == 0 and v>=u.
        # Let's implement DP for that.
        
        # dp[i][tight_u][tight_v][cmp] where cmp: 0 = u==v, 1 = u<v, 2 = u>v (invalid)
        # We only allow cmp=0 or 1.
        # bits of u, v, N from MSB to LSB.
        pass
    
    # Actually, known closed form: answer = sum_{k=0..N} (number of pairs (a,b) with a xor b = k)
    # But that's not easier.
    
    # Given time, let's implement brute for small N for verification, but we need fast for 10^18.
    # Let's implement the combinatorial DP on bits:
    # Let f(N) = #{(a,b): a xor b <= N, a+b <= N}
    # But we need #{(u,v): exists a,b with u=a xor b, v=a+b, u<=N, v<=N}
    # That's same as #{(a,b): a xor b <= N, a+b <= N} because mapping (a,b)->(u,v) is bijection onto valid (u,v).
    # Because given valid (u,v) there is unique (a,b) = ((v+u)/2, (v-u)/2).
    # So we just need to count pairs (a,b) >=0 with a xor b <= N and a+b <= N.
    
    # Now count pairs (a,b) with a xor b <= N and a+b <= N.
    # Bit DP: dp[pos][carry_xor][carry_sum] where carry_xor, carry_sum are 0/1 indicating whether prefix of a xor b is already less than prefix of N, similarly for a+b.
    # Actually we need two tightness flags: tight_xor, tight_sum.
    # dp[pos][tx][ts] = count.
    # iterate over bits a_bit, b_bit in {0,1}.
    # xor_bit = a_bit ^ b_bit, sum_bit = (a_bit + b_bit + carry) % 2, new_carry = (a_bit + b_bit + carry) // 2.
    # Wait sum is a+b, not per bit with carry? We need to handle full binary addition with carry across bits.
    # So we need carry state for sum.
    
    # Let's implement DP[pos][carry][tight_xor][tight_sum].
    # pos from 60 down to 0.
    # At pos, N_bit = (N>>pos)&1.
    # For a_bit, b_bit in {0,1}:
    #   xor_bit = a_bit ^ b_bit
    #   s = a_bit + b_bit + carry
    #   sum_bit = s & 1
    #   new_carry = s >> 1
    #   if tight_xor and xor_bit > N_bit: continue
    #   if tight_sum and sum_bit > N_bit: continue
    #   new_tight_xor = tight_xor and (xor_bit == N_bit)
    #   new_tight_sum = tight_sum and (sum_bit == N_bit)
    #   dp[pos-1][new_carry][new_tight_xor][new_tight_sum] += dp[pos][carry][tight_xor][tight_sum]
    
    # Initialize dp[60][0][1][1] = 1.
    # Answer = sum over dp[-1][carry][tx][ts] (pos=-1) all states.
    
    # But pos from 60 down to 0, we need 61 bits because 10^18 < 2^60.
    # Actually 2^60 ~ 1.15e18, so 60 bits enough. Let's use 61 bits for safety.
    
    max_bit = 60
    dp = [[[0]*2 for _ in range(2)] for __ in range(2)]  # dp[carry][tight_xor][tight_sum]
    dp[0][1][1] = 1
    
    for pos in range(max_bit, -1, -1):
        N_bit = (N >> pos) & 1
        new_dp = [[[0]*2 for _ in range(2)] for __ in range(2)]
        for carry in (0,1):
            for tight_xor in (0,1):
                for tight_sum in (0,1):
                    val = dp[carry][tight_xor][tight_sum]
                    if val == 0:
                        continue
                    for a_bit in (0,1):
                        for b_bit in (0,1):
                            xor_bit = a_bit ^ b_bit
                            if tight_xor and xor_bit > N_bit:
                                continue
                            s = a_bit + b_bit + carry
                            sum_bit = s & 1
                            if tight_sum and sum_bit > N_bit:
                                continue
                            new_carry = s >> 1
                            new_tight_xor = tight_xor and (xor_bit == N_bit)
                            new_tight_sum = tight_sum and (sum_bit == N_bit)
                            new_dp[new_carry][new_tight_xor][new_tight_sum] = (
                                new_dp[new_carry][new_tight_xor][new_tight_sum] + val) % MOD
        dp = new_dp
    
    ans = 0
    for carry in (0,1):
        for tx in (0,1):
            for ts in (0,1):
                ans = (ans + dp[carry][tx][ts]) % MOD
    return ans

def generate_one(rand, N_limit):
    """Generate one valid N."""
    # generate N in [1, N_limit]
    # distribution: mix small, large, random
    r = rand.random()
    if r < 0.2:
        N = rand.randint(1, 100)
    elif r < 0.4:
        N = rand.randint(1, 10**6)
    elif r < 0.6:
        N = rand.randint(10**12, min(10**18, N_limit))
    else:
        # full range
        N = rand.randint(1, N_limit)
    return N

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    N_limit = 10**18
    
    for idx in range(args.num):
        N = generate_one(random, N_limit)
        # write to file
        filename = os.path.join(args.out_dir, f'test_{idx:03d}.in')
        with open(filename, 'w') as f:
            f.write(str(N) + '\n')

if __name__ == '__main__':
    main()
