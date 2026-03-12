#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

const int MOD = 200003;
const int G = 2; // primitive root modulo MOD

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int N;
    cin >> N;
    vector<int> A(N);
    for (int i = 0; i < N; ++i) {
        cin >> A[i];
    }
    
    // Precompute log and exp tables for MOD-1 sized cyclic group
    int size = MOD - 1;
    vector<int> log_val(MOD, -1);
    vector<int> exp_val(size);
    long long cur = 1;
    for (int i = 0; i < size; ++i) {
        log_val[cur] = i;
        exp_val[i] = cur;
        cur = (cur * G) % MOD;
    }
    
    // Frequency of each exponent (0..MOD-2)
    vector<long long> freq_exp(size, 0);
    for (int x : A) {
        if (x == 0) continue;
        int e = log_val[x];
        freq_exp[e]++;
    }
    
    // Convolution using FFT size next power of two >= 2*size
    int conv_size = 1;
    while (conv_size < 2 * size) conv_size <<= 1;
    
    vector<double> real1(conv_size, 0.0), imag1(conv_size, 0.0);
    for (int i = 0; i < size; ++i) {
        real1[i] = freq_exp[i];
    }
    
    // FFT
    auto fft = [](vector<double>& real, vector<double>& imag, bool invert) {
        int n = real.size();
        for (int i = 1, j = 0; i < n; ++i) {
            int bit = n >> 1;
            for (; j & bit; bit >>= 1) j ^= bit;
            j ^= bit;
            if (i < j) {
                swap(real[i], real[j]);
                swap(imag[i], imag[j]);
            }
        }
        for (int len = 2; len <= n; len <<= 1) {
            double ang = 2 * M_PI / len * (invert ? -1 : 1);
            double wlen_r = cos(ang), wlen_i = sin(ang);
            for (int i = 0; i < n; i += len) {
                double wr = 1.0, wi = 0.0;
                for (int j = 0; j < len / 2; ++j) {
                    double u_r = real[i + j], u_i = imag[i + j];
                    double v_r = real[i + j + len / 2] * wr - imag[i + j + len / 2] * wi;
                    double v_i = real[i + j + len / 2] * wi + imag[i + j + len / 2] * wr;
                    real[i + j] = u_r + v_r;
                    imag[i + j] = u_i + v_i;
                    real[i + j + len / 2] = u_r - v_r;
                    imag[i + j + len / 2] = u_i - v_i;
                    double nwr = wr * wlen_r - wi * wlen_i;
                    wi = wr * wlen_i + wi * wlen_r;
                    wr = nwr;
                }
            }
        }
        if (invert) {
            for (int i = 0; i < n; ++i) {
                real[i] /= n;
                imag[i] /= n;
            }
        }
    };
    
    vector<double> real2 = real1, imag2 = imag1;
    fft(real1, imag1, false);
    fft(real2, imag2, false);
    for (int i = 0; i < conv_size; ++i) {
        double r = real1[i] * real2[i] - imag1[i] * imag2[i];
        double im = real1[i] * imag2[i] + imag1[i] * real2[i];
        real1[i] = r;
        imag1[i] = im;
    }
    fft(real1, imag1, true);
    
    vector<long long> conv(conv_size);
    for (int i = 0; i < conv_size; ++i) {
        conv[i] = (long long)(real1[i] + 0.5);
    }
    
    // Sum contributions from exponent sums
    long long total = 0;
    for (int s = 0; s < conv_size; ++s) {
        if (conv[s] == 0) continue;
        int exp_sum = s % size;
        int prod = exp_val[exp_sum]; // g^(e1+e2) mod MOD
        total += conv[s] * prod;
    }
    
    // Pairs where one element is zero
    long long zero_cnt = 0;
    for (int x : A) if (x == 0) zero_cnt++;
    long long non_zero = N - zero_cnt;
    total += zero_cnt * non_zero * 0; // Ai*Aj mod MOD = 0 if one is zero
    
    // Subtract i=j terms (each element with itself)
    for (int x : A) {
        if (x == 0) continue;
        int e = log_val[x];
        long long self_pair = (long long)x * x % MOD;
        total -= self_pair;
    }
    
    // Each pair counted twice in convolution
    total /= 2;
    
    cout << total << '\n';
    return 0;
}
